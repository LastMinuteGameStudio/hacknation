"""A3: propozycja mapowania kolumn pliku → pola v0.5 (heurystyka + synonimy + analiza zawartości).

Kontrakt: każda kolumna dostaje dokładnie jedną propozycję (pole albo None). Jedno pole najwyżej raz.
Kolumna z geometrią (JSON z lat/long lub coordinates, WKT) → types.POLE_GEOMETRIA.
Adres w jednym polu → types.POLE_ADRES_PELNY, godziny w jednym polu → types.POLE_GODZINY.
Kolejność: poprzednie mapowanie (edycja zbioru) > nazwa kolumny (synonimy, podobieństwo) skorygowana zawartością
> sama zawartość. Przydział zachłanny od najwyższej pewności.
"""

from __future__ import annotations

import difflib
import json
import re
import unicodedata
from typing import Optional

from .synonimy import SYNONIMY
from .types import POLE_ADRES_PELNY, POLE_GEOMETRIA, POLE_GODZINY, MappingSuggestion, Schema, Table

POLA_SPECJALNE = (POLE_GEOMETRIA, POLE_ADRES_PELNY, POLE_GODZINY)


def norm(s: str) -> str:
    """Małe litery, bez polskich znaków, bez spacji, podkreśleń i interpunkcji (zostaje '/' dla 24/7)."""
    s = s.strip().lower().replace("ł", "l")
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9/@]", "", s)


def _slownik_synonimow(schema: Schema) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for f in schema.pola:
        out.setdefault(f.pole, []).extend([norm(f.pole), norm(f.nazwa)])
    for pole, syn in SYNONIMY.items():
        if pole in POLA_SPECJALNE or pole in out:
            out.setdefault(pole, []).extend(norm(s) for s in syn)
    return {p: [s for s in dict.fromkeys(v) if s] for p, v in out.items()}


# --- analiza zawartości ---------------------------------------------------------------------------

_LICZBA = re.compile(r"^[-+]?\d+(?:[.,]\d+)?$")
_KOD = re.compile(r"^\d{2}-\d{3}$")
_KOD_W_TEKSCIE = re.compile(r"\b\d{2}-\d{3}\b")
_GODZ = re.compile(r"\d{1,2}[:.]\d{2}\s*[-–]\s*\d{1,2}[:.]\d{2}|24\s*/\s*7|24\s*h|ca[lł]odob", re.I)
_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[a-z]{2,}$", re.I)
_TEL = re.compile(r"^\+?[\d\s()-]{9,16}$")
_WKT = re.compile(r"^\s*POINT\s*\(", re.I)
_PARA = re.compile(r"^\s*\(?\s*[-+]?\d{1,2}[.,]\d+\s*[,; ]\s*[-+]?\d{1,2}[.,]\d+\s*\)?\s*$")
_LOGICZNE = {"tak", "nie", "true", "false", "t", "n", "yes", "no", "0", "1", "prawda", "falsz"}


def _liczba(s: str) -> Optional[float]:
    s = s.strip()
    if not _LICZBA.match(s):
        return None
    return float(s.replace(",", "."))


def _czy_geometria(v: str) -> bool:
    v = v.strip()
    if _WKT.match(v) or _PARA.match(v):
        return True
    if v.startswith(("{", "[")):
        try:
            d = json.loads(v)
        except ValueError:
            return False
        tekst = json.dumps(d).lower()
        return "coordinates" in tekst or '"lat' in tekst or (isinstance(d, list) and len(d) >= 2)
    return False


