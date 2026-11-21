"""T0: test dymny szkieletu. Ścieżka D dodaje testy na realnych plikach w tests/ (fixtury w tests/fixtury/)."""

from fastapi.testclient import TestClient

from app.main import SCHEMA, app


def test_schemat_wczytany():
    assert SCHEMA.wersja == "0.5"
    assert len(SCHEMA.pola) >= 50
    assert "dostepnosc" in SCHEMA.slowniki
    assert SCHEMA.pole("szerokosc_geograficzna").wymagalnosc == "O"


def test_endpointy_kontraktu():
    c = TestClient(app)
    assert c.get("/api/zdrowie").json()["status"] == "ok"
    s = c.get("/api/schemat").json()
    assert s["wersja"] == "0.5" and s["pola"]
    r = c.post("/api/importy", files={"plik": ("krosno.csv", b"a,b\n1,2\n", "text/csv")}).json()
    assert r["import_id"] and r["mapowanie_propozycja"]
    w = c.post(f"/api/importy/{r['import_id']}/walidacja",
               json={"mapowanie": {}, "dysponent": {"nazwa": "UM Krosno", "typ": "jst"}}).json()
    assert "mozna_publikowac" in w
    p = c.post(f"/api/importy/{r['import_id']}/publikacja").json()
    assert p["url_csv"].endswith(".csv")
    assert c.get("/szablon.csv").status_code == 200
