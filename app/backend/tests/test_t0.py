"""T0: test dymny szkieletu. Pełny przebieg API: tests/test_api_*.py (ścieżka B)."""

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
    assert c.get("/szablon.csv").status_code == 200
