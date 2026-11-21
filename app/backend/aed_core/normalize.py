"""A4: normalizacja wartości do formatu v0.5 + pola stałe i domyślne.

Zakres: liczby (przecinek dziesiętny), współrzędne (zamiana lat/lon per wiersz, geometria JSON/WKT/„lat, lon”),
daty → ISO 8601, wartości logiczne → true/false, słowniki (synonimy wartości → kody), godziny („24h”,
opening_hours, „pn-pt 8-16”, „dni powszednie 7:00-17:00”) → dostepny_24_7 + godziny_pn..swieta,
adres w jednym polu → cecha / ulica / nr / kod / miejscowość, telefon → 9 cyfr (+48), kody TERYT jako tekst.
Pola stałe: dysponent_* z Provider, zrodlo_danych, data_aktualizacji, wartosci_stale (`fixed`).
Domyślne + ostrzeżenia: id_aed (WYGENEROWANO_ID), status=nieznany (DOMYSLNY_STATUS),
data_weryfikacji=today (DOMYSLNA_DATA_WERYFIKACJI). Gdy pole nie ma kolumny ani wartości stałej, komunikat jest
jeden na plik (wiersz=None, w pierwszym rekordzie); gdy kolumna jest, a komórka pusta: komunikat per wiersz.
Geokodowanie (A7), gdy brak współrzędnych, a jest adres: najwyżej 200 adresów na plik, 8 równolegle.
"""

from __future__ import annotations

import hashlib
import json
import re
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timedelta
from typing import Optional

from .mapping import norm
from .synonimy import LOGICZNE, WARTOSCI
from .types import (
    POLE_ADRES_PELNY,
    POLE_GEOMETRIA,
    POLE_GODZINY,
    AddressQuery,
    Geocoder,
    GeoResult,
    Message,
    Provider,
    RecordResult,
    Schema,
    Table,
)

MAX_GEOKODOWAN = 200
GEOKODOWANIE_ROWNOLEGLE = 8
DNI = ["godziny_pn", "godziny_wt", "godziny_sr", "godziny_cz", "godziny_pt", "godziny_so", "godziny_nd"]
POLA_GODZIN = DNI + ["godziny_swieta"]

_WARTOSCI_N = {s: {norm(k): v for k, v in d.items()} for s, d in WARTOSCI.items()}
_LOGICZNE_N = {norm(k): v for k, v in LOGICZNE.items()}


# --- proste formaty -------------------------------------------------------------------------------


def _czysc(v: str) -> str:
    v = (v or "").replace(" ", " ").strip()
    if v.startswith("'"):  # apostrof z Excela wymuszający tekst
        v = v[1:].strip()
    v = re.sub(r"\s+", " ", v)
    return "" if v.lower() in ("null", "none", "nan", "brak", "-", "--", "b.d.", "bd", "n/a") else v


def _liczba_tekst(v: str) -> str:
    """Liczba dziesiętna jako tekst z kropką, z precyzją z pliku."""
    s = v.strip().replace(" ", "")
    if re.fullmatch(r"[-+]?\d+,\d+", s):
        s = s.replace(",", ".")
    return s.lstrip("+")


def _float(v: str) -> Optional[float]:
    try:
        return float(_liczba_tekst(v))
    except ValueError:
        return None


def _data(v: str) -> Optional[str]:
    v = v.strip()
    m = re.match(r"^(\d{4})[-./](\d{1,2})[-./](\d{1,2})(?:[ T].*)?$", v)
    if m:
        y, mo, d = m.groups()
    else:
        m = re.match(r"^(\d{1,2})[-./](\d{1,2})[-./](\d{4})(?:[ T].*)?$", v)
        if m:
            d, mo, y = m.groups()
        elif re.fullmatch(r"\d{5}(\.0+)?", v) and 20000 <= float(v) <= 80000:  # numer seryjny daty z Excela
            return (date(1899, 12, 30) + timedelta(days=int(float(v)))).isoformat()
        else:
            return None
    try:
        return date(int(y), int(mo), int(d)).isoformat()
    except ValueError:
        return None


def _telefon(v: str) -> str:
    pierwszy = re.split(r"[,;/]| lub | i ", v)[0]
    cyfry = re.sub(r"\D", "", pierwszy)
    if cyfry.startswith("0048"):
        cyfry = cyfry[2:]
    if len(cyfry) == 11 and cyfry.startswith("48"):
        return "+" + cyfry
    if len(cyfry) == 10 and cyfry.startswith("0"):
        cyfry = cyfry[1:]
    if len(cyfry) == 9:
        return cyfry
    return v


