"""A5: walidacja rekordów: O = błąd, Z = ostrzeżenie (zbiorczo per pole), formaty, słowniki,
współrzędne w Polsce (bbox ok. 49.0–54.9 N, 14.1–24.2 E), duplikaty id_aed / numer_seryjny (błąd),
bliskie punkty < 5 m (ostrzeżenie). Kody: app/KONTRAKT.md, sekcja 4.

Rekordy z `pominiety = True` nie są walidowane (i tak nie trafią do publikacji).
Zwraca tylko komunikaty walidacji; komunikaty normalizacji są w RecordResult.messages.
"""

from __future__ import annotations

import math
import re
from collections import defaultdict
from datetime import date, datetime

from .types import Message, RecordResult, Schema

LAT_MIN, LAT_MAX = 49.0, 54.9
LON_MIN, LON_MAX = 14.1, 24.2
BLISKO_M = 5.0
MIN_MIEJSC = 5

_GODZ = re.compile(r"^(?:X|zamkniete|(?:[01]\d|2[0-4]):[0-5]\d-(?:[01]\d|2[0-4]):[0-5]\d"
                   r"(?:,(?:[01]\d|2[0-4]):[0-5]\d-(?:[01]\d|2[0-4]):[0-5]\d)*)$")
_LICZBA = re.compile(r"^-?\d+(?:\.\d+)?$")

_FORMATY: dict[str, tuple[re.Pattern, str]] = {
    "kod_pocztowy": (re.compile(r"^\d{2}-\d{3}$"), "kod pocztowy w formacie NN-NNN"),
    "kod_terc": (re.compile(r"^\d{7}$"), "7 cyfr TERYT TERC (z rodzajem gminy)"),
    "kod_simc": (re.compile(r"^\d{7}$"), "7 cyfr TERYT SIMC"),
    "kod_ulic": (re.compile(r"^\d{5}$"), "5 cyfr TERYT ULIC"),
    "telefon_kontaktowy": (re.compile(r"^(?:\+48)?\d{9}$"), "9 cyfr, opcjonalnie z +48"),
    "email_kontaktowy": (re.compile(r"^[^@\s]+@[^@\s]+\.[A-Za-z]{2,}$"), "adres e-mail"),
    "zdjecie_url": (re.compile(r"^https?://\S+$"), "adres URL zaczynający się od https://"),
    "osm_id": (re.compile(r"^(?:node|way)/\d+$"), "node/<liczba> albo way/<liczba>"),
    "dysponent_regon": (re.compile(r"^(?:\d{9}|\d{14})$"), "9 lub 14 cyfr"),
}


def _msg(poziom, kod, komunikat, wiersz=None, pole=None) -> Message:
    return Message(poziom=poziom, kod=kod, komunikat=komunikat, wiersz=wiersz, pole=pole)


def _data_ok(v: str) -> bool:
    try:
        date.fromisoformat(v)
        return bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}", v))
    except ValueError:
        return False


def _data_czas_ok(v: str) -> bool:
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}", v):
        return False
    try:
        datetime.fromisoformat(v)
        return True
    except ValueError:
        return False


