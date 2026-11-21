"""B3: pliki publiczne zbioru /d/{slug}.csv | .json | .csv-metadata.json (KONTRAKT.md §2 „Pliki publiczne”)."""

from __future__ import annotations

import json
from typing import Optional

from fastapi import Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from . import core
from .config import BASE_URL, LICENCJA
from .db import Rekord, Zbior
from .importy import SCHEMA, _iso, blad

CSV = "text/csv; charset=utf-8"
JSON = "application/json; charset=utf-8"
CSVW = "application/csvm+json; charset=utf-8"
NAGLOWKI = {"Access-Control-Allow-Origin": "*", "Cache-Control": "no-cache"}  # dane otwarte: dostęp z innych domen


def rozbij_nazwe(nazwa: str) -> tuple[str, str]:
    """„k7q2m9xa.csv-metadata.json” → („k7q2m9xa”, „csv-metadata.json”)."""
    for rozszerzenie in ("csv-metadata.json", "csv", "json"):
        if nazwa.endswith("." + rozszerzenie):
            return nazwa[: -len(rozszerzenie) - 1], rozszerzenie
    raise blad(404, "NIE_ZNALEZIONO", "Nie ma takiego pliku. Dostępne: .csv, .json, .csv-metadata.json.")


def _zbior(db: Session, slug: str) -> Zbior:
    z = db.scalar(select(Zbior).where(Zbior.slug == slug))
    if z is None or z.status != "opublikowany":
        raise blad(404, "NIE_ZNALEZIONO", "Nie ma zbioru o tym adresie.")
    return z


def rekordy(db: Session, zbior_id: int) -> list[dict[str, str]]:
    return list(db.scalars(select(Rekord.dane).where(Rekord.zbior_id == zbior_id).order_by(Rekord.lp, Rekord.id)))


def tytul(z: Zbior) -> str:
    return f"Defibrylatory AED: {z.dysponent_nazwa}"


def metadane(z: Zbior, liczba: Optional[int] = None) -> dict:
    m = {
        "tytul": tytul(z),
        "slug": z.slug,
        "dysponent": z.dysponent_nazwa,
        "dysponent_typ": z.dysponent_typ,
        "licencja": LICENCJA,
        "licencja_url": "https://creativecommons.org/publicdomain/zero/1.0/",
        "wersja_zakresu": SCHEMA.wersja,
        "utworzono": _iso(z.utworzono),
        "zaktualizowano": _iso(z.zaktualizowano),
        "url_csv": f"{BASE_URL}/d/{z.slug}.csv",
        "url_metadane": f"{BASE_URL}/d/{z.slug}.csv-metadata.json",
    }
    if liczba is not None:
        m["liczba_rekordow"] = liczba
    return m


def plik(db: Session, nazwa: str) -> Response:
    slug, rodzaj = rozbij_nazwe(nazwa)
    z = _zbior(db, slug)
    if rodzaj == "csv-metadata.json":
        m = core.csvw_metadata(SCHEMA, f"{BASE_URL}/d/{slug}.csv", tytul(z))
        m["dc:modified"] = _iso(z.zaktualizowano)
        return Response(json.dumps(m, ensure_ascii=False, indent=1).encode("utf-8"), media_type=CSVW, headers=NAGLOWKI)
    recs = rekordy(db, z.id)
    if rodzaj == "csv":
        return Response(core.to_csv(recs, SCHEMA, public_only=True), media_type=CSV,
                        headers=NAGLOWKI | {"Content-Disposition": f'inline; filename="aed-{slug}.csv"'})
    return Response(core.to_json(recs, SCHEMA, metadane(z, len(recs))), media_type=JSON, headers=NAGLOWKI)
