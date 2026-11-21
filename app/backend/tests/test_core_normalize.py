from datetime import date
from pathlib import Path

import pytest

from aed_core.mapping import suggest_mapping
from aed_core.normalize import (
    MAX_GEOKODOWAN,
    formatuj,
    normalize_table,
    parsuj_adres,
    parsuj_geometrie,
    parsuj_godziny,
)
from aed_core.parsers import read_table
from aed_core.schema import load_schema
from aed_core.types import GeoResult, Provider, Table

FIX = Path(__file__).parent / "fixtury"
SCHEMA = load_schema(Path(__file__).resolve().parents[3] / "zakres-danych")
DZIS = date(2026, 11, 22)
UM = Provider(nazwa="Urząd Miasta Krosna", typ="jst", slug="krosno")


def norm_plik(nazwa, fixed=None, geocoder=None, mapping=None):
    t = read_table((FIX / nazwa).read_bytes(), nazwa)
    m = mapping or {s.kolumna: s.pole for s in suggest_mapping(t, SCHEMA)}
    return normalize_table(t, m, SCHEMA, UM, DZIS, geocoder, fixed)


def kody(r):
    return [m.kod for m in r.messages]


# --- funkcje pomocnicze ---------------------------------------------------------------------------


@pytest.mark.parametrize("tekst,oczek", [
    ("ul. Jasna, 38-400 Krosno", {"cecha_ulicy": "ulica", "nazwa_ulicy": "Jasna", "kod_pocztowy": "38-400", "miejscowosc": "Krosno"}),
    ("ul. Kazimierza Wielkiego 4, , 38-400 Krosno", {"nazwa_ulicy": "Kazimierza Wielkiego", "nr_budynku": "4"}),
    ("Al.. Piłsudskiego 95, 05-270 Marki", {"cecha_ulicy": "aleja", "nazwa_ulicy": "Piłsudskiego", "nr_budynku": "95"}),
    ("Rynek 1, 38-400 Krosno", {"nazwa_ulicy": "Rynek", "nr_budynku": "1"}),
    ("Krosno, ul. Jasna 5/3", {"miejscowosc": "Krosno", "nazwa_ulicy": "Jasna", "nr_budynku": "5/3"}),
    ("Krosno ul. Jasna 5 lok. 3", {"miejscowosc": "Krosno", "nr_budynku": "5", "nr_lokalu": "3"}),
])
def test_parsuj_adres(tekst, oczek):
    a = parsuj_adres(tekst)
    for k, v in oczek.items():
        assert a[k] == v


def test_parsuj_adres_nieudany():
    assert parsuj_adres("12") is None


@pytest.mark.parametrize("tekst,oczek", [
    ('{"type":"Point","coordinates":[22.7750936,49.7812096]}', ("49.7812096", "22.7750936")),
    ('{"type":"Point","coordinates":{"lat":"49.7812096","long":"22.7750936"}}', ("49.7812096", "22.7750936")),
    ('{"type":"Point","coordinates":[[21.0148748892902,52.2086170695684]]}', ("52.2086170695684", "21.0148748892902")),
    ("POINT(21.01 52.20)", ("52.20", "21.01")),
    ("52.1, 21.2", ("52.1", "21.2")),
    ("52,1; 21,2", ("52.1", "21.2")),
    ("coś", None),
])
def test_parsuj_geometrie(tekst, oczek):
    assert parsuj_geometrie(tekst) == oczek


def test_godziny_24():
    for t in ["24h", "Całodobowo", "24/7", "całą dobę"]:
        g = parsuj_godziny(t)
        assert g["dostepny_24_7"] == "tak" and g["godziny_pn"] == "X" and g["godziny_swieta"] == "X"


