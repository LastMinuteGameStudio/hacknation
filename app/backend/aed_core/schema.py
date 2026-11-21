"""Wczytanie wzorcowego zakresu v0.5 (zakres-danych/zakres-pol.csv + slowniki.csv). Jedno źródło prawdy."""

from __future__ import annotations

import csv
import re
from pathlib import Path

from .types import Field, Schema

WERSJA = "0.5"


def _slownik_z_formatu(typ: str, fmt: str) -> str | None:
    if typ != "słownik":
        return None
    m = re.search(r"słownik:\s*([a-z0-9_]+)", fmt)
    return m.group(1) if m else None


def load_schema(zakres_dir: Path) -> Schema:
    pola: list[Field] = []
    with open(zakres_dir / "zakres-pol.csv", encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            pola.append(
                Field(
                    lp=int(r["lp"]),
                    grupa=r["grupa"],
                    pole=r["pole"],
                    nazwa=r["nazwa"],
                    typ=r["typ"],
                    format=r["format"],
                    wymagalnosc=r["wymagalnosc"],  # type: ignore[arg-type]
                    publiczne=r["publiczne"].strip().lower() == "true",
                    opis=r["opis"],
                    przyklad=r["przyklad"],
                    slownik=_slownik_z_formatu(r["typ"], r["format"]),
                )
            )
    slowniki: dict[str, list[tuple[str, str]]] = {}
    with open(zakres_dir / "slowniki.csv", encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            slowniki.setdefault(r["slownik"], []).append((r["kod"], r["znaczenie"]))
    return Schema(wersja=WERSJA, pola=pola, slowniki=slowniki)
