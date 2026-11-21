"""Wybór: prawdziwy rdzeń (aed_core) albo atrapa z app/mock.py, osobno dla każdej funkcji.

MOCK=auto (domyślnie): woła rdzeń; gdy zgłosi NotImplementedError, woła atrapę i zapamiętuje to w ATRAPY_UZYTE.
MOCK=1: zawsze atrapy. MOCK=0: tylko rdzeń (NotImplementedError leci dalej).
"""

from __future__ import annotations

from typing import Optional

from aed_core import export, mapping, normalize, parsers, validate
from aed_core.geocode import GugikGeocoder
from aed_core.types import AddressQuery, GeoResult

from . import mock
from .config import MOCK

ATRAPY_UZYTE: set[str] = set()


def _wybierz(nazwa: str, prawdziwa, atrapa):
    def f(*args, **kwargs):
        if MOCK == "1":
            ATRAPY_UZYTE.add(nazwa)
            return atrapa(*args, **kwargs)
        try:
            return prawdziwa(*args, **kwargs)
        except NotImplementedError:
            if MOCK == "0":
                raise
            ATRAPY_UZYTE.add(nazwa)
            return atrapa(*args, **kwargs)

    f.__name__ = nazwa
    return f


read_table = _wybierz("read_table", parsers.read_table, mock.read_table)
suggest_mapping = _wybierz("suggest_mapping", mapping.suggest_mapping, mock.suggest_mapping)
normalize_table = _wybierz("normalize_table", normalize.normalize_table, mock.normalize_table)
validate_records = _wybierz("validate_records", validate.validate_records, mock.validate_records)
to_csv = _wybierz("to_csv", export.to_csv, mock.to_csv)
to_json = _wybierz("to_json", export.to_json, mock.to_json)
csvw_metadata = _wybierz("csvw_metadata", export.csvw_metadata, mock.csvw_metadata)


class Geokoder:
    """GugikGeocoder z cache w bazie. Gdy geokoder rdzenia nie działa (NotImplementedError), zwraca None."""

    def __init__(self, cache) -> None:
        self._g = GugikGeocoder(cache=cache)

    def geocode(self, query: AddressQuery) -> Optional[GeoResult]:
        try:
            return self._g.geocode(query)
        except NotImplementedError:
            if MOCK == "0":
                raise
            ATRAPY_UZYTE.add("geocode")
            return None