@pytest.mark.parametrize("tekst,pn,so", [
    ("Mo-Fr 08:00-16:00; Sa 09:00-13:00; Su off", "08:00-16:00", "09:00-13:00"),
    ("dni powszednie 07:00-17:30", "07:00-17:30", "zamkniete"),
    ("Poniedziałek - Piątek w godzinach od 8.30 do 15.30", "08:30-15:30", "zamkniete"),
    ("poniedziałek - piątek od 7;00 do 20;00", "07:00-20:00", "zamkniete"),
    ("pn-pt 8-16", "08:00-16:00", "zamkniete"),
    ("8-16", "08:00-16:00", "08:00-16:00"),
    ("Poniedziałek - Niedziela 8.00 - 18.00", "08:00-18:00", "08:00-18:00"),
])
def test_godziny(tekst, pn, so):
    g = parsuj_godziny(tekst)
    assert g["godziny_pn"] == pn and g["godziny_so"] == so and g["dostepny_24_7"] == "nie"


def test_godziny_wolny_tekst():
    assert parsuj_godziny("W godzinach otwarcia stacji metra") is None


@pytest.mark.parametrize("pole,wej,wyj", [
    ("szerokosc_geograficzna", "52,395198", "52.395198"),
    ("kod_pocztowy", "05120", "05-120"),
    ("kod_pocztowy", "5120", "05-120"),
    ("kod_simc", "920806", "0920806"),
    ("kod_terc", "140801", "140801"),
    ("telefon_kontaktowy", "'+48166779500", "+48166779500"),
    ("telefon_kontaktowy", "16 677 95 00", "166779500"),
    ("telefon_kontaktowy", "(0-16) 677-95-00", "166779500"),
    ("data_weryfikacji", "2022-11-10 09:54:00", "2022-11-10"),
    ("data_weryfikacji", "15.11.2026", "2026-11-15"),
    ("data_weryfikacji", "45231", "2023-11-01"),
    ("wewnatrz_budynku", "Wewnątrz budynku", "true"),
    ("wewnatrz_budynku", "Wewnątrz budynku, gabinet zabiegowy", "true"),
    ("wewnatrz_budynku", "Na zewnątrz budynku", "false"),
    ("wewnatrz_budynku", "TAK", "true"),
    ("dostepnosc", "Publiczny", "publiczny"),
    ("dostepnosc", "ogólnodostępny", "publiczny"),
    ("dostepny_24_7", "Ograniczona", "ograniczony"),
    ("dostepny_24_7", "Nie (dostęp: pon. - piątek 8:00 - 16:00)", "nie"),
    ("status", "czynny", "sprawny"),
    ("status", "Sprawny", "sprawny"),
    ("kondygnacja", "parter", "0"),
    ("kondygnacja", "-2", "-2"),
    ("godziny_pn", "8:00-16:00", "08:00-16:00"),
    ("godziny_so", "nieczynne", "zamkniete"),
    ("status", "coś dziwnego", "coś dziwnego"),
])
def test_formatuj(pole, wej, wyj):
    assert formatuj(pole, wej, SCHEMA) == wyj


# --- pliki ----------------------------------------------------------------------------------------


def test_krosno_pelny():
    rr = norm_plik("krosno.csv", fixed={"wewnatrz_budynku": "true", "dostepnosc": "publiczny", "dostepny_24_7": "nie"})
    assert len(rr) == 21
    r = rr[0]
    assert r.wiersz == 2
    rec = r.record
    assert rec["szerokosc_geograficzna"] == "49.718809346153336"
    assert rec["dlugosc_geograficzna"] == "21.72034402175176"
    assert rec["nazwa_obiektu"] == "Zespół Krytych Pływalni"
    assert rec["nazwa_ulicy"] == "Jasna" and rec["nr_budynku"] == "" and rec["miejscowosc"] == "Krosno"
    assert rec["wewnatrz_budynku"] == "true" and rec["dostepnosc"] == "publiczny"
    assert rec["dysponent_nazwa"] == "Urząd Miasta Krosna" and rec["dysponent_typ"] == "jst"
    assert rec["zrodlo_danych"] == "dysponent"
    assert rec["data_aktualizacji"].startswith("2026-11-22T")
    assert rec["status"] == "nieznany" and rec["data_weryfikacji"] == "2026-11-22"
    assert rec["id_aed"].startswith("krosno-") and len(rec["id_aed"]) == len("krosno-") + 6
    assert rec["id_zrodlowe"] == "1"
    # komunikaty o domyślnych wartościach: raz na plik
    plikowe = [m for m in r.messages if m.wiersz is None]
    assert {m.kod for m in plikowe} == {"DOMYSLNY_STATUS", "DOMYSLNA_DATA_WERYFIKACJI", "WYGENEROWANO_ID"}
    assert all("DOMYSLNY_STATUS" not in kody(x) for x in rr[1:])
    assert rr[9].record["nr_budynku"] == "4"


