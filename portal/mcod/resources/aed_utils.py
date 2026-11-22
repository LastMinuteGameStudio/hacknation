"""Wykaz AED w portalu: integracja czystej logiki (mcod/resources/aed/) z modelami Django.

Wzór: dga_utils.py (wykaz chronionych danych DGA). Różnice:
- źródłem są zasoby z flagą `Resource.is_aed_list` od wielu dostawców (nie jeden zasób na instytucję),
- treść jest scalana rekord po rekordzie w zakresie v0.5, z kolumnami pochodzenia i oznaczeniem duplikatów,
- wynik to zasób z plikiem głównym CSV (RFC 4180) i plikiem dodatkowym XLSX,
- do wykazu trafiają tylko wykazy bez błędów walidacji i z licencją CC0 1.0 albo CC BY 4.0.

Opis: portal/WYKAZ-AED.md.
"""

import datetime
import logging
import os
from pathlib import Path
from typing import TYPE_CHECKING, List, Optional, Tuple

from django.apps import apps
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import transaction

from mcod.resources.aed.merge import (
    Pominiety,
    WynikScalania,
    ZrodloWykazu,
    powod_licencji,
    scal_wykazy,
    to_csv_bytes,
    to_xlsx_bytes,
)
from mcod.resources.aed.reader import ROZSZERZENIA, BladOdczytu, Tabela, read_table
from mcod.resources.aed.schema import load_zakres
from mcod.resources.aed.validation import BLAD, Komunikat, bledy, validate_table

if TYPE_CHECKING:
    from mcod.datasets.models import Dataset
    from mcod.resources.models import AggregatedAEDInfo, Resource

logger = logging.getLogger("mcod")

XLSX_MIMETYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


class AEDListValidationError(Exception):
    """Zasób z flagą „Wykaz AED” nie spełnia zakresu v0.5 (albo ma licencję, która wyklucza go z wykazu)."""

    def __init__(self, komunikaty: List[Komunikat]):
        self.komunikaty = komunikaty
        super().__init__([k.as_dict() for k in komunikaty])


# --- wykaz zbiorczy -------------------------------------------------------------------------------


def get_aggregated_aed_info() -> Optional["AggregatedAEDInfo"]:
    AggregatedAEDInfo = apps.get_model("resources", "AggregatedAEDInfo")
    return AggregatedAEDInfo.objects.last()


def get_main_aed_resource() -> Optional["Resource"]:
    info = get_aggregated_aed_info()
    return info.main_aed_resource if info else None


def get_main_aed_dataset() -> Optional["Dataset"]:
    info = get_aggregated_aed_info()
    return info.main_aed_dataset if info else None


# --- źródła ---------------------------------------------------------------------------------------


def get_aed_source_resources():
    """Opublikowane zasoby z flagą „Wykaz AED” (bez wykazu zbiorczego), posortowane wg instytucji."""
    Resource = apps.get_model("resources", "Resource")
    main = get_main_aed_resource()
    return (
        Resource.objects.filter(is_aed_list=True, status="published")
        .exclude(id=main.pk if main else None)
        .select_related("dataset__organization")
        .order_by("dataset__organization__title", "id")
    )


def resource_extension(resource: "Resource") -> str:
    ext = (resource.format or "").lower()
    if ext not in ROZSZERZENIA and resource.main_file:
        ext = os.path.splitext(resource.main_file.name)[1].lower().lstrip(".")
    return ext


def read_aed_resource_table(resource: "Resource") -> Tabela:
    """Czyta surowy plik główny zasobu (nie tabular_data portalu, żeby nie zmieniać typów wartości)."""
    if not resource.main_file:
        raise BladOdczytu("Zasób nie ma pliku głównego (wykaz AED musi być plikiem CSV albo XLSX).")
    try:
        with resource.main_file.open("rb") as f:
            content = f.read()
    except (OSError, ValueError) as exc:
        raise BladOdczytu(f"Nie udało się odczytać pliku głównego zasobu: {exc}")
    return read_table(content, resource_extension(resource))


def resource_license_name(resource: "Resource") -> str:
    return resource.dataset.license_name or ""


def resource_url(resource: "Resource") -> str:
    try:
        return resource.frontend_absolute_url
    except Exception:  # noqa: BLE001 - adres jest informacyjny, brak nie blokuje scalania
        return f"{settings.BASE_URL}/pl/dataset/{resource.dataset_id}/resource/{resource.pk}"


def resource_to_source(resource: "Resource") -> ZrodloWykazu:
    zmiana = resource.modified or resource.created
    return ZrodloWykazu(
        instytucja=resource.institution.title,
        zasob_id=resource.pk,
        url=resource_url(resource),
        data_aktualizacji=zmiana.replace(microsecond=0).isoformat() if zmiana else "",
        licencja=resource_license_name(resource),
        tabela=read_aed_resource_table(resource),
    )


