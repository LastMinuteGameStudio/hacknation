"""A2: odczyt CSV (separator, kodowanie utf-8/cp1250, BOM, cudzysłowy) i XLSX (openpyxl) → Table.

Wymagania: wykrywanie wiersza nagłówka (np. tytuł nad tabelą), puste wiersze pomijane,
wartości jako tekst (liczby z XLSX bez utraty precyzji współrzędnych), komunikaty w Table.messages.
Przypadek z Marek: cały wiersz w jednym polu w cudzysłowie, trzeba go rozpoznać i rozbić.
"""

from __future__ import annotations

from typing import Optional

from .types import Table

MAX_BAJTOW = 10 * 1024 * 1024
MAX_WIERSZY = 20_000


def read_table(content: bytes, filename: str, sheet: Optional[str] = None) -> Table:
    raise NotImplementedError("A2: parsers.read_table")
