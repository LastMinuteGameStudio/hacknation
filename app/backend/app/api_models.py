"""Modele Pydantic = kontrakt API (app/KONTRAKT.md, sekcja 2). Lustro: frontend/src/api/types.ts."""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel

Poziom = Literal["blad", "ostrzezenie", "info"]


class Komunikat(BaseModel):
    poziom: Poziom
    kod: str
    komunikat: str
    wiersz: Optional[int] = None
    pole: Optional[str] = None


class Dysponent(BaseModel):
    nazwa: str
    typ: str
    telefon: Optional[str] = None
    email: Optional[str] = None


class PoleSchematu(BaseModel):
    pole: str
    nazwa: str
    grupa: str
    typ: str
    format: str
    wymagalnosc: Literal["O", "Z", "F"]
    publiczne: bool
    opis: str
    przyklad: str
    slownik: Optional[str] = None


class PozycjaSlownika(BaseModel):
    kod: str
    znaczenie: str


class SchematOut(BaseModel):
    wersja: str
    pola: list[PoleSchematu]
    slowniki: dict[str, list[PozycjaSlownika]]


class Kolumna(BaseModel):
    indeks: int
    nazwa: str
    przyklady: list[str]


class PropozycjaMapowania(BaseModel):
    kolumna: str
    pole: Optional[str]
    pewnosc: float
    powod: str


class ImportOut(BaseModel):
    import_id: str
    plik_nazwa: str
    liczba_wierszy: int
    arkusze: list[str] = []
    kolumny: list[Kolumna]
    podglad: list[list[str]]
    mapowanie_propozycja: list[PropozycjaMapowania]
    komunikaty: list[Komunikat] = []


class WalidacjaIn(BaseModel):
    mapowanie: dict[str, Optional[str]]
    dysponent: Dysponent
    wartosci_stale: dict[str, str] = {}  # pole v0.5 -> wartość dla wszystkich AED w pliku


class WalidacjaOut(BaseModel):
    liczba_rekordow: int
    liczba_pominietych: int = 0  # rekordy niepublikowane (GEOKODOWANIE_BRAK)
    liczba_bledow: int
    liczba_ostrzezen: int
    komunikaty: list[Komunikat]
    podglad_wyniku: list[dict[str, str]]
    mozna_publikowac: bool


class PublikacjaOut(BaseModel):
    slug: str
    token_edycji: Optional[str]
    url_csv: str
    url_json: str
    url_metadane: str
    url_edycji: str


class ZbiorOut(BaseModel):
    slug: str
    dysponent: Dysponent
    utworzono: str
    zaktualizowano: str
    liczba_rekordow: int
    mapowanie: dict[str, Optional[str]]


class ZdrowieOut(BaseModel):
    status: str
    baza: bool
    wersja_zakresu: str


class SynchronizacjaIn(BaseModel):
    url: Optional[str]  # None = wyłącz synchronizację
    co_ile_godzin: int = 24


class SynchronizacjaOut(BaseModel):
    url: Optional[str]
    co_ile_godzin: int
    status: Literal["brak", "aktywna", "wstrzymana", "blad"]
    komunikaty: list[Komunikat] = []
    ostatnia_proba: Optional[str] = None
    ostatni_sukces: Optional[str] = None
    liczba_rekordow: int
