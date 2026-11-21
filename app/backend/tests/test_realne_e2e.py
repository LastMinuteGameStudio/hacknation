"""D3: end-to-end na realnych plikach.

1) Rdzeń: plik → read_table → suggest_mapping → normalize_table → validate_records → export.to_csv:
   CSV zgodny z RFC 4180 (UTF-8 bez BOM, przecinek, CRLF, cudzysłowy tylko gdy trzeba) i z zakresem v0.5
   (nagłówek = pola publiczne w kolejności zakresu = nagłówek zakres-danych/szablon-aed-publiczny.csv).
2) API: upload → walidacja (mapowanie z propozycji, bez poprawek) → publikacja → GET /d/{slug}.csv.
   Czeka na B3 (/d/{slug}.csv): przy 404 test jest xfail.
"""

from __future__ import annotations

import csv
import io
import os
import re
import tempfile

import pytest

from tests.fixtury import oczekiwania as oc

E2E = [oc.wg_pliku(p) for p in ("krosno.csv", "legionowo.csv", "przemysl.csv", "przemysl_2024.csv",
                                "warszawa_19115.geojson", "marki.csv")]
NIEPUBLICZNE = {"telefon_kontaktowy", "email_kontaktowy", "producent", "model", "numer_seryjny", "serwisant_nazwa"}


def _ids(lst):
    return [e["plik"] for e in lst]


def _naglowek_szablonu() -> list[str]:
    return (oc.ZAKRES / "szablon-aed-publiczny.csv").read_text(encoding="utf-8").splitlines()[0].split(",")


def sprawdz_rfc4180(dane: bytes, sch) -> list[list[str]]:
    """Zwraca wiersze (z nagłówkiem). AssertionError przy niezgodności."""
    assert not dane.startswith(b"\xef\xbb\xbf"), "CSV ma BOM"
    tekst = dane.decode("utf-8")  # UTF-8
    assert tekst.endswith("\r\n"), "ostatni wiersz bez CRLF"
    # CRLF między rekordami: każdy \n poza cudzysłowami musi być poprzedzony \r
    w_cudz = False
    for i, ch in enumerate(tekst):
        if ch == '"':
            w_cudz = not w_cudz
        elif ch == "\n" and not w_cudz:
            assert i > 0 and tekst[i - 1] == "\r", f"samotne LF na pozycji {i}"
    assert not w_cudz, "niezamknięty cudzysłów"
    wiersze = list(csv.reader(io.StringIO(tekst, newline=""), delimiter=",", quotechar='"', strict=True))
    naglowek = wiersze[0]
    assert naglowek == sch.publiczne, "nagłówek ≠ pola publiczne v0.5 w kolejności zakresu"
    assert naglowek == _naglowek_szablonu(), "nagłówek ≠ szablon-aed-publiczny.csv"
    assert not NIEPUBLICZNE & set(naglowek)
    for n, w in enumerate(wiersze[1:], 2):
        assert len(w) == len(naglowek), f"wiersz CSV {n}: {len(w)} pól zamiast {len(naglowek)}"
    # cudzysłowy tylko gdy potrzebne: pole w cudzysłowie musi zawierać , " CR albo LF
    for pole in re.findall(r'(?:^|,)"((?:[^"]|"")*)"(?=,|\r\n)', tekst, flags=re.M):
        assert re.search(r'[,"\r\n]', pole.replace('""', '"')), f"zbędny cudzysłów: {pole!r}"
    # round-trip: ten sam zapis przez csv.writer
    buf = io.StringIO(newline="")
    csv.writer(buf, lineterminator="\r\n", quoting=csv.QUOTE_MINIMAL).writerows(wiersze)
    assert buf.getvalue() == tekst, "zapis różni się od csv.writer(QUOTE_MINIMAL, CRLF)"
    return wiersze