def _kod_pocztowy(v: str) -> str:
    c = re.sub(r"\D", "", v)
    if len(c) == 4:  # zero wiodące zgubione w Excelu
        c = "0" + c
    return f"{c[:2]}-{c[2:]}" if len(c) == 5 else v


def _cyfry(v: str, dlugosc: Optional[int] = None) -> str:
    s = v.strip()
    if re.fullmatch(r"\d+\.0+", s):
        s = s.split(".")[0]
    if not re.fullmatch(r"[\d\s-]+", s):
        return v
    c = re.sub(r"\D", "", s)
    if dlugosc and len(c) < dlugosc:
        c = c.zfill(dlugosc)
    return c


def _slownik(v: str, slownik: str, schema: Schema) -> str:
    kody = [k for k, _ in schema.slowniki.get(slownik, [])]
    if v in kody:
        return v
    n = norm(v)
    syn = _WARTOSCI_N.get(slownik, {})
    for k in kody:
        if n == norm(k):
            return k
    if n in syn:
        return syn[n]
    # „Nie (dostęp: pon. - pt 8-16)”, „Wewnątrz budynku, gabinet” → pierwsze słowo / prefiks
    pierwsze = norm(re.split(r"[\s(,;:]", v.strip(), maxsplit=1)[0])
    if pierwsze in syn:
        return syn[pierwsze]
    for k in kody:
        if pierwsze == norm(k):
            return k
    return v


def _logiczny(v: str) -> str:
    n = norm(v)
    if n in _LOGICZNE_N:
        return _LOGICZNE_N[n]
    for k in sorted(_LOGICZNE_N, key=len, reverse=True):
        if len(k) >= 6 and n.startswith(k):
            return _LOGICZNE_N[k]
    pierwsze = norm(re.split(r"[\s(,;:]", v.strip(), maxsplit=1)[0])
    return _LOGICZNE_N.get(pierwsze, v)


def _calkowita(v: str) -> str:
    n = norm(v)
    if n in ("parter", "p", "0"):
        return "0"
    if n in ("piwnica", "suterena"):
        return "-1"
    m = re.fullmatch(r"\s*([-+]?\d+)(?:[.,]0+)?\s*(?:pietro|p\.?)?\s*", v.lower().replace("piętro", "pietro"))
    return str(int(m.group(1))) if m else v


# --- godziny --------------------------------------------------------------------------------------

_DZIEN = [
    (0, r"mo|pn|pon(?:iedzia[lł]ek|iedzia[lł]ku)?"),
    (1, r"tu|wt|wto(?:rek|rku)?"),
    (2, r"we|[sś]r|[sś]ro(?:da|dy)?"),
    (3, r"th|cz|czw(?:artek|artku)?"),
    (4, r"fr|pt|pi[aą](?:tek|tku)?"),
    (5, r"sa|so|sob(?:ota|oty)?"),
    (6, r"su|nd|ndz|nie(?:dz|dziela|dzieli)?"),
    (7, r"ph|[sś]wi[eę]ta|dni [sś]wi[aą]teczne"),
]
_DZIEN_RE = "|".join(f"(?P<d{i}>{p})" for i, p in _DZIEN)
_DZIEN_SLOWO = re.compile(r"(?<![a-ząćęłńóśźż])(?:" + "|".join(p for _, p in _DZIEN) + r")\.?(?![a-ząćęłńóśźż])")
_CZAS = r"(\d{1,2})(?:[:.;](\d{2}))?"
_PRZEDZIAL = re.compile(_CZAS + r"\s*(?:-|–|do)\s*" + _CZAS)
_24 = re.compile(r"24\s*/\s*7|24\s*h|ca[lł]odob|ca[lł][aą] dob|non\s*-?stop|00:00\s*-\s*24:00", re.I)
_ZAMKN = re.compile(r"off|closed|zamkni[eę]t|nieczynn|nieczynne", re.I)


def _dzien_idx(tok: str) -> Optional[int]:
    m = re.fullmatch(_DZIEN_RE, tok.strip().rstrip("."), re.I)
    if not m:
        return None
    for i, _ in _DZIEN:
        if m.group(f"d{i}"):
            return i
    return None


