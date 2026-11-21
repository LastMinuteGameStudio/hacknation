"""A2: odczyt CSV (separator, kodowanie utf-8/cp1250, BOM, cudzysłowy), XLSX (openpyxl) i GeoJSON → Table.

- Wiersz nagłówka wykrywany automatycznie (wiersze tytułowe nad tabelą są pomijane).
- Puste wiersze i stopki („Sporządził: …”) są pomijane; numer wiersza rows[i] w arkuszu: Table.numer_wiersza(i).
- XLSX: scalone komórki dziedziczą wartość (pionowo: wiersze danych, poziomo: grupy nagłówka), nagłówek
  dwupoziomowy jest składany, bez podanego arkusza wybieramy ten z największą liczbą wierszy danych.
- Wartości zawsze jako tekst; liczby z XLSX bez utraty precyzji (bez notacji wykładniczej).
- Przypadek z Marek: cały wiersz w jednym polu w cudzysłowie → rozpoznajemy i rozbijamy.
- Błędy blokujące plik (format, rozmiar, liczba wierszy, pusty plik) → wyjątek BladPliku.
"""

from __future__ import annotations

import csv
import io
import json
import math
import re
from datetime import date, datetime, time
from decimal import Decimal
from typing import Optional

from .types import Message, Table

MAX_BAJTOW = 10 * 1024 * 1024
MAX_WIERSZY = 20_000
SEPARATORY = [",", ";", "\t", "|"]


class BladPliku(Exception):
    """Błąd blokujący cały plik. API zamienia go na HTTP `status` z detail {kod, komunikat}."""

    def __init__(self, kod: str, komunikat: str, status: int = 422) -> None:
        super().__init__(komunikat)
        self.kod = kod
        self.komunikat = komunikat
        self.status = status


# --- dekodowanie i CSV ----------------------------------------------------------------------------


def _dekoduj(content: bytes) -> str:
    if content.startswith(b"\xff\xfe") or content.startswith(b"\xfe\xff"):
        return content.decode("utf-16")
    try:
        return content.decode("utf-8-sig")
    except UnicodeDecodeError:
        return content.decode("cp1250", errors="replace")


def _wykryj_separator(text: str) -> str:
    probka = "\n".join(text.splitlines()[:60])
    najlepszy, wynik_naj = ",", (-1.0, 0)
    for sep in SEPARATORY:
        try:
            wiersze = [r for r in csv.reader(io.StringIO(probka), delimiter=sep) if any(c.strip() for c in r)]
        except csv.Error:
            continue
        if not wiersze:
            continue
        dlugosci = [len(r) for r in wiersze]
        moda = max(set(dlugosci), key=dlugosci.count)
        if moda < 2:
            continue
        zgodnosc = sum(1 for d in dlugosci if d == moda) / len(dlugosci)
        wynik = (round(zgodnosc, 2), moda)
        if wynik > wynik_naj:
            najlepszy, wynik_naj = sep, wynik
    return najlepszy


def _czytaj_csv(content: bytes) -> list[list[str]]:
    text = _dekoduj(content)
    sep = _wykryj_separator(text)
    return [list(r) for r in csv.reader(io.StringIO(text, newline=""), delimiter=sep)]


# --- XLSX -----------------------------------------------------------------------------------------


def _liczba_na_tekst(v: float) -> str:
    if math.isnan(v) or math.isinf(v):
        return ""
    if v == int(v) and abs(v) < 1e15:
        return str(int(v))
    s = repr(v)
    cyfry = len(re.sub(r"[^0-9]", "", s.split("e")[0]).lstrip("0"))
    if cyfry > 15:  # artefakt binarny (np. 52.395198000000001); Excel trzyma 15 cyfr znaczących
        s = format(v, ".15g")
    d = Decimal(s)
    t = format(d, "f")
    if "." in t:
        t = t.rstrip("0").rstrip(".")
    return t


def _komorka_na_tekst(v: object) -> str:
    if v is None:
        return ""
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, int):
        return str(v)
    if isinstance(v, float):
        return _liczba_na_tekst(v)
    if isinstance(v, datetime):
        if v.time() == time(0, 0):
            return v.date().isoformat()
        return v.isoformat(timespec="seconds")
    if isinstance(v, (date, time)):
        return v.isoformat()
    return str(v)


