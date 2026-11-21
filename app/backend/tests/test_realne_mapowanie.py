"""D2: jakość mapowania na realnych plikach (oczekiwania: tests/fixtury/oczekiwane/*.json).

Decyzja zespołu: Krosno, Legionowo, Przemyśl (oba pliki) i Warszawa 19115 → 100% bez ręcznych poprawek.
Marki (uszkodzony) → naprawiony albo jasno zgłoszony. Syntetyczne XLSX → cel, nie wymóg (xfail, nie blokują).
Brak implementacji w rdzeniu (NotImplementedError) → xfail, żeby testy mogły być na main przed ścieżką A.
"""

from __future__ import annotations

import pytest

from tests.fixtury import oczekiwania as oc

WSZYSTKIE = oc.wszystkie()
WYMAGANE = [e for e in WSZYSTKIE if e.get("wymaga_100")]
MARKI = [e for e in WSZYSTKIE if e.get("uszkodzony")]
SYNTETYCZNE = [e for e in WSZYSTKIE if e.get("syntetyczny")]


def _ids(lst):
    return [e["plik"] for e in lst]


def _mapuj(exp):
    from aed_core.mapping import suggest_mapping

    try:
        t = oc.wczytaj_tabele(exp)
        return t, oc.ocen_mapowanie(exp, t, suggest_mapping(t, oc.schema()))
    except NotImplementedError as e:
        pytest.xfail(f"rdzeń: {e}")


def _opis(o) -> str:
    return "\n".join(f"  {k!r}: oczekiwane {e!r}, otrzymane {g!r}" for k, e, g in o.pomylki)


def test_sa_wszystkie_wymagane_fixtury():
    pliki = {e["plik"] for e in WYMAGANE}
    assert {"krosno.csv", "legionowo.csv", "przemysl.csv", "przemysl_2024.csv", "warszawa_19115.geojson"} <= pliki


@pytest.mark.parametrize("exp", WYMAGANE, ids=_ids(WYMAGANE))
def test_mapowanie_100_procent(exp):
    t, o = _mapuj(exp)
    assert len(t.rows) == exp["liczba_wierszy"]
    assert o.procent == 100.0, f"{exp['plik']}: {o.procent:.0f}%\n{_opis(o)}"


@pytest.mark.parametrize("exp", WYMAGANE + MARKI, ids=_ids(WYMAGANE + MARKI))
def test_jedno_pole_najwyzej_raz(exp):
    _, o = _mapuj(exp)
    pola = [p for p in o.mapowanie.values() if p]
    assert len(pola) == len(set(pola)), f"pole przypisane do kilku kolumn: {o.mapowanie}"


@pytest.mark.parametrize("exp", MARKI, ids=_ids(MARKI))
def test_marki_naprawione_albo_zgloszone(exp):
    t, o = _mapuj(exp)
    naprawione = len(t.columns) == len(exp["kolumny_po_naprawie"]) and len(t.rows) == exp["liczba_wierszy"]
    zgloszone = any(m.poziom in ("blad", "ostrzezenie") for m in t.messages)
    assert naprawione or zgloszone, "Marki: plik ani naprawiony, ani zgłoszony komunikatem"
    assert zgloszone, "Marki: naprawa uszkodzonego pliku powinna być widoczna dla dostawcy (ostrzeżenie)"
    if naprawione:
        assert o.procent == 100.0, _opis(o)


@pytest.mark.xfail(strict=False, reason="syntetyczne XLSX: cel dla heurystyki, nie wymóg MVP")
@pytest.mark.parametrize("exp", SYNTETYCZNE, ids=_ids(SYNTETYCZNE))
def test_syntetyczne_mapowanie(exp):
    t, o = _mapuj(exp)
    assert len(t.rows) == exp["liczba_wierszy"], f"wierszy {len(t.rows)}, oczekiwane {exp['liczba_wierszy']}"
    assert o.procent == 100.0, f"{o.procent:.0f}%\n{_opis(o)}"


def test_szablon_v05_mapuje_sie_1_do_1():
    """Nasz szablon (zakres-danych/szablon-aed.csv) przechodzi bez mapowania: każda kolumna → pole o tej nazwie."""
    from aed_core.mapping import suggest_mapping
    from aed_core.parsers import read_table

    sch = oc.schema()
    # szablon ma sam nagłówek: dokładamy jeden wiersz z przykładami z zakresu
    p = oc.ZAKRES / "szablon-aed.csv"
    naglowek = p.read_text(encoding="utf-8").splitlines()[0]
    przyklady = [sch.pole(k).przyklad if k in sch.nazwy else "" for k in naglowek.split(",")]
    tresc = (naglowek + "\r\n" + ",".join('"' + v.replace('"', '""') + '"' for v in przyklady) + "\r\n").encode()
    try:
        t = read_table(tresc, p.name)
        sug = suggest_mapping(t, sch)
    except NotImplementedError as e:
        pytest.xfail(f"rdzeń: {e}")
    zle = [(s.kolumna, s.pole) for s in sug if s.pole != s.kolumna.strip()]
    assert not zle, zle
