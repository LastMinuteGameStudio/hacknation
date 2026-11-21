"""Atrapy funkcji rdzenia (aed_core) o tym samym interfejsie co KONTRAKT.md §3.

API woła je zamiast rdzenia, gdy funkcja rdzenia zgłasza NotImplementedError (MOCK=auto) albo zawsze (MOCK=1).
Są celowo proste: front (C) dostaje prawdziwe kolumny i rekordy z wgranego pliku, zanim ścieżka A skończy rdzeń.
Gdy dana funkcja rdzenia działa, atrapa przestaje być wołana sama (patrz app/core.py).
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
import re
import unicodedata
from datetime import date
from typing import Optional

from aed_core.types import (
    POLE_ADRES_PELNY,
    POLE_GEOMETRIA,
    POLE_GODZINY,
    MappingSuggestion,
    Message,
    Provider,
    RecordResult,
    Schema,
    Table,
)

from .config import ZAKRES_DIR

ATRAPA = Message("info", "ATRAPA", "Część konwersji działa w trybie uproszczonym: rdzeń jeszcze nie jest gotowy.")


def _klucz(s: str) -> str:
    s = unicodedata.normalize("NFKD", s.replace("ł", "l").replace("Ł", "L"))
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]", "", s.lower())


def _unikalne_naglowki(cols: list[str]) -> list[str]:
    wynik: list[str] = []
    licznik: dict[str, int] = {}
    for i, c in enumerate(cols):
        c = (c or "").strip() or f"Kolumna {i + 1}"
        licznik[c] = licznik.get(c, 0) + 1
        wynik.append(c if licznik[c] == 1 else f"{c} ({licznik[c]})")
    return wynik


def read_table(content: bytes, filename: str, sheet: Optional[str] = None) -> Table:
    if filename.lower().endswith(".xlsx"):
        import openpyxl

        wb = openpyxl.load_workbook(io.BytesIO(content), read_only=True, data_only=True)
        ws = wb[sheet] if sheet and sheet in wb.sheetnames else wb.worksheets[0]
        rows = [["" if v is None else str(v) for v in r] for r in ws.iter_rows(values_only=True)]
        sheets = wb.sheetnames
    else:
        try:
            txt = content.decode("utf-8-sig")
        except UnicodeDecodeError:
            txt = content.decode("cp1250", errors="replace")
        try:
            dialect = csv.Sniffer().sniff(txt[:4096], delimiters=",;\t|")
            delim = dialect.delimiter
        except csv.Error:
            delim = ","
        rows = list(csv.reader(io.StringIO(txt), delimiter=delim))
        sheets = []
    rows = [r for r in rows if any(v.strip() for v in r)]
    if not rows:
        return Table(columns=[], rows=[], sheets=sheets, messages=[Message("blad", "PUSTY_PLIK", "Plik nie zawiera danych.")])
    cols = _unikalne_naglowki(rows[0])
    dane = [(r + [""] * len(cols))[: len(cols)] for r in rows[1:]]
    return Table(columns=cols, rows=dane, sheets=sheets, messages=[])


def suggest_mapping(
    table: Table, schema: Schema, previous: Optional[dict[str, Optional[str]]] = None
) -> list[MappingSuggestion]:
    po_kluczu = {_klucz(f.pole): f.pole for f in schema.pola} | {_klucz(f.nazwa): f.pole for f in schema.pola}
    po_kluczu |= {"geometria": POLE_GEOMETRIA, "geometry": POLE_GEOMETRIA, "adres": POLE_ADRES_PELNY,
                  "godziny": POLE_GODZINY, "openinghours": POLE_GODZINY}
    zajete: set[str] = set()
    wynik = []
    for c in table.columns:
        if previous and c in previous and (previous[c] is None or previous[c] not in zajete):
            pole, pewnosc, powod = previous[c], 0.99, "mapowanie z poprzedniej wersji"
        else:
            pole = po_kluczu.get(_klucz(c))
            pewnosc, powod = (0.9, "nazwa kolumny") if pole else (0.0, "brak dopasowania")
        if pole in zajete:
            pole, pewnosc, powod = None, 0.0, "pole już przypisane innej kolumnie"
        if pole:
            zajete.add(pole)
        wynik.append(MappingSuggestion(kolumna=c, pole=pole, pewnosc=pewnosc, powod=powod))
    return wynik


def normalize_table(
    table: Table,
    mapping: dict[str, Optional[str]],
    schema: Schema,
    provider: Provider,
    today: date,
    geocoder=None,
    fixed: Optional[dict[str, str]] = None,
) -> list[RecordResult]:
    idx = {pole: table.columns.index(k) for k, pole in mapping.items() if pole and k in table.columns}
    wynik = []
    for i, row in enumerate(table.rows):
        rec = {f.pole: "" for f in schema.pola}
        for pole, j in idx.items():
            v = row[j].strip()
            if pole in rec:
                rec[pole] = v
            elif pole == POLE_ADRES_PELNY:
                _rozbij_adres(v, rec)
            elif pole == POLE_GEOMETRIA:
                _rozbij_geometrie(v, rec)
            elif pole == POLE_GODZINY and re.search(r"24\s*(h|/7)|całodob", v.lower()):
                rec["dostepny_24_7"] = "tak"
        for pole, v in (fixed or {}).items():
            if pole in rec and not rec[pole]:
                rec[pole] = v
        rec["dysponent_nazwa"] = provider.nazwa
        rec["dysponent_typ"] = provider.typ
        if "telefon_kontaktowy" in rec:
            rec["telefon_kontaktowy"] = provider.telefon or ""
        if "email_kontaktowy" in rec:
            rec["email_kontaktowy"] = provider.email or ""
        if "zrodlo_danych" in rec and not rec["zrodlo_danych"]:
            rec["zrodlo_danych"] = "jst" if provider.typ == "jst" else "dysponent"
        if "data_aktualizacji" in rec:
            rec["data_aktualizacji"] = today.isoformat()
        msgs: list[Message] = []
        wiersz = table.header_row + 1 + i
        if not rec.get("status"):
            rec["status"] = "nieznany"
        if "data_weryfikacji" in rec and not rec["data_weryfikacji"]:
            rec["data_weryfikacji"] = today.isoformat()
        if not rec["id_aed"]:
            h = hashlib.sha1(f"{rec.get('numer_seryjny')}|{rec.get('szerokosc_geograficzna')}|{rec.get('dlugosc_geograficzna')}|{i}".encode()).hexdigest()[:6]
            rec["id_aed"] = f"{rec.get('kod_terc') or provider.slug or 'aed'}-{h}"
        wynik.append(RecordResult(wiersz=wiersz, record=rec, messages=msgs))
    return wynik


_ADRES = re.compile(r"^(?:ul\.\s*|al\.\s*|pl\.\s*)?(?P<ulica>[^,\d]+?)\s*(?P<nr>\d+\S*)?\s*,\s*(?P<kod>\d{2}-\d{3})?\s*(?P<miasto>.*)$")


def _rozbij_adres(v: str, rec: dict) -> None:
    """„ul. Jasna 5, 38-400 Krosno” → nazwa_ulicy, nr_budynku, kod_pocztowy, miejscowosc (tylko puste pola)."""
    m = _ADRES.match(v)
    if not m:
        return
    for pole, grupa in (("nazwa_ulicy", "ulica"), ("nr_budynku", "nr"), ("kod_pocztowy", "kod"), ("miejscowosc", "miasto")):
        if pole in rec and not rec[pole] and m.group(grupa):
            rec[pole] = m.group(grupa).strip()


def _rozbij_geometrie(v: str, rec: dict) -> None:
    liczby = re.findall(r"-?\d+\.\d+", v)
    if len(liczby) >= 2:
        a, b = float(liczby[0]), float(liczby[1])
        lat, lon = (liczby[0], liczby[1]) if a > b else (liczby[1], liczby[0])  # w Polsce szerokość > długość
        rec["szerokosc_geograficzna"] = rec["szerokosc_geograficzna"] or lat
        rec["dlugosc_geograficzna"] = rec["dlugosc_geograficzna"] or lon


def validate_records(records: list[RecordResult], schema: Schema) -> list[Message]:
    msgs = []
    for f in schema.pola:
        if f.wymagalnosc != "O":
            continue
        puste = [r.wiersz for r in records if not r.record.get(f.pole)]
        if puste and len(puste) == len(records):
            msgs.append(Message("blad", "BRAK_POLA_OBOWIAZKOWEGO", f"Brak pola „{f.nazwa}”.", None, f.pole))
        else:
            msgs += [Message("blad", "BRAK_POLA_OBOWIAZKOWEGO", f"Puste pole „{f.nazwa}”.", w, f.pole) for w in puste]
    return msgs


def to_csv(records: list[dict[str, str]], schema: Schema, public_only: bool = True) -> bytes:
    pola = schema.publiczne if public_only else schema.nazwy
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\r\n")
    w.writerow(pola)
    for r in records:
        w.writerow([r.get(p, "") for p in pola])
    return buf.getvalue().encode("utf-8")


def to_json(records: list[dict[str, str]], schema: Schema, metadata: dict) -> bytes:
    pola = schema.publiczne
    return json.dumps({"metadane": metadata, "rekordy": [{p: r.get(p, "") for p in pola} for r in records]},
                      ensure_ascii=False, indent=1).encode("utf-8")


def csvw_metadata(schema: Schema, csv_url: str, title: str) -> dict:
    m = json.loads((ZAKRES_DIR / "szablon-aed-publiczny.csv-metadata.json").read_text(encoding="utf-8"))
    m["url"] = csv_url
    m["dc:title"] = title
    return m