def _arkusz_na_siatke(ws) -> tuple[list[list[str]], set[int]]:
    """Siatka tekstów + indeksy wierszy z poziomo scalonymi komórkami (grupy w nagłówku dwupoziomowym).

    Scalone komórki: w pionie wartość dziedziczą wszystkie wiersze (np. miejscowość dla kilku AED),
    w poziomie wszystkie kolumny, o ile scalenie nie obejmuje prawie całej szerokości (tytuł, stopka).
    """
    grid: list[list[str]] = []
    for row in ws.iter_rows(min_row=1, min_col=1, values_only=True):
        grid.append([_komorka_na_tekst(v) for v in row])
        if len(grid) > MAX_WIERSZY + 100:
            break
    ncol = max((len(r) for r in grid), default=0)
    poziome: set[int] = set()
    for rng in ws.merged_cells.ranges:
        r0, c0, r1, c1 = rng.min_row - 1, rng.min_col - 1, rng.max_row - 1, rng.max_col - 1
        szer = c1 - c0 + 1
        if r0 >= len(grid) or (szer > 1 and szer >= 0.8 * ncol):
            continue
        wart = grid[r0][c0] if c0 < len(grid[r0]) else ""
        for r in range(r0, min(r1, len(grid) - 1) + 1):
            if len(grid[r]) <= c1:
                grid[r].extend([""] * (c1 + 1 - len(grid[r])))
            for c in range(c0, c1 + 1):
                grid[r][c] = wart
        if szer > 1:
            poziome.add(r0)
    return grid, poziome


def _wynik_arkusza(grid: list[list[str]]) -> tuple[int, int]:
    return sum(1 for r in grid if _niepuste(r) >= 3), sum(1 for r in grid if _niepuste(r) >= 2)


def _czytaj_xlsx(content: bytes, sheet: Optional[str]) -> tuple[list[list[str]], list[str], set[int]]:
    import openpyxl

    try:
        wb = openpyxl.load_workbook(io.BytesIO(content), data_only=True)
    except Exception as e:  # uszkodzony plik albo nie-XLSX z rozszerzeniem .xlsx
        raise BladPliku("NIEOBSLUGIWANY_FORMAT", f"Nie udało się otworzyć pliku XLSX ({e.__class__.__name__}).", 415)
    arkusze = list(wb.sheetnames)
    if sheet is not None and sheet not in arkusze:
        raise BladPliku("NIE_ZNALEZIONO", f"W pliku nie ma arkusza „{sheet}”. Arkusze: {', '.join(arkusze)}.", 404)
    if sheet is not None:
        grid, poziome = _arkusz_na_siatke(wb[sheet])
    else:  # arkusz z największą liczbą wierszy wyglądających na dane (pierwszy przy remisie)
        najlepszy = None
        for n in arkusze:
            g, p = _arkusz_na_siatke(wb[n])
            w = _wynik_arkusza(g)
            if najlepszy is None or w > najlepszy[0]:
                najlepszy = (w, g, p)
        _, grid, poziome = najlepszy  # type: ignore[misc]
    wb.close()
    return grid, arkusze, poziome


# --- GeoJSON (zakres dodatkowy) -------------------------------------------------------------------


def _czytaj_geojson(content: bytes) -> list[list[str]]:
    try:
        data = json.loads(_dekoduj(content))
    except ValueError:
        raise BladPliku("NIEOBSLUGIWANY_FORMAT", "Plik JSON jest niepoprawny.", 415)
    if not isinstance(data, dict) or data.get("type") != "FeatureCollection":
        raise BladPliku("NIEOBSLUGIWANY_FORMAT", "Obsługujemy JSON tylko jako GeoJSON FeatureCollection.", 415)
    kolumny: list[str] = []
    wiersze: list[dict[str, str]] = []
    for f in data.get("features") or []:
        props = (f or {}).get("properties") or {}
        w = {}
        for k, v in props.items():
            if k not in kolumny:
                kolumny.append(k)
            w[k] = "" if v is None else (json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else str(v))
        w["geometry"] = json.dumps(f.get("geometry"), ensure_ascii=False) if f.get("geometry") else ""
        wiersze.append(w)
    kolumny.append("geometry")
    return [kolumny] + [[w.get(k, "") for k in kolumny] for w in wiersze]


