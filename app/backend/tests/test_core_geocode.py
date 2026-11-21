import json

import httpx

from aed_core.geocode import GugikGeocoder, adres_tekst, klucz
from aed_core.types import AddressQuery


def adres(**kw):
    return {"type": "address", "results": {"1": {"city": "Krosno", "street": "Lwowska", "number": "28A", "teryt": "186101",
            "simc": "0952410", "ulic": "11467", "code": "38-400", "x": "21.7711294533718", "y": "49.684015450621",
            "accuracy": "1", **kw}}}


class Cache:
    def __init__(self):
        self.d = {}

    def get(self, k):
        return self.d.get(k)

    def put(self, k, v):
        self.d[k] = v


def geo(handler, **kw):
    zapytania = []

    def h(req):
        zapytania.append(req)
        return handler(req)

    g = GugikGeocoder(client=httpx.Client(transport=httpx.MockTransport(h)), **kw)
    return g, zapytania


Q = AddressQuery(ulica="Lwowska", nr_budynku="28a", kod_pocztowy="38-400", miejscowosc="Krosno")


def test_adres_tekst():
    assert adres_tekst(Q) == "38-400 Krosno, Lwowska 28a"
    assert adres_tekst(AddressQuery(ulica="Wola", nr_budynku="12", miejscowosc="Wola")) == "Wola 12"


def test_trafienie_i_cache():
    c = Cache()
    g, z = geo(lambda r: httpx.Response(200, json=adres()), cache=c, nominatim=False)
    r = g.geocode(Q)
    assert (r.lat, r.lon) == (49.684015450621, 21.7711294533718)
    assert r.dokladnosc == "punkt_adresowy" and r.kod_terc == "186101" and r.kod_simc == "0952410"
    assert not r.niejednoznaczny
    assert z[0].url.params["address"] == "38-400 Krosno, Lwowska 28a" and z[0].url.params["srid"] == "4326"
    g.geocode(Q)
    assert len(z) == 1 and klucz(Q) in c.d


def test_wiele_wynikow_zawezenie_kodem():
    d = {"type": "address", "results": {
        "1": {"city": "Krosno", "code": "64-000", "teryt": "302110", "x": "16.8", "y": "52.2", "accuracy": "1"},
        "2": {"city": "Krosno", "code": "38-400", "teryt": "186101", "x": "21.77", "y": "49.68", "accuracy": "1"}}}
    g, _ = geo(lambda r: httpx.Response(200, json=d), nominatim=False)
    r = g.geocode(Q)
    assert r.lat == 49.68 and not r.niejednoznaczny
    r2 = g.geocode(AddressQuery(ulica="Jasna", miejscowosc="Krosno"))
    assert r2.niejednoznaczny


def test_bez_numeru_ulica_przyblizone():
    def h(req):
        if "28a" in req.url.params["address"]:
            return httpx.Response(200, json={"type": "address", "results": None})
        return httpx.Response(200, json={"type": "street", "results": {"1": {"city": "Krosno", "teryt": "186101",
                                                                       "x": "21.72", "y": "49.71", "accuracy": "1"}}})
    g, z = geo(h, nominatim=False)
    r = g.geocode(Q)
    assert r.dokladnosc == "przyblizone" and r.niejednoznaczny and len(z) == 2


def test_nominatim_zapas():
    def h(req):
        if "gugik" in req.url.host:
            return httpx.Response(200, json={"type": "address", "results": None})
        assert req.url.params["countrycodes"] == "pl" and "User-Agent" in req.headers
        return httpx.Response(200, json=[{"lat": "49.7", "lon": "21.7", "address": {"house_number": "28a", "postcode": "38-400"}}])
    g, _ = geo(h)
    g.client.headers["User-Agent"] = "test"
    r = g.geocode(Q)
    assert r.lat == 49.7 and r.dokladnosc == "punkt_adresowy"


def test_brak_i_blad_sieci_nie_cacheowany():
    c = Cache()
    g, _ = geo(lambda r: httpx.Response(503), cache=c, nominatim=False)
    assert g.geocode(Q) is None and c.d == {}
    g2, _ = geo(lambda r: httpx.Response(200, json={"type": "address", "results": None}), cache=c, nominatim=False)
    assert g2.geocode(Q) is None and klucz(Q) in c.d


def test_bez_miejscowosci_nie_pyta():
    g, z = geo(lambda r: httpx.Response(200, json=adres()), nominatim=False)
    assert g.geocode(AddressQuery(ulica="Lwowska")) is None and not z
