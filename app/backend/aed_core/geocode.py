"""A7: geokoder GUGiK UUG (https://services.gugik.gov.pl/uug/?request=GetAddress&address=...&srid=4326), bez klucza.

Zwraca x (lon), y (lat), teryt (6 cyfr gminy), simc, ulic, code (kod pocztowy), accuracy.
Kolejność prób: adres z numerem → (bez trafienia) sama ulica, przybliżone → Nominatim jako zapas (UA, 1/s).
Przy wielu wynikach zawężamy kodem pocztowym, gminą (TERC) i nazwą miejscowości; gdy dalej kilka → niejednoznaczny.
Cache przez GeocodeCache (w API: tabela geokod_cache). Trafienia i brak trafienia są cache'owane,
błędy sieci nie (żeby chwilowa awaria nie zapisała „adresu nie ma”).
"""

from __future__ import annotations

import re
import threading
import time
import unicodedata
from typing import Optional

import httpx

from .types import AddressQuery, GeocodeCache, GeoResult

GUGIK_URL = "https://services.gugik.gov.pl/uug/"
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
USER_AGENT = "misja-aed-konwerter/0.1 (hackathon, geokodowanie adresow AED)"
MIN_DOKLADNOSC = 0.6  # accuracy GUGiK poniżej → wynik niejednoznaczny


class BladSieci(Exception):
    pass


def _n(s: str) -> str:
    s = (s or "").strip().lower().replace("ł", "l")
    s = unicodedata.normalize("NFKD", s)
    return re.sub(r"[^a-z0-9]", "", "".join(c for c in s if not unicodedata.combining(c)))


def klucz(q: AddressQuery) -> str:
    return "|".join([_n(q.ulica), _n(q.nr_budynku), re.sub(r"\D", "", q.kod_pocztowy), _n(q.miejscowosc),
                     re.sub(r"\D", "", q.kod_terc)[:6]])


def adres_tekst(q: AddressQuery, z_numerem: bool = True) -> str:
    miejsce = " ".join(x for x in (q.kod_pocztowy.strip(), q.miejscowosc.strip()) if x)
    nr = q.nr_budynku.strip() if z_numerem else ""
    if q.ulica.strip() and _n(q.ulica) != _n(q.miejscowosc):
        return f"{miejsce}, {q.ulica.strip()} {nr}".strip().strip(",").strip()
    return f"{miejsce} {nr}".strip()  # wieś bez ulic: „Wola Przykładowa 12”


