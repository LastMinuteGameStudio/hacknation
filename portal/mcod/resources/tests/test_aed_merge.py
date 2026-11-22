"""Wykaz AED: walidacja zakresu v0.5 i scalanie wykazów (czysta logika, bez bazy i Django).

Uruchomienie bez reszty portalu: python -m pytest -p no:django mcod/resources/tests/test_aed_merge.py
(conftest portalu wymaga bazy; te testy jej nie potrzebują).
"""

import csv
import io

import pytest

from mcod.resources.aed.merge import (
    KOLUMNY_POCHODZENIA,
    LICENCJA_CC0,
    LICENCJA_CC_BY,
    ZrodloWykazu,
    scal_wykazy,
    to_csv_bytes,
    to_xlsx_bytes,
)
from mcod.resources.aed.reader import BladOdczytu, read_table
from mcod.resources.aed.schema import load_zakres
from mcod.resources.aed.validation import bledy, validate_table

ZAKRES = load_zakres()


def rekord(id_aed, lat, lon, **kw):
    r = {
        "id_aed": id_aed,
        "szerokosc_geograficzna": lat,
        "dlugosc_geograficzna": lon,
        "nazwa_obiektu": "Urząd Gminy",
        "nazwa_ulicy": "Rynek",
        "nr_budynku": "1",
        "miejscowosc": "Krosno",
        "wewnatrz_budynku": "true",
        "dostepnosc": "publiczny",
        "dostepny_24_7": "tak",
        "status": "sprawny",
        "data_weryfikacji": "2026-11-01",
        "dysponent_nazwa": "Gmina Krosno",
        "zrodlo_danych": "dysponent",
        "data_aktualizacji": "2026-11-21T10:00:00",
    }
    r.update(kw)
    return r


def plik_csv(rekordy, kolumny=None):
    kolumny = kolumny or list(rekordy[0].keys())
    buf = io.StringIO(newline="")
    w = csv.DictWriter(buf, fieldnames=kolumny, lineterminator="\r\n", extrasaction="ignore")
    w.writeheader()
    w.writerows(rekordy)
    return buf.getvalue().encode("utf-8")


def zrodlo(instytucja, zasob_id, rekordy, licencja=LICENCJA_CC0, kolumny=None):
    return ZrodloWykazu(
        instytucja=instytucja,
        zasob_id=zasob_id,
        url=f"https://dane.gov.pl/pl/dataset/1/resource/{zasob_id}",
        data_aktualizacji="2026-11-21T10:00:00",
        licencja=licencja,
        tabela=read_table(plik_csv(rekordy, kolumny), "csv"),
    )


# --- odczyt i walidacja ---------------------------------------------------------------------------


def test_poprawny_wykaz_bez_bledow():
    t = read_table(plik_csv([rekord("1861011-a1", "49.693000", "21.765000")]), "csv")
    assert bledy(validate_table(t, ZAKRES)) == []


def test_odczyt_csv_srednik_cp1250_i_numery_wierszy():
    tekst = "id_aed;miejscowosc\r\n\r\n1;Łódź\r\n"
    t = read_table(tekst.encode("cp1250"), "csv")
    assert t.naglowek == ["id_aed", "miejscowosc"]
    assert t.wiersze == [{"id_aed": "1", "miejscowosc": "Łódź"}]
    assert t.numery == [3]


def test_odczyt_xlsx_zachowuje_tekst():
    from openpyxl import Workbook

    wb = Workbook()
    ws = wb.active
    ws.append(["id_aed", "kod_terc", "szerokosc_geograficzna", "data_weryfikacji"])
    import datetime

    ws.append(["a1", "0201011", 49.5, datetime.datetime(2026, 11, 1)])
    buf = io.BytesIO()
    wb.save(buf)
    t = read_table(buf.getvalue(), "xlsx")
    assert t.wiersze[0] == {"id_aed": "a1", "kod_terc": "0201011", "szerokosc_geograficzna": "49.5",
                            "data_weryfikacji": "2026-11-01"}


def test_nieobslugiwany_format():
    with pytest.raises(BladOdczytu):
        read_table(b"{}", "json")


def test_brak_kolumny_obowiazkowej_to_blad_naglowka():
    r = rekord("a1", "49.693000", "21.765000")
    del r["status"]
    k = validate_table(read_table(plik_csv([r]), "csv"), ZAKRES)
    b = bledy(k)
    assert [x.kod for x in b] == ["BRAK_KOLUMNY"]
    assert "status" in b[0].komunikat and b[0].wiersz == 1


