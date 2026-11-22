"""S1: synchronizacja zbioru z URL źródła (demo: Przemyśl, CSV na stronie urzędu).

Każde odświeżenie przechodzi zwykłą ścieżką: import powiązany ze zbiorem → walidacja z zapamiętanym mapowaniem,
dysponentem i wartościami stałymi → publikacja pod tym samym slugiem. Dane nie są podmieniane, a synchronizacja
się wstrzymuje, gdy:
- zniknie zmapowana kolumna albo pojawi się nowa (ZMIANA_STRUKTURY),
- walidacja da błędy (SA_BLEDY),
- zmieni się ponad połowa id_aed albo rekordów będzie o ponad połowę mniej (ZA_DUZA_ZMIANA; `wymus=True` pomija).
Wznowienie: PUT /api/zbiory/{slug}/zrodlo albo POST …/synchronizacja?wymus=true.
"""

from __future__ import annotations

import hashlib
import ipaddress
import logging
import os
import socket
import threading
from datetime import datetime, timedelta, timezone
from pathlib import PurePosixPath
from typing import Optional
from urllib.parse import urlparse

import httpx
from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from . import importy
from .api_models import Dysponent, Komunikat, SynchronizacjaIn, SynchronizacjaOut, WalidacjaIn
from .config import MAX_BAJTOW
from .db import Import, Rekord, SessionLocal, Synchronizacja, Zbior

log = logging.getLogger("aed.synchronizacja")

PROG_ZMIANY = 0.5
INTERWAL_S = int(os.environ.get("SYNC_INTERWAL_S", "300"))  # co ile sekund harmonogram sprawdza zaległe zbiory
POZWOL_LOKALNE = os.environ.get("SYNC_POZWOL_LOKALNE", "0") == "1"  # tylko testy/dev: adresy prywatne i localhost
UA = "TuAED-synchronizacja/0.1 (hackathon Misja AED)"


class BladPobierania(Exception):
    pass


def _k(poziom: str, kod: str, komunikat: str) -> dict:
    return Komunikat(poziom=poziom, kod=kod, komunikat=komunikat).model_dump()


# --- pobieranie -----------------------------------------------------------------------------------


def sprawdz_url(url: str) -> None:
    """Tylko http(s) do adresów publicznych: aplikacja jest w internecie, więc nie wpuszczamy żądań do sieci dockera."""
    u = urlparse(url)
    if u.scheme not in ("http", "https") or not u.hostname:
        raise BladPobierania("Adres musi zaczynać się od http:// albo https://.")
    if POZWOL_LOKALNE:
        return
    try:
        adresy = {ai[4][0] for ai in socket.getaddrinfo(u.hostname, u.port or 443, proto=socket.IPPROTO_TCP)}
    except socket.gaierror:
        raise BladPobierania(f"Nie znaleziono serwera {u.hostname}.")
    for a in adresy:
        ip = ipaddress.ip_address(a.split("%")[0])
        if not ip.is_global:
            raise BladPobierania("Adres wskazuje na sieć prywatną. Podaj publiczny adres pliku.")


def _nazwa_pliku(url: str, content_type: str) -> str:
    nazwa = PurePosixPath(urlparse(url).path).name or "zrodlo"
    if PurePosixPath(nazwa).suffix.lower() in importy.FORMATY:
        return nazwa
    ct = content_type.lower()
    if "spreadsheetml" in ct:
        return nazwa + ".xlsx"
    if "json" in ct:
        return nazwa + ".geojson"
    return nazwa + ".csv"


def pobierz(url: str) -> tuple[bytes, str]:
    """→ (treść, nazwa pliku z rozszerzeniem dla parsera). Przekierowania sprawdzamy tak samo jak adres wejściowy."""
    for _ in range(5):
        sprawdz_url(url)
        try:
            with httpx.stream("GET", url, timeout=30.0, follow_redirects=False, headers={"User-Agent": UA}) as r:
                if r.is_redirect:
                    url = str(r.next_request.url) if r.next_request else ""
                    continue
                if r.status_code != 200:
                    raise BladPobierania(f"Serwer źródła odpowiedział kodem {r.status_code}.")
                tresc = bytearray()
                for kawalek in r.iter_bytes():
                    tresc += kawalek
                    if len(tresc) > MAX_BAJTOW:
                        raise BladPobierania("Plik źródła jest większy niż 10 MB.")
                return bytes(tresc), _nazwa_pliku(url, r.headers.get("content-type", ""))
        except httpx.HTTPError as e:
            raise BladPobierania(f"Nie udało się pobrać pliku ({type(e).__name__}).")
    raise BladPobierania("Za dużo przekierowań.")