def _dni_w_segmencie(seg: str) -> Optional[list[int]]:
    s = seg.lower()
    if re.search(r"dni powszedni|dni robocz|w dni robocze|robocze", s):
        return [0, 1, 2, 3, 4]
    if re.search(r"weekend", s):
        return [5, 6]
    if re.search(r"codziennie|ka[zż]dego dnia|wszystkie dni", s):
        return list(range(7))
    tokeny = [(m.start(), m.end(), _dzien_idx(m.group(0))) for m in _DZIEN_SLOWO.finditer(s)]
    tokeny = [t for t in tokeny if t[2] is not None]
    if not tokeny:
        return None
    dni: list[int] = []
    j = 0
    while j < len(tokeny):
        a = tokeny[j]
        if j + 1 < len(tokeny):
            b = tokeny[j + 1]
            miedzy = s[a[1]:b[0]]
            if re.fullmatch(r"\s*(?:-|–|do)\s*", miedzy) and a[2] < 7 and b[2] < 7:
                lo, hi = a[2], b[2]
                dni.extend(range(lo, hi + 1) if lo <= hi else list(range(lo, 7)) + list(range(0, hi + 1)))
                j += 2
                continue
        dni.append(a[2])  # type: ignore[arg-type]
        j += 1
    return sorted(set(dni))


def _hhmm(h: str, m: Optional[str]) -> Optional[str]:
    hh, mm = int(h), int(m or 0)
    if hh > 24 or mm > 59 or (hh == 24 and mm):
        return None
    return f"{hh:02d}:{mm:02d}"


def parsuj_godziny(tekst: str) -> Optional[dict[str, str]]:
    """Godziny w jednym polu → {dostepny_24_7, godziny_*}. None, gdy nie da się zrozumieć."""
    t = tekst.strip()
    if not t:
        return None
    if _24.search(t) and not _PRZEDZIAL.search(_24.sub("", t)):
        out = {p: "X" for p in POLA_GODZIN}
        out["dostepny_24_7"] = "tak"
        return out
    t = re.sub(r"(\d{1,2});(\d{2})", r"\1:\2", t)  # „7;00” to literówka zamiast „7:00”, nie separator
    wynik: dict[int, str] = {}
    segmenty = [s for s in re.split(r"[;\n|]|,(?!\d)", t) if s.strip()]
    znaleziono = False
    for seg in segmenty:
        seg_c = seg
        przedzialy = []
        for m in _PRZEDZIAL.finditer(seg_c):
            od, do = _hhmm(m.group(1), m.group(2)), _hhmm(m.group(3), m.group(4))
            if od and do:
                przedzialy.append(f"{od}-{do}")
        dni = _dni_w_segmencie(_PRZEDZIAL.sub(" ", seg_c))
        if przedzialy:
            wartosc = ",".join(przedzialy) if len(przedzialy) > 1 else przedzialy[0]
            for d in (dni if dni is not None else list(range(7))):
                wynik[d] = wartosc
            znaleziono = True
        elif dni is not None and _ZAMKN.search(seg_c):
            for d in dni:
                wynik[d] = "zamkniete"
            znaleziono = True
    if not znaleziono:
        # tekst w środku zdania („…7;00 do 20;00” bez dni) albo zupełnie wolny tekst
        return None
    out = {}
    for i, pole in enumerate(POLA_GODZIN):
        if i in wynik:
            out[pole] = wynik[i]
        elif i < 7:
            out[pole] = "zamkniete"
    if all(out.get(p) == "00:00-24:00" for p in DNI):
        out = {p: "X" for p in POLA_GODZIN}
        out["dostepny_24_7"] = "tak"
    else:
        out["dostepny_24_7"] = "nie"
    return out


def _godziny_pola(v: str) -> str:
    if v.upper() == "X":
        return "X"
    if _ZAMKN.search(v):
        return "zamkniete"
    r = [f"{_hhmm(m.group(1), m.group(2))}-{_hhmm(m.group(3), m.group(4))}" for m in _PRZEDZIAL.finditer(v)
         if _hhmm(m.group(1), m.group(2)) and _hhmm(m.group(3), m.group(4))]
    if _24.search(v):
        return "00:00-24:00"
    return ",".join(r) if r else v


# --- geometria ------------------------------------------------------------------------------------