def _analiza(wartosci: list[str]) -> tuple[Optional[str], float, str]:
    """Pole przypuszczalne na podstawie samej zawartości: (pole, pewność, powód)."""
    w = [v.strip() for v in wartosci if v and v.strip()]
    if not w:
        return None, 0.0, "pusta kolumna"
    n = len(w)

    def ulamek(pred) -> float:
        return sum(1 for v in w if pred(v)) / n

    if ulamek(_czy_geometria) >= 0.8:
        return POLE_GEOMETRIA, 0.85, "zawartość: geometria (współrzędne w jednej komórce)"
    liczby = [_liczba(v) for v in w]
    if all(x is not None for x in liczby):
        miejsca = [len(re.split(r"[.,]", v)[1]) if re.search(r"[.,]", v) else 0 for v in w]
        if sum(miejsca) / n >= 2:
            if all(49.0 <= x <= 55.0 for x in liczby):  # type: ignore[operator]
                return "szerokosc_geograficzna", 0.7, "zawartość: liczby 49–55"
            if all(14.0 <= x <= 24.2 for x in liczby):  # type: ignore[operator]
                return "dlugosc_geograficzna", 0.7, "zawartość: liczby 14–24,2"
    if ulamek(lambda v: bool(_KOD.match(v))) >= 0.8:
        return "kod_pocztowy", 0.75, "zawartość: kody NN-NNN"
    if ulamek(lambda v: bool(_KOD_W_TEKSCIE.search(v)) and bool(re.search(r"[A-Za-zÀ-ž]{3,}", v))) >= 0.6:
        return POLE_ADRES_PELNY, 0.7, "zawartość: adres z kodem pocztowym w jednym polu"
    if ulamek(lambda v: bool(_GODZ.search(v))) >= 0.6:
        return POLE_GODZINY, 0.6, "zawartość: godziny"
    if ulamek(lambda v: bool(_EMAIL.match(v))) >= 0.8:
        return "email_kontaktowy", 0.7, "zawartość: adresy e-mail"
    if ulamek(lambda v: bool(_TEL.match(v)) and len(re.sub(r"\D", "", v)) in (9, 11)) >= 0.8:
        return "telefon_kontaktowy", 0.5, "zawartość: numery telefonów"
    if ulamek(lambda v: bool(re.match(r"^(node|way)/\d+$", v))) >= 0.8:
        return "osm_id", 0.8, "zawartość: identyfikatory OSM"
    if ulamek(lambda v: bool(re.match(r"^https?://\S+\.(jpe?g|png)$", v, re.I))) >= 0.8:
        return "zdjecie_url", 0.6, "zawartość: adresy zdjęć"
    return None, 0.0, ""


def _stala(wartosci: list[str]) -> bool:
    w = [v.strip().lower() for v in wartosci if v and v.strip()]
    return len(w) >= 3 and len(set(w)) == 1


def _same_male_liczby(wartosci: list[str]) -> bool:
    w = [v.strip() for v in wartosci if v and v.strip()]
    return bool(w) and all(re.fullmatch(r"\d{1,6}", v) for v in w)


def _sr_dlugosc(wartosci: list[str]) -> float:
    w = [v.strip() for v in wartosci if v and v.strip()]
    return sum(len(v) for v in w) / len(w) if w else 0.0


# --- ocena nazwy ----------------------------------------------------------------------------------


def _wynik_nazwy(kol: str, syn: dict[str, list[str]]) -> list[tuple[float, str, str]]:
    k = norm(kol)
    if not k:
        return []
    wyniki: list[tuple[float, str, str]] = []
    for pole, lista in syn.items():
        best, powod = 0.0, ""
        for s in lista:
            if k == s:
                sc = 0.97 if s == norm(pole) else 0.92
                if sc > best:
                    best, powod = sc, "nazwa kolumny"
            elif len(s) >= 5 and len(k) >= 5 and (s in k or (k in s and len(k) / len(s) >= 0.7)):
                sc = 0.6 + 0.25 * min(len(s), len(k)) / max(len(s), len(k))
                if sc > best:
                    best, powod = sc, "nazwa kolumny (częściowo)"
            elif len(s) >= 5 and len(k) >= 5:
                r = difflib.SequenceMatcher(None, k, s).ratio()
                if r >= 0.85 and r * 0.85 > best:
                    best, powod = r * 0.85, "nazwa kolumny (podobna)"
        if best > 0:
            wyniki.append((best, pole, powod))
    return wyniki


