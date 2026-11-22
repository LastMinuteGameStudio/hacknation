"""Wykaz zbiorczy AED (wzór: tasks/dga.py, create_main_dga_resource_task).

1. create_main_aed_resource_task: zbiera opublikowane zasoby z flagą „Wykaz AED” od wszystkich dostawców, scala je
   (aed/merge.py), zapisuje CSV i XLSX, tworzy nowy zasób w zbiorze „Defibrylatory AED: wykaz zbiorczy”
   (zbiór powstaje przy pierwszym uruchomieniu) i planuje krok 2.
2. finalize_main_aed_resource_task: czeka, aż portal zwaliduje nowy zasób (plik, link, dane). Po sukcesie zapisuje
   AggregatedAEDInfo i usuwa poprzedni wykaz zbiorczy; po błędzie albo po wyczerpaniu prób usuwa nowy zasób,
   a poprzedni wykaz zostaje.

Ręcznie: `python manage.py shell -c "from mcod.resources.tasks import create_main_aed_resource_task as t; t.delay()"`
albo synchronicznie `t.apply()`. Harmonogram: celeryapp.py, „aed_main_resource_creation” (codziennie 3:45).
"""

import logging
from typing import List, Optional

from django.apps import apps

from mcod.core.tasks import extended_shared_task
from mcod.resources.aed_utils import (
    build_main_aed_list,
    clean_up_main_aed,
    create_main_aed_resource,
    get_aed_source_resources,
    summary_from_result,
    update_aggregated_aed_info,
    write_main_aed_files,
)
from mcod.resources.dga_utils import (
    FailedValidationException,
    PendingValidationException,
    check_all_resource_validations_status,
)

logger = logging.getLogger("mcod")

FINALIZE_COUNTDOWN = 20  # s, pierwsze sprawdzenie walidacji nowego zasobu


@extended_shared_task(
    atomic=False,
    name="mcod.resources.tasks.create_main_aed_resource_task",
)
def create_main_aed_resource_task() -> Optional[dict]:
    logger.info("Wykaz zbiorczy AED: start.")
    wynik = build_main_aed_list(get_aed_source_resources())
    summary = summary_from_result(wynik)
    if not wynik.dolaczone:
        logger.warning("Wykaz zbiorczy AED: brak poprawnych wykazów dostawców, poprzedni wykaz zostaje.")
        return summary

    csv_path, xlsx_path = write_main_aed_files(wynik)
    resource_pk: Optional[int] = None
    dataset_pk: Optional[int] = None
    try:
        resource_pk, dataset_pk = create_main_aed_resource(csv_path, xlsx_path, wynik)
    except Exception:
        logger.exception("Wykaz zbiorczy AED: nie udało się utworzyć zasobu.")
        clean_up_main_aed(resource_pk, dataset_pk, (csv_path, xlsx_path))
        raise
    finally:
        # pliki trafiły do magazynu zasobów portalu, kopie robocze nie są potrzebne
        clean_up_main_aed(None, None, (csv_path, xlsx_path))

    finalize_main_aed_resource_task.apply_async(
        args=(resource_pk, dataset_pk, summary), countdown=FINALIZE_COUNTDOWN
    )
    summary["resource_id"] = resource_pk
    return summary


@extended_shared_task(
    max_retries=10,
    atomic=False,
    retry_countdown=30,
    retry_on_errors=(PendingValidationException,),
    bind=True,
    name="mcod.resources.tasks.finalize_main_aed_resource_task",
)
def finalize_main_aed_resource_task(self, resource_pk: int, dataset_pk: Optional[int], summary: dict) -> None:
    Resource = apps.get_model("resources", "Resource")
    resource = Resource.objects.get(pk=resource_pk)
    try:
        check_all_resource_validations_status(resource)
    except PendingValidationException:
        if self.request.retries >= self.max_retries:
            logger.error("Wykaz zbiorczy AED: walidacja zasobu %s nie skończyła się, usuwam go.", resource_pk)
            clean_up_main_aed(resource_pk, dataset_pk)
        raise
    except FailedValidationException:
        logger.error("Wykaz zbiorczy AED: zasób %s nie przeszedł walidacji portalu, usuwam go.", resource_pk)
        clean_up_main_aed(resource_pk, dataset_pk)
        raise
    info = update_aggregated_aed_info(resource, summary)
    logger.info("Wykaz zbiorczy AED gotowy: zasób %s, %s AED z %s wykazów, %s duplikatów, licencja %s.",
                resource_pk, info.records_count, info.sources_count, info.duplicates_count, info.license_name)


__all__: List[str] = ["create_main_aed_resource_task", "finalize_main_aed_resource_task"]