def parsuj_geometrie(v: str) -> Optional[tuple[str, str]]:
    """→ (szerokość, długość) jako tekst z precyzją z pliku. GeoJSON [lon,lat], {lat,long}, WKT, „lat, lon”."""
    s = v.strip()
    m = re.match(r"^\s*(?:SRID=\d+;)?POINT\s*Z?\s*\(\s*([-+\d.,]+)\s+([-+\d.,]+)", s, re.I)
    if m:
        return _liczba_tekst(m.group(2)), _liczba_tekst(m.group(1))
    if s.startswith(("{", "[")):
        try:
            d = json.loads(s, parse_float=str, parse_int=str)
        except ValueError:
            return None
        return _z_json(d)
    m = re.fullmatch(r"\(?\s*([-+]?\d{1,3}(?:\.\d+)?)\s*[,; ]\s*([-+]?\d{1,3}(?:\.\d+)?)\s*\)?", s)
    if m:
        return m.group(1), m.group(2)  # w tekście zwykle „lat, lon”; zamianę wykryje _wspolrzedne
    m = re.fullmatch(r"\(?\s*([-+]?\d{1,3},\d+)\s*[; ]\s*([-+]?\d{1,3},\d+)\s*\)?", s)
    if m:
        return _liczba_tekst(m.group(1)), _liczba_tekst(m.group(2))
    return None


def _z_json(d) -> Optional[tuple[str, str]]:
    if isinstance(d, dict):
        low = {k.lower(): v for k, v in d.items()}
        lat = next((low[k] for k in ("lat", "latitude", "y", "szerokosc") if k in low), None)
        lon = next((low[k] for k in ("long", "lon", "lng", "longitude", "x", "dlugosc") if k in low), None)
        if lat is not None and lon is not None and not isinstance(lat, (dict, list)):
            return str(lat), str(lon)
        for k in ("coordinates", "geometry", "point", "location"):
            if k in low:
                r = _z_json(low[k])
                if r:
                    return r
        return None
    if isinstance(d, list):
        if len(d) >= 2 and all(isinstance(x, str) for x in d[:2]):
            return d[1], d[0]  # GeoJSON: [lon, lat]
        if d and isinstance(d[0], (list, dict)):
            return _z_json(d[0])
    return None


# --- adres ----------------------------------------------------------------------------------------

_CECHY = {
    "ul": "ulica", "ulica": "ulica", "al": "aleja", "aleja": "aleja", "aleje": "aleja", "pl": "plac",
    "plac": "plac", "os": "osiedle", "osiedle": "osiedle", "rondo": "rondo", "skwer": "skwer",
    "bulw": "bulwar", "bulwar": "bulwar",
}
_CECHA_RE = re.compile(r"^(ul|ulica|al|aleja|aleje|pl|plac|os|osiedle|rondo|skwer|bulw|bulwar)(?:\.+\s*|\s+)", re.I)
_NR_RE = re.compile(r"^(.*?\D)\s+(\d+[a-zA-Z]?(?:\s*[/-]\s*\d+[a-zA-Z]?)?)\s*(?:(?:lok\.?|m\.?)\s*(\d+\w*))?$")


def _ulica_z_cecha(tekst: str) -> tuple[str, str]:
    t = tekst.strip()
    m = _CECHA_RE.match(t)
    if m:
        return _CECHY[m.group(1).lower()], t[m.end():].strip()
    return "", t


