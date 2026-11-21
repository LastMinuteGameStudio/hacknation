"""A6: eksport: CSV RFC 4180 (UTF-8 bez BOM, przecinek, CRLF, pola publiczne w kolejności zakresu), JSON, CSVW.
Wzór CSVW: zakres-danych/szablon-aed-publiczny.csv-metadata.json.
"""

from __future__ import annotations

from .types import Schema


def to_csv(records: list[dict[str, str]], schema: Schema, public_only: bool = True) -> bytes:
    raise NotImplementedError("A6: export.to_csv")


def to_json(records: list[dict[str, str]], schema: Schema, metadata: dict) -> bytes:
    raise NotImplementedError("A6: export.to_json")


def csvw_metadata(schema: Schema, csv_url: str, title: str) -> dict:
    raise NotImplementedError("A6: export.csvw_metadata")