# --- wspólna obróbka siatki -----------------------------------------------------------------------


def _niepuste(r: list[str]) -> int:
    return sum(1 for c in r if c.strip())


def _rozbij_jednopolowe(grid: list[list[str]]) -> tuple[list[list[str]], bool]:
    """Przypadek Marek: każdy wiersz to jedna komórka z całym wierszem CSV w środku."""
    niepuste = [r for r in grid if _niepuste(r)]
    if not niepuste or any(_niepuste(r) > 1 for r in niepuste):
        return grid, False
    teksty = [next(c for c in r if c.strip()) for r in niepuste]
    for sep in [",", ";", "\t", "|"]:
        rozbite = [next(csv.reader([t], delimiter=sep, skipinitialspace=True)) for t in teksty]
        dl = [len(r) for r in rozbite]
        moda = max(set(dl), key=dl.count)
        if moda >= 3 and sum(1 for d in dl if d == moda) / len(dl) >= 0.8:
            out = []
            for r in grid:
                if _niepuste(r):
                    t = next(c for c in r if c.strip())
                    out.append(next(csv.reader([t], delimiter=sep, skipinitialspace=True)))
                else:
                    out.append([])
            return out, True
    return grid, False


def _wyglada_na_liczbe(s: str) -> bool:
    return bool(re.fullmatch(r"\s*[-+]?\d+([.,]\d+)?\s*", s))


def _wykryj_naglowek(grid: list[list[str]]) -> int:
    """Indeks (0-based) wiersza nagłówka: pierwszy szeroki wiersz z tekstami, po którym są dane."""
    szerokosci = [_niepuste(r) for r in grid[:200] if _niepuste(r)]
    if not szerokosci:
        return 0
    maks = max(szerokosci)
    prog = max(2, math.ceil(0.5 * maks)) if maks >= 2 else 1
    for i, r in enumerate(grid[:50]):
        n = _niepuste(r)
        if n < prog:
            continue
        liczby = sum(1 for c in r if c.strip() and _wyglada_na_liczbe(c))
        if liczby > n / 2:
            continue  # wiersz danych bez nagłówka nad nim: szukamy dalej, a w razie czego bierzemy pierwszy szeroki
        return i
    for i, r in enumerate(grid):
        if _niepuste(r) >= prog:
            return i
    return 0


def _nazwy_kolumn(surowe: list[str]) -> list[str]:
    out: list[str] = []
    licznik: dict[str, int] = {}
    for i, n in enumerate(surowe):
        n = re.sub(r"\s+", " ", n.replace("﻿", "")).strip() or f"Kolumna {i + 1}"
        if n in licznik:
            licznik[n] += 1
            n2 = f"{n} ({licznik[n]})"
            while n2 in licznik:
                licznik[n] += 1
                n2 = f"{n} ({licznik[n]})"
            n = n2
        licznik.setdefault(n, 1)
        out.append(n)
    return out


_STOPKA = re.compile(r"^\s*(sporz[aą]dzi|opracowa|podpis|data sporz|[zź]r[oó]d[lł]o|razem|suma|wykona|zatwierdzi|"
                     r"sprawdzi|uwaga:|\*)", re.I)


