"""Atrapy odpowiedzi zgodne z kontraktem: front (C) może działać, zanim powstaną rdzeń (A) i API (B).
Ścieżka B usuwa użycie atrap, gdy prawdziwe endpointy działają."""

from __future__ import annotations

import uuid

from .api_models import (
    ImportOut,
    Kolumna,
    Komunikat,
    PropozycjaMapowania,
    PublikacjaOut,
    WalidacjaOut,
)
from .config import BASE_URL

_KOLUMNY = ["Długość geograficzna", "Szerokość geograficzna", " Nazwa", " Lokalizacja", " Adres", " Numer Id"]
_WIERSZE = [
    ["21.72034402175176", "49.718809346153336", "Defibrylator", "Zespół  Krytych Pływalni", "ul. Jasna, 38-400 Krosno", "1"],
    ["21.71133598253567", "49.719088753029276", "Defibrylator", "Kampus Sportowo-dydaktyczny, portiernia", "ul. Stanisława Wyspiańskiego 20, 38-400 Krosno", "2"],
    ["21.715090873839404", "49.72174399261284", "Defibrylator", "OSP Turaszówka", "ul. Rzeszowska, 38-400 Krosno", "3"],
]


def import_out(plik_nazwa: str = "krosno.csv") -> ImportOut:
    return ImportOut(
        import_id=str(uuid.uuid4()),
        plik_nazwa=plik_nazwa,
        liczba_wierszy=21,
        arkusze=[],
        kolumny=[Kolumna(indeks=i, nazwa=n, przyklady=[w[i] for w in _WIERSZE]) for i, n in enumerate(_KOLUMNY)],
        podglad=_WIERSZE,
        mapowanie_propozycja=[
            PropozycjaMapowania(kolumna=_KOLUMNY[0], pole="dlugosc_geograficzna", pewnosc=0.97, powod="nazwa kolumny"),
            PropozycjaMapowania(kolumna=_KOLUMNY[1], pole="szerokosc_geograficzna", pewnosc=0.97, powod="nazwa kolumny"),
            PropozycjaMapowania(kolumna=_KOLUMNY[2], pole=None, pewnosc=0.6, powod="ta sama wartość w każdym wierszu"),
            PropozycjaMapowania(kolumna=_KOLUMNY[3], pole="nazwa_obiektu", pewnosc=0.7, powod="nazwa kolumny"),
            PropozycjaMapowania(kolumna=_KOLUMNY[4], pole="_adres_pelny", pewnosc=0.8, powod="zawartość: adres w jednym polu"),
            PropozycjaMapowania(kolumna=_KOLUMNY[5], pole="id_zrodlowe", pewnosc=0.75, powod="nazwa kolumny"),
        ],
        komunikaty=[Komunikat(poziom="info", kod="ATRAPA", komunikat="Odpowiedź przykładowa: rdzeń konwersji jeszcze nie działa.")],
    )


def walidacja_out() -> WalidacjaOut:
    kom = [
        Komunikat(poziom="ostrzezenie", kod="DOMYSLNY_STATUS", komunikat="Brak kolumny ze stanem urządzenia. Ustawiono „nieznany” dla 21 AED.", pole="status"),
        Komunikat(poziom="ostrzezenie", kod="DOMYSLNA_DATA_WERYFIKACJI", komunikat="Brak daty weryfikacji. Wpisano datę wgrania. Podaj datę ostatniego sprawdzenia urządzenia.", pole="data_weryfikacji"),
        Komunikat(poziom="ostrzezenie", kod="BRAK_POLA_ZALECANEGO", komunikat="Brak godzin dostępności w 21 wierszach.", pole="godziny_pn"),
        Komunikat(poziom="info", kod="ROZBITO_ADRES", komunikat="Adres rozbito na ulicę, numer, kod pocztowy i miejscowość.", wiersz=2, pole="nazwa_ulicy"),
    ]
    return WalidacjaOut(
        liczba_rekordow=21,
        liczba_bledow=0,
        liczba_ostrzezen=3,
        komunikaty=kom,
        podglad_wyniku=[
            {"id_aed": "1861011-0001", "szerokosc_geograficzna": "49.718809", "dlugosc_geograficzna": "21.720344",
             "nazwa_obiektu": "Zespół Krytych Pływalni", "nazwa_ulicy": "Jasna", "kod_pocztowy": "38-400",
             "miejscowosc": "Krosno", "status": "nieznany", "dysponent_nazwa": "Urząd Miasta Krosna"},
        ],
        mozna_publikowac=True,
    )


def publikacja_out(slug: str = "atrapa01", token: str | None = "atrapa-token") -> PublikacjaOut:
    return PublikacjaOut(
        slug=slug,
        token_edycji=token,
        url_csv=f"{BASE_URL}/d/{slug}.csv",
        url_json=f"{BASE_URL}/d/{slug}.json",
        url_metadane=f"{BASE_URL}/d/{slug}.csv-metadata.json",
        url_edycji=f"{BASE_URL}/edycja/{slug}?token={token or ''}",
    )
