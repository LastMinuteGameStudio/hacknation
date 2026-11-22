"""Walidacja wykazu AED według wzorcowego zakresu v0.5.

Przeniesione z rdzenia TuAED (app/backend/aed_core/validate.py) i rozszerzone o kontrolę nagłówków,
bo w portalu sprawdzamy gotowy plik dostawcy, a nie wynik naszej konwersji:
- nagłówek: kolumny pól obowiązkowych muszą być (błąd), kolumny spoza zakresu są ostrzeżeniem,
  powtórzona kolumna to błąd,
- pola obowiązkowe (O): puste = błąd, zalecane (Z): jedno zbiorcze ostrzeżenie na pole,
- formaty i słowniki: błąd dla pól O, ostrzeżenie dla pozostałych,
- współrzędne w Polsce (błąd), niska precyzja (ostrzeżenie),
- powtórzony id_aed albo numer seryjny (błąd), punkty bliżej niż 5 m (ostrzeżenie).

Do wykazu zbiorczego trafia tylko wykaz bez błędów; ostrzeżenia go nie blokują.
"""

import math
import re
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime
from typing import Dict, List, Optional, Pattern, Set, Tuple

from mcod.resources.aed.reader import Tabela
from mcod.resources.aed.schema import Pole, Zakres

BLAD = "blad"
OSTRZEZENIE = "ostrzezenie"

LAT_MIN, LAT_MAX = 49.0, 54.9
LON_MIN, LON_MAX = 14.1, 24.2
BLISKO_M = 5.0
MIN_MIEJSC = 5
MAX_KOMUNIKATOW_NA_KOD = 20  # dalsze komunikaty tego samego rodzaju zliczamy w jednym

_GODZ = re.compile(r"^(?:X|zamkniete|(?:[01]\d|2[0-4]):[0-5]\d-(?:[01]\d|2[0-4]):[0-5]\d"
                   r"(?:,(?:[01]\d|2[0-4]):[0-5]\d-(?:[01]\d|2[0-4]):[0-5]\d)*)$")
_LICZBA = re.compile(r"^-?\d+(?:\.\d+)?$")

