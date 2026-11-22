"""Wykaz AED w portalu: wybór zasobów, walidacja zasobu, zadanie tworzące wykaz zbiorczy (z bazą, styl test_main_dga.py).

Czysta logika scalania jest w test_aed_merge.py. Tu odczyt pliku zasobu jest podmieniony (mock), żeby testy
nie zależały od magazynu plików; sprawdzamy integrację z modelami i zadaniami.
"""

import csv
import io
from unittest import mock

import pytest
from django.test import override_settings

from mcod.datasets.factories import DatasetFactory
from mcod.organizations.factories import OrganizationFactory
from mcod.resources.aed.reader import read_table
from mcod.resources.aed_utils import (
    build_main_aed_list,
    get_aed_source_resources,
    get_main_aed_resource,
    summary_from_result,
    update_aggregated_aed_info,
    validate_aed_resource,
)
from mcod.resources.factories import ResourceFactory
from mcod.resources.models import AggregatedAEDInfo, Resource
from mcod.resources.tasks import create_main_aed_resource_task

CC_BY = 2
CC_BY_NC = 4


def _rekord(id_aed, lat, lon, **kw):
    r = {
        "id_aed": id_aed, "szerokosc_geograficzna": lat, "dlugosc_geograficzna": lon, "nazwa_obiektu": "Urząd",
        "nazwa_ulicy": "Rynek", "miejscowosc": "Krosno", "wewnatrz_budynku": "true", "dostepnosc": "publiczny",
        "dostepny_24_7": "tak", "status": "sprawny", "data_weryfikacji": "2026-11-01", "dysponent_nazwa": "Gmina",
        "zrodlo_danych": "dysponent", "data_aktualizacji": "2026-11-21T10:00:00",
    }
    r.update(kw)
    return r


def _tabela(rekordy):
    buf = io.StringIO(newline="")
    kolumny = list(dict.fromkeys(k for r in rekordy for k in r))
    w = csv.DictWriter(buf, fieldnames=kolumny, restval="", lineterminator="\r\n")
    w.writeheader()
    w.writerows(rekordy)
    return read_table(buf.getvalue().encode("utf-8"), "csv")


def _wykaz(instytucja, license_chosen=CC_BY, **kw):
    org = OrganizationFactory(title=instytucja)
    ds = DatasetFactory(organization=org, license_chosen=license_chosen, status="published")
    params = dict(dataset=ds, status="published", is_aed_list=True, format="csv")
    params.update(kw)
    return ResourceFactory(**params)


@pytest.fixture
def trzy_wykazy():
    a = _wykaz("Gmina Krosno")
    b = _wykaz("Szpital Krosno")
    c = _wykaz("Fundacja", license_chosen=CC_BY_NC)
    tabele = {
        a.pk: _tabela([_rekord("a1", "49.693000", "21.765000", numer_seryjny="SN-1")]),
        b.pk: _tabela([_rekord("b1", "49.693100", "21.765000"), _rekord("b2", "49.900000", "21.900000",
                                                                         numer_seryjny="sn-1")]),
        c.pk: _tabela([_rekord("c1", "50.100000", "21.000000")]),
    }
    with mock.patch("mcod.resources.aed_utils.read_aed_resource_table", side_effect=lambda r: tabele[r.pk]):
        yield a, b, c


@pytest.mark.django_db
def test_zrodla_tylko_opublikowane_z_flaga():
    z_flaga = _wykaz("A")
    _wykaz("B", status="draft")
    ResourceFactory(status="published", is_aed_list=False)
    assert list(get_aed_source_resources()) == [z_flaga]


@pytest.mark.django_db
def test_scalanie_dostawcow_duplikaty_i_licencja(trzy_wykazy):
    a, b, c = trzy_wykazy
    wynik = build_main_aed_list(get_aed_source_resources())
    dup = {r["id_aed"]: r["duplikat_id_aed"] for r in wynik.rekordy}
    assert dup == {"a1": "", "b1": "a1", "b2": "a1"}  # b1 po odległości, b2 po numerze seryjnym
    assert [p.zrodlo.zasob_id for p in wynik.pominiete] == [c.pk]
    assert "licencji" in wynik.pominiete[0].powod
    assert wynik.rekordy[0]["zrodlo_instytucja"] == "Gmina Krosno"
    assert wynik.rekordy[0]["licencja_zrodla"] == "CC BY 4.0"


