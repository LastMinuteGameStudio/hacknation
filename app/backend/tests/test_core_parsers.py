import io
from pathlib import Path

import openpyxl
import pytest

from aed_core.parsers import MAX_WIERSZY, BladPliku, read_table

FIX = Path(__file__).parent / "fixtury"


def test_krosno_przecinek_naglowki_przyciete():
    t = read_table((FIX / "krosno.csv").read_bytes(), "krosno.csv")
    assert t.columns[:3] == ["Długość geograficzna", "Szerokość geograficzna", "Nazwa"]
    assert t.header_row == 1
    assert t.rows[0][0] == "21.72034402175176"
    assert t.rows[0][4] == "ul. Jasna, 38-400 Krosno"


def test_legionowo_bom():
    t = read_table((FIX / "legionowo.csv").read_bytes(), "legionowo.csv")
    assert t.columns[0] == "nazwa"
    assert t.rows[0][7] == "140801" and t.rows[0][8] == "0920806"
    assert t.rows[9][0] == 'Pływalnia "Wodne Piaski"'


def test_przemysl_srednik_i_geometria():
    t = read_table((FIX / "przemysl.csv").read_bytes(), "przemysl.csv")
    assert "geometry" in t.columns and "home_number" in t.columns
    g = t.rows[0][t.columns.index("geometry")]
    assert g.startswith('{"type":"Point"')
    assert len(t.rows) == 21


@pytest.mark.parametrize("nazwa", ["marki.csv", "marki.xlsx"])
def test_marki_caly_wiersz_w_jednym_polu(nazwa):
    t = read_table((FIX / nazwa).read_bytes(), nazwa)
    assert t.columns == ["Długość geograficzna", "Szerokość geograficzna", "Nazwa", "Lokalizacja", "Adres", "Numer Id"]
    assert t.rows[0][:2] == ["52.326697", "21.107557"]
    assert t.rows[0][4] == "Al.. Piłsudskiego 95, 05-270 Marki"
    assert len(t.rows) == 8
    assert any(m.kod == "ROZBITO_WIERSZE" for m in t.messages)


def test_marki_xlsx_arkusze():
    t = read_table((FIX / "marki.xlsx").read_bytes(), "marki.xlsx")
    assert t.sheets == ["Defibrylator_GminaMiastoMarki_1"]


def test_cp1250_i_tytul_nad_tabela():
    tekst = "Wykaz defibrylatorów w gminie\n\nnazwa;ulica;lat;lon\nUrząd Gminy;Łąkowa 1;50,1;19,9\nSzkoła;Źródlana 2;50,2;19,8\n"
    t = read_table(tekst.encode("cp1250"), "aed.csv")
    assert t.columns == ["nazwa", "ulica", "lat", "lon"]
    assert t.header_row == 3
    assert t.rows[0] == ["Urząd Gminy", "Łąkowa 1", "50,1", "19,9"]
    assert any(m.kod == "POMINIETO_WIERSZE_TYTULOWE" for m in t.messages)


def test_powtorzone_i_puste_naglowki():
    t = read_table(b"a,a,,b\n1,2,3,4\n", "x.csv")
    assert t.columns == ["a", "a (2)", "Kolumna 3", "b"]


def test_puste_wiersze_w_srodku_pomijane_z_numeracja():
    t = read_table(b"a,b\n1,2\n\n3,4\n\n\n", "x.csv")
    assert t.rows == [["1", "2"], ["3", "4"]]
    assert [t.numer_wiersza(i) for i in range(2)] == [2, 4]


def test_stopka_pomijana():
    t = read_table("a,b,c\n1,2,3\nSporządził: Jan K.,,\n".encode(), "x.csv")
    assert t.rows == [["1", "2", "3"]]


def test_syntetyczny_gmina_scalone_i_stopka():
    t = read_table((FIX / "syntetyczny_gmina.xlsx").read_bytes(), "g.xlsx")
    assert t.header_row == 4 and len(t.rows) == 5
    m = t.columns.index("Miejscowość")
    assert [r[m] for r in t.rows] == ["Przykładowo"] * 3 + ["Wola Przykładowa"] * 2
    assert [t.numer_wiersza(i) for i in range(5)] == [5, 6, 7, 8, 9]