# --- główna funkcja -------------------------------------------------------------------------------


def suggest_mapping(
    table: Table, schema: Schema, previous: Optional[dict[str, Optional[str]]] = None
) -> list[MappingSuggestion]:
    syn = _slownik_synonimow(schema)
    znane = set(schema.nazwy) | set(POLA_SPECJALNE)
    previous = previous or {}
    kandydaci: list[tuple[float, int, str, str]] = []  # (pewność, indeks kolumny, pole, powód)
    stale: set[int] = set()
    kolumny_wart: list[list[str]] = []

    for i, kol in enumerate(table.columns):
        wart = [r[i] for r in table.rows[:200] if i < len(r)]
        kolumny_wart.append(wart)
        if _stala(wart):
            stale.add(i)
        zaw_pole, zaw_pew, zaw_powod = _analiza(wart)
        oceny: dict[str, tuple[float, str]] = {}
        for sc, pole, powod in _wynik_nazwy(kol, syn):
            oceny[pole] = (sc, powod)

        # korekty zawartością
        if zaw_pole == POLE_GEOMETRIA:
            for p in ("szerokosc_geograficzna", "dlugosc_geograficzna"):
                oceny.pop(p, None)
            sc = max(oceny.get(POLE_GEOMETRIA, (0.0, ""))[0], 0.0)
            oceny[POLE_GEOMETRIA] = (max(sc, 0.9 if sc else zaw_pew), "zawartość: geometria" if not sc else "nazwa i zawartość")
        if zaw_pole == POLE_ADRES_PELNY:
            for p in ("nazwa_ulicy", "miejscowosc", "opis_lokalizacji", "nazwa_obiektu"):
                if p in oceny:
                    oceny[POLE_ADRES_PELNY] = (max(oceny[p][0], zaw_pew), "zawartość: pełny adres w jednym polu")
                    oceny.pop(p)
        if zaw_pole == POLE_GODZINY and "dostepny_24_7" in oceny and not any(
            _liczba(v) is None and len(v) > 12 for v in wart
        ):
            pass  # krótkie "24h"/"tak" zostają w dostepny_24_7
        elif zaw_pole == POLE_GODZINY and "dostepny_24_7" in oceny:
            oceny[POLE_GODZINY] = (oceny.pop("dostepny_24_7")[0], "zawartość: godziny w wolnym tekście")
        if "id_aed" in oceny or "id_zrodlowe" in oceny:
            # same liczby porządkowe nie są dobrym id_aed: lepiej id_zrodlowe, a id_aed wygenerujemy
            if _same_male_liczby(wart) and "id_aed" in oceny and oceny["id_aed"][1] != "nazwa kolumny":
                oceny["id_zrodlowe"] = oceny.pop("id_aed")
        if norm(kol) in ("lp", "lp.", "l.p", "nrlp", "liczbaporzadkowa"):
            kandydaci.append((0.99, i, "", "liczba porządkowa, nie importujemy"))
            continue
        niepuste = [v for v in wart if v.strip() and norm(v) not in ("parter", "piwnica", "suterena")]
        if niepuste and sum(1 for v in niepuste if _liczba(v) is not None) / len(niepuste) < 0.8:
            for p in ("szerokosc_geograficzna", "dlugosc_geograficzna", "kondygnacja", "przeglad_co_miesiecy"):
                oceny.pop(p, None)  # nazwa pasuje, ale w kolumnie nie ma liczb
        for p in ("status", "dostepnosc", "zabezpieczenie", "dysponent_typ", "cecha_ulicy", "dokladnosc_polozenia"):
            if p in oceny and _same_male_liczby(wart):
                oceny[p] = (0.3, "liczby zamiast kodów słownika (inne znaczenie kolumny?)")
        if "uwagi" in oceny and _sr_dlugosc(wart) > 300:
            oceny["uwagi"] = (0.2, "długi opis (np. marketingowy), domyślnie nie importujemy")
        if i in stale:
            for p in list(oceny):
                if p in ("nazwa_obiektu", "opis_lokalizacji", "id_zrodlowe", "id_aed", "nazwa_ulicy"):
                    oceny[p] = (min(oceny[p][0], 0.3), "ta sama wartość we wszystkich wierszach")
        if not oceny and zaw_pole and zaw_pole != POLE_GEOMETRIA:
            oceny[zaw_pole] = (zaw_pew, zaw_powod)
        elif zaw_pole and zaw_pole in oceny and zaw_pole not in POLA_SPECJALNE:
            sc, _ = oceny[zaw_pole]
            oceny[zaw_pole] = (min(0.99, sc + 0.05), "nazwa i zawartość kolumny")
        elif zaw_pole and zaw_pole not in oceny:
            oceny[zaw_pole] = (zaw_pew * 0.8, zaw_powod)

        for pole, (sc, powod) in oceny.items():
            kandydaci.append((sc, i, pole, powod))

    przydzial: dict[int, tuple[str, float, str]] = {}
    zajete: set[str] = set()
    # 1) poprzednie mapowanie (edycja zbioru) ma pierwszeństwo
    for i, kol in enumerate(table.columns):
        if kol in previous:
            pole = previous[kol]
            if pole is None:
                przydzial[i] = ("", 1.0, "poprzednie mapowanie: nie importuj")
            elif pole in znane and pole not in zajete:
                przydzial[i] = (pole, 1.0, "poprzednie mapowanie")
                zajete.add(pole)
    # 2) zachłannie od najwyższej pewności (remis: kolumna wcześniej w pliku)
    for sc, i, pole, powod in sorted(kandydaci, key=lambda t: (-t[0], t[1])):
        if i in przydzial or (pole and pole in zajete) or sc < 0.35:
            continue
        przydzial[i] = (pole, round(sc, 2), powod)
        if pole:
            zajete.add(pole)

    # 3) nazwa_obiektu jest obowiązkowa: gdy przypadła kolumnie stałej („Defibrylator”) albo nikomu,
    #    weź kolumnę z opis_lokalizacji o różnych wartościach (Krosno, Marki: „Lokalizacja” = nazwa obiektu)
    nazwa_i = next((i for i, (p, _, _) in przydzial.items() if p == "nazwa_obiektu"), None)
    opis_i = next((i for i, (p, _, _) in przydzial.items() if p == "opis_lokalizacji"), None)
    z_poprzedniego = {i for i, kol in enumerate(table.columns) if kol in previous}
    if ((nazwa_i is None or nazwa_i in stale) and opis_i is not None and opis_i not in stale
            and not ({nazwa_i, opis_i} & z_poprzedniego)):
        if nazwa_i is not None:
            del przydzial[nazwa_i]
        przydzial[opis_i] = ("nazwa_obiektu", 0.6, "kolumna lokalizacji jako nazwa obiektu (kolumna nazwy jest pusta lub stała)")
    for i in stale:
        if i not in przydzial:
            przydzial[i] = ("", 0.0, "ta sama wartość we wszystkich wierszach")

    out: list[MappingSuggestion] = []
    for i, kol in enumerate(table.columns):
        odrzucone = [k for k in kandydaci if k[1] == i]
        domyslny = ("", 0.0, max(odrzucone)[3] if odrzucone else "brak dopasowania")
        pole, sc, powod = przydzial.get(i, domyslny)
        out.append(MappingSuggestion(kolumna=kol, pole=pole or None, pewnosc=sc if pole else (sc if "poprzednie" in powod else 0.0),
                                     powod=powod))
    return out