# --- stan -----------------------------------------------------------------------------------------


def _iso(d: Optional[datetime]) -> Optional[str]:
    return importy._iso(d) if d else None


def out(db: Session, z: Zbior) -> SynchronizacjaOut:
    s = db.get(Synchronizacja, z.id)
    n = db.scalar(select(func.count()).select_from(Rekord).where(Rekord.zbior_id == z.id)) or 0
    if s is None:
        return SynchronizacjaOut(url=None, co_ile_godzin=24, status="brak", liczba_rekordow=n)
    return SynchronizacjaOut(
        url=s.url, co_ile_godzin=s.co_ile_godzin, status=s.status,  # type: ignore[arg-type]
        komunikaty=[Komunikat(**k) for k in (s.komunikaty or [])],
        ostatnia_proba=_iso(s.ostatnia_proba), ostatni_sukces=_iso(s.ostatni_sukces), liczba_rekordow=n,
    )


def ustaw(db: Session, z: Zbior, body: SynchronizacjaIn) -> SynchronizacjaOut:
    s = db.get(Synchronizacja, z.id)
    if not body.url:
        if s is not None:
            db.delete(s)
            db.commit()
        return out(db, z)
    url = body.url.strip()
    try:
        sprawdz_url(url)
    except BladPobierania as e:
        raise importy.blad(422, "ZLY_URL", str(e))
    if not 1 <= body.co_ile_godzin <= 24 * 30:
        raise importy.blad(422, "ZLY_URL", "Częstotliwość: od 1 godziny do 30 dni.")
    if s is None:
        s = Synchronizacja(zbior_id=z.id)
        db.add(s)
    if s.url != url:
        s.hash_pliku = None
    s.url, s.co_ile_godzin = url, body.co_ile_godzin
    s.status, s.komunikaty = "aktywna", []
    db.commit()
    return synchronizuj(db, z)


# --- synchronizacja -------------------------------------------------------------------------------


def _wstrzymaj(s: Synchronizacja, komunikaty: list[dict]) -> None:
    s.status, s.komunikaty = "wstrzymana", komunikaty


def synchronizuj(db: Session, z: Zbior, wymus: bool = False) -> SynchronizacjaOut:
    s = db.get(Synchronizacja, z.id)
    if s is None:
        raise importy.blad(404, "NIE_ZNALEZIONO", "Ten zbiór nie ma ustawionego źródła. Najpierw podaj adres pliku.")
    s.ostatnia_proba = datetime.now(timezone.utc)
    try:
        _synchronizuj(db, z, s, wymus)
    except BladPobierania as e:
        s.status, s.komunikaty = "blad", [_k("blad", "BLAD_POBIERANIA", str(e))]
    except HTTPException as e:  # BladPliku z parsera, limity
        d = e.detail if isinstance(e.detail, dict) else {"kod": "BLAD_POBIERANIA", "komunikat": str(e.detail)}
        s.status, s.komunikaty = "blad", [_k("blad", d.get("kod", "BLAD_POBIERANIA"), d.get("komunikat", ""))]
    db.commit()
    return out(db, z)