def validate_aed_resource(resource: "Resource") -> List[Komunikat]:
    """Walidacja zasobu z flagą: zakres v0.5 i licencja. Wywoływana w process_resource_file_data_task."""
    try:
        tabela = read_aed_resource_table(resource)
    except BladOdczytu as exc:
        return [Komunikat(BLAD, "ODCZYT", str(exc))]
    komunikaty = validate_table(tabela, load_zakres())
    powod = powod_licencji(resource_license_name(resource))
    if powod:
        komunikaty.insert(0, Komunikat(BLAD, "LICENCJA", powod))
    return komunikaty


def validate_aed_resource_or_raise(resource: "Resource") -> List[Komunikat]:
    komunikaty = validate_aed_resource(resource)
    if bledy(komunikaty):
        raise AEDListValidationError(bledy(komunikaty))
    for k in komunikaty:
        logger.info("Wykaz AED, zasób %s: %s %s", resource.pk, k.kod, k.komunikat)
    return komunikaty


def build_main_aed_list(resources) -> WynikScalania:
    zrodla: List[ZrodloWykazu] = []
    nieczytelne: List[Pominiety] = []
    for resource in resources:
        try:
            zrodla.append(resource_to_source(resource))
        except (BladOdczytu, OSError, ValueError) as exc:
            logger.warning("Wykaz AED: pomijam zasób %s, nie da się go odczytać: %s", resource.pk, exc)
            nieczytelne.append(Pominiety(
                ZrodloWykazu(resource.institution.title, resource.pk, resource_url(resource), "",
                             resource_license_name(resource), Tabela([], [], [])),
                f"Nie udało się odczytać pliku: {exc}",
            ))
    wynik = scal_wykazy(zrodla, load_zakres())
    wynik.pominiete.extend(nieczytelne)
    for p in wynik.pominiete:
        logger.warning("Wykaz AED: pominięty zasób %s (%s): %s", p.zrodlo.zasob_id, p.zrodlo.instytucja, p.powod)
    return wynik


def summary_from_result(wynik: WynikScalania) -> dict:
    """Podsumowanie scalania (JSON, przekazywane do zadania finalizującego i zapisywane w AggregatedAEDInfo)."""
    return {
        "sources_count": len(wynik.dolaczone),
        "skipped_count": len(wynik.pominiete),
        "records_count": len(wynik.rekordy),
        "duplicates_count": wynik.liczba_duplikatow,
        "license_name": wynik.licencja,
        "report": {
            "dolaczone": [{"zasob_id": z.zasob_id, "instytucja": z.instytucja, "licencja": z.licencja,
                           "liczba_aed": len(z.tabela.wiersze)} for z in wynik.dolaczone],
            "pominiete": [{"zasob_id": p.zrodlo.zasob_id, "instytucja": p.zrodlo.instytucja, "powod": p.powod,
                           "bledy": [k.as_dict()["message"] for k in p.komunikaty[:10]]} for p in wynik.pominiete],
        },
    }


# --- pliki, zbiór i zasób wykazu zbiorczego -------------------------------------------------------


def write_main_aed_files(wynik: WynikScalania) -> Tuple[Path, Path]:
    katalog = Path(settings.MAIN_AED_RESOURCE_CREATION_ROOT)
    katalog.mkdir(parents=True, exist_ok=True)
    dzien = datetime.date.today().strftime("%Y%m%d")
    csv_path = katalog / f"{settings.MAIN_AED_FILE_NAME_PREFIX}-{dzien}.csv"
    xlsx_path = katalog / f"{settings.MAIN_AED_FILE_NAME_PREFIX}-{dzien}.xlsx"
    csv_path.write_bytes(to_csv_bytes(wynik))
    xlsx_path.write_bytes(to_xlsx_bytes(wynik, settings.MAIN_AED_XLSX_WORKSHEET_NAME))
    return csv_path, xlsx_path


def _license_fields(licencja: str) -> dict:
    """Licencja zbioru wykazu: CC0 1.0 albo CC BY 4.0 (Dataset.license_chosen)."""
    Dataset = apps.get_model("datasets", "Dataset")
    kod = Dataset.LICENSE_CC0 if licencja == "CC0 1.0" else Dataset.LICENSE_CC_BY
    return {"license_chosen": kod}


