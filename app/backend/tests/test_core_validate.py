from pathlib import Path

from aed_core.schema import load_schema
from aed_core.types import RecordResult
from aed_core.validate import validate_records

SCHEMA = load_schema(Path(__file__).resolve().parents[3] / "zakres-danych")


def rekord(**kw):
    r = {p: "" for p in SCHEMA.nazwy}
    r.update(id_aed="x-1", szerokosc_geograficzna="52.395198", dlugosc_geograficzna="20.931382",
             nazwa_obiektu="Urząd", nazwa_ulicy="Piłsudskiego", miejscowosc="Legionowo", wewnatrz_budynku="true",
             dostepnosc="publiczny", dostepny_24_7="tak", status="sprawny", data_weryfikacji="2026-11-15",
             dysponent_nazwa="UM", zrodlo_danych="dysponent", data_aktualizacji="2026-11-22T10:00:00")
    for p in ("godziny_pn", "godziny_wt", "godziny_sr", "godziny_cz", "godziny_pt", "godziny_so", "godziny_nd",
              "godziny_swieta"):
        r[p] = "X"
    r.update(kw)
    return r


def val(*recs):
    return validate_records([RecordResult(wiersz=i + 2, record=r) for i, r in enumerate(recs)], SCHEMA)


def kody(msgs, poziom=None):
    return {m.kod for m in msgs if poziom is None or m.poziom == poziom}


def test_poprawny_rekord_bez_bledow():
    assert not kody(val(rekord()), "blad")


def test_brak_pola_obowiazkowego_raz_na_plik():
    m = val(rekord(dostepnosc=""), rekord(id_aed="x-2", dostepnosc="", szerokosc_geograficzna="52.5"))
    b = [x for x in m if x.kod == "BRAK_POLA_OBOWIAZKOWEGO"]
    assert len(b) == 1 and b[0].wiersz is None and b[0].pole == "dostepnosc"


def test_brak_pola_obowiazkowego_w_wierszu():
    m = val(rekord(), rekord(id_aed="x-2", nazwa_obiektu="", szerokosc_geograficzna="52.5"))
    b = [x for x in m if x.kod == "BRAK_POLA_OBOWIAZKOWEGO"]
    assert [(x.wiersz, x.pole) for x in b] == [(3, "nazwa_obiektu")]


def test_zalecane_zbiorczo():
    m = val(rekord(), rekord(id_aed="x-2", szerokosc_geograficzna="52.5"))
    z = [x for x in m if x.kod == "BRAK_POLA_ZALECANEGO" and x.pole == "kod_pocztowy"]
    assert len(z) == 1 and z[0].wiersz is None and z[0].poziom == "ostrzezenie"


def test_formaty_i_slowniki():
    m = val(rekord(status="czynny", kod_pocztowy="05120", wewnatrz_budynku="tak", data_weryfikacji="15.11.2026",
                   kod_terc="140801", godziny_pn="8-16"))
    poz = {(x.pole, x.kod, x.poziom) for x in m}
    assert ("status", "WARTOSC_SPOZA_SLOWNIKA", "blad") in poz
    assert ("kod_pocztowy", "ZLY_FORMAT", "ostrzezenie") in poz
    assert ("wewnatrz_budynku", "ZLY_FORMAT", "blad") in poz
    assert ("data_weryfikacji", "ZLY_FORMAT", "blad") in poz
    assert ("kod_terc", "ZLY_FORMAT", "ostrzezenie") in poz
    assert ("godziny_pn", "ZLY_FORMAT", "ostrzezenie") in poz


def test_poza_polska_i_precyzja():
    m = val(rekord(szerokosc_geograficzna="48.1"), rekord(id_aed="x-2", szerokosc_geograficzna="52.4", dlugosc_geograficzna="20.9312"),
            rekord(id_aed="x-3", szerokosc_geograficzna="52.7851", dlugosc_geograficzna="20.772605"))
    assert [x.wiersz for x in m if x.kod == "POZA_POLSKA"] == [2]
    assert [x.wiersz for x in m if x.kod == "NISKA_PRECYZJA"] == [3]


def test_duplikaty_i_bliskie_punkty():
    m = val(rekord(numer_seryjny="A1"), rekord(numer_seryjny="a1", szerokosc_geograficzna="52.395199"),
            rekord(id_aed="x-3", szerokosc_geograficzna="52.5"))
    assert [x.wiersz for x in m if x.kod == "DUPLIKAT_ID"] == [3]
    assert [x.wiersz for x in m if x.kod == "DUPLIKAT_NR_SERYJNEGO"] == [3]
    assert [x.wiersz for x in m if x.kod == "BLISKIE_PUNKTY"] == [3]


def test_pominiete_nie_walidowane():
    rr = [RecordResult(wiersz=2, record=rekord(szerokosc_geograficzna=""), pominiety=True)]
    assert validate_records(rr, SCHEMA) == []