def _synchronizuj(db: Session, z: Zbior, s: Synchronizacja, wymus: bool) -> None:
    tresc, nazwa = pobierz(s.url)
    h = hashlib.sha256(tresc).hexdigest()
    if h == s.hash_pliku and not wymus:
        s.status = "aktywna"
        s.komunikaty = [_k("info", "BEZ_ZMIAN", "Plik źródła się nie zmienił od ostatniej synchronizacji.")]
        return

    imp_out = importy.nowy_import(db, nazwa, tresc, None, zbior=z)
    kolumny = {k.nazwa for k in imp_out.kolumny}
    mapowanie = z.mapowanie or {}
    brak = [k for k, pole in mapowanie.items() if pole and k not in kolumny]
    nowe = sorted(kolumny - set(mapowanie))
    if brak or nowe:
        opis = "; ".join(x for x in (
            f"brak kolumn: {', '.join(brak)}" if brak else "",
            f"nowe kolumny: {', '.join(nowe)}" if nowe else "",
        ) if x)
        _wstrzymaj(s, [_k("blad", "ZMIANA_STRUKTURY",
                          f"Zmieniła się struktura pliku źródła ({opis}). Sprawdź mapowanie przez link edycji.")])
        return

    dysponent = Dysponent(nazwa=z.dysponent_nazwa, typ=z.dysponent_typ, telefon=z.telefon_kontaktowy, email=z.email_kontaktowy)
    w = importy.waliduj(db, imp_out.import_id, WalidacjaIn(mapowanie=mapowanie, dysponent=dysponent, wartosci_stale=z.wartosci_stale or {}))
    if not w.mozna_publikowac:
        bledy = [k.model_dump() for k in w.komunikaty if k.poziom == "blad"][:5]
        _wstrzymaj(s, [_k("blad", "SA_BLEDY", f"Nowa wersja pliku ma {w.liczba_bledow} błędów, dane nie zostały podmienione.")] + bledy)
        return

    stare = set(db.scalars(select(Rekord.id_aed).where(Rekord.zbior_id == z.id)))
    imp = db.get(Import, imp_out.import_id)
    nowe_id = {r["dane"].get("id_aed", "") for r in (imp.rekordy or [])}
    if stare and not wymus:
        zmienione = 1 - len(stare & nowe_id) / len(stare)
        if zmienione > PROG_ZMIANY or len(nowe_id) < len(stare) * PROG_ZMIANY:
            _wstrzymaj(s, [_k("ostrzezenie", "ZA_DUZA_ZMIANA",
                              f"Zmieniło się {round(zmienione * 100)}% identyfikatorów AED (było {len(stare)}, jest {len(nowe_id)}). "
                              "Możliwa zmiana formatu w źródle. Sprawdź podgląd i potwierdź synchronizację ręcznie.")])
            return

    importy.publikuj(db, imp_out.import_id)
    s.status, s.hash_pliku = "aktywna", h
    s.ostatni_sukces = datetime.now(timezone.utc)
    s.komunikaty = [_k("info", "ZSYNCHRONIZOWANO", f"Opublikowano {w.liczba_rekordow} AED z pliku źródła.")]


# --- harmonogram ----------------------------------------------------------------------------------


def zalegle(db: Session, teraz: datetime) -> list[int]:
    wynik = []
    for s in db.scalars(select(Synchronizacja).where(Synchronizacja.status.in_(("aktywna", "blad")))):
        ostatnia = s.ostatnia_proba
        if ostatnia is not None and ostatnia.tzinfo is None:
            ostatnia = ostatnia.replace(tzinfo=timezone.utc)
        if ostatnia is None or teraz - ostatnia >= timedelta(hours=s.co_ile_godzin):
            wynik.append(s.zbior_id)
    return wynik


def uruchom_zalegle() -> None:
    with SessionLocal() as db:
        for zbior_id in zalegle(db, datetime.now(timezone.utc)):
            z = db.get(Zbior, zbior_id)
            if z is None:
                continue
            try:
                synchronizuj(db, z)
            except Exception:  # noqa: BLE001 — jeden zły zbiór nie może zatrzymać pozostałych
                db.rollback()
                log.exception("synchronizacja zbioru %s", z.slug)


def start_harmonogramu() -> threading.Event:
    stop = threading.Event()

    def petla() -> None:
        while not stop.wait(INTERWAL_S):
            try:
                uruchom_zalegle()
            except Exception:  # noqa: BLE001
                log.exception("harmonogram synchronizacji")

    threading.Thread(target=petla, name="synchronizacja", daemon=True).start()
    return stop
