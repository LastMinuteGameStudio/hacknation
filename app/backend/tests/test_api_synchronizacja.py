"""S1: synchronizacja z URL źródła. Pobieranie podmienione na fixtury (bez sieci)."""

import os
import tempfile
from datetime import datetime, timedelta, timezone

os.environ.setdefault("DATABASE_URL", f"sqlite:///{tempfile.mkdtemp()}/test.db")

import pytest  # noqa: E402

from tests.fixtury import oczekiwania as oc  # noqa: E402
from tests.test_api_import import c  # noqa: E402

from app import synchronizacja as sync  # noqa: E402
from app.db import SessionLocal, Synchronizacja  # noqa: E402

URL = "https://przemysl.example.pl/open-data/aed.csv"


@pytest.fixture
def zrodlo(monkeypatch):
    """Zmienna „zawartość pliku pod URL”; sprawdz_url przepuszcza example.pl bez DNS."""
    stan = {"tresc": (oc.FIXTURY / "przemysl_2024.csv").read_bytes()}
    monkeypatch.setattr(sync, "pobierz", lambda url: (stan["tresc"], "aed.csv"))
    monkeypatch.setattr(sync, "sprawdz_url", lambda url: None)
    return stan


def _opublikuj(plik="przemysl_2024.csv"):
    exp = oc.wg_pliku(plik)
    p = oc.FIXTURY / plik
    imp = c.post("/api/importy", files={"plik": (p.name, p.read_bytes(), "text/csv")}).json()
    d = exp["dostawca"]
    w = c.post(f"/api/importy/{imp['import_id']}/walidacja", json={
        "mapowanie": {m["kolumna"]: m["pole"] for m in imp["mapowanie_propozycja"]},
        "dysponent": {"nazwa": d["nazwa"], "typ": d["typ"]}, "wartosci_stale": exp["wartosci_stale"]}).json()
    assert w["mozna_publikowac"], w["komunikaty"][:5]
    return c.post(f"/api/importy/{imp['import_id']}/publikacja").json()


def _id(slug):
    return [line.split(",")[0] for line in c.get(f"/d/{slug}.csv").text.splitlines()[1:]]


def test_brak_zrodla_i_zly_token():
    p = _opublikuj()
    s, t = p["slug"], p["token_edycji"]
    assert c.get(f"/api/zbiory/{s}/zrodlo?token=zly").status_code == 403
    o = c.get(f"/api/zbiory/{s}/zrodlo?token={t}").json()
    assert o["status"] == "brak" and o["url"] is None and o["liczba_rekordow"] == 21
    assert c.post(f"/api/zbiory/{s}/synchronizacja?token={t}").status_code == 404


def test_zly_url():
    p = _opublikuj()
    r = c.put(f"/api/zbiory/{p['slug']}/zrodlo?token={p['token_edycji']}", json={"url": "ftp://x/a.csv"})
    assert r.status_code == 422 and r.json()["detail"]["kod"] == "ZLY_URL"
    with pytest.raises(sync.BladPobierania):
        sync.sprawdz_url("http://127.0.0.1:8000/api/zdrowie")
    with pytest.raises(sync.BladPobierania):
        sync.sprawdz_url("http://db:5432/")  # sieć dockera / brak DNS


def test_synchronizacja_przemysl_zmiana_formatu_geometrii(zrodlo):
    p = _opublikuj()
    s, t = p["slug"], p["token_edycji"]
    przed = _id(s)
    o = c.put(f"/api/zbiory/{s}/zrodlo?token={t}", json={"url": URL, "co_ile_godzin": 6}).json()
    assert o["status"] == "aktywna" and o["co_ile_godzin"] == 6 and o["ostatni_sukces"]
    assert o["komunikaty"][0]["kod"] == "ZSYNCHRONIZOWANO"

    o = c.post(f"/api/zbiory/{s}/synchronizacja?token={t}").json()
    assert o["komunikaty"][0]["kod"] == "BEZ_ZMIAN"

    # źródło zmienia format geometrii ({lat,long} → [lon,lat]): te same AED, ten sam URL
    zrodlo["tresc"] = (oc.FIXTURY / "przemysl.csv").read_bytes()
    o = c.post(f"/api/zbiory/{s}/synchronizacja?token={t}").json()
    assert o["status"] == "aktywna" and o["komunikaty"][0]["kod"] == "ZSYNCHRONIZOWANO", o
    assert _id(s) == przed


def test_wstrzymanie_przy_zmianie_struktury_i_bledach(zrodlo):
    p = _opublikuj()
    s, t = p["slug"], p["token_edycji"]
    c.put(f"/api/zbiory/{s}/zrodlo?token={t}", json={"url": URL})
    tekst = (oc.FIXTURY / "przemysl_2024.csv").read_text(encoding="utf-8-sig")
    zrodlo["tresc"] = tekst.replace(";geometry;", ";geo;", 1).encode()
    o = c.post(f"/api/zbiory/{s}/synchronizacja?token={t}").json()
    assert o["status"] == "wstrzymana" and o["komunikaty"][0]["kod"] == "ZMIANA_STRUKTURY"
    assert "geometry" in o["komunikaty"][0]["komunikat"] and o["liczba_rekordow"] == 21  # dane nietknięte


def test_wstrzymanie_przy_duzej_zmianie_i_wymuszenie(zrodlo):
    p = _opublikuj()
    s, t = p["slug"], p["token_edycji"]
    c.put(f"/api/zbiory/{s}/zrodlo?token={t}", json={"url": URL})
    linie = (oc.FIXTURY / "przemysl_2024.csv").read_text(encoding="utf-8-sig").splitlines()
    zrodlo["tresc"] = "\n".join(linie[:6]).encode()  # 5 z 21 AED
    o = c.post(f"/api/zbiory/{s}/synchronizacja?token={t}").json()
    assert o["status"] == "wstrzymana" and o["komunikaty"][0]["kod"] == "ZA_DUZA_ZMIANA"
    assert o["liczba_rekordow"] == 21
    o = c.post(f"/api/zbiory/{s}/synchronizacja?token={t}&wymus=true").json()
    assert o["status"] == "aktywna" and o["liczba_rekordow"] == 5


def test_blad_pobierania(monkeypatch):
    p = _opublikuj()
    s, t = p["slug"], p["token_edycji"]
    monkeypatch.setattr(sync, "sprawdz_url", lambda url: None)

    def nie_dziala(url):
        raise sync.BladPobierania("Serwer źródła odpowiedział kodem 503.")

    monkeypatch.setattr(sync, "pobierz", nie_dziala)
    o = c.put(f"/api/zbiory/{s}/zrodlo?token={t}", json={"url": URL}).json()
    assert o["status"] == "blad" and o["komunikaty"][0]["kod"] == "BLAD_POBIERANIA" and o["liczba_rekordow"] == 21


def test_harmonogram_wybiera_zalegle(zrodlo):
    p = _opublikuj()
    s, t = p["slug"], p["token_edycji"]
    c.put(f"/api/zbiory/{s}/zrodlo?token={t}", json={"url": URL, "co_ile_godzin": 1})
    with SessionLocal() as db:
        teraz = datetime.now(timezone.utc)
        mid = db.query(Synchronizacja).order_by(Synchronizacja.zbior_id.desc()).first().zbior_id
        assert mid not in sync.zalegle(db, teraz)
        assert mid in sync.zalegle(db, teraz + timedelta(hours=1, minutes=1))
    c.put(f"/api/zbiory/{s}/zrodlo?token={t}", json={"url": None})
    assert c.get(f"/api/zbiory/{s}/zrodlo?token={t}").json()["status"] == "brak"
