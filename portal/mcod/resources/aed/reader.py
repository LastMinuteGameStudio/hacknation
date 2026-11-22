"""Odczyt wykazu AED dostawcy (CSV albo XLSX) do nagłówka i listy wierszy, wszystkie wartości jako tekst.

Czytamy surowy plik, a nie `resource.tabular_data` portalu: rzutowanie typów w portalu zamieniłoby
np. kod TERC „0201011” na liczbę 201011, a współrzędną „49.785100” na „49.7851”.
"""

import csv
import datetime
import io
from dataclasses import dataclass
from decimal import Decimal
from typing import Dict, List

ROZSZERZENIA = ("csv", "xlsx")


class BladOdczytu(Exception):
    """Pliku nie da się odczytać jako wykazu (format, kodowanie, brak nagłówka)."""


def _dekoduj(content: bytes) -> str:
    if content.startswith((b"\xff\xfe", b"\xfe\xff")):
        try:
            return content.decode("utf-16")
        except UnicodeDecodeError:
            raise BladOdczytu("Nie udało się odczytać kodowania pliku (oczekiwane UTF-8).")
    for kodowanie in ("utf-8-sig", "cp1250"):
        try:
            return content.decode(kodowanie)
        except UnicodeDecodeError:
            continue
    raise BladOdczytu("Nie udało się odczytać kodowania pliku (oczekiwane UTF-8).")


def _separator(tekst: str) -> str:
    pierwsza = tekst.split("\n", 1)[0]
    return max([",", ";", "\t", "|"], key=pierwsza.count)


def _komorka(v) -> str:
    if v is None:
        return ""
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, datetime.datetime):
        if v.time() == datetime.time(0, 0):
            return v.date().isoformat()
        return v.replace(microsecond=0).isoformat()
    if isinstance(v, datetime.date):
        return v.isoformat()
    if isinstance(v, float):
        return repr(int(v)) if v.is_integer() and abs(v) < 1e15 else repr(v)
    if isinstance(v, Decimal):
        return format(v, "f")
    return str(v).strip()


@dataclass
class Tabela:
    naglowek: List[str]
    wiersze: List[Dict[str, str]]  # nazwa kolumny → tekst
    numery: List[int]  # numer wiersza w pliku (nagłówek = 1) dla wiersze[i]


def _wiersze(siatka: List[List[str]]) -> Tabela:
    niepuste = [(i + 1, w) for i, w in enumerate(siatka) if any(c.strip() for c in w)]
    if not niepuste:
        raise BladOdczytu("Plik nie zawiera nagłówka ani danych.")
    naglowek = [c.strip() for c in niepuste[0][1]]
    wiersze, numery = [], []
    for nr, w in niepuste[1:]:
        w = list(w) + [""] * (len(naglowek) - len(w))
        wiersze.append({k: w[i].strip() for i, k in enumerate(naglowek) if k})
        numery.append(nr)
    return Tabela(naglowek, wiersze, numery)


def read_table(content: bytes, extension: str) -> Tabela:
    """Nagłówek to pierwszy niepusty wiersz; puste wiersze są pomijane (numery wierszy zostają jak w pliku)."""
    ext = (extension or "").lower().lstrip(".")
    if ext == "csv":
        tekst = _dekoduj(content)
        try:
            czytnik = csv.reader(io.StringIO(tekst, newline=""), delimiter=_separator(tekst))
            return _wiersze([list(w) for w in czytnik])
        except csv.Error as exc:
            raise BladOdczytu(f"Nie udało się odczytać pliku CSV: {exc}")
    if ext == "xlsx":
        from openpyxl import load_workbook

        try:
            wb = load_workbook(io.BytesIO(content), read_only=True, data_only=True)
            try:
                if not wb.worksheets:
                    raise BladOdczytu("Plik XLSX nie ma arkuszy.")
                siatka = [[_komorka(c) for c in w] for w in wb.worksheets[0].iter_rows(values_only=True)]
            finally:
                wb.close()
        except BladOdczytu:
            raise
        except Exception as exc:  # noqa: BLE001 - uszkodzony plik ma dać komunikat walidacji, nie wyjątek zadania
            raise BladOdczytu(f"Nie udało się otworzyć pliku XLSX: {exc}")
        return _wiersze(siatka)
    raise BladOdczytu(f"Wykaz AED musi być plikiem CSV albo XLSX (jest: {ext or 'nieznany'}).")
