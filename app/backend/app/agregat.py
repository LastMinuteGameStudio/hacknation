"""B4: agregat /d/aed-polska.csv (z OSM) i /d/aed-polska-bez-osm.csv (KONTRAKT.md §2 „Pliki publiczne”).

Źródła: dane/wynik/aed_unikalne.csv (OSM + inne źródła, po deduplikacji; dane/README.md) + opublikowane zbiory z bazy.
Kolumny: pola publiczne v0.5 + `zrodlo`, `licencja_zrodla`.
- Rekord z bazy: `id_aed` = `<slug>:<id_aed>`, `zrodlo` = `tuaed:<slug>`, `licencja_zrodla` = CC0 1.0, `status_walidacji` = oczekuje.
- Rekord dostawcy jest główny: rekord z dane/wynik bliżej niż 30 m od rekordu dostawcy dostaje
  `duplikat_id_aed` = `id_aed` tego rekordu (nic nie usuwamy). Rekordy dostawców są na początku pliku.
- Brak wartości = „X” (konwencja dane/wynik i CSVW `null: "X"`).
"""

from __future__ import annotations

import csv
import io
import math
import threading
from dataclasses import dataclass
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .config import DANE_WYNIK_DIR, LICENCJA
from .db import Rekord, Zbior
from .importy import SCHEMA

PLIKI = {"aed-polska.csv": True, "aed-polska-bez-osm.csv": False}  # nazwa → czy z OSM
PROG_M = 30.0
BRAK = "X"
KOMORKA = 0.001  # stopnie; ~111 m szerokości, ~70 m długości w Polsce, więc sąsiednie komórki pokrywają 30 m
KOLUMNY = SCHEMA.publiczne + ["zrodlo", "licencja_zrodla"]


def odleglosc_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * 6_371_000 * math.asin(math.sqrt(a))


def _wsp(r: dict) -> Optional[tuple[float, float]]:
    try:
        return float(r["szerokosc_geograficzna"]), float(r["dlugosc_geograficzna"])
    except (KeyError, TypeError, ValueError):
        return None


def _komorka(lat: float, lon: float) -> tuple[int, int]:
    return int(math.floor(lat / KOMORKA)), int(math.floor(lon / KOMORKA))


@dataclass
class _Baza:
    rekordy: list[dict]  # tylko KOLUMNY
    siatka: dict[tuple[int, int], list[int]]  # komórka → indeksy rekordów


_baza: Optional[_Baza] = None
_cache: dict[str, tuple[tuple, bytes]] = {}
_lock = threading.Lock()


def _wczytaj_baze() -> _Baza:
    global _baza
    if _baza is None:
        rekordy: list[dict] = []
        sciezka = DANE_WYNIK_DIR / "aed_unikalne.csv"
        if sciezka.exists():
            with open(sciezka, encoding="utf-8", newline="") as f:
                for r in csv.DictReader(f):
                    rekordy.append({k: (r.get(k) or BRAK) for k in KOLUMNY})
        siatka: dict[tuple[int, int], list[int]] = {}
        for i, r in enumerate(rekordy):
            w = _wsp(r)
            if w:
                siatka.setdefault(_komorka(*w), []).append(i)
        _baza = _Baza(rekordy, siatka)
    return _baza


def _rekordy_dostawcow(db: Session) -> list[dict]:
    wynik = []
    q = (
        select(Zbior.slug, Rekord.dane)
        .join(Rekord, Rekord.zbior_id == Zbior.id)
        .where(Zbior.status == "opublikowany")
        .order_by(Zbior.id, Rekord.lp, Rekord.id)
    )
    for slug, dane in db.execute(q):
        r = {k: (dane.get(k) or BRAK) for k in SCHEMA.publiczne}
        r["id_aed"] = f"{slug}:{dane.get('id_aed', '')}"
        r["status_walidacji"] = "oczekuje"
        r["duplikat_id_aed"] = BRAK
        r["zrodlo"] = f"tuaed:{slug}"
        r["licencja_zrodla"] = LICENCJA
        wynik.append(r)
    return wynik


def _duplikaty(baza: _Baza, dostawcy: list[dict]) -> dict[int, str]:
    """Indeks rekordu z dane/wynik → id_aed najbliższego rekordu dostawcy w promieniu 30 m."""
    najblizszy: dict[int, tuple[float, str]] = {}
    for d in dostawcy:
        w = _wsp(d)
        if not w:
            continue
        ci, cj = _komorka(*w)
        for di in (-1, 0, 1):
            for dj in (-1, 0, 1):
                for i in baza.siatka.get((ci + di, cj + dj), ()):
                    b = _wsp(baza.rekordy[i])
                    m = odleglosc_m(w[0], w[1], b[0], b[1])
                    if m < PROG_M and (i not in najblizszy or m < najblizszy[i][0]):
                        najblizszy[i] = (m, d["id_aed"])
    return {i: v[1] for i, v in najblizszy.items()}


def _zbuduj(db: Session, z_osm: bool) -> bytes:
    baza = _wczytaj_baze()
    dostawcy = _rekordy_dostawcow(db)
    dup = _duplikaty(baza, dostawcy)
    buf = io.StringIO(newline="")
    w = csv.writer(buf, lineterminator="\r\n")
    w.writerow(KOLUMNY)
    for r in dostawcy:
        w.writerow([r.get(k, BRAK) for k in KOLUMNY])
    for i, r in enumerate(baza.rekordy):
        if not z_osm and r["zrodlo"] == "osm":
            continue
        if i in dup:
            r = r | {"duplikat_id_aed": dup[i]}
        w.writerow([r[k] for k in KOLUMNY])
    return buf.getvalue().encode("utf-8")


def plik(db: Session, nazwa: str) -> bytes:
    """Gotowy CSV agregatu. Cache do zmiany zbiorów w bazie (liczba rekordów, ostatnia aktualizacja)."""
    klucz = (
        db.scalar(select(func.count()).select_from(Rekord)),
        db.scalar(select(func.max(Zbior.zaktualizowano))),
        db.scalar(select(func.count()).select_from(Zbior)),
    )
    with _lock:
        if nazwa in _cache and _cache[nazwa][0] == klucz:
            return _cache[nazwa][1]
        tresc = _zbuduj(db, PLIKI[nazwa])
        _cache[nazwa] = (klucz, tresc)
        return tresc