class GugikGeocoder:
    def __init__(self, cache: Optional[GeocodeCache] = None, timeout: float = 10.0, nominatim: bool = True,
                 client: Optional[httpx.Client] = None) -> None:
        self.cache = cache
        self.timeout = timeout
        self.nominatim = nominatim
        self.client = client or httpx.Client(timeout=timeout, headers={"User-Agent": USER_AGENT})
        self._nom_lock = threading.Lock()
        self._nom_ostatnio = 0.0

    # --- publiczne --------------------------------------------------------------------------------

    def geocode(self, query: AddressQuery) -> Optional[GeoResult]:
        if not (query.miejscowosc.strip() or query.kod_pocztowy.strip()):
            return None
        k = klucz(query)
        if self.cache is not None:
            try:
                hit = self.cache.get(k)
            except Exception:
                hit = None
            if hit is not None:
                return hit
        try:
            wynik = self._geocode(query)
        except BladSieci:
            return None  # nie cache'ujemy
        if self.cache is not None:
            try:
                self.cache.put(k, wynik)
            except Exception:
                pass
        return wynik

    # --- wewnętrzne -------------------------------------------------------------------------------

    def _geocode(self, q: AddressQuery) -> Optional[GeoResult]:
        bledy = 0
        proby = [(adres_tekst(q, True), "punkt_adresowy")]
        if q.nr_budynku.strip():
            proby.append((adres_tekst(q, False), "przyblizone"))
        for tekst, dokl in proby:
            try:
                wyniki = self._gugik(tekst)
            except BladSieci:
                bledy += 1
                continue
            r = self._wybierz(wyniki, q, dokl)
            if r:
                if dokl == "przyblizone":
                    r.niejednoznaczny = True  # numer budynku nieznaleziony, punkt na ulicy
                return r
        if self.nominatim:
            try:
                r = self._nominatim(q)
            except BladSieci:
                bledy += 1
                r = None
            if r:
                return r
        if bledy:
            raise BladSieci()
        return None

    def _get(self, url: str, params: dict) -> dict | list:
        for proba in range(2):
            try:
                resp = self.client.get(url, params=params, timeout=self.timeout)
                if resp.status_code >= 500:
                    raise httpx.HTTPStatusError("5xx", request=resp.request, response=resp)
                resp.raise_for_status()
                return resp.json()
            except (httpx.HTTPError, ValueError):
                if proba == 1:
                    raise BladSieci()
                time.sleep(0.3)
        raise BladSieci()

    def _gugik(self, tekst: str) -> list[dict]:
        d = self._get(GUGIK_URL, {"request": "GetAddress", "address": tekst, "srid": "4326"})
        if not isinstance(d, dict):
            return []
        wyniki = d.get("results") or {}
        if isinstance(wyniki, dict):
            wyniki = list(wyniki.values())
        typ = d.get("type", "")
        out = []
        for w in wyniki:
            if isinstance(w, dict) and w.get("x") and w.get("y"):
                w = dict(w)
                w["_typ"] = typ
                out.append(w)
        return out

    def _wybierz(self, wyniki: list[dict], q: AddressQuery, dokl: str) -> Optional[GeoResult]:
        if not wyniki:
            return None
        kand = wyniki
        kod = q.kod_pocztowy.strip()
        terc = re.sub(r"\D", "", q.kod_terc)[:6]
        miasto = _n(q.miejscowosc)
        for filtr in (
            (lambda w: kod and w.get("code") == kod),
            (lambda w: terc and str(w.get("teryt", ""))[:6] == terc),
            (lambda w: miasto and _n(w.get("city", "")) == miasto),
        ):
            zaw = [w for w in kand if filtr(w)]
            if zaw:
                kand = zaw
        if miasto and not any(_n(w.get("city", "")) == miasto for w in kand) and not kod and not terc:
            return None  # trafienie w innej miejscowości
        kand = sorted(kand, key=lambda w: -float(w.get("accuracy") or 0))
        w = kand[0]
        try:
            lat, lon = float(w["y"]), float(w["x"])
        except (TypeError, ValueError):
            return None
        if w.get("_typ") != "address":
            dokl = "przyblizone"
        acc = float(w.get("accuracy") or 0)
        niejedn = (len(kand) > 1 and len({(round(float(x["y"]), 4), round(float(x["x"]), 4)) for x in kand}) > 1) \
            or acc < MIN_DOKLADNOSC
        return GeoResult(lat=lat, lon=lon, dokladnosc=dokl, kod_terc=str(w.get("teryt") or ""),
                         kod_simc=str(w.get("simc") or ""), kod_ulic=str(w.get("ulic") or ""),
                         kod_pocztowy=str(w.get("code") or ""), niejednoznaczny=niejedn)

    def _nominatim(self, q: AddressQuery) -> Optional[GeoResult]:
        params = {"format": "jsonv2", "countrycodes": "pl", "limit": "3", "addressdetails": "1"}
        if q.ulica.strip() and _n(q.ulica) != _n(q.miejscowosc):
            params["street"] = f"{q.nr_budynku} {q.ulica}".strip()
        if q.miejscowosc.strip():
            params["city"] = q.miejscowosc.strip()
        if q.kod_pocztowy.strip():
            params["postalcode"] = q.kod_pocztowy.strip()
        with self._nom_lock:  # zasady Nominatim: najwyżej 1 zapytanie na sekundę
            czekaj = 1.0 - (time.monotonic() - self._nom_ostatnio)
            if czekaj > 0:
                time.sleep(czekaj)
            try:
                d = self._get(NOMINATIM_URL, params)
            finally:
                self._nom_ostatnio = time.monotonic()
        if not isinstance(d, list) or not d:
            return None
        w = d[0]
        adres = w.get("address") or {}
        dokl = "punkt_adresowy" if adres.get("house_number") and q.nr_budynku.strip() else "przyblizone"
        return GeoResult(lat=float(w["lat"]), lon=float(w["lon"]), dokladnosc=dokl,
                         kod_pocztowy=str(adres.get("postcode") or ""),
                         niejednoznaczny=len(d) > 1 or dokl == "przyblizone")