def test_syntetyczny_osir_pusty_wiersz():
    t = read_table((FIX / "syntetyczny_osir.xlsx").read_bytes(), "o.xlsx")
    assert len(t.rows) == 3 and [t.numer_wiersza(i) for i in range(3)] == [2, 4, 5]
    assert t.columns[2] == "Uwagi" and t.columns[7] == "Uwagi (2)"


def test_syntetyczny_powiat_arkusz_i_naglowek_dwupoziomowy():
    t = read_table((FIX / "syntetyczny_powiat.xlsx").read_bytes(), "p.xlsx")
    assert t.sheets == ["Informacje", "Defibrylatory", "Legenda"]
    assert t.columns[:8] == ["Nr ewid.", "Jednostka", "Ulica", "Nr", "Kod", "Miejscowość", "Szerokość", "Długość"]
    assert len(t.rows) == 4 and t.numer_wiersza(0) == 4
    assert t.rows[0][6] == "49.8851234" and t.rows[0][10] == "2026-03-15"


def test_tab_i_krotsze_wiersze():
    t = read_table(b"a\tb\tc\n1\t2\n", "x.tsv")
    assert t.rows == [["1", "2", ""]]


def _xlsx(rows):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "AED"
    for r in rows:
        ws.append(r)
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


def test_xlsx_liczby_bez_utraty_precyzji():
    import datetime

    data = _xlsx([["Tytuł raportu"], [], ["lat", "lon", "nr", "data"],
                  [52.395198, 20.93138, 12, datetime.datetime(2026, 11, 15)],
                  [49.718809346153336, 1e-7, 7.0, None]])
    t = read_table(data, "aed.xlsx")
    assert t.header_row == 3
    assert t.rows[0] == ["52.395198", "20.93138", "12", "2026-11-15"]
    assert t.rows[1][0].startswith("49.7188093461533")
    assert t.rows[1][1] == "0.0000001" and t.rows[1][2] == "7"


def test_xlsx_wybor_arkusza():
    wb = openpyxl.Workbook()
    wb.active.title = "Pusty"
    ws = wb.create_sheet("Dane")
    ws.append(["a", "b"])
    ws.append(["1", "2"])
    buf = io.BytesIO()
    wb.save(buf)
    t = read_table(buf.getvalue(), "x.xlsx")
    assert t.sheets == ["Pusty", "Dane"] and t.columns == ["a", "b"]
    t2 = read_table(buf.getvalue(), "x.xlsx", sheet="Dane")
    assert t2.rows == [["1", "2"]]
    with pytest.raises(BladPliku) as e:
        read_table(buf.getvalue(), "x.xlsx", sheet="Brak")
    assert e.value.kod == "NIE_ZNALEZIONO"


def test_geojson_warszawa():
    t = read_table((FIX / "warszawa_19115.geojson").read_bytes(), "warszawa_19115.geojson")
    assert "location_street" in t.columns and t.columns[-1] == "geometry"
    assert "coordinates" in t.rows[0][-1]


@pytest.mark.parametrize(
    "content,nazwa,kod",
    [
        (b"x" * (10 * 1024 * 1024 + 1), "a.csv", "ZA_DUZY_PLIK"),
        (b"%PDF-1.4", "a.pdf", "NIEOBSLUGIWANY_FORMAT"),
        (b"", "a.csv", "PUSTY_PLIK"),
        (b"a,b\n", "a.csv", "PUSTY_PLIK"),
        (b"a,b\n" + b"1,2\n" * (MAX_WIERSZY + 1), "a.csv", "ZA_DUZO_WIERSZY"),
    ],
)
def test_bledy_pliku(content, nazwa, kod):
    with pytest.raises(BladPliku) as e:
        read_table(content, nazwa)
    assert e.value.kod == kod