def _do_tabeli(grid: list[list[str]], sheets: list[str], messages: list[Message], poziome: Optional[set[int]] = None) -> Table:
    poziome = poziome or set()
    grid, rozbito = _rozbij_jednopolowe(grid)
    if rozbito:
        messages.append(
            Message("ostrzezenie", "ROZBITO_WIERSZE",
                    "Każdy wiersz pliku był zapisany w jednej komórce; rozdzieliliśmy go na kolumny. Sprawdź podgląd.")
        )
    if not any(_niepuste(r) for r in grid):
        raise BladPliku("PUSTY_PLIK", "Plik nie zawiera danych.")
    h = _wykryj_naglowek(grid)
    naglowek = list(grid[h])
    pierwszy_danych = h + 1
    # nagłówek dwupoziomowy: grupy scalone w poziomie („Adres” nad Ulica/Nr/Kod), pod nimi same teksty
    if h in poziome and h + 1 < len(grid):
        pod = grid[h + 1]
        tekstowe = [c for c in pod if c.strip()]
        if len(tekstowe) >= 2 and not any(_wyglada_na_liczbe(c) for c in tekstowe):
            szer_n = max(len(naglowek), len(pod))
            naglowek = [
                (pod[j] if j < len(pod) and pod[j].strip() else (naglowek[j] if j < len(naglowek) else ""))
                for j in range(szer_n)
            ]
            pierwszy_danych = h + 2
            messages.append(Message("info", "NAGLOWEK_DWUPOZIOMOWY",
                                    f"Nagłówek tabeli zajmuje wiersze {h + 1}–{h + 2}; nazwy kolumn wzięliśmy z wiersza {h + 2}."))
    numery = list(range(pierwszy_danych, len(grid)))  # indeksy siatki
    numery = [k for k in numery if _niepuste(grid[k])]
    # stopka („Sporządził: …”, „Razem”): wiersze na końcu z jedną komórką
    while numery and _niepuste(grid[numery[-1]]) <= 1 and len(naglowek) >= 3 and \
            _STOPKA.match(next(c for c in grid[numery[-1]] if c.strip())):
        numery.pop()
    dane = [grid[k] for k in numery]

    def ostatnia(r: list[str]) -> int:
        for j in range(len(r) - 1, -1, -1):
            if r[j].strip():
                return j + 1
        return 0

    szer = max([ostatnia(naglowek)] + [ostatnia(r) for r in dane])
    if len(dane) > MAX_WIERSZY:
        raise BladPliku("ZA_DUZO_WIERSZY", f"Plik ma ponad {MAX_WIERSZY} wierszy danych. Podziel go na mniejsze.", 413)
    if not dane:
        raise BladPliku("PUSTY_PLIK", "Plik ma nagłówek, ale nie ma wierszy danych.")
    kolumny = _nazwy_kolumn((naglowek + [""] * szer)[:szer])
    rows = [[c.strip() for c in (r + [""] * szer)[:szer]] for r in dane]
    if h > 0:
        messages.append(Message("info", "POMINIETO_WIERSZE_TYTULOWE",
                                f"Nagłówek tabeli wykryto w wierszu {h + 1}; wiersze nad nim pominięto."))
    return Table(columns=kolumny, rows=rows, sheets=sheets, messages=messages, header_row=pierwszy_danych,
                 row_numbers=[k + 1 for k in numery])


def read_table(content: bytes, filename: str, sheet: Optional[str] = None) -> Table:
    if len(content) > MAX_BAJTOW:
        raise BladPliku("ZA_DUZY_PLIK", "Plik jest większy niż 10 MB.", 413)
    nazwa = (filename or "").lower()
    ext = nazwa.rsplit(".", 1)[-1] if "." in nazwa else ""
    messages: list[Message] = []
    if ext == "xlsx" or (content[:4] == b"PK\x03\x04" and ext not in ("csv", "txt")):
        grid, sheets, poziome = _czytaj_xlsx(content, sheet)
        return _do_tabeli(grid, sheets, messages, poziome)
    if ext in ("geojson", "json"):
        return _do_tabeli(_czytaj_geojson(content), [], messages)
    if ext in ("csv", "txt", "tsv", ""):
        if b"\x00" in content[:4096] and not content.startswith((b"\xff\xfe", b"\xfe\xff")):
            raise BladPliku("NIEOBSLUGIWANY_FORMAT", "Plik nie wygląda na tekstowy CSV.", 415)
        return _do_tabeli(_czytaj_csv(content), [], messages)
    if ext == "xls":
        raise BladPliku("NIEOBSLUGIWANY_FORMAT", "Stary format XLS nie jest obsługiwany. Zapisz plik jako XLSX lub CSV.", 415)
    raise BladPliku("NIEOBSLUGIWANY_FORMAT", "Obsługujemy pliki CSV i XLSX.", 415)