_FORMATY: Dict[str, Tuple[Pattern, str]] = {
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


@dataclass
class Komunikat:
    poziom: str  # blad | ostrzezenie
    kod: str
    komunikat: str
    wiersz: Optional[int] = None  # numer wiersza w pliku (nagłówek = 1)
    pole: Optional[str] = None

    def as_dict(self) -> Dict[str, object]:
        """Kształt błędu walidacji portalu (jak goodtables): TaskResult.message czyta klucz „message”."""
        tekst = self.komunikat if self.wiersz is None else f"Wiersz {self.wiersz}: {self.komunikat}"
        return {"code": f"aed-{self.kod.lower().replace('_', '-')}", "message": tekst,
                "row-number": self.wiersz, "column-name": self.pole}


def bledy(komunikaty: List[Komunikat]) -> List[Komunikat]:
    return [k for k in komunikaty if k.poziom == BLAD]


def _data_ok(v: str) -> bool:
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", v):
        return False
    try:
        date.fromisoformat(v)
        return True
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


def odleglosc_m(a: Tuple[float, float], b: Tuple[float, float]) -> float:
    lat1, lon1, lat2, lon2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = math.sin((lat2 - lat1) / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2
    return 2 * 6371000 * math.asin(math.sqrt(h))


def wspolrzedne(rekord: Dict[str, str]) -> Optional[Tuple[float, float]]:
    lat_s, lon_s = rekord.get("szerokosc_geograficzna", ""), rekord.get("dlugosc_geograficzna", "")
    if not (_LICZBA.match(lat_s or "") and _LICZBA.match(lon_s or "")):
        return None
    return float(lat_s), float(lon_s)


def sprawdz_wartosc(p: Pole, v: str, zakres: Zakres) -> Optional[Tuple[str, str]]:
    """(kod, opis) gdy wartość pola jest niezgodna z zakresem, inaczej None."""
    if p.typ == "słownik" and p.slownik:
        kody = zakres.kody(p.slownik)
        if v not in kody:
            return "WARTOSC_SPOZA_SLOWNIKA", f"„{v}” nie jest wartością ze słownika {p.slownik} ({', '.join(kody)})"
        return None
    if p.typ == "liczba dziesiętna":
        return None if _LICZBA.match(v) else ("ZLY_FORMAT", f"„{v}” nie jest liczbą z kropką dziesiętną")
    if p.typ == "liczba całkowita":
        return None if re.fullmatch(r"-?\d+", v) else ("ZLY_FORMAT", f"„{v}” nie jest liczbą całkowitą")
    if p.typ == "logiczny":
        return None if v in ("true", "false") else ("ZLY_FORMAT", f"„{v}”: oczekiwane true albo false")
    if p.typ == "data":
        return None if _data_ok(v) else ("ZLY_FORMAT", f"„{v}” nie jest datą RRRR-MM-DD")
    if p.typ == "data i czas":
        return None if _data_czas_ok(v) else ("ZLY_FORMAT", f"„{v}” nie jest datą i czasem RRRR-MM-DDTGG:MM:SS")
    if p.typ == "godziny":
        return None if _GODZ.match(v) else ("ZLY_FORMAT", f"„{v}”: oczekiwane GG:MM-GG:MM, zamkniete albo X")
    if p.pole in _FORMATY:
        wzor, opis = _FORMATY[p.pole]
        if not wzor.match(v):
            return "ZLY_FORMAT", f"„{v}”: oczekiwane {opis}"
    return None


def _naglowek(tabela: Tabela, zakres: Zakres) -> List[Komunikat]:
    out: List[Komunikat] = []
    znane = set(zakres.nazwy)
    widziane: Set[str] = set()
    for k in tabela.naglowek:
        if not k:
            continue
        if k in widziane:
            out.append(Komunikat(BLAD, "POWTORZONA_KOLUMNA", f"Kolumna „{k}” występuje w nagłówku więcej niż raz.", 1, k))
        widziane.add(k)
    brak = [p for p in zakres.obowiazkowe if p not in widziane]
    if brak:
        out.append(Komunikat(BLAD, "BRAK_KOLUMNY",
                             "Brak kolumn pól obowiązkowych zakresu v0.5: " + ", ".join(brak)
                             + ". Nagłówek musi używać nazw pól z zakresu (np. id_aed, szerokosc_geograficzna).", 1))
    obce = [k for k in tabela.naglowek if k and k not in znane]
    if obce:
        out.append(Komunikat(OSTRZEZENIE, "NIEZNANA_KOLUMNA",
                             "Kolumny spoza zakresu v0.5 zostaną pominięte w wykazie zbiorczym: " + ", ".join(obce) + ".", 1))
    return out


def _zalecane(p: Pole, puste: List[int], wszystkich: int) -> Komunikat:
    ile = len(puste)
    tekst = "we wszystkich wierszach" if ile == wszystkich else f"w {ile} wierszach, m.in. {', '.join(map(str, puste[:5]))}"
    return Komunikat(OSTRZEZENIE, "BRAK_POLA_ZALECANEGO", f"Brak pola zalecanego „{p.nazwa}” ({p.pole}) {tekst}.", None, p.pole)


def _ogranicz(komunikaty: List[Komunikat]) -> List[Komunikat]:
    """Najwyżej MAX_KOMUNIKATOW_NA_KOD komunikatów jednego rodzaju, reszta jako jeden zbiorczy."""
    ile: Dict[Tuple[str, str], int] = defaultdict(int)
    out: List[Komunikat] = []
    for k in komunikaty:
        ile[(k.poziom, k.kod)] += 1
        if ile[(k.poziom, k.kod)] <= MAX_KOMUNIKATOW_NA_KOD:
            out.append(k)
    for (poziom, kod), n in ile.items():
        if n > MAX_KOMUNIKATOW_NA_KOD:
            out.append(Komunikat(poziom, kod, f"… i jeszcze {n - MAX_KOMUNIKATOW_NA_KOD} podobnych ({kod})."))
    return out


def validate_table(tabela: Tabela, zakres: Zakres) -> List[Komunikat]:
    out = _naglowek(tabela, zakres)
    if not tabela.wiersze:
        out.append(Komunikat(BLAD, "BRAK_WIERSZY", "Wykaz nie zawiera żadnego AED."))
        return out
    obecne = set(tabela.naglowek)
    rr = list(zip(tabela.numery, tabela.wiersze))

    # 1) wymagalność (pole O bez kolumny zgłosił już nagłówek)
    godziny_puste: Set[int] = set()
    godziny_pole: Optional[Pole] = None
    for p in zakres.pola:
        puste = [nr for nr, w in rr if not w.get(p.pole, "")]
        if not puste:
            continue
        if p.wymagalnosc == "O" and p.pole in obecne:
            out.extend(Komunikat(BLAD, "BRAK_POLA_OBOWIAZKOWEGO", f"Puste pole obowiązkowe „{p.nazwa}” ({p.pole}).", nr, p.pole)
                       for nr in puste)
        elif p.wymagalnosc == "Z":
            if p.pole.startswith("godziny_"):
                if all(w.get("dostepny_24_7") == "tak" for _, w in rr):
                    continue
                godziny_puste.update(puste)
                godziny_pole = godziny_pole or p
                continue
            out.append(_zalecane(p, puste, len(rr)))
    if godziny_pole:
        out.append(Komunikat(OSTRZEZENIE, "BRAK_POLA_ZALECANEGO",
                             f"Brak godzin dostępności (godziny_pn…godziny_swieta) w {len(godziny_puste)} wierszach.",
                             None, "godziny_pn"))

    # 2) formaty i słowniki
    for nr, w in rr:
        for p in zakres.pola:
            v = w.get(p.pole, "")
            if not v:
                continue
            wynik = sprawdz_wartosc(p, v, zakres)
            if wynik:
                kod, opis = wynik
                out.append(Komunikat(BLAD if p.wymagalnosc == "O" else OSTRZEZENIE, kod, f"{p.nazwa}: {opis}.", nr, p.pole))

    # 3) współrzędne: Polska i precyzja
    punkty: List[Tuple[int, Tuple[float, float]]] = []
    for nr, w in rr:
        xy = wspolrzedne(w)
        if xy is None:
            continue
        lat, lon = xy
        if not (LAT_MIN <= lat <= LAT_MAX and LON_MIN <= lon <= LON_MAX):
            out.append(Komunikat(BLAD, "POZA_POLSKA", f"Współrzędne {lat}, {lon} leżą poza Polską.", nr,
                                 "szerokosc_geograficzna"))
            continue
        miejsca = max(len(s.split(".")[1]) if "." in s else 0
                      for s in (w["szerokosc_geograficzna"], w["dlugosc_geograficzna"]))
        if miejsca < MIN_MIEJSC:
            out.append(Komunikat(OSTRZEZENIE, "NISKA_PRECYZJA",
                                 f"Współrzędne mają {miejsca} miejsc po przecinku (zalecane co najmniej 6).", nr,
                                 "szerokosc_geograficzna"))
        punkty.append((nr, xy))

    # 4) duplikaty w wykazie dostawcy
    for pole, kod, nazwa in (("id_aed", "DUPLIKAT_ID", "identyfikator AED"),
                             ("numer_seryjny", "DUPLIKAT_NR_SERYJNEGO", "numer seryjny")):
        pierwszy: Dict[str, int] = {}
        for nr, w in rr:
            v = w.get(pole, "")
            if not v:
                continue
            k = v.strip().lower() if pole == "numer_seryjny" else v
            if k in pierwszy:
                out.append(Komunikat(BLAD, kod, f"Powtórzony {nazwa} „{v}” (pierwszy raz w wierszu {pierwszy[k]}).", nr, pole))
            else:
                pierwszy[k] = nr

    # 5) bliskie punkty (< 5 m), siatka ok. 11 m
    siatka: Dict[Tuple[int, int], List[int]] = defaultdict(list)
    for i, (_, (lat, lon)) in enumerate(punkty):
        siatka[(int(lat * 10000), int(lon * 10000))].append(i)
    for i, (nr, p) in enumerate(punkty):
        ki, kj = int(p[0] * 10000), int(p[1] * 10000)
        for di in (-1, 0, 1):
            for dj in (-1, 0, 1):
                for j in siatka.get((ki + di, kj + dj), []):
                    if j >= i:
                        continue
                    d = odleglosc_m(p, punkty[j][1])
                    if d < BLISKO_M:
                        out.append(Komunikat(OSTRZEZENIE, "BLISKIE_PUNKTY",
                                             f"AED jest {d:.1f} m od AED z wiersza {punkty[j][0]}; sprawdź, czy to nie duplikat.",
                                             nr, "szerokosc_geograficzna"))
    return _ogranicz(out)
