"""A6: eksport: CSV RFC 4180 (UTF-8 bez BOM, przecinek, CRLF, pola publiczne w kolejności zakresu), JSON, CSVW.
Wzór CSVW: zakres-danych/szablon-aed-publiczny.csv-metadata.json (opis kolumn budujemy ze Schema, ta sama struktura).
"""

from __future__ import annotations

import csv
import io
import json

from .types import Schema

_GODZINY_FORMAT = "([01][0-9]|2[0-3]):[0-5][0-9]-([01][0-9]|2[0-4]):[0-5][0-9]|zamkniete"
_TYPY = {
    "tekst": "string",
    "liczba dziesiętna": "decimal",
    "liczba całkowita": "integer",
    "logiczny": "boolean",
    "data": "date",
    "data i czas": "dateTime",
    "URL": "anyURI",
}


def _pola(schema: Schema, public_only: bool = True) -> list[str]:
    return schema.publiczne if public_only else schema.nazwy


def to_csv(records: list[dict[str, str]], schema: Schema, public_only: bool = True) -> bytes:
    pola = _pola(schema, public_only)
    buf = io.StringIO(newline="")
    w = csv.writer(buf, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL, lineterminator="\r\n")
    w.writerow(pola)
    for r in records:
        w.writerow([(r.get(p) or "") for p in pola])
    return buf.getvalue().encode("utf-8")


def to_json(records: list[dict[str, str]], schema: Schema, metadata: dict) -> bytes:
    pola = _pola(schema, True)
    dane = {"metadane": metadata, "rekordy": [{p: (r.get(p) or "") for p in pola} for r in records]}
    return json.dumps(dane, ensure_ascii=False, indent=1).encode("utf-8")


def _datatype(f, schema: Schema):
    if f.typ == "słownik" and f.slownik:
        return {"base": "string", "format": "|".join(k for k, _ in schema.slowniki.get(f.slownik, []))}
    if f.typ == "godziny":
        return {"base": "string", "format": _GODZINY_FORMAT}
    return _TYPY.get(f.typ, "string")


def csvw_metadata(schema: Schema, csv_url: str, title: str) -> dict:
    kolumny = []
    for p in schema.publiczne:
        f = schema.pole(p)
        kolumny.append({
            "name": f.pole,
            "titles": [f.pole, f.nazwa],  # CSVW §5.5.1: titles musi zawierać tekst nagłówka CSV
            "dc:description": f.opis,
            "datatype": _datatype(f, schema),
            "required": f.wymagalnosc == "O",
        })
    return {
        "@context": ["http://www.w3.org/ns/csvw", {"@language": "pl"}],
        "url": csv_url,
        "dc:title": title,
        "dc:description": f"Defibrylatory AED w formacie wzorcowego zakresu danych, wersja {schema.wersja} "
                          "(tylko pola publiczne). Licencja CC0 1.0.",
        "dc:license": "https://creativecommons.org/publicdomain/zero/1.0/",
        "dialect": {"encoding": "utf-8", "delimiter": ",", "header": True, "lineTerminators": ["\r\n"]},
        "tableSchema": {"null": "X", "primaryKey": "id_aed", "columns": kolumny},
    }
