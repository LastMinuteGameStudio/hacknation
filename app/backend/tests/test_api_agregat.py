"""B4: agregat /d/aed-polska.csv i /d/aed-polska-bez-osm.csv."""

import csv
import io
import os
import tempfile

os.environ.setdefault("DATABASE_URL", f"sqlite:///{tempfile.mkdtemp()}/test.db")

from tests.test_api_import import DYSPONENT, c  # noqa: E402

from app import agregat  # noqa: E402
from app.importy import SCHEMA  # noqa: E402

# Rekord OSM z dane/wynik/aed_unikalne.csv (pierwszy wiersz): Schronisko PTTK Markowe Szczawiny.
OSM_ID, OSM_LAT, OSM_LON = "osm:node/477958354", 49.5878956, 19.5168185


def _wiersze(nazwa):
    r = c.get(f"/d/{nazwa}")
    assert r.status_code == 200 and r.headers["content-type"] == "text/csv; charset=utf-8"
    assert not r.content.startswith(b"\xef\xbb\xbf")
    return list(csv.DictReader(io.StringIO(r.content.decode("utf-8"), newline="")))


def _opublikuj_punkt(lat, lon, nazwa_obiektu):
    tresc = (f"id,lat,lon,nazwa,ulica,miasto\n"
             f"P1,{lat:.7f},{lon:.7f},{nazwa_obiektu},Markowe Szczawiny,Zawoja\n").encode()
    imp = c.post("/api/importy", files={"plik": ("punkt.csv", tresc, "text/csv")}).json()
    m = {"id": "id_zrodlowe", "lat": "szerokosc_geograficzna", "lon": "dlugosc_geograficzna",
         "nazwa": "nazwa_obiektu", "ulica": "nazwa_ulicy", "miasto": "miejscowosc"}
    stale = {"wewnatrz_budynku": "true", "dostepnosc": "publiczny", "dostepny_24_7": "tak"}
    w = c.post(f"/api/importy/{imp['import_id']}/walidacja",
               json={"mapowanie": m, "dysponent": DYSPONENT, "wartosci_stale": stale}).json()
    assert w["mozna_publikowac"], w["komunikaty"]
    return c.post(f"/api/importy/{imp['import_id']}/publikacja").json()["slug"]


def test_odleglosc():
    assert abs(agregat.odleglosc_m(52.0, 21.0, 52.0, 21.001) - 68.5) < 1


def test_agregat_z_osm_i_bez_osm_oraz_duplikat():
    slug = _opublikuj_punkt(OSM_LAT + 0.0001, OSM_LON, "Schronisko")  # ~11 m od punktu OSM
    wiersze = _wiersze("aed-polska.csv")
    assert list(wiersze[0]) == SCHEMA.publiczne + ["zrodlo", "licencja_zrodla"]
    nasze = [w for w in wiersze if w["zrodlo"] == f"tuaed:{slug}"]
    assert len(nasze) == 1
    n = nasze[0]
    assert n["id_aed"].startswith(f"{slug}:") and n["licencja_zrodla"] == "CC0 1.0"
    assert n["status_walidacji"] == "oczekuje" and n["duplikat_id_aed"] == "X"
    osm = next(w for w in wiersze if w["id_aed"] == OSM_ID)
    assert osm["duplikat_id_aed"] == n["id_aed"]  # rekord dostawcy jest główny, OSM zostaje
    assert sum(w["zrodlo"] == "osm" for w in wiersze) > 18000
    assert "" not in {v for w in wiersze[:50] for v in w.values()}  # brak = „X”

    bez = _wiersze("aed-polska-bez-osm.csv")
    assert not any(w["zrodlo"] == "osm" for w in bez)
    assert any(w["zrodlo"] == f"tuaed:{slug}" for w in bez)
    assert len(bez) == len(wiersze) - sum(w["zrodlo"] == "osm" for w in wiersze)


def test_daleki_punkt_nie_jest_duplikatem():
    slug = _opublikuj_punkt(OSM_LAT + 0.001, OSM_LON, "Daleko")  # ~111 m
    wiersze = _wiersze("aed-polska.csv")
    nasz = next(w for w in wiersze if w["zrodlo"] == f"tuaed:{slug}")
    assert not any(w["duplikat_id_aed"] == nasz["id_aed"] for w in wiersze)