def test_nieznana_kolumna_to_ostrzezenie():
    r = rekord("a1", "49.693000", "21.765000", Lp="1")
    k = validate_table(read_table(plik_csv([r]), "csv"), ZAKRES)
    assert not bledy(k)
    assert any(x.kod == "NIEZNANA_KOLUMNA" and "Lp" in x.komunikat for x in k)


def test_puste_pole_obowiazkowe_i_zle_formaty():
    rr = [
        rekord("a1", "49.693000", "21.765000", miejscowosc=""),
        rekord("a2", "49.694000", "21.766000", dostepnosc="dla wszystkich", kod_pocztowy="38400"),
        rekord("a3", "59.000000", "21.766000"),
    ]
    k = validate_table(read_table(plik_csv(rr, list(rr[1].keys())), "csv"), ZAKRES)
    kody = {(x.kod, x.wiersz, x.poziom) for x in k}
    assert ("BRAK_POLA_OBOWIAZKOWEGO", 2, "blad") in kody
    assert ("WARTOSC_SPOZA_SLOWNIKA", 3, "blad") in kody
    assert ("ZLY_FORMAT", 3, "ostrzezenie") in kody  # kod pocztowy to pole zalecane
    assert ("POZA_POLSKA", 4, "blad") in kody


def test_duplikat_id_w_wykazie_dostawcy():
    rr = [rekord("a1", "49.693000", "21.765000"), rekord("a1", "49.793000", "21.765000")]
    k = validate_table(read_table(plik_csv(rr), "csv"), ZAKRES)
    assert [x.kod for x in bledy(k)] == ["DUPLIKAT_ID"]


def test_komunikat_w_ksztalcie_walidacji_portalu():
    r = rekord("a1", "49.693000", "21.765000", status="")
    k = bledy(validate_table(read_table(plik_csv([r]), "csv"), ZAKRES))[0]
    d = k.as_dict()
    assert d["code"] == "aed-brak-pola-obowiazkowego"
    assert d["message"].startswith("Wiersz 2: ")
    assert d["row-number"] == 2 and d["column-name"] == "status"


# --- scalanie -------------------------------------------------------------------------------------


def test_dwoch_dostawcow_i_kolumny_pochodzenia():
    a = zrodlo("Gmina Krosno", 11, [rekord("1861011-a1", "49.693000", "21.765000")])
    b = zrodlo("Miasto Przemyśl", 12, [rekord("1862011-b1", "49.784000", "22.767000")], licencja=LICENCJA_CC_BY)
    w = scal_wykazy([b, a], ZAKRES)
    assert w.kolumny == ZAKRES.publiczne + KOLUMNY_POCHODZENIA
    assert "numer_seryjny" not in w.kolumny and "telefon_kontaktowy" not in w.kolumny
    assert [r["id_aed"] for r in w.rekordy] == ["1861011-a1", "1862011-b1"]  # kolejność wg instytucji
    assert w.rekordy[0]["zrodlo_instytucja"] == "Gmina Krosno"
    assert w.rekordy[0]["zrodlo_zasob_id"] == "11"
    assert w.rekordy[1]["licencja_zrodla"] == LICENCJA_CC_BY
    assert w.rekordy[1]["zrodlo_url"].endswith("/resource/12")
    assert w.pominiete == [] and w.liczba_duplikatow == 0
    assert w.licencja == LICENCJA_CC_BY  # jedno źródło na CC BY → cały wykaz CC BY


def test_licencja_cc0_gdy_wszystkie_zrodla_cc0():
    a = zrodlo("A", 1, [rekord("a1", "49.693000", "21.765000")])
    b = zrodlo("B", 2, [rekord("b1", "50.693000", "21.765000")])
    assert scal_wykazy([a, b], ZAKRES).licencja == LICENCJA_CC0


def test_duplikat_po_numerze_seryjnym():
    a = zrodlo("Gmina Krosno", 1, [rekord("a1", "49.693000", "21.765000", numer_seryjny="SN-123")])
    b = zrodlo("Szpital Krosno", 2, [rekord("b1", "49.700000", "21.780000", numer_seryjny="sn-123 ")])
    w = scal_wykazy([a, b], ZAKRES)
    assert len(w.rekordy) == 2  # oba zostają
    assert w.rekordy[0]["duplikat_id_aed"] == ""
    assert w.rekordy[1]["duplikat_id_aed"] == "a1"
    assert w.liczba_duplikatow == 1


