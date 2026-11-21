"""D1/D3: wartości rekordów po normalize_table i komunikaty normalize + validate na realnych plikach.

Mapowanie bierzemy z suggest_mapping bez poprawek (decyzja zespołu), wartości stałe z oczekiwań
(to krok „ustaw dla wszystkich AED w pliku” w kreatorze). Geokoder wyłączony (wszystkie pliki mają współrzędne).
"""

from __future__ import annotations

import pytest

from tests.fixtury import oczekiwania as oc

WSZYSTKIE = oc.wszystkie()
REALNE = [e for e in WSZYSTKIE if not e.get("syntetyczny")]
SYNTETYCZNE = [e for e in WSZYSTKIE if e.get("syntetyczny")]


def _ids(lst):
    return [e["plik"] for e in lst]


def _przebieg(exp):
    from aed_core.mapping import suggest_mapping
    from aed_core.validate import validate_records

    sch = oc.schema()
    try:
        t = oc.wczytaj_tabele(exp)
        mapowanie = {s.kolumna: s.pole for s in suggest_mapping(t, sch)}
        rek = oc.normalizuj(exp, t, mapowanie, sch)
        walid = validate_records(rek, sch)
    except NotImplementedError as e:
        pytest.xfail(f"rdzeń: {e}")
    return t, rek, walid


@pytest.mark.parametrize("exp", REALNE, ids=_ids(REALNE))
def test_wartosci_rekordow(exp):
    _, rek, _ = _przebieg(exp)
    assert len(rek) == exp["liczba_wierszy"]
    roznice = oc.porownaj_rekordy(exp, rek)
    assert not roznice, "\n".join(roznice)


@pytest.mark.parametrize("exp", REALNE, ids=_ids(REALNE))
def test_komunikaty(exp):
    t, rek, walid = _przebieg(exp)
    problemy = oc.sprawdz_kody(exp, oc.kody(rek, walid, t))
    assert not problemy, "\n".join(problemy)


@pytest.mark.parametrize("exp", REALNE, ids=_ids(REALNE))
def test_mozna_publikowac(exp):
    """Pliki realne z wartościami stałymi nie mają błędów i żaden rekord nie jest pominięty."""
    _, rek, walid = _przebieg(exp)
    bledy = [m for m in walid if m.poziom == "blad"] + [m for r in rek for m in r.messages if m.poziom == "blad"]
    assert not bledy, [(m.kod, m.wiersz, m.pole, m.komunikat) for m in bledy[:10]]
    assert not [r.wiersz for r in rek if r.pominiety]


@pytest.mark.parametrize("exp", REALNE, ids=_ids(REALNE))
def test_pola_stale_i_domyslne(exp):
    _, rek, _ = _przebieg(exp)
    for r in rek:
        assert r.record["dysponent_nazwa"] == exp["dostawca"]["nazwa"]
        assert r.record["status"], r.wiersz
        assert r.record["data_weryfikacji"], r.wiersz
        assert r.record["id_aed"], r.wiersz
        for pole, v in (exp.get("wartosci_stale") or {}).items():
            assert r.record[pole], (r.wiersz, pole)
    ids = [r.record["id_aed"] for r in rek]
    assert len(ids) == len(set(ids)), "id_aed nieunikalne w pliku"


@pytest.mark.parametrize("exp", REALNE, ids=_ids(REALNE))
def test_id_aed_stabilne_przy_ponownym_wgraniu(exp):
    _, rek1, _ = _przebieg(exp)
    _, rek2, _ = _przebieg(exp)
    assert [r.record["id_aed"] for r in rek1] == [r.record["id_aed"] for r in rek2]


@pytest.mark.xfail(strict=False, reason="syntetyczne XLSX: cel dla heurystyki, nie wymóg MVP")
@pytest.mark.parametrize("exp", SYNTETYCZNE, ids=_ids(SYNTETYCZNE))
def test_syntetyczne_rekordy(exp):
    t, rek, walid = _przebieg(exp)
    problemy = oc.porownaj_rekordy(exp, rek) + oc.sprawdz_kody(exp, oc.kody(rek, walid, t))
    assert len(rek) == exp["liczba_wierszy"]
    assert not problemy, "\n".join(problemy)
