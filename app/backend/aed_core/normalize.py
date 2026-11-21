"""A4: normalizacja wartości do formatu v0.5 + pola stałe i domyślne.

Zakres: liczby (przecinek dziesiętny), współrzędne (zamiana lat/lon, geometria JSON/WKT), daty → ISO 8601,
wartości logiczne (tak/nie/1/0) → true/false, słowniki (synonimy wartości → kody), godziny („24h”, opening_hours → godziny_pn..nd),
adres w jednym polu → ulica / nr / kod / miejscowość, telefon → 9 cyfr.
Pola stałe: dysponent_* z Provider, zrodlo_danych, data_aktualizacji.
Domyślne + ostrzeżenia: id_aed (WYGENEROWANO_ID), status=nieznany (DOMYSLNY_STATUS), data_weryfikacji=today (DOMYSLNA_DATA_WERYFIKACJI).
Geokodowanie (A7) wywoływane tu, gdy brak współrzędnych, a jest adres; limit 200 adresów na plik.
"""

from __future__ import annotations

from datetime import date
from typing import Optional

from .types import Geocoder, Provider, RecordResult, Schema, Table


def normalize_table(
    table: Table,
    mapping: dict[str, Optional[str]],
    schema: Schema,
    provider: Provider,
    today: date,
    geocoder: Optional[Geocoder] = None,
) -> list[RecordResult]:
    raise NotImplementedError("A4: normalize.normalize_table")