def sprawdz_formaty_v05(wiersze: list[list[str]], sch) -> list[str]:
    """Formaty pól publicznych wg zakresu v0.5. Zwraca listę naruszeń."""
    nag = wiersze[0]
    slowniki = {f.pole: {k for k, _ in sch.slowniki.get(f.slownik, [])} for f in sch.pola if f.slownik}
    reg = {
        "szerokosc_geograficzna": r"^-?\d{1,2}\.\d+$",
        "dlugosc_geograficzna": r"^-?\d{1,3}\.\d+$",
        "kod_pocztowy": r"^\d{2}-\d{3}$",
        "kod_simc": r"^\d{7}$",
        "wewnatrz_budynku": r"^(true|false)$",
        "tryb_pediatryczny": r"^(true|false)$",
        "kondygnacja": r"^-?\d+$",
        "data_aktualizacji": r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$",
    }
    for f in sch.pola:
        if f.typ == "data":
            reg[f.pole] = r"^\d{4}-\d{2}-\d{2}$"
        if f.typ == "godziny":
            reg[f.pole] = r"^(\d{2}:\d{2}-\d{2}:\d{2}(,\d{2}:\d{2}-\d{2}:\d{2})*|zamkniete|X)$"
    bledy = []
    for n, w in enumerate(wiersze[1:], 2):
        r = dict(zip(nag, w))
        for pole, v in r.items():
            if not v:
                if sch.pole(pole).wymagalnosc == "O":
                    bledy.append(f"wiersz {n}: puste pole O {pole}")
                continue
            if pole in reg and not re.match(reg[pole], v):
                bledy.append(f"wiersz {n}: {pole}={v!r} niezgodne z formatem")
            if pole in slowniki and v not in slowniki[pole]:
                bledy.append(f"wiersz {n}: {pole}={v!r} spoza słownika")
        if r.get("szerokosc_geograficzna") and not 49.0 <= float(r["szerokosc_geograficzna"]) <= 54.9:
            bledy.append(f"wiersz {n}: szerokość poza Polską")
        if r.get("dlugosc_geograficzna") and not 14.1 <= float(r["dlugosc_geograficzna"]) <= 24.2:
            bledy.append(f"wiersz {n}: długość poza Polską")
    return bledy


# --- 1) rdzeń -----------------------------------------------------------------------------------


@pytest.mark.parametrize("exp", E2E, ids=_ids(E2E))
def test_rdzen_plik_do_csv(exp):
    from aed_core.export import to_csv
    from aed_core.mapping import suggest_mapping
    from aed_core.validate import validate_records

    sch = oc.schema()
    try:
        t = oc.wczytaj_tabele(exp)
        mapowanie = {s.kolumna: s.pole for s in suggest_mapping(t, sch)}
        rek = oc.normalizuj(exp, t, mapowanie, sch)
        walid = validate_records(rek, sch)
        do_publikacji = [r.record for r in rek if not r.pominiety]
        dane = to_csv(do_publikacji, sch, public_only=True)
    except NotImplementedError as e:
        pytest.xfail(f"rdzeń: {e}")
    assert not [m for m in walid if m.poziom == "blad"], [(m.kod, m.wiersz, m.komunikat) for m in walid if m.poziom == "blad"][:10]
    wiersze = sprawdz_rfc4180(dane, sch)
    assert len(wiersze) - 1 == len(do_publikacji) == exp["liczba_wierszy"]
    bledy = sprawdz_formaty_v05(wiersze, sch)
    assert not bledy, "\n".join(bledy[:20])


def test_to_csv_cudzyslowy_i_przecinki():
    """Wartości z przecinkiem, cudzysłowem i nową linią muszą być poprawnie ujęte (RFC 4180 §2.6–2.7)."""
    from aed_core.export import to_csv

    sch = oc.schema()
    rec = {p: "" for p in sch.nazwy}
    rec.update({"id_aed": "x-000001", "nazwa_obiektu": 'Pływalnia "Wodne Piaski", hala', "opis_lokalizacji": "hol\nparter",
                "szerokosc_geograficzna": "52.4", "dlugosc_geograficzna": "20.9", "telefon_kontaktowy": "123456789"})
    try:
        dane = to_csv([rec], sch, public_only=True)
    except NotImplementedError as e:
        pytest.xfail(f"rdzeń: {e}")
    wiersze = sprawdz_rfc4180(dane, sch)
    r = dict(zip(wiersze[0], wiersze[1]))
    assert r["nazwa_obiektu"] == 'Pływalnia "Wodne Piaski", hala'
    assert r["opis_lokalizacji"] == "hol\nparter"
    assert "123456789" not in dane.decode()