def parsuj_adres(v: str) -> Optional[dict[str, str]]:
    """„ul. Jasna 5, 38-400 Krosno” → {cecha_ulicy, nazwa_ulicy, nr_budynku, nr_lokalu, kod_pocztowy, miejscowosc}."""
    t = re.sub(r"\s+", " ", v).strip().strip(",")
    if not t:
        return None
    out: dict[str, str] = {}
    m = re.search(r"\b(\d{2})\s*-\s*(\d{3})\b", t)
    if m:
        out["kod_pocztowy"] = f"{m.group(1)}-{m.group(2)}"
        po = t[m.end():].strip(" ,")
        przed = t[:m.start()].strip(" ,")
        if po:
            miasto, _, reszta = po.partition(",")
            out["miejscowosc"] = miasto.strip()
            przed = ", ".join(x for x in (przed, reszta.strip()) if x)
        t = przed
    czesci = [c.strip() for c in t.split(",") if c.strip()]
    if "miejscowosc" not in out and len(czesci) >= 2:
        # „Krosno, ul. Jasna 5” albo „ul. Jasna 5, Krosno”: miejscowość to część bez cechy i bez numeru
        for idx in (len(czesci) - 1, 0):
            c = czesci[idx]
            if not _CECHA_RE.match(c) and not re.search(r"\d", c):
                out["miejscowosc"] = c
                czesci.pop(idx)
                break
    if "miejscowosc" not in out and len(czesci) == 1:
        # „Krosno ul. Jasna 5”
        m2 = re.search(r"\s(ul|al|pl|os)\.", czesci[0], re.I)
        if m2:
            out["miejscowosc"] = czesci[0][:m2.start()].strip()
            czesci = [czesci[0][m2.start():].strip()]
    if czesci:
        ulica = czesci[0]
        cecha, ulica = _ulica_z_cecha(ulica)
        m3 = _NR_RE.match(ulica)
        if m3:
            ulica, nr, lok = m3.group(1).strip(), m3.group(2).replace(" ", ""), m3.group(3)
            out["nr_budynku"] = nr
            if lok:
                out["nr_lokalu"] = lok
        elif re.fullmatch(r"\d+[a-zA-Z]?(?:/\d+)?", ulica):
            out["nr_budynku"], ulica = ulica, ""
        if ulica:
            out["nazwa_ulicy"] = ulica
        if cecha:
            out["cecha_ulicy"] = cecha
        if len(czesci) > 1 and "nr_lokalu" not in out:
            reszta = " ".join(czesci[1:])
            mlok = re.fullmatch(r"(?:lok\.?|m\.?|lokal)\s*(\d+\w*)", reszta, re.I)
            if mlok:
                out["nr_lokalu"] = mlok.group(1)
    if not out.get("nazwa_ulicy") and not out.get("miejscowosc"):
        return None
    return out


# --- id_aed ---------------------------------------------------------------------------------------


def _skrot(rec: dict[str, str]) -> str:
    if rec.get("numer_seryjny"):
        zrodlo = "sn:" + norm(rec["numer_seryjny"])
    else:
        lat, lon = _float(rec.get("szerokosc_geograficzna", "")), _float(rec.get("dlugosc_geograficzna", ""))
        wsp = f"{lat:.4f},{lon:.4f}" if lat is not None and lon is not None else ""
        zrodlo = f"{wsp}|{norm(rec.get('nazwa_obiektu', ''))}"
    return hashlib.sha1(zrodlo.encode("utf-8")).hexdigest()[:6]


def _prefiks(rec: dict[str, str], provider: Provider) -> str:
    terc = re.sub(r"\D", "", rec.get("kod_terc", ""))
    if len(terc) in (6, 7):
        return terc
    if provider.slug:
        return provider.slug
    return re.sub(r"[^a-z0-9]+", "-", norm(provider.nazwa))[:20] or "aed"


# --- formatowanie jednego pola --------------------------------------------------------------------


def formatuj(pole: str, v: str, schema: Schema) -> str:
    """Wartość z pliku → format v0.5 (bez walidacji; nieznane wartości zostają, validate je zgłosi)."""
    v = _czysc(v)
    if not v:
        return ""
    try:
        f = schema.pole(pole)
    except KeyError:
        return v
    if pole in ("szerokosc_geograficzna", "dlugosc_geograficzna"):
        return _liczba_tekst(v)
    if f.typ == "liczba całkowita":
        return _calkowita(v)
    if f.typ == "logiczny":
        return _logiczny(v)
    if f.typ == "słownik" and f.slownik:
        return _slownik(v, f.slownik, schema)
    if f.typ == "data":
        return _data(v) or v
    if f.typ == "godziny":
        return _godziny_pola(v)
    if pole == "kod_pocztowy":
        return _kod_pocztowy(v)
    if pole == "telefon_kontaktowy":
        return _telefon(v)
    if pole == "email_kontaktowy":
        return v.lower().removeprefix("mailto:")
    if pole == "kod_terc":
        return _cyfry(v)
    if pole == "kod_simc":
        return _cyfry(v, 7)
    if pole == "kod_ulic":
        return _cyfry(v, 5)
    if pole == "dysponent_regon":
        return _cyfry(v)
    if pole == "id_aed" or pole == "id_zrodlowe":
        return v[:-2] if re.fullmatch(r"\d+\.0", v) else v
    return v


# --- główna funkcja -------------------------------------------------------------------------------