@pytest.mark.django_db
def test_walidacja_zasobu_z_licencja_by_nc(trzy_wykazy):
    _, _, c = trzy_wykazy
    kody = [k.kod for k in validate_aed_resource(c)]
    assert kody[0] == "LICENCJA"


@pytest.mark.django_db
def test_zadanie_tworzy_wykaz_zbiorczy(trzy_wykazy, tmp_path):
    org = OrganizationFactory(title="Ministerstwo Cyfryzacji")
    with override_settings(MAIN_AED_DATASET_OWNER_ORGANIZATION_PK=org.pk, MAIN_AED_RESOURCE_CREATION_ROOT=str(tmp_path)), \
            mock.patch("mcod.resources.tasks.aed.finalize_main_aed_resource_task.apply_async") as finalize:
        summary = create_main_aed_resource_task()

    nowy = Resource.objects.get(pk=summary["resource_id"])
    assert nowy.is_aed_list is False
    assert nowy.dataset.title == "Defibrylatory AED: wykaz zbiorczy"
    assert nowy.dataset.organization == org
    assert nowy.main_file.name.endswith(".csv")
    assert [f.format for f in nowy.other_files] == ["xlsx"]
    assert summary["records_count"] == 3 and summary["duplicates_count"] == 2
    assert summary["sources_count"] == 2 and summary["skipped_count"] == 1
    assert summary["license_name"] == "CC BY 4.0"
    assert finalize.call_args.kwargs["args"][0] == nowy.pk

    # krok 2 (po walidacji portalu): AggregatedAEDInfo wskazuje nowy zasób, stary jest usuwany
    info = update_aggregated_aed_info(nowy, summary)
    assert get_main_aed_resource() == nowy
    assert info.records_count == 3 and info.license_name == "CC BY 4.0"
    with override_settings(MAIN_AED_RESOURCE_CREATION_ROOT=str(tmp_path)), \
            mock.patch("mcod.resources.tasks.aed.finalize_main_aed_resource_task.apply_async"):
        summary2 = create_main_aed_resource_task()
    drugi = Resource.objects.get(pk=summary2["resource_id"])
    assert drugi.dataset == nowy.dataset  # ten sam zbiór
    update_aggregated_aed_info(drugi, summary2)
    assert AggregatedAEDInfo.objects.count() == 1
    assert not Resource.objects.filter(pk=nowy.pk).exists()


@pytest.mark.django_db
def test_bez_poprawnych_wykazow_nic_nie_tworzy():
    zly = _wykaz("Fundacja", license_chosen=CC_BY_NC)
    with mock.patch("mcod.resources.aed_utils.read_aed_resource_table",
                    return_value=_tabela([_rekord("x1", "50.0", "20.0")])):
        summary = create_main_aed_resource_task()
    assert "resource_id" not in summary
    assert summary["skipped_count"] == 1
    assert summary_from_result(build_main_aed_list([]))["records_count"] == 0
    assert zly.pk


def test_schemat_wykazu_aed_wszystkie_kolumny_tekstowe():
    """Zgadnięte typy (integer, date) nie mogą odrzucać pliku v0.5 przed walidacją zakresu."""
    from mcod.resources.tasks.process_resource_file_data import _aed_list_tabular_data_schema

    tds = {
        "fields": [
            {"name": "nr_budynku", "type": "integer", "format": "default"},
            {"name": "lon", "type": "date", "format": "any"},
        ],
        "missingValues": [""],
    }
    wynik = _aed_list_tabular_data_schema(tds)
    assert [(f["name"], f["type"], f["format"]) for f in wynik["fields"]] == [
        ("nr_budynku", "string", "default"),
        ("lon", "string", "default"),
    ]
    assert wynik["missingValues"] == [""]
    assert tds["fields"][0]["type"] == "integer"
