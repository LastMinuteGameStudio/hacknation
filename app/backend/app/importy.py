"""B2: logika import → walidacja → publikacja i edycji przez prywatny link (KONTRAKT.md §2)."""

from __future__ import annotations

import hashlib
import hmac
import secrets
from collections import defaultdict
from dataclasses import asdict
from datetime import date, datetime, timezone
from pathlib import PurePath
from typing import Optional

from fastapi import HTTPException, UploadFile
from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from aed_core.parsers import BladPliku
from aed_core.schema import load_schema
from aed_core.types import Message, Provider

from . import core
from .api_models import (
    Dysponent,
    ImportOut,
    Kolumna,
    Komunikat,
    PropozycjaMapowania,
    PublikacjaOut,
    WalidacjaIn,
    WalidacjaOut,
    ZbiorOut,
)
from .config import BASE_URL, MAX_BAJTOW, MAX_WIERSZY, ZAKRES_DIR
from .db import DbGeocodeCache, Import, Rekord, Zbior

SCHEMA = load_schema(ZAKRES_DIR)
FORMATY = {".csv", ".xlsx", ".geojson"}
SLUG_ZNAKI = "abcdefghijkmnpqrstuvwxyz23456789"  # bez l, o, 0, 1 (czytelne w URL)
MAX_KOMUNIKATOW_NA_KOD = 20
PODGLAD_WIERSZY = 10
PODGLAD_WYNIKU = 20


def blad(status: int, kod: str, komunikat: str) -> HTTPException:
    return HTTPException(status_code=status, detail={"kod": kod, "komunikat": komunikat})


def _teraz() -> datetime:
    return datetime.now(timezone.utc)


# --- token i slug ---------------------------------------------------------------------------------