def _msg(poziom, kod, komunikat, wiersz=None, pole=None) -> Message:
    return Message(poziom=poziom, kod=kod, komunikat=komunikat, wiersz=wiersz, pole=pole)


def _wspolrzedne(rec: dict[str, str], wiersz: int, msgs: list[Message]) -> None:
    lat, lon = _float(rec["szerokosc_geograficzna"]), _float(rec["dlugosc_geograficzna"])
    if lat is None or lon is None:
        return
    if 14.0 <= lat <= 24.2 and 49.0 <= lon <= 55.0:
        rec["szerokosc_geograficzna"], rec["dlugosc_geograficzna"] = rec["dlugosc_geograficzna"], rec["szerokosc_geograficzna"]
        msgs.append(_msg("ostrzezenie", "ZAMIENIONE_WSPOLRZEDNE",
                         "Szerokość i długość geograficzna były zamienione miejscami; poprawiliśmy.", wiersz,
                         "szerokosc_geograficzna"))


def normalize_table(
    table: Table,
    mapping: dict[str, Optional[str]],
    schema: Schema,
    provider: Provider,
    today: date,
    geocoder: Optional[Geocoder] = None,
    fixed: Optional[dict[str, str]] = None,  # wartosci_stale z /walidacja: pole -> wartość dla całego pliku
) -> list[RecordResult]:
    fixed = {k: v for k, v in (fixed or {}).items() if v not in (None, "") and k in schema.nazwy}
    nazwy = schema.nazwy
    kol_idx = {c: i for i, c in enumerate(table.columns)}
    mapa = [(kol_idx[k], p) for k, p in mapping.items() if p and k in kol_idx]
    zmapowane = {p for _, p in mapa}
    teraz = datetime.now().replace(microsecond=0)
    data_akt = datetime.combine(today, teraz.time()).isoformat()

    wyniki: list[RecordResult] = []
    for i, row in enumerate(table.rows):
        if not any((c or "").strip() for c in row):
            continue
        wiersz = table.header_row + 1 + i
        rec = {p: "" for p in nazwy}
        msgs: list[Message] = []
        godziny_tekst = ""
        for idx, pole in mapa:
            surowe = _czysc(row[idx] if idx < len(row) else "")
            if not surowe:
                continue
            if pole == POLE_GEOMETRIA:
                g = parsuj_geometrie(surowe)
                if g:
                    rec["szerokosc_geograficzna"] = rec["szerokosc_geograficzna"] or g[0]
                    rec["dlugosc_geograficzna"] = rec["dlugosc_geograficzna"] or g[1]
                else:
                    msgs.append(_msg("ostrzezenie", "ZLY_FORMAT", f"Nie rozpoznano geometrii: „{surowe[:60]}”.",
                                     wiersz, "szerokosc_geograficzna"))
            elif pole == POLE_ADRES_PELNY:
                a = parsuj_adres(surowe)
                if a:
                    for k, v in a.items():
                        if not rec[k]:
                            rec[k] = v
                    msgs.append(_msg("info", "ROZBITO_ADRES", f"Adres „{surowe}” rozbito na części.", wiersz, "nazwa_ulicy"))
                else:
                    msgs.append(_msg("ostrzezenie", "NIE_ROZBITO_ADRESU",
                                     f"Nie udało się rozbić adresu „{surowe}”; uzupełnij ulicę i miejscowość.", wiersz,
                                     "nazwa_ulicy"))
            elif pole == POLE_GODZINY:
                godziny_tekst = surowe
            else:
                rec[pole] = formatuj(pole, surowe, schema)

        # wartości stałe (nie nadpisują niepustych wartości z kolumn)
        for p, v in fixed.items():
            if not rec[p]:
                rec[p] = formatuj(p, v, schema)

        # godziny w jednym polu
        if godziny_tekst:
            g = parsuj_godziny(godziny_tekst)
            if g:
                for k, v in g.items():
                    if k == "dostepny_24_7":
                        if not rec[k] or v == "tak":  # „całodobowo” w godzinach wygrywa z kolumną dostępności
                            rec[k] = v
                    elif not rec[k]:
                        rec[k] = v
            else:
                rec["uwagi"] = "; ".join(x for x in (rec["uwagi"], f"Godziny: {godziny_tekst}") if x)
                msgs.append(_msg("ostrzezenie", "NIEZROZUMIALE_GODZINY",
                                 f"Nie zrozumieliśmy godzin „{godziny_tekst[:80]}”; przenieśliśmy je do uwag.", wiersz,
                                 "godziny_pn"))
        if rec["dostepny_24_7"] == "tak":
            for p in POLA_GODZIN:
                rec[p] = "X"

        # adres: cecha w nazwie ulicy, brak ulicy
        if rec["nazwa_ulicy"]:
            cecha, ul = _ulica_z_cecha(rec["nazwa_ulicy"])
            if cecha and ul:
                rec["nazwa_ulicy"] = ul
                rec["cecha_ulicy"] = rec["cecha_ulicy"] or cecha
        if rec["nr_budynku"] and rec["nazwa_ulicy"] and rec["nazwa_ulicy"].endswith(" " + rec["nr_budynku"]):
            rec["nazwa_ulicy"] = rec["nazwa_ulicy"][: -len(rec["nr_budynku"]) - 1].strip()
        if not rec["nazwa_ulicy"] and rec["miejscowosc"]:
            rec["nazwa_ulicy"] = rec["miejscowosc"]
            msgs.append(_msg("info", "ULICA_Z_MIEJSCOWOSCI",
                             f"Brak ulicy: w polu ulicy wpisano miejscowość „{rec['miejscowosc']}” (zasada zakresu v0.5).",
                             wiersz, "nazwa_ulicy"))

        _wspolrzedne(rec, wiersz, msgs)

        # pola stałe
        rec["dysponent_nazwa"] = rec["dysponent_nazwa"] or provider.nazwa
        rec["dysponent_typ"] = rec["dysponent_typ"] or formatuj("dysponent_typ", provider.typ or "", schema)
        if provider.telefon and not rec["telefon_kontaktowy"]:
            rec["telefon_kontaktowy"] = formatuj("telefon_kontaktowy", provider.telefon, schema)
        if provider.email and not rec["email_kontaktowy"]:
            rec["email_kontaktowy"] = formatuj("email_kontaktowy", provider.email, schema)
        rec["zrodlo_danych"] = rec["zrodlo_danych"] or "dysponent"
        rec["data_aktualizacji"] = data_akt

        wyniki.append(RecordResult(wiersz=wiersz, record=rec, messages=msgs))

    _geokoduj(wyniki, geocoder)
    _domyslne(wyniki, zmapowane, set(fixed), provider, today)
    return wyniki


