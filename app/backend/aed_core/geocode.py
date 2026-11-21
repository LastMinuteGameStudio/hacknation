"""A7: geokoder GUGiK UUG (https://services.gugik.gov.pl/uug/?request=GetAddress&address=...&srid=4326), bez klucza.

Zwraca x (lon), y (lat), teryt (6 cyfr gminy), simc, ulic, code (kod pocztowy), accuracy.
Przy wielu wynikach zawężamy kodem pocztowym albo gminą (TERC). Brak trafienia → Nominatim jako zapas (UA, 1/s).
Cache przez GeocodeCache (w API: tabela geokod_cache).
"""

from __future__ import annotations

from typing import Optional

from .types import AddressQuery, GeocodeCache, GeoResult

GUGIK_URL = "https://services.gugik.gov.pl/uug/"


class GugikGeocoder:
    def __init__(self, cache: Optional[GeocodeCache] = None, timeout: float = 10.0) -> None:
        self.cache = cache
        self.timeout = timeout

    def geocode(self, query: AddressQuery) -> Optional[GeoResult]:
        raise NotImplementedError("A7: GugikGeocoder.geocode")
