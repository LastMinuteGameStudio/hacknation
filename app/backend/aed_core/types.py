"""Typy współdzielone przez rdzeń (ścieżka A) i API (ścieżka B). Kontrakt: app/KONTRAKT.md, sekcja 3."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, Optional, Protocol

Poziom = Literal["blad", "ostrzezenie", "info"]

# Specjalne pole mapowania: kolumna z geometrią (JSON / WKT / "lat,lon"), rozbijana na szerokość i długość.
POLE_GEOMETRIA = "_geometria"
# Specjalne pole mapowania: adres w jednym polu ("ul. Jasna 5, 38-400 Krosno"), rozbijany na części.
POLE_ADRES_PELNY = "_adres_pelny"
# Specjalne pole mapowania: godziny w jednym polu (opening_hours, "pn-pt 8-16", "24h") → dostepny_24_7 + godziny_*.
POLE_GODZINY = "_godziny"


@dataclass
class Message:
    poziom: Poziom
    kod: str
    komunikat: str
    wiersz: Optional[int] = None  # numer wiersza w arkuszu, jak widzi go dostawca (nagłówek w 1 → dane od 2); None = cały plik
    pole: Optional[str] = None


@dataclass
class Field:
    lp: int
    grupa: str
    pole: str
    nazwa: str
    typ: str
    format: str
    wymagalnosc: Literal["O", "Z", "F"]
    publiczne: bool
    opis: str
    przyklad: str
    slownik: Optional[str] = None  # nazwa słownika, gdy typ == "słownik"


@dataclass
class Schema:
    wersja: str
    pola: list[Field]
    slowniki: dict[str, list[tuple[str, str]]]  # nazwa -> [(kod, znaczenie)]

    def pole(self, nazwa: str) -> Field:
        for f in self.pola:
            if f.pole == nazwa:
                return f
        raise KeyError(nazwa)

    @property
    def nazwy(self) -> list[str]:
        return [f.pole for f in self.pola]

    @property
    def publiczne(self) -> list[str]:
        return [f.pole for f in self.pola if f.publiczne]


@dataclass
class Table:
    """Plik dostawcy po odczytaniu: nagłówki + wiersze jako tekst."""

    columns: list[str]
    rows: list[list[str]]
    sheets: list[str] = field(default_factory=list)
    messages: list[Message] = field(default_factory=list)
    header_row: int = 1  # numer wiersza nagłówka w arkuszu
    row_numbers: list[int] = field(default_factory=list)  # numer wiersza rows[i] w arkuszu; pusta = header_row + 1 + i

    def numer_wiersza(self, i: int) -> int:
        if i < len(self.row_numbers):
            return self.row_numbers[i]
        return self.header_row + 1 + i


@dataclass
class MappingSuggestion:
    kolumna: str
    pole: Optional[str]  # None = nie importuj
    pewnosc: float  # 0..1
    powod: str  # np. "nazwa kolumny", "zawartość: liczby 49–55"


@dataclass
class Provider:
    nazwa: str
    typ: str
    telefon: Optional[str] = None
    email: Optional[str] = None
    slug: Optional[str] = None  # do generowania id_aed, gdy brak kod_terc


@dataclass
class RecordResult:
    wiersz: int  # numer wiersza w arkuszu, jak widzi go dostawca
    record: dict[str, str]  # pole v0.5 -> wartość sformatowana jak w CSV ("" = brak)
    messages: list[Message] = field(default_factory=list)
    pominiety: bool = False  # True = nie publikować (np. GEOKODOWANIE_BRAK)


@dataclass
class AddressQuery:
    ulica: str = ""
    nr_budynku: str = ""
    kod_pocztowy: str = ""
    miejscowosc: str = ""
    kod_terc: str = ""


@dataclass
class GeoResult:
    lat: float
    lon: float
    dokladnosc: str  # kod ze słownika dokladnosc_polozenia
    kod_terc: str = ""
    kod_simc: str = ""
    kod_ulic: str = ""
    kod_pocztowy: str = ""
    niejednoznaczny: bool = False


class Geocoder(Protocol):
    def geocode(self, query: AddressQuery) -> Optional[GeoResult]: ...


class GeocodeCache(Protocol):
    def get(self, key: str) -> Optional[GeoResult]: ...

    def put(self, key: str, value: Optional[GeoResult]) -> None: ...