def _domyslne(wyniki: list[RecordResult], zmapowane: set[str], stale: set[str], provider: Provider, today: date) -> None:
    if not wyniki:
        return
    plik: list[Message] = []

    def domyslna(pole: str, wartosc_fn, kod: str, tekst_plik: str, tekst_wiersz: str) -> None:
        cale = pole not in zmapowane and pole not in stale
        ile = 0
        for r in wyniki:
            if r.record[pole]:
                continue
            r.record[pole] = wartosc_fn(r)
            ile += 1
            if not cale:
                r.messages.append(_msg("ostrzezenie", kod, tekst_wiersz, r.wiersz, pole))
        if cale and ile:
            plik.append(_msg("ostrzezenie", kod, tekst_plik, None, pole))

    domyslna("status", lambda r: "nieznany", "DOMYSLNY_STATUS",
             "Plik nie ma kolumny ze stanem urządzenia: ustawiliśmy status „nieznany” dla wszystkich AED.",
             "Brak statusu: ustawiliśmy „nieznany”.")
    domyslna("data_weryfikacji", lambda r: today.isoformat(), "DOMYSLNA_DATA_WERYFIKACJI",
             f"Plik nie ma daty weryfikacji: ustawiliśmy datę wgrania ({today.isoformat()}).",
             f"Brak daty weryfikacji: ustawiliśmy datę wgrania ({today.isoformat()}).")

    # id_aed: stabilny skrót z treści rekordu, kolizje w pliku → -2, -3
    uzyte = {r.record["id_aed"] for r in wyniki if r.record["id_aed"]}

    def nowe_id(r: RecordResult) -> str:
        baza = f"{_prefiks(r.record, provider)}-{_skrot(r.record)}"
        kand, n = baza, 1
        while kand in uzyte:
            n += 1
            kand = f"{baza}-{n}"
        uzyte.add(kand)
        return kand

    domyslna("id_aed", nowe_id, "WYGENEROWANO_ID",
             "Plik nie ma identyfikatorów AED: nadaliśmy je automatycznie (te same przy ponownym wgraniu tych samych AED).",
             "Brak identyfikatora AED: nadaliśmy go automatycznie.")
    wyniki[0].messages[:0] = plik