# --- 2) API -------------------------------------------------------------------------------------


API = [oc.wg_pliku(p) for p in ("krosno.csv", "przemysl_2024.csv", "legionowo.csv")]


@pytest.fixture(scope="module")
def klient():
    os.environ.setdefault("DATABASE_URL", f"sqlite:///{tempfile.mkdtemp()}/test.db")
    from fastapi.testclient import TestClient

    from app.main import app

    with TestClient(app) as c:
        yield c


def _xfail_gdy_atrapy(etap: str) -> None:
    """API B zastępuje niegotowe funkcje rdzenia atrapami (app/core.py, ATRAPY_UZYTE): wtedy wynik nie jest miarodajny."""
    try:
        from app.core import ATRAPY_UZYTE
    except ImportError:
        return
    if ATRAPY_UZYTE:
        pytest.xfail(f"{etap}: API użyło atrap rdzenia: {sorted(ATRAPY_UZYTE)}")


@pytest.mark.parametrize("exp", API, ids=_ids(API))
def test_api_upload_walidacja_publikacja_csv(klient, exp):
    c = klient
    p = oc.FIXTURY / exp["plik"]
    r = c.post("/api/importy", files={"plik": (p.name, p.read_bytes(), "application/octet-stream")})
    assert r.status_code == 200, r.text
    imp = r.json()
    if any(k["kod"] == "ATRAPA" for k in imp.get("komunikaty", [])):
        pytest.xfail("B2: API zwraca atrapy")
    assert imp["liczba_wierszy"] == exp["liczba_wierszy"]
    mapowanie = {m["kolumna"]: m["pole"] for m in imp["mapowanie_propozycja"]}  # bez poprawek
    d = exp["dostawca"]
    w = c.post(f"/api/importy/{imp['import_id']}/walidacja", json={
        "mapowanie": mapowanie, "dysponent": {"nazwa": d["nazwa"], "typ": d["typ"]},
        "wartosci_stale": exp.get("wartosci_stale") or {}})
    assert w.status_code == 200, w.text
    w = w.json()
    _xfail_gdy_atrapy("walidacja")
    assert w["mozna_publikowac"], [k for k in w["komunikaty"] if k["poziom"] == "blad"]
    assert w["liczba_rekordow"] == exp["liczba_wierszy"] and w["liczba_pominietych"] == 0
    pub = c.post(f"/api/importy/{imp['import_id']}/publikacja")
    assert pub.status_code == 200, pub.text
    pub = pub.json()
    slug = pub["slug"]
    assert pub["url_csv"].endswith(f"/d/{slug}.csv")

    g = c.get(f"/d/{slug}.csv")
    if g.status_code == 404:
        pytest.xfail("B3: /d/{slug}.csv jeszcze nie działa")
    assert g.status_code == 200
    _xfail_gdy_atrapy("eksport")
    assert g.headers["content-type"].replace(" ", "").lower() == "text/csv;charset=utf-8"
    sch = oc.schema()
    wiersze = sprawdz_rfc4180(g.content, sch)
    assert len(wiersze) - 1 == exp["liczba_wierszy"]
    assert not sprawdz_formaty_v05(wiersze, sch)
    r0 = dict(zip(wiersze[0], wiersze[1]))
    assert r0["dysponent_nazwa"] == d["nazwa"]
    for pole, oczek in exp["rekordy"][0]["pola"].items():
        if pole in r0:
            assert oc.wartosc_pasuje(oczek, r0[pole]), (pole, oczek, r0[pole])

    meta = c.get(f"/d/{slug}.csv-metadata.json")
    if meta.status_code == 200:
        assert meta.json()["url"].endswith(f"/d/{slug}.csv")
