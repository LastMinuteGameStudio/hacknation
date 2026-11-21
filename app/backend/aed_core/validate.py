"""A5: walidacja rekordów: O = błąd, Z = ostrzeżenie (zbiorczo per pole), formaty, słowniki,
współrzędne w Polsce (bbox ok. 49.0–54.9 N, 14.1–24.2 E), duplikaty id_aed / numer_seryjny (błąd),
bliskie punkty < 5 m (ostrzeżenie). Kody: app/KONTRAKT.md, sekcja 4.
"""

from __future__ import annotations

from .types import Message, RecordResult, Schema


def validate_records(records: list[RecordResult], schema: Schema) -> list[Message]:
    raise NotImplementedError("A5: validate.validate_records")
