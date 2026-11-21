"""B2: import → walidacja → publikacja, edycja przez prywatny link. Baza: SQLite w katalogu tymczasowym."""

import os
import tempfile
from pathlib import Path

os.environ.setdefault("DATABASE_URL", f"sqlite:///{tempfile.mkdtemp()}/test.db")

from fastapi.testclient import TestClient  # noqa: E402

from app.db import Rekord, SessionLocal, Zbior  # noqa: E402
from app.importy import hash_tokenu, zgrupuj  # noqa: E402
from app.main import app  # noqa: E402
from aed_core.types import Message  # noqa: E402

FIX = Path(__file__).parent / "fixtury"
c = TestClient(app)

MAPOWANIE = {
    "Długość geograficzna": "dlugosc_geograficzna",
    "Szerokość geograficzna": "szerokosc_geograficzna",
    "Nazwa": None,
    "Lokalizacja": "nazwa_obiektu",
    "Adres": "nazwa_ulicy",
    "Numer Id": "id_zrodlowe",
}
DYSPONENT = {"nazwa": "Urząd Miasta Krosna", "typ": "jst", "telefon": "134343434", "email": "aed@um.krosno.pl"}
STALE = {"wewnatrz_budynku": "true", "dostepnosc": "publiczny", "dostepny_24_7": "nie", "miejscowosc": "Krosno"}


def _wgraj(url="/api/importy", nazwa="krosno.csv"):
    r = c.post(url, files={"plik": (nazwa, (FIX / nazwa).read_bytes(), "text/csv")})
    assert r.status_code == 200, r.text
    return r.json()


def _mapowanie(imp):
    # nazwy kolumn z pliku (parser może je przyciąć), dopasowane po treści
    return {k["nazwa"]: MAPOWANIE.get(k["nazwa"].strip()) for k in imp["kolumny"]}


def _waliduj(imp, stale=STALE):
    r = c.post(f"/api/importy/{imp['import_id']}/walidacja",
               json={"mapowanie": _mapowanie(imp), "dysponent": DYSPONENT, "wartosci_stale": stale})
    assert r.status_code == 200, r.text
    return r.json()


def test_import_zwraca_kolumny_z_pliku():
    imp = _wgraj()
    assert imp["liczba_wierszy"] == 21
    assert [k["nazwa"].strip() for k in imp["kolumny"]][:2] == ["Długość geograficzna", "Szerokość geograficzna"]
    assert len(imp["podglad"]) == 10
    assert len(imp["mapowanie_propozycja"]) == len(imp["kolumny"])
    assert imp["kolumny"][0]["przyklady"]


def test_zly_format_i_brak_importu():
    r = c.post("/api/importy", files={"plik": ("a.pdf", b"%PDF", "application/pdf")})
    assert r.status_code == 415 and r.json()["detail"]["kod"] == "NIEOBSLUGIWANY_FORMAT"
    r = c.post("/api/importy/nie-ma/walidacja", json={"mapowanie": {}, "dysponent": DYSPONENT})
    assert r.status_code == 404 and r.json()["detail"]["kod"] == "NIE_ZNALEZIONO"


def test_publikacja_wymaga_walidacji_bez_bledow():
    imp = _wgraj()
    assert c.post(f"/api/importy/{imp['import_id']}/publikacja").status_code == 409
    w = _waliduj(imp, stale={})  # brak wartości stałych dla pól O → błędy
    assert not w["mozna_publikowac"] and w["liczba_bledow"] > 0
    r = c.post(f"/api/importy/{imp['import_id']}/publikacja")
    assert r.status_code == 409 and r.json()["detail"]["kod"] == "SA_BLEDY"


def test_pelny_przebieg_i_edycja():
    imp = _wgraj()
    w = _waliduj(imp)
    assert w["mozna_publikowac"], w["komunikaty"]
    assert w["liczba_rekordow"] == 21
    assert len(w["podglad_wyniku"]) == 20
    assert "telefon_kontaktowy" not in w["podglad_wyniku"][0]  # tylko pola publiczne

    p = c.post(f"/api/importy/{imp['import_id']}/publikacja").json()
    slug, token = p["slug"], p["token_edycji"]
    assert token and len(token) >= 32
    assert p["url_csv"].endswith(f"/d/{slug}.csv") and f"token={token}" in p["url_edycji"]

    with SessionLocal() as s:
        z = s.query(Zbior).filter_by(slug=slug).one()
        assert z.token_edycji_hash == hash_tokenu(token) and token not in z.token_edycji_hash
        assert s.query(Rekord).filter_by(zbior_id=z.id).count() == 21

    # prywatny link
    assert c.get(f"/api/zbiory/{slug}?token=zly").status_code == 403
    assert c.get(f"/api/zbiory/{slug}").json()["detail"]["kod"] == "ZLY_TOKEN"
    assert c.get(f"/api/zbiory/nieistnieje?token={token}").status_code == 404
    zb = c.get(f"/api/zbiory/{slug}?token={token}").json()
    assert zb["liczba_rekordow"] == 21 and zb["dysponent"]["nazwa"] == DYSPONENT["nazwa"]
    assert zb["mapowanie"] == _mapowanie(imp)

    # ponowne wgranie (mniejszy plik) zastępuje rekordy pod tym samym slugiem
    r = c.post(f"/api/zbiory/{slug}/importy?token=zly", files={"plik": ("krosno.csv", b"a\n1\n", "text/csv")})
    assert r.status_code == 403
    mniejszy = "\n".join((FIX / "krosno.csv").read_text(encoding="utf-8").splitlines()[:6]).encode()
    r = c.post(f"/api/zbiory/{slug}/importy?token={token}", files={"plik": ("krosno.csv", mniejszy, "text/csv")})
    imp2 = r.json()
    poprzednie = {m["kolumna"]: m["pole"] for m in imp2["mapowanie_propozycja"]}
    assert poprzednie["Lokalizacja" if "Lokalizacja" in poprzednie else " Lokalizacja"] == "nazwa_obiektu"
    w2 = _waliduj(imp2)
    assert w2["liczba_rekordow"] == 5
    p2 = c.post(f"/api/importy/{imp2['import_id']}/publikacja").json()
    assert p2["slug"] == slug and p2["token_edycji"] is None and p2["url_csv"] == p["url_csv"]
    assert c.get(f"/api/zbiory/{slug}?token={token}").json()["liczba_rekordow"] == 5


def test_zgrupuj_ponad_20_wierszy():
    msgs = [Message("ostrzezenie", "NISKA_PRECYZJA", "Mało miejsc po przecinku.", w, "szerokosc_geograficzna") for w in range(2, 30)]
    msgs.append(Message("info", "X", "pojedynczy", 5, None))
    g = zgrupuj(msgs)
    assert len(g) == 2
    assert g[0].wiersz is None and "28 wierszy" in g[0].komunikat and "2, 3, 4" in g[0].komunikat
