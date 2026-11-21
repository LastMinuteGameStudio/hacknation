"""Demo (tests/fixtury/DEMO.md): Przemyśl. Kopia z 2024 → publikacja → aktualizacja plikiem „na żywo”
przez prywatny link edycji → ten sam URL, te same id_aed, mimo zmiany formatu geometrii.
"""

from __future__ import annotations

import csv
import io
import os
import tempfile

import pytest

from tests.fixtury import oczekiwania as oc

STARY = oc.wg_pliku("przemysl_2024.csv")
NOWY = oc.wg_pliku("przemysl.csv")
POMIJANE = {"data_aktualizacji"}


def _rekordy(exp):
    from aed_core.mapping import suggest_mapping

    sch = oc.schema()
    try:
        t = oc.wczytaj_tabele(exp)
        return oc.normalizuj(exp, t, {s.kolumna: s.pole for s in suggest_mapping(t, sch)}, sch)
    except NotImplementedError as e:
        pytest.xfail(f"rdzeń: {e}")


def test_demo_rdzen_oba_formaty_geometrii_daja_te_same_rekordy():
    stare, nowe = _rekordy(STARY), _rekordy(NOWY)
    assert len(stare) == len(nowe) == 21
    for a, b in zip(stare, nowe):
        roz = {k: (a.record.get(k), b.record.get(k)) for k in set(a.record) | set(b.record)
               if k not in POMIJANE and a.record.get(k) != b.record.get(k)}
        assert not roz, f"wiersz {a.wiersz}: {roz}"


@pytest.fixture(scope="module")
def klient():
    os.environ.setdefault("DATABASE_URL", f"sqlite:///{tempfile.mkdtemp()}/test.db")
    from fastapi.testclient import TestClient

    from app.main import app

    with TestClient(app) as c:
        yield c


def _xfail_gdy_atrapy():
    try:
        from app.core import ATRAPY_UZYTE
    except ImportError:
        return
    if ATRAPY_UZYTE:
        pytest.xfail(f"API użyło atrap rdzenia: {sorted(ATRAPY_UZYTE)}")


def _wgraj_i_waliduj(c, url, exp):
    p = oc.FIXTURY / exp["plik"]
    r = c.post(url, files={"plik": (p.name, p.read_bytes(), "text/csv")})
    assert r.status_code == 200, r.text
    imp = r.json()
    d = exp["dostawca"]
    w = c.post(f"/api/importy/{imp['import_id']}/walidacja", json={
        "mapowanie": {m["kolumna"]: m["pole"] for m in imp["mapowanie_propozycja"]},
        "dysponent": {"nazwa": d["nazwa"], "typ": d["typ"]}, "wartosci_stale": exp["wartosci_stale"]})
    assert w.status_code == 200, w.text
    _xfail_gdy_atrapy()
    assert w.json()["mozna_publikowac"], w.json()["komunikaty"][:5]
    p = c.post(f"/api/importy/{imp['import_id']}/publikacja")
    assert p.status_code == 200, p.text
    return p.json()


def _id_z_csv(c, slug):
    g = c.get(f"/d/{slug}.csv")
    if g.status_code == 404:
        pytest.xfail("B3: /d/{slug}.csv jeszcze nie działa")
    assert g.status_code == 200
    return [r["id_aed"] for r in csv.DictReader(io.StringIO(g.content.decode("utf-8")))]


def test_demo_api_aktualizacja_pod_tym_samym_url(klient):
    c = klient
    pub1 = _wgraj_i_waliduj(c, "/api/importy", STARY)
    slug, token = pub1["slug"], pub1["token_edycji"]
    ids1 = _id_z_csv(c, slug)
    assert len(ids1) == 21

    pub2 = _wgraj_i_waliduj(c, f"/api/zbiory/{slug}/importy?token={token}", NOWY)
    assert pub2["slug"] == slug and pub2["url_csv"] == pub1["url_csv"]
    assert pub2["token_edycji"] is None
    ids2 = _id_z_csv(c, slug)
    assert ids2 == ids1, "id_aed zmieniły się po ponownym wgraniu"

    zly = c.get(f"/api/zbiory/{slug}?token=zly")
    assert zly.status_code == 403