def _geokoduj(wyniki: list[RecordResult], geocoder: Optional[Geocoder]) -> None:
    potrzebne = [r for r in wyniki if not (r.record["szerokosc_geograficzna"] and r.record["dlugosc_geograficzna"])
                 and (r.record["miejscowosc"] or r.record["kod_pocztowy"])]
    if not potrzebne or geocoder is None:
        return

    def zapytanie(r: RecordResult) -> AddressQuery:
        rec = r.record
        ulica = rec["nazwa_ulicy"] if rec["nazwa_ulicy"] != rec["miejscowosc"] else ""
        return AddressQuery(ulica=ulica, nr_budynku=rec["nr_budynku"], kod_pocztowy=rec["kod_pocztowy"],
                            miejscowosc=rec["miejscowosc"], kod_terc=rec["kod_terc"])

    def klucz(q: AddressQuery) -> tuple:
        return (norm(q.ulica), norm(q.nr_budynku), q.kod_pocztowy, norm(q.miejscowosc), q.kod_terc)

    unikalne: dict[tuple, AddressQuery] = {}
    przypisanie: list[tuple[RecordResult, tuple]] = []
    pominiete = 0
    for r in potrzebne:
        q = zapytanie(r)
        k = klucz(q)
        if k not in unikalne and len(unikalne) >= MAX_GEOKODOWAN:
            r.pominiety = True
            pominiete += 1
            continue
        unikalne.setdefault(k, q)
        przypisanie.append((r, k))
    if pominiete:
        wyniki[0].messages.append(_msg(
            "ostrzezenie", "ZA_DUZO_DO_GEOKODOWANIA",
            f"Ponad {MAX_GEOKODOWAN} adresów bez współrzędnych: ustaliliśmy położenie pierwszych {MAX_GEOKODOWAN}, "
            f"{pominiete} AED nie zostanie opublikowanych. Dodaj współrzędne w pliku.", None, "szerokosc_geograficzna"))

    def jeden(q: AddressQuery) -> Optional[GeoResult]:
        try:
            return geocoder.geocode(q)
        except Exception:
            return None

    with ThreadPoolExecutor(max_workers=GEOKODOWANIE_ROWNOLEGLE) as ex:
        wyn = dict(zip(unikalne.keys(), ex.map(jeden, unikalne.values())))

    for r, k in przypisanie:
        g = wyn.get(k)
        rec = r.record
        adres = ", ".join(x for x in (f"{zapytanie(r).ulica} {rec['nr_budynku']}".strip(),
                                      f"{rec['kod_pocztowy']} {rec['miejscowosc']}".strip()) if x)
        if g is None:
            r.pominiety = True
            r.messages.append(_msg("ostrzezenie", "GEOKODOWANIE_BRAK",
                                   f"Nie znaleźliśmy adresu „{adres}”: ten AED nie zostanie opublikowany. "
                                   "Dodaj współrzędne lub popraw adres.", r.wiersz, "szerokosc_geograficzna"))
            continue
        rec["szerokosc_geograficzna"] = f"{g.lat:.6f}"
        rec["dlugosc_geograficzna"] = f"{g.lon:.6f}"
        rec["dokladnosc_polozenia"] = rec["dokladnosc_polozenia"] or g.dokladnosc or "punkt_adresowy"
        for pole, wart in (("kod_terc", g.kod_terc), ("kod_simc", g.kod_simc), ("kod_ulic", g.kod_ulic),
                           ("kod_pocztowy", g.kod_pocztowy)):
            if wart and not rec[pole]:
                rec[pole] = wart
        if g.niejednoznaczny:
            r.messages.append(_msg("ostrzezenie", "GEOKODOWANIE_NIEJEDNOZNACZNE",
                                   f"Adres „{adres}” jest niejednoznaczny; wybraliśmy najlepsze trafienie. Sprawdź punkt na mapie.",
                                   r.wiersz, "szerokosc_geograficzna"))
        else:
            r.messages.append(_msg("info", "GEOKODOWANIE_OK",
                                   f"Współrzędne ustalone z adresu „{adres}” (punkt adresowy budynku).", r.wiersz,
                                   "szerokosc_geograficzna"))