def test_id_stabilne_i_unikalne():
    a = [r.record["id_aed"] for r in norm_plik("krosno.csv")]
    b = [r.record["id_aed"] for r in norm_plik("krosno.csv")]
    assert a == b
    assert len(set(a)) == len(a)  # wiersze 10 i 11 to ten sam adres, ale inne współrzędne/nazwa albo -2


def test_id_kolizja():
    t = Table(columns=["lat", "lon", "nazwa"], rows=[["52.1", "21.1", "A"], ["52.1", "21.1", "A"]])
    rr = normalize_table(t, {"lat": "szerokosc_geograficzna", "lon": "dlugosc_geograficzna", "nazwa": "nazwa_obiektu"},
                         SCHEMA, UM, DZIS)
    assert rr[1].record["id_aed"] == rr[0].record["id_aed"] + "-2"


def test_marki_zamiana_per_wiersz():
    rr = norm_plik("marki.csv")
    assert rr[0].record["szerokosc_geograficzna"] == "52.326697"
    assert rr[0].record["dlugosc_geograficzna"] == "21.107557"
    assert "ZAMIENIONE_WSPOLRZEDNE" in kody(rr[0])
    w8 = next(r for r in rr if r.wiersz == 8)
    assert w8.record["szerokosc_geograficzna"] == "49.718809346153336"
    assert "ZAMIENIONE_WSPOLRZEDNE" not in kody(w8)
    assert rr[0].record["nazwa_obiektu"] == "Urząd Miasta Marki"
    assert rr[0].record["cecha_ulicy"] == "aleja"


@pytest.mark.parametrize("plik", ["przemysl.csv", "przemysl_2024.csv"])
def test_przemysl(plik):
    rr = norm_plik(plik)
    rec = rr[0].record
    assert rec["szerokosc_geograficzna"] == "49.7812096" and rec["dlugosc_geograficzna"] == "22.7750936"
    assert rec["nazwa_ulicy"] == "Juliusza Słowackiego" and rec["nr_budynku"] == "12"
    tel = {r.record["telefon_kontaktowy"] for r in rr} - {""}
    assert tel == {"+48166779500"}


def test_warszawa():
    rr = norm_plik("warszawa_19115.geojson")
    assert len(rr) == 708
    rec = rr[0].record
    assert rec["szerokosc_geograficzna"] == "52.2086170695684"
    assert rec["wewnatrz_budynku"] == "true" and rec["dostepnosc"] == "publiczny"
    assert rec["dostepny_24_7"] == "ograniczony"
    assert rec["godziny_pn"] == "08:00-18:00" and rec["godziny_wt"] == "08:00-16:00"
    assert rec["data_weryfikacji"] == "2022-11-10"
    assert rec["kondygnacja"] == "0" and rec["nr_budynku"] == "25/27"
    assert {r.record["wewnatrz_budynku"] for r in rr} <= {"true", "false"}
    assert {r.record["dostepnosc"] for r in rr} <= {"publiczny", "prywatny"}
    niezrozumiale = [r for r in rr if "NIEZROZUMIALE_GODZINY" in kody(r)]
    assert niezrozumiale and all(r.record["uwagi"].startswith("Godziny: ") for r in niezrozumiale)


def test_legionowo():
    rr = norm_plik("legionowo.csv")
    rec = rr[0].record
    assert rec["kod_simc"] == "0920806" and rec["kod_terc"] == "140801"
    assert rec["id_aed"].startswith("140801-")
    assert rec["nazwa_obiektu"] == "Urząd Miasta Legionowo"