def test_duplikat_po_odleglosci_do_30_m():
    a = zrodlo("Gmina Krosno", 1, [rekord("a1", "49.693000", "21.765000"), rekord("a2", "49.700000", "21.765000")])
    # b1 ok. 22 m od a1, b2 ok. 45 m od a2
    b = zrodlo("Szpital Krosno", 2, [rekord("b1", "49.693200", "21.765000"), rekord("b2", "49.700400", "21.765000")])
    w = scal_wykazy([a, b], ZAKRES)
    dup = {r["id_aed"]: r["duplikat_id_aed"] for r in w.rekordy}
    assert dup == {"a1": "", "a2": "", "b1": "a1", "b2": ""}


def test_bliskie_punkty_tego_samego_dostawcy_nie_sa_duplikatem_miedzy_dostawcami():
    a = zrodlo("Gmina Krosno", 1, [rekord("a1", "49.693000", "21.765000"), rekord("a2", "49.693100", "21.765000")])
    w = scal_wykazy([a], ZAKRES)
    assert all(r["duplikat_id_aed"] == "" for r in w.rekordy)


def test_duplikat_trzeciego_wskazuje_rekord_glowny():
    a = zrodlo("A", 1, [rekord("a1", "49.693000", "21.765000")])
    b = zrodlo("B", 2, [rekord("b1", "49.693100", "21.765000")])
    c = zrodlo("C", 3, [rekord("c1", "49.693150", "21.765000")])
    w = scal_wykazy([a, b, c], ZAKRES)
    assert {r["id_aed"]: r["duplikat_id_aed"] for r in w.rekordy} == {"a1": "", "b1": "a1", "c1": "a1"}


def test_zasob_z_bledem_walidacji_pominiety():
    a = zrodlo("Gmina Krosno", 1, [rekord("a1", "49.693000", "21.765000")])
    zly = rekord("b1", "49.784000", "22.767000")
    del zly["dostepny_24_7"]
    b = zrodlo("Miasto Przemyśl", 2, [zly])
    w = scal_wykazy([a, b], ZAKRES)
    assert [r["id_aed"] for r in w.rekordy] == ["a1"]
    assert len(w.pominiete) == 1 and w.pominiete[0].zrodlo is b
    assert "błędów walidacji" in w.pominiete[0].powod
    assert w.pominiete[0].komunikaty[0].kod == "BRAK_KOLUMNY"
    assert [z.zasob_id for z in w.dolaczone] == [1]


def test_zasob_z_licencja_by_nc_pominiety():
    a = zrodlo("Gmina Krosno", 1, [rekord("a1", "49.693000", "21.765000")])
    b = zrodlo("Fundacja", 2, [rekord("b1", "49.784000", "22.767000")], licencja="CC BY-NC 4.0")
    w = scal_wykazy([a, b], ZAKRES)
    assert [r["id_aed"] for r in w.rekordy] == ["a1"]
    assert w.pominiete[0].zrodlo is b
    assert "licencji" in w.pominiete[0].powod and "CC BY-NC 4.0" in w.pominiete[0].powod
    assert w.licencja == LICENCJA_CC0


def test_eksport_csv_rfc4180_i_xlsx():
    a = zrodlo("Gmina, Krosno", 1, [rekord("a1", "49.693000", "21.765000", kod_terc="0201011")])
    w = scal_wykazy([a], ZAKRES)
    dane = to_csv_bytes(w)
    assert not dane.startswith(b"\xef\xbb\xbf")
    assert dane.count(b"\r\n") == 2
    assert b'"Gmina, Krosno"' in dane
    wiersze = list(csv.DictReader(io.StringIO(dane.decode("utf-8"))))
    assert wiersze[0]["kod_terc"] == "0201011" and wiersze[0]["szerokosc_geograficzna"] == "49.693000"

    t = read_table(to_xlsx_bytes(w), "xlsx")
    assert t.naglowek == w.kolumny
    assert t.wiersze[0]["kod_terc"] == "0201011" and t.wiersze[0]["szerokosc_geograficzna"] == "49.693000"
