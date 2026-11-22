"""Wzorcowy zakres danych o AED v0.5. Kopia plików zakres-danych/zakres-pol.csv i slowniki.csv z repozytorium
projektu (jedno źródło prawdy: przy zmianie zakresu podmienia się oba pliki w katalogu zakres/)."""

import csv
import re
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional, Tuple

WERSJA = "0.5"
ZAKRES_DIR = Path(__file__).resolve().parent / "zakres"


@dataclass(frozen=True)
class Pole:
    pole: str
    nazwa: str
    typ: str
    wymagalnosc: str  # O obowiązkowe, Z zalecane, F fakultatywne
    publiczne: bool
    slownik: Optional[str] = None


@dataclass
class Zakres:
    wersja: str
    pola: List[Pole]
    slowniki: Dict[str, List[Tuple[str, str]]] = field(default_factory=dict)

    @property
    def nazwy(self) -> List[str]:
        return [p.pole for p in self.pola]

    @property
    def publiczne(self) -> List[str]:
        return [p.pole for p in self.pola if p.publiczne]

    @property
    def obowiazkowe(self) -> List[str]:
        return [p.pole for p in self.pola if p.wymagalnosc == "O"]

    def pole(self, nazwa: str) -> Pole:
        for p in self.pola:
            if p.pole == nazwa:
                return p
        raise KeyError(nazwa)

    def kody(self, slownik: str) -> List[str]:
        return [k for k, _ in self.slowniki.get(slownik, [])]


def _slownik(typ: str, fmt: str) -> Optional[str]:
    if typ != "słownik":
        return None
    m = re.search(r"słownik:\s*([a-z0-9_]+)", fmt)
    return m.group(1) if m else None


@lru_cache(maxsize=4)
def load_zakres(katalog: Optional[str] = None) -> Zakres:
    d = Path(katalog) if katalog else ZAKRES_DIR
    pola: List[Pole] = []
    with open(d / "zakres-pol.csv", encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            pola.append(Pole(
                pole=r["pole"], nazwa=r["nazwa"], typ=r["typ"], wymagalnosc=r["wymagalnosc"],
                publiczne=r["publiczne"].strip().lower() == "true", slownik=_slownik(r["typ"], r["format"]),
            ))
    slowniki: Dict[str, List[Tuple[str, str]]] = {}
    with open(d / "slowniki.csv", encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            slowniki.setdefault(r["slownik"], []).append((r["kod"], r["znaczenie"]))
    return Zakres(wersja=WERSJA, pola=pola, slowniki=slowniki)