def test_wartosc_stala_nie_nadpisuje_kolumny_i_24_7_daje_x():
    t = Table(columns=["lat", "lon", "dostep", "24"], rows=[["52.1", "21.1", "", "tak"], ["52.2", "21.2", "prywatny", "nie"]])
    m = {"lat": "szerokosc_geograficzna", "lon": "dlugosc_geograficzna", "dostep": "dostepnosc", "24": "dostepny_24_7"}
    rr = normalize_table(t, m, SCHEMA, UM, DZIS, fixed={"dostepnosc": "publiczny"})
    assert rr[0].record["dostepnosc"] == "publiczny" and rr[1].record["dostepnosc"] == "prywatny"
    assert rr[0].record["godziny_pn"] == "X" and rr[1].record["godziny_pn"] == ""


def test_ulica_z_miejscowosci_i_pusty_wiersz():
    t = Table(columns=["miejscowosc", "lat", "lon"], rows=[["Wola Mała", "50.1", "20.1"], ["", "", ""]], header_row=3)
    rr = normalize_table(t, {"miejscowosc": "miejscowosc", "lat": "szerokosc_geograficzna", "lon": "dlugosc_geograficzna"},
                         SCHEMA, UM, DZIS)
    assert len(rr) == 1 and rr[0].wiersz == 4
    assert rr[0].record["nazwa_ulicy"] == "Wola Mała" and "ULICA_Z_MIEJSCOWOSCI" in kody(rr[0])


def test_status_z_kolumna_pusta_komorka_per_wiersz():
    t = Table(columns=["lat", "lon", "stan"], rows=[["52.1", "21.1", "czynny"], ["52.2", "21.2", ""]])
    rr = normalize_table(t, {"lat": "szerokosc_geograficzna", "lon": "dlugosc_geograficzna", "stan": "status"},
                         SCHEMA, UM, DZIS)
    assert rr[0].record["status"] == "sprawny" and rr[1].record["status"] == "nieznany"
    assert [m.wiersz for m in rr[1].messages if m.kod == "DOMYSLNY_STATUS"] == [3]


class FakeGeo:
    def __init__(self, wynik=None):
        self.zapytania = []
        self.wynik = wynik

    def geocode(self, q):
        self.zapytania.append(q)
        if q.miejscowosc == "Nigdzie":
            return None
        return self.wynik or GeoResult(lat=49.6951234, lon=21.7651234, dokladnosc="punkt_adresowy", kod_terc="1861011",
                                       niejednoznaczny=q.nr_budynku == "")


def test_geokodowanie():
    t = Table(columns=["adres"], rows=[["ul. Rynek 1, 38-400 Krosno"], ["ul. Jasna, 38-400 Krosno"],
                                       ["ul. Rynek 1, 38-400 Krosno"], ["ul. Polna 1, 00-001 Nigdzie"]])
    g = FakeGeo()
    rr = normalize_table(t, {"adres": "_adres_pelny"}, SCHEMA, UM, DZIS, geocoder=g)
    assert len(g.zapytania) == 3  # identyczny adres pytany raz
    assert rr[0].record["szerokosc_geograficzna"] == "49.695123"
    assert rr[0].record["dokladnosc_polozenia"] == "punkt_adresowy"
    assert rr[0].record["kod_terc"] == "1861011" and rr[0].record["id_aed"].startswith("1861011-")
    assert "GEOKODOWANIE_OK" in kody(rr[0])
    assert "GEOKODOWANIE_NIEJEDNOZNACZNE" in kody(rr[1])
    assert rr[3].pominiety and "GEOKODOWANIE_BRAK" in kody(rr[3])
    assert not rr[0].pominiety


def test_limit_geokodowan():
    t = Table(columns=["ulica", "nr", "miasto"], rows=[["Polna", str(i), "Krosno"] for i in range(MAX_GEOKODOWAN + 5)])
    g = FakeGeo()
    rr = normalize_table(t, {"ulica": "nazwa_ulicy", "nr": "nr_budynku", "miasto": "miejscowosc"}, SCHEMA, UM, DZIS, geocoder=g)
    assert len(g.zapytania) == MAX_GEOKODOWAN
    assert sum(r.pominiety for r in rr) == 5
    assert "ZA_DUZO_DO_GEOKODOWANIA" in kody(rr[0])
