"""B1: schemat bazy (PostgreSQL, SQLAlchemy 2). Model: app/PLAN.md §3 „Model danych”.

Tabele tworzone przy starcie (create_all); bez migracji w MVP. Testy: DATABASE_URL=sqlite:///…
"""

from __future__ import annotations

import uuid
from dataclasses import asdict
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import (
    JSON,
    DateTime,
    ForeignKey,
    Integer,
    LargeBinary,
    String,
    Text,
    create_engine,
    select,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

from aed_core.types import GeoResult

from .config import DATABASE_URL

JSONType = JSON().with_variant(JSONB(), "postgresql")


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class Zbior(Base):
    __tablename__ = "zbior"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    token_edycji_hash: Mapped[str] = mapped_column(String(128))  # sha256 hex; sam token nigdy nie trafia do bazy
    dysponent_nazwa: Mapped[str] = mapped_column(Text)
    dysponent_typ: Mapped[str] = mapped_column(String(64))
    telefon_kontaktowy: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)  # niepubliczne
    email_kontaktowy: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)  # niepubliczne
    mapowanie: Mapped[dict] = mapped_column(JSONType, default=dict)
    wartosci_stale: Mapped[dict] = mapped_column(JSONType, default=dict)
    zrodlo_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # S1: synchronizacja z URL
    status: Mapped[str] = mapped_column(String(32), default="opublikowany")
    utworzono: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    zaktualizowano: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)


class Rekord(Base):
    __tablename__ = "rekord"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    zbior_id: Mapped[int] = mapped_column(ForeignKey("zbior.id", ondelete="CASCADE"), index=True)
    lp: Mapped[int] = mapped_column(Integer, default=0)  # kolejność jak w pliku dostawcy
    id_aed: Mapped[str] = mapped_column(String(128))
    dane: Mapped[dict] = mapped_column(JSONType)  # wszystkie pola v0.5 (też niepubliczne), wartości jako tekst
    ostrzezenia: Mapped[list] = mapped_column(JSONType, default=list)


class Import(Base):
    __tablename__ = "import"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    zbior_id: Mapped[Optional[int]] = mapped_column(ForeignKey("zbior.id", ondelete="SET NULL"), nullable=True)
    # Rezerwowany przy wgraniu (stałe id_aed od pierwszej walidacji); przy imporcie z linku edycji = slug zbioru.
    slug: Mapped[str] = mapped_column(String(32), index=True)
    plik_nazwa: Mapped[str] = mapped_column(Text)
    plik: Mapped[bytes] = mapped_column(LargeBinary)  # cały plik: walidacja czyta wszystkie wiersze
    arkusz: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    kolumny: Mapped[list] = mapped_column(JSONType, default=list)
    podglad: Mapped[list] = mapped_column(JSONType, default=list)
    mapowanie: Mapped[Optional[dict]] = mapped_column(JSONType, nullable=True)
    wartosci_stale: Mapped[Optional[dict]] = mapped_column(JSONType, nullable=True)
    dysponent: Mapped[Optional[dict]] = mapped_column(JSONType, nullable=True)
    rekordy: Mapped[Optional[list]] = mapped_column(JSONType, nullable=True)  # wynik ostatniej walidacji (bez pominiętych)
    wynik_walidacji: Mapped[Optional[dict]] = mapped_column(JSONType, nullable=True)  # WalidacjaOut
    opublikowano: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    utworzono: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class GeokodCache(Base):
    __tablename__ = "geokod_cache"
    zapytanie: Mapped[str] = mapped_column(Text, primary_key=True)
    lat: Mapped[Optional[float]] = mapped_column(nullable=True)  # None = adresu nie znaleziono (też cache'ujemy)
    lon: Mapped[Optional[float]] = mapped_column(nullable=True)
    dokladnosc: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    wynik: Mapped[Optional[dict]] = mapped_column(JSONType, nullable=True)  # pełny GeoResult (TERC, SIMC, ULIC…)
    utworzono: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


def _engine_kwargs(url: str) -> dict:
    if url.startswith("sqlite"):
        return {"connect_args": {"check_same_thread": False}}
    return {"pool_pre_ping": True}


engine = create_engine(DATABASE_URL, future=True, **_engine_kwargs(DATABASE_URL))
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


class DbGeocodeCache:
    """GeocodeCache (aed_core.types) w tabeli geokod_cache. Każda operacja we własnej sesji (wątki geokodera)."""

    def get(self, key: str) -> Optional[GeoResult]:
        with SessionLocal() as s:
            row = s.get(GeokodCache, key)
            if row is None or row.wynik is None:
                return None
            return GeoResult(**row.wynik)

    def has(self, key: str) -> bool:
        with SessionLocal() as s:
            return s.scalar(select(GeokodCache.zapytanie).where(GeokodCache.zapytanie == key)) is not None

    def put(self, key: str, value: Optional[GeoResult]) -> None:
        try:
            with SessionLocal() as s:
                s.merge(
                    GeokodCache(
                        zapytanie=key,
                        lat=value.lat if value else None,
                        lon=value.lon if value else None,
                        dokladnosc=value.dokladnosc if value else None,
                        wynik=asdict(value) if value else None,
                        utworzono=_now(),
                    )
                )
                s.commit()
        except Exception:  # noqa: BLE001 — wyścig dwóch wątków o ten sam klucz nie może przerwać walidacji
            pass


def init_db() -> bool:
    """Tworzy tabele. Zwraca False, gdy baza jest niedostępna."""
    try:
        Base.metadata.create_all(engine)
        return True
    except Exception:  # noqa: BLE001 — brak bazy nie może blokować startu w trybie dev
        return False


def db_ok() -> bool:
    try:
        with engine.connect() as c:
            c.execute(text("select 1"))
        return True
    except Exception:  # noqa: BLE001
        return False
