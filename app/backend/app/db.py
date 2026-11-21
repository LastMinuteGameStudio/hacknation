"""B1: schemat bazy (PostgreSQL, SQLAlchemy 2). Tabele tworzone przy starcie (create_all); bez migracji w MVP."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text, create_engine, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

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
    token_edycji_hash: Mapped[str] = mapped_column(String(128))
    dysponent_nazwa: Mapped[str] = mapped_column(Text)
    dysponent_typ: Mapped[str] = mapped_column(String(64))
    telefon_kontaktowy: Mapped[str | None] = mapped_column(String(32), nullable=True)
    email_kontaktowy: Mapped[str | None] = mapped_column(String(256), nullable=True)
    mapowanie: Mapped[dict] = mapped_column(JSONType, default=dict)
    zrodlo_url: Mapped[str | None] = mapped_column(Text, nullable=True)  # S1: synchronizacja z URL
    utworzono: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    zaktualizowano: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)


class Rekord(Base):
    __tablename__ = "rekord"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    zbior_id: Mapped[int] = mapped_column(ForeignKey("zbior.id", ondelete="CASCADE"), index=True)
    id_aed: Mapped[str] = mapped_column(String(128))
    dane: Mapped[dict] = mapped_column(JSONType)  # pola v0.5, wartości jako tekst
    ostrzezenia: Mapped[list] = mapped_column(JSONType, default=list)


class Import(Base):
    __tablename__ = "import"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    zbior_id: Mapped[int | None] = mapped_column(ForeignKey("zbior.id", ondelete="SET NULL"), nullable=True)
    plik_nazwa: Mapped[str] = mapped_column(Text)
    tabela: Mapped[dict] = mapped_column(JSONType)  # {"columns": [...], "rows": [[...]]}
    mapowanie: Mapped[dict | None] = mapped_column(JSONType, nullable=True)
    dysponent: Mapped[dict | None] = mapped_column(JSONType, nullable=True)
    wynik: Mapped[dict | None] = mapped_column(JSONType, nullable=True)  # rekordy + komunikaty po walidacji
    utworzono: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class GeokodCache(Base):
    __tablename__ = "geokod_cache"
    zapytanie: Mapped[str] = mapped_column(Text, primary_key=True)
    wynik: Mapped[dict | None] = mapped_column(JSONType, nullable=True)
    utworzono: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


engine = create_engine(DATABASE_URL, pool_pre_ping=True, future=True)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


def init_db() -> bool:
    """Tworzy tabele. Zwraca False, gdy baza jest niedostępna (aplikacja działa wtedy w trybie atrap)."""
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
