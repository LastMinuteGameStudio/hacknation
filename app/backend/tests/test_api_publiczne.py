"""B3: pliki publiczne /d/{slug}.csv | .json | .csv-metadata.json i szablony."""

import csv
import io
import os
import tempfile

os.environ.setdefault("DATABASE_URL", f"sqlite:///{tempfile.mkdtemp()}/test.db")

from tests.test_api_import import DYSPONENT, _waliduj, _wgraj, c  # noqa: E402

from app.importy import SCHEMA  # noqa: E402


def _opublikuj():
    imp = _wgraj()
    assert _waliduj(imp)["mozna_publikowac"]
    return c.post(f"/api/importy/{imp['import_id']}/publikacja").json()


def test_csv_rfc4180_tylko_pola_publiczne():
    p = _opublikuj()
    r = c.get(f"/d/{p['slug']}.csv")
    assert r.status_code == 200
    assert r.headers["content-type"] == "text/csv; charset=utf-8"
    b = r.content
    assert not b.startswith(b"\xef\xbb\xbf")  # bez BOM
    assert b.count(b"\r\n") >= 22 and b"\n" not in b.replace(b"\r\n", b"")
    wiersze = list(csv.reader(io.StringIO(b.decode("utf-8"), newline="")))
    assert wiersze[0] == SCHEMA.publiczne
    assert len(wiersze) == 22
    assert "telefon_kontaktowy" not in wiersze[0] and DYSPONENT["email"] not in b.decode()
    assert p["url_csv"].endswith(f"/d/{p['slug']}.csv")


def test_json_i_csvw():
    p = _opublikuj()
    j = c.get(f"/d/{p['slug']}.json").json()
    assert j["metadane"]["licencja"] == "CC0 1.0" and j["metadane"]["liczba_rekordow"] == 21
    assert len(j["rekordy"]) == 21 and set(j["rekordy"][0]) == set(SCHEMA.publiczne)
    m = c.get(f"/d/{p['slug']}.csv-metadata.json")
    assert m.status_code == 200
    assert m.json()["url"] == p["url_csv"]
    kolumny = m.json()["tableSchema"]["columns"]
    assert [k["name"] for k in kolumny] == SCHEMA.publiczne
    # CSVW §5.5.1: nagłówek CSV musi być wśród titles kolumny
    naglowek = c.get(f"/d/{p['slug']}.csv").text.splitlines()[0].split(",")
    for h, k in zip(naglowek, kolumny):
        assert h in k["titles"] and k["titles"][1] == SCHEMA.pole(h).nazwa


def test_brak_zbioru_i_zle_rozszerzenie():
    assert c.get("/d/nieistnieje.csv").json()["detail"]["kod"] == "NIE_ZNALEZIONO"
    p = _opublikuj()
    assert c.get(f"/d/{p['slug']}.xml").status_code == 404


def test_szablony():
    r = c.get("/szablon.csv")
    assert r.status_code == 200 and r.text.splitlines()[0].startswith("id_aed")
    assert c.get("/szablon.xlsx").status_code == 200