def _odleglosc_m(a: tuple[float, float], b: tuple[float, float]) -> float:
    lat1, lon1, lat2, lon2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = math.sin((lat2 - lat1) / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2
    return 2 * 6371000 * math.asin(math.sqrt(h))


def _sprawdz_pole(pole: str, v: str, f, schema: Schema) -> tuple[str, str] | None:
    """(kod, opis) gdy wartość zła, inaczej None."""
    if f.typ == "słownik" and f.slownik:
        kody = [k for k, _ in schema.slowniki.get(f.slownik, [])]
        if v not in kody:
            return "WARTOSC_SPOZA_SLOWNIKA", f"„{v}” nie jest wartością ze słownika {f.slownik} ({', '.join(kody)})"
        return None
    if f.typ == "liczba dziesiętna":
        if not _LICZBA.match(v):
            return "ZLY_FORMAT", f"„{v}” nie jest liczbą z kropką dziesiętną"
        return None
    if f.typ == "liczba całkowita":
        if not re.fullmatch(r"-?\d+", v):
            return "ZLY_FORMAT", f"„{v}” nie jest liczbą całkowitą"
        return None
    if f.typ == "logiczny":
        if v not in ("true", "false"):
            return "ZLY_FORMAT", f"„{v}”: oczekiwane true albo false"
        return None
    if f.typ == "data":
        if not _data_ok(v):
            return "ZLY_FORMAT", f"„{v}” nie jest datą RRRR-MM-DD"
        return None
    if f.typ == "data i czas":
        if not _data_czas_ok(v):
            return "ZLY_FORMAT", f"„{v}” nie jest datą i czasem RRRR-MM-DDTGG:MM:SS"
        return None
    if f.typ == "godziny":
        if not _GODZ.match(v):
            return "ZLY_FORMAT", f"„{v}”: oczekiwane GG:MM-GG:MM, zamkniete albo X"
        return None
    if pole in _FORMATY:
        wzor, opis = _FORMATY[pole]
        if not wzor.match(v):
            return "ZLY_FORMAT", f"„{v}”: oczekiwane {opis}"
    return None


def _zalecane(nazwa: str, pole: str, puste: list[int], wszystkich: int) -> Message:
    ile = len(puste)
    tekst = "we wszystkich wierszach" if ile == wszystkich else f"w {ile} wierszach, m.in. {', '.join(map(str, puste[:5]))}"
    return _msg("ostrzezenie", "BRAK_POLA_ZALECANEGO", f"Brak pola zalecanego „{nazwa}” {tekst}.", None, pole)


def validate_records(records: list[RecordResult], schema: Schema) -> list[Message]:
    out: list[Message] = []
    rr = [r for r in records if not r.pominiety]
    if not rr:
        return out

    # 1) wymagalność
    godziny_puste: set[int] = set()
    for f in schema.pola:
        puste = [r.wiersz for r in rr if not r.record.get(f.pole, "")]
        if not puste:
            continue
        if f.wymagalnosc == "O":
            if len(puste) == len(rr):
                out.append(_msg("blad", "BRAK_POLA_OBOWIAZKOWEGO",
                                f"Brak pola obowiązkowego „{f.nazwa}” ({f.pole}). Wskaż kolumnę z tą informacją "
                                "albo ustaw wartość dla wszystkich AED w pliku.", None, f.pole))
            else:
                for w in puste:
                    out.append(_msg("blad", "BRAK_POLA_OBOWIAZKOWEGO", f"Puste pole obowiązkowe „{f.nazwa}”.", w, f.pole))
        elif f.wymagalnosc == "Z":
            if f.pole.startswith("godziny_") and all(r.record.get("dostepny_24_7") == "tak" for r in rr):
                continue
            if f.pole.startswith("godziny_"):
                godziny_puste.update(puste)
                continue
            out.append(_zalecane(f.nazwa, f.pole, puste, len(rr)))
    if godziny_puste:  # 8 pól godzin → jedno ostrzeżenie zamiast ośmiu prawie identycznych
        out.append(_zalecane("Godziny dostępności (godziny_pn…godziny_swieta)", "godziny_pn", sorted(godziny_puste), len(rr)))

    # 2) formaty i słowniki
    for r in rr:
        for f in schema.pola:
            v = r.record.get(f.pole, "")
            if not v:
                continue
            wynik = _sprawdz_pole(f.pole, v, f, schema)
            if wynik:
                kod, opis = wynik
                poziom = "blad" if f.wymagalnosc == "O" else "ostrzezenie"
                out.append(_msg(poziom, kod, f"{f.nazwa}: {opis}.", r.wiersz, f.pole))

    # 3) współrzędne: Polska i precyzja
    punkty: list[tuple[RecordResult, tuple[float, float]]] = []
    for r in rr:
        lat_s, lon_s = r.record.get("szerokosc_geograficzna", ""), r.record.get("dlugosc_geograficzna", "")
        if not (_LICZBA.match(lat_s) and _LICZBA.match(lon_s)):
            continue
        lat, lon = float(lat_s), float(lon_s)
        if not (LAT_MIN <= lat <= LAT_MAX and LON_MIN <= lon <= LON_MAX):
            out.append(_msg("blad", "POZA_POLSKA", f"Współrzędne {lat_s}, {lon_s} leżą poza Polską.", r.wiersz,
                            "szerokosc_geograficzna"))
            continue
        # max, nie min: „49.7851” obok „22.772605” to zwykle obcięte zera (49.785100), nie niska precyzja
        miejsca = max(len(s.split(".")[1]) if "." in s else 0 for s in (lat_s, lon_s))
        if miejsca < MIN_MIEJSC:
            out.append(_msg("ostrzezenie", "NISKA_PRECYZJA",
                            f"Współrzędne {lat_s}, {lon_s} mają {miejsca} miejsc po przecinku (zalecane co najmniej 6); "
                            "położenie może być niedokładne o kilkadziesiąt metrów.", r.wiersz, "szerokosc_geograficzna"))
        punkty.append((r, (lat, lon)))

    # 4) duplikaty
    for pole, kod, nazwa in (("id_aed", "DUPLIKAT_ID", "identyfikator AED"),
                             ("numer_seryjny", "DUPLIKAT_NR_SERYJNEGO", "numer seryjny")):
        pierwszy: dict[str, int] = {}
        for r in rr:
            v = r.record.get(pole, "")
            if not v:
                continue
            k = v.strip().lower() if pole == "numer_seryjny" else v
            if k in pierwszy:
                out.append(_msg("blad", kod, f"Powtórzony {nazwa} „{v}” (pierwszy raz w wierszu {pierwszy[k]}).",
                                r.wiersz, pole))
            else:
                pierwszy[k] = r.wiersz

    # 5) bliskie punkty (< 5 m), siatka ok. 11 m
    siatka: dict[tuple[int, int], list[int]] = defaultdict(list)
    for idx, (_, (lat, lon)) in enumerate(punkty):
        siatka[(int(lat * 10000), int(lon * 10000))].append(idx)
    for idx, (r, p) in enumerate(punkty):
        ki, kj = int(p[0] * 10000), int(p[1] * 10000)
        for di in (-1, 0, 1):
            for dj in (-1, 0, 1):
                for jdx in siatka.get((ki + di, kj + dj), []):
                    if jdx >= idx:
                        continue
                    r2, p2 = punkty[jdx]
                    d = _odleglosc_m(p, p2)
                    if d < BLISKO_M:
                        out.append(_msg("ostrzezenie", "BLISKIE_PUNKTY",
                                        f"Ten AED jest {d:.1f} m od AED z wiersza {r2.wiersz}. Sprawdź, czy to nie duplikat "
                                        "albo skopiowane współrzędne.", r.wiersz, "szerokosc_geograficzna"))
    return out
