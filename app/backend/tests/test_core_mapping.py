from pathlib import Path

import pytest

from aed_core.mapping import norm, suggest_mapping
from aed_core.parsers import read_table
from aed_core.schema import load_schema
from aed_core.types import Table

FIX = Path(__file__).parent / "fixtury"
SCHEMA = load_schema(Path(__file__).resolve().parents[3] / "zakres-danych")


def mapa(nazwa: str, previous=None) -> dict:
    t = read_table((FIX / nazwa).read_bytes(), nazwa)
    return {m.kolumna: m.pole for m in suggest_mapping(t, SCHEMA, previous)}


def test_norm():
    assert norm(" Długość_geograficzna ") == "dlugoscgeograficzna"
    assert norm("Dostępny 24/7") == "dostepny24/7"


@pytest.mark.parametrize("plik", ["krosno.csv", "marki.csv", "marki.xlsx"])
def test_krosno_marki(plik):
    m = mapa(plik)
    assert m["Długość geograficzna"] == "dlugosc_geograficzna"
    assert m["Szerokość geograficzna"] == "szerokosc_geograficzna"
    assert m["Nazwa"] is None  # wszędzie „Defibrylator”
    assert m["Lokalizacja"] == "nazwa_obiektu"
    assert m["Adres"] == "_adres_pelny"
    assert m["Numer Id"] == "id_zrodlowe"


def test_legionowo_wzorcowy():
    m = mapa("legionowo.csv")
    for k, v in m.items():
        assert v == ("nazwa_obiektu" if k == "nazwa" else k)


@pytest.mark.parametrize("plik", ["przemysl.csv", "przemysl_2024.csv"])
def test_przemysl(plik):
    m = mapa(plik)
    assert m["geometry"] == "_geometria"
    assert m["street"] == "nazwa_ulicy" and m["home_number"] == "nr_budynku"
    assert m["city"] == "miejscowosc" and m["postcode"] == "kod_pocztowy"
    assert m["name"] == "nazwa_obiektu"
    assert m["description"] is None and m["category"] is None


def test_warszawa():
    m = mapa("warszawa_19115.geojson")
    assert m["geometry"] == "_geometria"
    assert m["device_availability"] == "dostepny_24_7"
    assert m["device_location"] == "wewnatrz_budynku"
    assert m["device_public_access"] == "dostepnosc"
    assert m["device_access_description"] == "_godziny"
    assert m["application_status"] is None  # status zgłoszenia, nie stan AED


def test_kazde_pole_najwyzej_raz_i_kazda_kolumna_ma_propozycje():
    for plik in ["krosno.csv", "przemysl.csv", "warszawa_19115.geojson"]:
        t = read_table((FIX / plik).read_bytes(), plik)
        s = suggest_mapping(t, SCHEMA)
        assert [x.kolumna for x in s] == t.columns
        pola = [x.pole for x in s if x.pole]
        assert len(pola) == len(set(pola))
        assert all(0 <= x.pewnosc <= 1 for x in s)


def test_analiza_zawartosci_bez_nazw():
    t = Table(columns=["A", "B", "C", "D", "E"], rows=[
        ["52.395198", "20.931382", "05-120", "pn-pt 08:00-16:00", "ul. Jasna 5, 38-400 Krosno"],
        ["52.421807", "20.939056", "05-119", "24h", "ul. Lwowska 1, 38-400 Krosno"],
        ["52.400177", "20.917295", "05-120", "8:00-15:00", "Rynek 1, 38-400 Krosno"],
    ])
    m = {x.kolumna: x.pole for x in suggest_mapping(t, SCHEMA)}
    assert m == {"A": "szerokosc_geograficzna", "B": "dlugosc_geograficzna", "C": "kod_pocztowy",
                 "D": "_godziny", "E": "_adres_pelny"}


def test_geometria_wkt_i_para():
    t = Table(columns=["polozenie", "wsp"], rows=[["POINT(21.0 52.2)", "52.1, 21.1"], ["POINT(21.1 52.3)", "52.2, 21.2"]])
    s = suggest_mapping(t, SCHEMA)
    assert s[0].pole == "_geometria"
    assert s[1].pole is None or s[1].pole == "_geometria"


def test_poprzednie_mapowanie_ma_pierwszenstwo():
    m = mapa("krosno.csv", previous={"Nazwa": "uwagi", "Numer Id": None, "Lokalizacja": "opis_lokalizacji"})
    assert m["Nazwa"] == "uwagi"
    assert m["Numer Id"] is None
    assert m["Lokalizacja"] == "opis_lokalizacji"


def test_podobne_nazwy():
    t = Table(columns=["Szerokosc geogr.", "Dlugosc geogr.", "Miejscowość", "Kod pocztowy", "Ulica", "Nr domu"],
              rows=[["50.0", "20.0", "Kraków", "30-001", "Floriańska", "1"]])
    m = {x.kolumna: x.pole for x in suggest_mapping(t, SCHEMA)}
    assert m["Szerokosc geogr."] == "szerokosc_geograficzna"
    assert m["Dlugosc geogr."] == "dlugosc_geograficzna"
    assert m["Nr domu"] == "nr_budynku" and m["Ulica"] == "nazwa_ulicy"