def hash_tokenu(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _nowy_slug(db: Session) -> str:
    while True:
        slug = "".join(secrets.choice(SLUG_ZNAKI) for _ in range(8))
        zajety = db.scalar(select(func.count()).select_from(Zbior).where(Zbior.slug == slug)) or db.scalar(
            select(func.count()).select_from(Import).where(Import.slug == slug)
        )
        if not zajety:
            return slug


def zbior_z_tokenem(db: Session, slug: str, token: str) -> Zbior:
    z = db.scalar(select(Zbior).where(Zbior.slug == slug))
    if z is None:
        raise blad(404, "NIE_ZNALEZIONO", "Nie ma zbioru o tym adresie.")
    if not token or not hmac.compare_digest(z.token_edycji_hash, hash_tokenu(token)):
        raise blad(403, "ZLY_TOKEN", "Link edycji jest nieprawidłowy. Użyj linku otrzymanego przy publikacji.")
    return z


def _iso(d: datetime) -> str:
    if d.tzinfo is None:  # SQLite gubi strefę
        d = d.replace(tzinfo=timezone.utc)
    return d.isoformat(timespec="seconds")


def zbior_out(db: Session, z: Zbior) -> ZbiorOut:
    n = db.scalar(select(func.count()).select_from(Rekord).where(Rekord.zbior_id == z.id)) or 0
    return ZbiorOut(
        slug=z.slug,
        dysponent=Dysponent(nazwa=z.dysponent_nazwa, typ=z.dysponent_typ, telefon=z.telefon_kontaktowy, email=z.email_kontaktowy),
        utworzono=_iso(z.utworzono),
        zaktualizowano=_iso(z.zaktualizowano),
        liczba_rekordow=n,
        mapowanie=z.mapowanie or {},
    )


# --- import ---------------------------------------------------------------------------------------


def _komunikat(m: Message) -> Komunikat:
    return Komunikat(poziom=m.poziom, kod=m.kod, komunikat=m.komunikat, wiersz=m.wiersz, pole=m.pole)


async def wczytaj_upload(plik: UploadFile) -> bytes:
    nazwa = plik.filename or ""
    if PurePath(nazwa).suffix.lower() not in FORMATY:
        raise blad(415, "NIEOBSLUGIWANY_FORMAT", "Obsługujemy pliki CSV, XLSX i GeoJSON. Zapisz arkusz w jednym z tych formatów.")
    tresc = await plik.read(MAX_BAJTOW + 1)
    if len(tresc) > MAX_BAJTOW:
        raise blad(413, "ZA_DUZY_PLIK", "Plik jest większy niż 10 MB. Podziel go na mniejsze części.")
    return tresc


def _czytaj(nazwa: str, tresc: bytes, arkusz: Optional[str]):
    try:
        t = core.read_table(tresc, nazwa, arkusz)
    except BladPliku as e:
        raise blad(e.status, e.kod, e.komunikat)
    except Exception as e:  # noqa: BLE001 — uszkodzony plik nie może dać 500
        raise blad(415, "NIEOBSLUGIWANY_FORMAT", f"Nie udało się odczytać pliku ({type(e).__name__}). Sprawdź, czy to poprawny CSV lub XLSX.")
    for m in t.messages:
        if m.poziom == "blad" and m.kod == "NIEOBSLUGIWANY_FORMAT":
            raise blad(415, m.kod, m.komunikat)
        if m.poziom == "blad" and m.kod in ("ZA_DUZY_PLIK", "ZA_DUZO_WIERSZY"):
            raise blad(413, m.kod, m.komunikat)
    if liczba_wierszy(t) > MAX_WIERSZY:
        raise blad(413, "ZA_DUZO_WIERSZY", f"Plik ma {liczba_wierszy(t)} wierszy, limit to {MAX_WIERSZY}. Podziel go na mniejsze części.")
    return t


def liczba_wierszy(t) -> int:
    """Wiersze z co najmniej jedną niepustą komórką (puste wiersze w środku zostają w rows)."""
    return sum(any(str(v).strip() for v in r) for r in t.rows)


def nowy_import(db: Session, nazwa: str, tresc: bytes, arkusz: Optional[str], zbior: Optional[Zbior] = None) -> ImportOut:
    t = _czytaj(nazwa, tresc, arkusz)
    poprzednie = zbior.mapowanie if zbior else None
    propozycje = core.suggest_mapping(t, SCHEMA, poprzednie)
    kolumny = [
        Kolumna(indeks=i, nazwa=c, przyklady=[r[i] for r in t.rows if i < len(r) and r[i].strip()][:3])
        for i, c in enumerate(t.columns)
    ]
    podglad = [[str(v) for v in r] for r in t.rows[:PODGLAD_WIERSZY]]
    imp = Import(
        zbior_id=zbior.id if zbior else None,
        slug=zbior.slug if zbior else _nowy_slug(db),
        plik_nazwa=nazwa,
        plik=tresc,
        arkusz=arkusz,
        kolumny=[k.model_dump() for k in kolumny],
        podglad=podglad,
    )
    db.add(imp)
    db.commit()
    return ImportOut(
        import_id=imp.id,
        plik_nazwa=nazwa,
        liczba_wierszy=liczba_wierszy(t),
        arkusze=t.sheets,
        kolumny=kolumny,
        podglad=podglad,
        mapowanie_propozycja=[PropozycjaMapowania(**asdict(p)) for p in propozycje],
        komunikaty=[_komunikat(m) for m in t.messages],
    )


def _import(db: Session, import_id: str) -> Import:
    imp = db.get(Import, import_id)
    if imp is None:
        raise blad(404, "NIE_ZNALEZIONO", "Nie ma takiego importu. Wgraj plik ponownie.")
    return imp


# --- walidacja ------------------------------------------------------------------------------------


def zgrupuj(msgs: list[Message]) -> list[Message]:
    """Ten sam kod w więcej niż 20 wierszach → jeden komunikat z wiersz=None i pierwszymi numerami wierszy."""
    grupy: dict[tuple, list[Message]] = defaultdict(list)
    for m in msgs:
        if m.wiersz is not None:
            grupy[(m.poziom, m.kod, m.pole)].append(m)
    duze = {k for k, v in grupy.items() if len(v) > MAX_KOMUNIKATOW_NA_KOD}
    wynik: list[Message] = []
    dodane: set[tuple] = set()
    for m in msgs:
        k = (m.poziom, m.kod, m.pole)
        if m.wiersz is None or k not in duze:
            wynik.append(m)
        elif k not in dodane:
            dodane.add(k)
            g = grupy[k]
            przyklady = ", ".join(str(x.wiersz) for x in g[:3])
            tekst = m.komunikat.rstrip(". ")
            wynik.append(Message(m.poziom, m.kod, f"{tekst}. Dotyczy {len(g)} wierszy, m.in. {przyklady}.", None, m.pole))
    return wynik


def waliduj(db: Session, import_id: str, body: WalidacjaIn) -> WalidacjaOut:
    imp = _import(db, import_id)
    t = _czytaj(imp.plik_nazwa, imp.plik, imp.arkusz)
    mapowanie = {k: v for k, v in body.mapowanie.items() if k in t.columns}
    d = body.dysponent
    provider = Provider(nazwa=d.nazwa, typ=d.typ, telefon=d.telefon, email=d.email, slug=imp.slug)
    wyniki = core.normalize_table(
        t, mapowanie, SCHEMA, provider, date.today(), core.Geokoder(DbGeocodeCache()), dict(body.wartosci_stale)
    )
    msgs = list(t.messages) + [m for r in wyniki for m in r.messages] + core.validate_records(wyniki, SCHEMA)
    msgs = zgrupuj(msgs)
    publikowane = [r for r in wyniki if not r.pominiety]
    publiczne = SCHEMA.publiczne
    liczba_bledow = sum(m.poziom == "blad" for m in msgs)
    out = WalidacjaOut(
        liczba_rekordow=len(publikowane),
        liczba_pominietych=len(wyniki) - len(publikowane),
        liczba_bledow=liczba_bledow,
        liczba_ostrzezen=sum(m.poziom == "ostrzezenie" for m in msgs),
        komunikaty=[_komunikat(m) for m in msgs],
        podglad_wyniku=[{p: r.record.get(p, "") for p in publiczne} for r in publikowane[:PODGLAD_WYNIKU]],
        mozna_publikowac=liczba_bledow == 0 and len(publikowane) > 0,
    )
    imp.mapowanie = body.mapowanie
    imp.wartosci_stale = dict(body.wartosci_stale)
    imp.dysponent = d.model_dump()
    imp.rekordy = [
        {"wiersz": r.wiersz, "dane": r.record, "komunikaty": [asdict(m) for m in r.messages]} for r in publikowane
    ]
    imp.wynik_walidacji = out.model_dump()
    db.commit()
    return out


# --- publikacja -----------------------------------------------------------------------------------


def urle(slug: str, token: Optional[str]) -> PublikacjaOut:
    return PublikacjaOut(
        slug=slug,
        token_edycji=token,
        url_csv=f"{BASE_URL}/d/{slug}.csv",
        url_json=f"{BASE_URL}/d/{slug}.json",
        url_metadane=f"{BASE_URL}/d/{slug}.csv-metadata.json",
        url_edycji=f"{BASE_URL}/edycja/{slug}" + (f"?token={token}" if token else ""),
    )


def publikuj(db: Session, import_id: str) -> PublikacjaOut:
    imp = _import(db, import_id)
    w = imp.wynik_walidacji
    if not w or not w.get("mozna_publikowac") or imp.rekordy is None:
        raise blad(409, "SA_BLEDY", "Najpierw popraw błędy i ponownie sprawdź plik. Publikacja wymaga walidacji bez błędów.")
    d = Dysponent(**imp.dysponent)
    token: Optional[str] = None
    if imp.zbior_id is not None:
        z = db.get(Zbior, imp.zbior_id)
        if z is None:
            raise blad(404, "NIE_ZNALEZIONO", "Zbiór powiązany z importem już nie istnieje.")
        db.execute(delete(Rekord).where(Rekord.zbior_id == z.id))
    else:
        token = secrets.token_urlsafe(32)
        z = Zbior(slug=imp.slug, token_edycji_hash=hash_tokenu(token), dysponent_nazwa=d.nazwa, dysponent_typ=d.typ)
        db.add(z)
        db.flush()
        imp.zbior_id = z.id
    z.dysponent_nazwa, z.dysponent_typ = d.nazwa, d.typ
    z.telefon_kontaktowy, z.email_kontaktowy = d.telefon, d.email
    z.mapowanie = imp.mapowanie or {}
    z.wartosci_stale = imp.wartosci_stale or {}
    z.zaktualizowano = _teraz()
    db.add_all(
        Rekord(zbior_id=z.id, lp=i, id_aed=r["dane"].get("id_aed", ""), dane=r["dane"], ostrzezenia=r["komunikaty"])
        for i, r in enumerate(imp.rekordy)
    )
    imp.opublikowano = _teraz()
    db.commit()
    return urle(z.slug, token)
