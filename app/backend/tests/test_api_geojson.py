"""S2: GeoJSON (RFC 7946) agregatu i pojedynczego zbioru."""

import csv
import io
import json
import os
import tempfile

os.environ.setdefault("DATABASE_URL", f"sqlite:///{tempfile.mkdtemp()}/test.db")

from tests.test_api_agregat import OSM_LAT, OSM_LON, _opublikuj_punkt  # noqa: E402
from tests.test_api_import import DYSPONENT, c  # noqa: E402
from tests.test_api_publiczne import _opublikuj  # noqa: E402

from app.importy import SCHEMA  # noqa: E402

KOLUMNY_AGREGATU = set(SCHEMA.publiczne) | {"zrodlo", "licencja_zrodla"}


def _geojson(url):
    r = c.get(url)
    assert r.status_code == 200, r.text
    assert r.headers["content-type"] == "application/geo+json"
    assert r.headers["access-control-allow-origin"] == "*"
    return json.loads(r.content.decode("utf-8"))


def _sprawdz_rfc7946(fc, kolumny):
    assert fc["type"] == "FeatureCollection" and isinstance(fc["features"], list)
    for f in fc["features"]:
        assert f["type"] == "Feature" and set(f) >= {"geometry", "properties"}
        g = f["geometry"]
        assert g["type"] == "Point" and len(g["coordinates"]) == 2
        lon, lat = g["coordinates"]
        assert isinstance(lon, float) and isinstance(lat, float)
        assert 14 < lon < 24.5 and 49 < lat < 55  # [lon, lat], nie odwrotnie
        assert set(f["properties"]) <= kolumny
        assert "X" not in f["properties"].values() and "" not in f["properties"].values()
        assert float(f["properties"]["szerokosc_geograficzna"]) == lat


def _liczba_wierszy_csv(url):
    return len(list(csv.reader(io.StringIO(c.get(url).content.decode("utf-8"), newline="")))) - 1


def test_geojson_zbioru():
    p = _opublikuj()
    fc = _geojson(f"/d/{p['slug']}.geojson")
    _sprawdz_rfc7946(fc, set(SCHEMA.publiczne))
    assert len(fc["features"]) == _liczba_wierszy_csv(f"/d/{p['slug']}.csv") == 21
    assert fc["metadane"]["licencja"] == "CC0 1.0"  # foreign member (RFC 7946 §6.1)
    assert DYSPONENT["email"] not in json.dumps(fc)  # tylko pola publiczne
    assert fc["features"][0]["id"] == fc["features"][0]["properties"]["id_aed"]


def test_geojson_agregatu_z_osm_i_bez():
    slug = _opublikuj_punkt(OSM_LAT + 0.0001, OSM_LON, "Schronisko")
    fc = _geojson("/d/aed-polska.geojson")
    _sprawdz_rfc7946(fc, KOLUMNY_AGREGATU)
    assert len(fc["features"]) == _liczba_wierszy_csv("/d/aed-polska.csv")
    nasz = next(f for f in fc["features"] if f["properties"]["zrodlo"] == f"tuaed:{slug}")
    assert nasz["properties"]["licencja_zrodla"] == "CC0 1.0"
    osm = next(f for f in fc["features"] if f["id"] == "osm:node/477958354")
    dostawcy = {f["id"] for f in fc["features"] if f["properties"]["zrodlo"].startswith("tuaed:")}
    assert osm["properties"]["duplikat_id_aed"] in dostawcy  # inne testy mogły dodać punkt w tym samym miejscu

    bez = _geojson("/d/aed-polska-bez-osm.geojson")
    assert len(bez["features"]) == _liczba_wierszy_csv("/d/aed-polska-bez-osm.csv")
    assert not any(f["properties"]["zrodlo"] == "osm" for f in bez["features"])


def test_geojson_odswieza_sie_po_publikacji():
    przed = len(_geojson("/d/aed-polska-bez-osm.geojson")["features"])
    _opublikuj_punkt(OSM_LAT + 0.01, OSM_LON, "Nowy")
    assert len(_geojson("/d/aed-polska-bez-osm.geojson")["features"]) == przed + 1