def create_main_aed_dataset(licencja: str) -> "Dataset":
    Organization = apps.get_model("organizations", "Organization")
    Dataset = apps.get_model("datasets", "Dataset")
    Category = apps.get_model("categories", "Category")
    Tag = apps.get_model("tags", "Tag")

    pk = settings.MAIN_AED_DATASET_OWNER_ORGANIZATION_PK
    if not pk:
        raise ObjectDoesNotExist("Ustaw MAIN_AED_DATASET_OWNER_ORGANIZATION_PK (instytucja, właściciel wykazu zbiorczego AED).")
    try:
        institution = Organization.objects.get(pk=pk)
    except Organization.DoesNotExist:
        raise ObjectDoesNotExist(f"Instytucja wykazu zbiorczego AED (pk={pk}) nie istnieje.")

    with transaction.atomic():
        dataset = Dataset.objects.create(
            title=settings.MAIN_AED_DATASET_DEFAULT_TITLE,
            notes=settings.MAIN_AED_DATASET_DEFAULT_DESC,
            organization=institution,
            update_notification_recipient_email=settings.MAIN_AED_DATASET_UPDATE_NOTIFICATION_EMAIL or "",
            has_dynamic_data=False,
            has_high_value_data=False,
            has_high_value_data_from_ec_list=False,
            has_research_data=False,
            update_frequency="daily",
            status="published",
            **_license_fields(licencja),
        )
        dataset.categories.set(Category.objects.filter(title__in=settings.MAIN_AED_DATASET_CATEGORIES_TITLES))
        jezyk = settings.LANGUAGES[0][0]
        dataset.tags.set([Tag.objects.get_or_create(name=n, language=jezyk)[0] for n in settings.MAIN_AED_DATASET_TAGS_NAMES])
        dataset.save()
    logger.info("Utworzono zbiór wykazu zbiorczego AED %s.", dataset.pk)
    return dataset


def _uploaded(path: Path, content_type: str) -> SimpleUploadedFile:
    return SimpleUploadedFile(name=path.name, content=path.read_bytes(), content_type=content_type)


def create_main_aed_resource(csv_path: Path, xlsx_path: Path, wynik: WynikScalania) -> Tuple[int, Optional[int]]:
    """Tworzy nowy zasób wykazu zbiorczego (CSV główny + XLSX dodatkowy). Zwraca (pk zasobu, pk nowego zbioru albo None).

    Stary zasób jest usuwany dopiero po udanej walidacji nowego (finalize_main_aed_resource), jak w DGA.
    """
    Resource = apps.get_model("resources", "Resource")
    ResourceFile = apps.get_model("resources", "ResourceFile")
    stary = get_main_aed_resource()
    dataset = get_main_aed_dataset()
    nowy_zbior: Optional[int] = None

    with transaction.atomic():
        if dataset is None:
            dataset = create_main_aed_dataset(wynik.licencja)
            nowy_zbior = dataset.pk
        else:
            for k, v in _license_fields(wynik.licencja).items():
                setattr(dataset, k, v)
            dataset.save()
        resource = Resource.objects.create(
            title=stary.title if stary else settings.MAIN_AED_RESOURCE_DEFAULT_TITLE,
            description=stary.description if stary else settings.MAIN_AED_RESOURCE_DEFAULT_DESC,
            dataset=dataset,
            has_dynamic_data=False,
            has_high_value_data=False,
            has_high_value_data_from_ec_list=False,
            has_research_data=False,
            contains_protected_data=False,
            is_aed_list=False,  # wykaz zbiorczy nie jest źródłem dla samego siebie
            status="published",
            data_date=datetime.date.today(),
        )
        # plik główny uruchamia walidację portalu (post_save ResourceFile), dodatkowy nie
        ResourceFile.objects.create(resource=resource, is_main=True, file=_uploaded(csv_path, "text/csv"))
        ResourceFile.objects.create(resource=resource, is_main=False, format="xlsx", file=_uploaded(xlsx_path, XLSX_MIMETYPE))
    logger.info("Utworzono zasób wykazu zbiorczego AED %s (%s AED).", resource.pk, len(wynik.rekordy))
    return resource.pk, nowy_zbior


def update_aggregated_aed_info(resource: "Resource", summary: dict) -> "AggregatedAEDInfo":
    """Zapisuje nowy zasób i podsumowanie w AggregatedAEDInfo, usuwa poprzedni wykaz zbiorczy."""
    AggregatedAEDInfo = apps.get_model("resources", "AggregatedAEDInfo")
    info = AggregatedAEDInfo.objects.last()
    stary = info.main_aed_resource if info else None
    with transaction.atomic():
        if info is None:
            info = AggregatedAEDInfo(resource=resource)
        info.resource = resource
        for k in ("sources_count", "skipped_count", "records_count", "duplicates_count", "license_name", "report"):
            setattr(info, k, summary[k])
        info.save()
        if stary and stary.pk != resource.pk:
            stary.delete()
            logger.info("Usunięto poprzedni zasób wykazu zbiorczego AED %s.", stary.pk)
    return info


def clean_up_main_aed(resource_pk: Optional[int], dataset_pk: Optional[int], paths: Tuple[Path, ...] = ()) -> None:
    Resource = apps.get_model("resources", "Resource")
    Dataset = apps.get_model("datasets", "Dataset")
    if resource_pk:
        Resource.raw.filter(pk=resource_pk).delete()
    if dataset_pk:
        Dataset.raw.filter(pk=dataset_pk).delete()
    for p in paths:
        try:
            os.remove(p)
        except OSError:
            pass
