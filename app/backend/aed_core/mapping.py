"""A3: propozycja mapowania kolumn pliku → pola v0.5 (heurystyka + synonimy + analiza zawartości).

Kontrakt: każda kolumna dostaje dokładnie jedną propozycję (pole albo None). Jedno pole najwyżej raz.
Kolumna z geometrią (JSON z lat/long lub coordinates, WKT) → types.POLE_GEOMETRIA.
Synonimy trzymamy w synonimy.py. Testy jakości: ścieżka D (raport % trafień na realnych plikach).
"""

from __future__ import annotations

from typing import Optional

from .types import MappingSuggestion, Schema, Table


def suggest_mapping(
    table: Table, schema: Schema, previous: Optional[dict[str, Optional[str]]] = None
) -> list[MappingSuggestion]:
    raise NotImplementedError("A3: mapping.suggest_mapping")
