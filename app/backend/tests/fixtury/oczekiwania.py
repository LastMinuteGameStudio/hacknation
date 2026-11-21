"""Wspólne narzędzia ścieżki D: wczytanie oczekiwań (oczekiwane/*.json), ocena mapowania i porównanie rekordów.

Używane przez tests/raport_mapowania.py i tests/test_realne_*.py. Format JSON: oczekiwane/README.md.
"""

from __future__ import annotations

import json
import re
import unicodedata
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any, Optional

FIXTURY = Path(__file__).parent
OCZEKIWANE = FIXTURY / "oczekiwane"
ZAKRES = Path(__file__).resolve().parents[4] / "zakres-danych"
DZIS = date(2026, 11, 22)  # stała data wgrania w testach


def wszystkie() -> list[dict]:
    return [json.loads(p.read_text(encoding="utf-8")) for p in sorted(OCZEKIWANE.glob("*.json"))]


def wg_pliku(plik: str) -> dict:
    for e in wszystkie():
        if e["plik"] == plik:
            return e
    raise KeyError(plik)


def schema():
    from aed_core.schema import load_schema

    return load_schema(ZAKRES)


def provider(exp: dict):
    from aed_core.types import Provider

    d = exp["dostawca"]
    return Provider(nazwa=d["nazwa"], typ=d["typ"], slug=d.get("slug"))


def wczytaj_tabele(exp: dict):
    from aed_core.parsers import read_table

    p = FIXTURY / exp["plik"]
    return read_table(p.read_bytes(), p.name, exp.get("arkusz"))


# --- dopasowanie kolumn -------------------------------------------------------------------------


def _norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s.strip().lower())
    s = "".join(c for c in s if not unicodedata.combining(c)).replace("ł", "l")
    return re.sub(r"\s+", " ", s)


def znajdz_kolumne(klucz: str, kolumny: list[str]) -> Optional[str]:
    """Kolumna z tabeli odpowiadająca kluczowi z oczekiwań: najpierw równość po strip(),
    potem po normalizacji, na końcu końcówka nazwy (nagłówek dwupoziomowy „Adres Ulica” ↔ „Ulica”)."""
    for k in kolumny:
        if k.strip() == klucz.strip():
            return k
    nk = _norm(klucz)
    for k in kolumny:
        if _norm(k) == nk:
            return k
    for k in kolumny:
        if _norm(k).endswith(" " + nk) or _norm(k).endswith(nk) and len(nk) > 3:
            return k
    return None


def _jako_lista(v: Any) -> list:
    return v if isinstance(v, list) else [v]


@dataclass
class OcenaMapowania:
    plik: str
    trafione: int = 0
    wszystkie: int = 0
    pomylki: list[tuple[str, Any, Any]] = field(default_factory=list)  # (kolumna, oczekiwane, otrzymane)
    nadmiarowe: list[str] = field(default_factory=list)  # kolumny tabeli spoza oczekiwań
    mapowanie: dict[str, Optional[str]] = field(default_factory=dict)  # kolumna z tabeli → pole

    @property
    def procent(self) -> float:
        return 100.0 * self.trafione / self.wszystkie if self.wszystkie else 0.0


def ocen_mapowanie(exp: dict, table, sugestie) -> OcenaMapowania:
    o = OcenaMapowania(plik=exp["plik"])
    o.mapowanie = {s.kolumna: s.pole for s in sugestie}
    uzyte: set[str] = set()
    for klucz, oczek in exp["mapowanie"].items():
        o.wszystkie += 1
        kol = znajdz_kolumne(klucz, table.columns)
        if kol is None:
            o.pomylki.append((klucz, oczek, "<brak kolumny w tabeli>"))
            continue
        uzyte.add(kol)
        got = o.mapowanie.get(kol, "<brak propozycji>")
        if got in _jako_lista(oczek):
            o.trafione += 1
        else:
            o.pomylki.append((klucz, oczek, got))
    o.nadmiarowe = [k for k in table.columns if k not in uzyte]
    return o


# --- rekordy ------------------------------------------------------------------------------------


def normalizuj(exp: dict, table, mapowanie: dict[str, Optional[str]], sch=None):
    from aed_core.normalize import normalize_table

    sch = sch or schema()
    return normalize_table(table, mapowanie, sch, provider(exp), DZIS, geocoder=None,
                           fixed=exp.get("wartosci_stale") or {})


def wartosc_pasuje(oczek: Any, got: str) -> bool:
    if isinstance(oczek, dict) and "regex" in oczek:
        return re.search(oczek["regex"], got or "") is not None
    return (got or "") in [("" if x is None else x) for x in _jako_lista(oczek)]


def porownaj_rekordy(exp: dict, rekordy) -> list[str]:
    """Lista różnic (pusta = zgodnie). rekordy: list[RecordResult]."""
    wg_wiersza = {r.wiersz: r for r in rekordy}
    roznice = []
    for r_exp in exp.get("rekordy", []):
        w = r_exp["wiersz"]
        r = wg_wiersza.get(w)
        if r is None:
            roznice.append(f"wiersz {w}: brak rekordu (są: {sorted(wg_wiersza)[:10]}...)")
            continue
        for pole, oczek in r_exp["pola"].items():
            got = r.record.get(pole, "<brak pola>")
            if not wartosc_pasuje(oczek, got):
                roznice.append(f"wiersz {w}, {pole}: oczekiwane {oczek!r}, otrzymane {got!r}")
    return roznice


def kody(rekordy, komunikaty_walidacji=(), table=None) -> set[str]:
    k = {m.kod for r in rekordy for m in r.messages} | {m.kod for m in komunikaty_walidacji}
    if table is not None:
        k |= {m.kod for m in table.messages}
    return k


def sprawdz_kody(exp: dict, wszystkie_kody: set[str]) -> list[str]:
    kom = exp.get("komunikaty", {})
    out = [f"brak komunikatu {k}" for k in kom.get("musza_byc", []) if k not in wszystkie_kody]
    out += [f"niepożądany komunikat {k}" for k in kom.get("nie_moze_byc", []) if k in wszystkie_kody]
    return out
