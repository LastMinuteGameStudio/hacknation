"""GET /api/zbiory: publiczna lista zbiorów (strona /dane)."""

import os
import tempfile

os.environ.setdefault("DATABASE_URL", f"sqlite:///{tempfile.mkdtemp()}/test.db")

from tests.test_api_import import DYSPONENT, c  # noqa: E402
from tests.test_api_publiczne import _opublikuj  # noqa: E402
from tests.test_api_synchronizacja import URL, zrodlo  # noqa: E402,F401  (fixture)
from tests.test_api_synchronizacja import _opublikuj as _opublikuj_przemysl  # noqa: E402

POLA = {"slug", "dysponent_nazwa", "dysponent_typ", "liczba_rekordow", "utworzono", "zaktualizowano",
        "synchronizacja", "url_csv", "url_json", "url_geojson", "url_metadane"}


def _lista():
    r = c.get("/api/zbiory")
    assert r.status_code == 200 and r.headers["access-control-allow-origin"] == "*"
    return r.json()


def test_lista_bez_danych_niepublicznych(zrodlo):  # noqa: F811
    p = _opublikuj()
    q = _opublikuj_przemysl()
    c.put(f"/api/zbiory/{q['slug']}/zrodlo?token={q['token_edycji']}", json={"url": URL, "co_ile_godzin": 12})
    lista = _lista()
    tekst = str(lista)
    for tajne in (DYSPONENT["email"], DYSPONENT["telefon"], p["token_edycji"], q["token_edycji"], URL, "token", "zrodlo_url"):
        assert tajne not in tekst
    assert all(set(z) == POLA for z in lista)

    po_slugu = {z["slug"]: z for z in lista}
    a, b = po_slugu[p["slug"]], po_slugu[q["slug"]]
    assert a["liczba_rekordow"] == 21 and a["synchronizacja"] is None and a["dysponent_typ"] == "jst"
    assert a["url_csv"] == p["url_csv"] and a["url_geojson"].endswith(f"/d/{p['slug']}.geojson")
    assert b["liczba_rekordow"] == 21
    assert b["synchronizacja"]["status"] == "aktywna" and b["synchronizacja"]["co_ile_godzin"] == 12
    assert b["synchronizacja"]["ostatni_sukces"]
    # od ostatnio aktualizowanych
    daty = [z["zaktualizowano"] for z in lista]
    assert daty == sorted(daty, reverse=True)
    assert lista.index(b) < lista.index(a)


def test_liczba_rekordow_po_podmianie():
    p = _opublikuj()
    s, t = p["slug"], p["token_edycji"]
    from tests.test_api_import import FIX, _waliduj
    mniejszy = "\n".join((FIX / "krosno.csv").read_text(encoding="utf-8").splitlines()[:4]).encode()
    imp = c.post(f"/api/zbiory/{s}/importy?token={t}", files={"plik": ("krosno.csv", mniejszy, "text/csv")}).json()
    assert _waliduj(imp)["mozna_publikowac"]
    c.post(f"/api/importy/{imp['import_id']}/publikacja")
    z = next(z for z in _lista() if z["slug"] == s)
    assert z["liczba_rekordow"] == 3
    assert _lista()[0]["slug"] == s
