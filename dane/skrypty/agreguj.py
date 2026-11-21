#!/usr/bin/env python3
"""Sprowadza surowe dane o AED (dane/surowe/) do wspólnego schematu i szuka duplikatów.

Wyniki (dane/wynik/):
  aed_wszystkie.csv / .geojson  - każdy rekord z każdego źródła, z oznaczeniem duplikatu
  aed_unikalne.csv / .geojson   - OSM + rekordy spoza OSM bez odpowiednika (bez duplikatów)
  aed_pojazdy_gdansk.csv        - pojazdy ZTM Gdańsk z AED (bez stałej lokalizacji)
  statystyki.json

Pliki CSV mają kolumny wzorcowego zakresu danych v0.5 (zakres-danych/zakres-pol.csv, wszystkie pola pełnej
ewidencji w tej samej kolejności) oraz kolumny dodatkowe agregacji (POLA_DODATKOWE). Brak wartości = znak umowny „X”.
Tylko biblioteka standardowa Pythona.
"""
import csv, json, math, re, sys, xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
RAW, OUT = BASE / "surowe", BASE / "wynik"
OUT.mkdir(exist_ok=True)

PROMIEN_OSM_M = 50     # rekord spoza OSM uznajemy za duplikat OSM, jeśli najbliższy punkt OSM jest bliżej
PROMIEN_INNE_M = 30    # duplikaty między źródłami spoza OSM

POLA = [
    "id_agregatu", "zrodlo", "id_zrodlowe", "osm_id",
    "szerokosc_geograficzna", "dlugosc_geograficzna",
    "nazwa_obiektu", "nazwa_ulicy", "nr_budynku", "kod_pocztowy", "miejscowosc", "dzielnica",
    "wewnatrz_budynku", "kondygnacja", "opis_lokalizacji",
    "dostepnosc", "dostepny_24_7", "godziny_dostepnosci",
    "producent", "model",
    "dysponent_nazwa", "telefon_kontaktowy",
    "data_weryfikacji", "zdjecie_url", "uwagi",
    "licencja_zrodla", "duplikat_z", "odleglosc_duplikatu_m",
]

# Kolejność ważności przy wyborze reprezentanta grupy duplikatów spoza OSM.
PRIORYTET = ["warszawa_19115", "inpost", "koszalin_um", "lodz_um", "krakow_arcgis_2022", "krakow_arcgis",
             "mikolow_arcgis", "pwr_2023", "pwr", "gliwice_crg", "lublin_um", "chelm_um",
             "wopr_zachodniopomorskie", "gdansk_um_2022"]

LICENCJE = {
    "osm": "ODbL 1.0 (© współtwórcy OpenStreetMap)",
    "warszawa_19115": "brak w feedzie; ten sam zbiór w API Otwarte dane Warszawy na CC BY",
    "inpost": "brak",
    "krakow_arcgis": "brak (konto prywatne ArcGIS Online)",
    "krakow_arcgis_2022": "brak (konto prywatne ArcGIS Online)",
    "mikolow_arcgis": "brak, właściciel nieznany",
    "pwr": "brak",
    "pwr_2023": "brak",
    "koszalin_um": "„Wszystkie prawa zastrzeżone” (Google My Maps)",
    "lodz_um": "brak (Google My Maps osadzona na uml.lodz.pl)",
    "gdansk_um_2022": "brak (tabela HTML na gdansk.pl, stan 25.02.2022)",
    "gliwice_crg": "brak (tabela HTML na gliwice.eu)",
    "wopr_zachodniopomorskie": "brak (tabela HTML na woprwz.pl)",
    "lublin_um": "brak (PDF na lublin.eu, stan 17.03.2026)",
    "chelm_um": "brak (HTML na samorzad.gov.pl)",
}
GEOKODOWANE = {"gdansk_um_2022", "gliwice_crg", "wopr_zachodniopomorskie", "lublin_um", "chelm_um"}
PROMIEN_GEOKOD_M = 100  # współrzędne z geokodowania adresu są mniej dokładne


def rec(**kw):
    r = {k: "" for k in POLA}
    for k, v in kw.items():
        if v is None:
            v = ""
        r[k] = v.strip() if isinstance(v, str) else v
    r["licencja_zrodla"] = LICENCJE[r["zrodlo"]]
    return r


def tf(v):
    return "" if v is None else ("true" if v else "false")


BEZ_GEOMETRII = Counter()


def feats(name):
    out = []
    for f in json.load(open(RAW / name, encoding="utf-8"))["features"]:
        if f.get("geometry") and f["geometry"].get("coordinates"):
            out.append(f)
        else:
            BEZ_GEOMETRII[name] += 1
    return out


def xy(f):
    c = f["geometry"]["coordinates"]
    while isinstance(c[0], list):   # Warszawa: [[lon, lat]] (niezgodne z RFC 7946)
        c = c[0]
    return float(c[1]), float(c[0])


# ---------- Źródła ----------

# Słownik „dostepnosc” zakresu v0.5: publiczny / klienci / na_prosbe / prywatny
OSM_ACCESS = {"yes": "publiczny", "permissive": "publiczny", "public": "publiczny",
              "customers": "klienci", "private": "prywatny", "no": "prywatny",
              "permit": "na_prosbe", "employees": "prywatny", "staff": "prywatny"}


def osm():
    for f in feats("osm_pl.geojson"):
        p = f["properties"]; lat, lon = xy(f)
        oh = p.get("opening_hours", "")
        ind = p.get("indoor")
        yield rec(
            zrodlo="osm", id_zrodlowe=f'{p["@osm_type"]}/{p["@osm_id"]}', osm_id=f'{p["@osm_type"]}/{p["@osm_id"]}',
            szerokosc_geograficzna=lat, dlugosc_geograficzna=lon,
            nazwa_obiektu=p.get("name") or p.get("description:pl") or p.get("description", ""),
            nazwa_ulicy=p.get("addr:street"), nr_budynku=p.get("addr:housenumber"),
            kod_pocztowy=p.get("addr:postcode"), miejscowosc=p.get("addr:city"),
            wewnatrz_budynku={"yes": "true", "no": "false"}.get(ind, ""),
            kondygnacja=p.get("level"),
            opis_lokalizacji=p.get("defibrillator:location:pl") or p.get("defibrillator:location", ""),
            dostepnosc=OSM_ACCESS.get(p.get("access", ""), p.get("access", "")),
            dostepny_24_7="tak" if oh == "24/7" else ("nie" if oh else ""),
            godziny_dostepnosci=oh, producent=p.get("manufacturer"), model=p.get("model"),
            dysponent_nazwa=p.get("operator"), telefon_kontaktowy=p.get("phone") or p.get("emergency:phone"),
            data_weryfikacji=p.get("check_date") or p.get("survey:date", ""),
            zdjecie_url=p.get("image") or "", uwagi=p.get("note") or p.get("fixme") or "",
        )


def warszawa():
    for f in feats("warszawa_19115.geojson"):
        p = f["properties"]; lat, lon = xy(f)
        av = (p.get("device_availability") or "").strip()
        yield rec(
            zrodlo="warszawa_19115", id_zrodlowe=p["defibrillator_id"],
            szerokosc_geograficzna=lat, dlugosc_geograficzna=lon,
            nazwa_obiektu=p.get("location_object_name"), nazwa_ulicy=p.get("location_street"),
            nr_budynku=p.get("location_building"), kod_pocztowy=p.get("location_postcode"),
            miejscowosc=p.get("location_city") or "Warszawa", dzielnica=p.get("location_district"),
            wewnatrz_budynku={"Wewnątrz budynku": "true", "Na zewnątrz budynku": "false"}.get(p.get("device_location"), ""),
            kondygnacja=p.get("location_floor"), opis_lokalizacji=p.get("location_description"),
            dostepnosc={"Publiczny": "publiczny", "Prywatny": "prywatny"}.get(p.get("device_public_access"), p.get("device_public_access")),
            dostepny_24_7={"Tak": "tak", "Nie": "nie", "Ograniczona": "ograniczony"}.get(av, ""),
            godziny_dostepnosci=p.get("device_access_description") or ("" if av in ("Tak", "Nie", "Ograniczona") else av),
            producent=p.get("device_manufacturer"),
            data_weryfikacji=(p.get("application_date_last_verification") or "")[:10],
        )


def inpost():
    for f in feats("inpost.geojson"):
        p = f["properties"]; lat, lon = xy(f)
        if p.get("status") != "active":
            continue
        m = re.match(r"(\d\d-\d\d\d)\s+(.*)", p.get("address_2", ""))
        ul = p.get("address_1", "")
        mu = re.match(r"(.*?)\s+(\d+\S*)$", ul)
        yield rec(
            zrodlo="inpost", id_zrodlowe=p["name"], szerokosc_geograficzna=lat, dlugosc_geograficzna=lon,
            nazwa_obiektu=f'Paczkomat InPost {p["name"]}',
            nazwa_ulicy=mu.group(1) if mu else ul, nr_budynku=mu.group(2) if mu else "",
            kod_pocztowy=m.group(1) if m else "", miejscowosc=m.group(2) if m else p.get("area"),
            wewnatrz_budynku="false", opis_lokalizacji=p.get("location_description"),
            dostepnosc="publiczny", dostepny_24_7="tak", godziny_dostepnosci="24/7",
            dysponent_nazwa="InPost (Helpbox 365)",
        )


def krakow():
    for f in feats("krakow_wasniowskip.geojson"):
        p = f["properties"]; lat, lon = xy(f)
        yield rec(zrodlo="krakow_arcgis", id_zrodlowe=p["objectid"], szerokosc_geograficzna=lat, dlugosc_geograficzna=lon,
                  nazwa_obiektu=p.get("lokalizacj"), nazwa_ulicy=p.get("ulica"), miejscowosc=p.get("miasto"),
                  opis_lokalizacji=p.get("uwagi"))
    for f in feats("krakow_pica.geojson"):
        p = f["properties"]; lat, lon = xy(f)
        yield rec(zrodlo="krakow_arcgis_2022", id_zrodlowe=p["objectid"], szerokosc_geograficzna=lat, dlugosc_geograficzna=lon,
                  nazwa_obiektu=p.get("nazwa"), nazwa_ulicy=p.get("ulica"), nr_budynku=p.get("nr"),
                  kod_pocztowy=p.get("kod"), miejscowosc=p.get("miasto"),
                  uwagi=f'geokodowanie z adresu (score {p.get("score")})')


def mikolow():
    for f in feats("mikolow.geojson"):
        p = f["properties"]; lat, lon = xy(f)
        adr = p.get("adres") or ""
        miasto, _, ul = adr.partition(",")
        pol = p.get("Położenie") or ""
        yield rec(zrodlo="mikolow_arcgis", id_zrodlowe=p["OBJECTID"], szerokosc_geograficzna=lat, dlugosc_geograficzna=lon,
                  nazwa_obiektu=p.get("Lokalizacja"), nazwa_ulicy=ul, miejscowosc=miasto or "Mikołów",
                  kondygnacja=p.get("Pietro"), opis_lokalizacji=pol,
                  wewnatrz_budynku="false" if "zewnątrz" in pol.lower() else ("true" if "wewnątrz" in pol.lower() else ""))


def pwr():
    for name, src, key in (("pwr_defibrylatory.geojson", "pwr", "budynek"),
                           ("pwr_Defibrylatory_2023.geojson", "pwr_2023", "Oznaczenie")):
        for f in feats(name):
            p = f["properties"]; lat, lon = xy(f)
            yield rec(zrodlo=src, id_zrodlowe=p["FID"], szerokosc_geograficzna=lat, dlugosc_geograficzna=lon,
                      nazwa_obiektu=f'Politechnika Wrocławska, budynek {p.get(key)}', miejscowosc="Wrocław",
                      kondygnacja=p.get("piętro", ""), uwagi=p.get("Uwagi", ""),
                      dysponent_nazwa="Politechnika Wrocławska")


def kml(plik):
    ns = {"k": "http://www.opengis.net/kml/2.2"}
    root = ET.parse(RAW / plik).getroot()
    for i, pm in enumerate(root.iter("{http://www.opengis.net/kml/2.2}Placemark")):
        c = pm.find(".//k:coordinates", ns)
        if c is None:
            continue
        lon, lat = map(float, c.text.strip().split(",")[:2])
        yield i, lat, lon, (pm.findtext("k:name", "", ns) or "").strip(), (pm.findtext("k:description", "", ns) or "").strip()


def lodz():
    for i, lat, lon, nm, ds in kml("lodz_um.kml"):
        czesci = [x.strip() for x in re.split(r"<br\s*/?>", ds) if x.strip()]
        nazwa = czesci[0] if czesci else nm
        nazwa = re.sub(r"^\d+\s+", "", nazwa)
        adr = re.sub(r"^defibrylator\s*-\s*", "", nm, flags=re.I)
        mu = re.match(r"(?:ul\.\s*)?(.*?)\s+(\d+\S*?)(?:,.*)?$", adr)
        miejsce = " ".join(czesci[1:]).lower()
        yield rec(zrodlo="lodz_um", id_zrodlowe=i, szerokosc_geograficzna=lat, dlugosc_geograficzna=lon,
                  nazwa_obiektu=nazwa, nazwa_ulicy=mu.group(1) if mu else adr, nr_budynku=mu.group(2) if mu else "",
                  miejscowosc="Łódź", opis_lokalizacji=" ".join(czesci[1:]),
                  wewnatrz_budynku="false" if "zewn" in miejsce else ("true" if "wewn" in miejsce else ""))


BEZ_WSPOLRZEDNYCH = []


def wykazy():
    p = RAW / "wykazy" / "wykazy_geokod.json"
    if not p.exists():
        return
    for x in json.load(open(p, encoding="utf-8")):
        pola = {k: x.get(k, "") for k in ("zrodlo", "id_zrodlowe", "nazwa_obiektu", "miejscowosc", "dzielnica",
                                          "opis_lokalizacji", "wewnatrz_budynku", "godziny_dostepnosci", "dostepny_24_7")}
        pola["nazwa_ulicy"] = x["adres"]
        # trafienia w miejscowość / dzielnicę / obszar to centroidy, a nie położenie AED
        if "lat" not in x or x["geokod_typ"].split("/")[0] in ("place", "boundary", "landuse"):
            pola["uwagi"] = f'geokodowanie nieudane lub zbyt ogólne ({x.get("geokod_typ", "brak trafienia")})'
            BEZ_WSPOLRZEDNYCH.append(rec(**pola, szerokosc_geograficzna="", dlugosc_geograficzna=""))
            continue
        yield rec(**pola, szerokosc_geograficzna=x["lat"], dlugosc_geograficzna=x["lon"],
                  uwagi=f'współrzędne z geokodowania Nominatim ({x["geokod_tryb"]}, {x["geokod_typ"]}): {x["geokod_nazwa"]}')


def koszalin():
    ns = {"k": "http://www.opengis.net/kml/2.2"}
    root = ET.parse(RAW / "koszalin.kml").getroot()
    for i, pm in enumerate(root.iter("{http://www.opengis.net/kml/2.2}Placemark")):
        c = pm.find(".//k:coordinates", ns)
        if c is None:
            continue
        lon, lat = map(float, c.text.strip().split(",")[:2])
        nm = (pm.findtext("k:name", "", ns) or "").strip()
        ds = (pm.findtext("k:description", "", ns) or "").strip()
        yield rec(zrodlo="koszalin_um", id_zrodlowe=nm or i, szerokosc_geograficzna=lat, dlugosc_geograficzna=lon,
                  nazwa_obiektu=nm, opis_lokalizacji=re.sub(r"<[^>]+>", " ", ds), miejscowosc="Koszalin",
                  dysponent_nazwa="Urząd Miejski w Koszalinie")


# ---------- Eksport do wzorcowego zakresu danych v0.5 ----------

ZAKRES = BASE.parent / "zakres-danych"
ZNAK_BRAKU = "X"
DNI = ["pn", "wt", "sr", "cz", "pt", "so", "nd"]
POLA_GODZIN = [f"godziny_{d}" for d in DNI] + ["godziny_swieta"]
POLA_DODATKOWE = ["zrodlo", "dzielnica", "licencja_zrodla", "odleglosc_duplikatu_m"]


def wczytaj_zakres():
    """Kolumny i słowniki z zakresu v0.5 – jedno źródło prawdy, bez kopiowania listy pól."""
    with open(ZAKRES / "zakres-pol.csv", encoding="utf-8") as fh:
        pola = [r["pole"] for r in csv.DictReader(fh)]
    slowniki = defaultdict(set)
    with open(ZAKRES / "slowniki.csv", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            slowniki[r["slownik"]].add(r["kod"])
    return pola, slowniki


POLA_ZAKRESU, SLOWNIKI = wczytaj_zakres()
POLA_WYJSCIA = POLA_ZAKRESU + POLA_DODATKOWE

# Słownik „zrodlo_danych” v0.5 (dysponent / jst / zgloszenie_obywatela / inne). OSM to dane poglądowe (ODbL) → „inne”.
ZRODLO_DANYCH = {
    "osm": "inne", "warszawa_19115": "jst", "inpost": "dysponent", "krakow_arcgis": "inne", "krakow_arcgis_2022": "inne",
    "mikolow_arcgis": "inne", "pwr": "dysponent", "pwr_2023": "dysponent", "koszalin_um": "jst", "lodz_um": "jst",
    "gdansk_um_2022": "jst", "gliwice_crg": "jst", "wopr_zachodniopomorskie": "inne", "lublin_um": "jst", "chelm_um": "jst",
}

_OSM_DZIEN = {"Mo": 0, "Tu": 1, "We": 2, "Th": 3, "Fr": 4, "Sa": 5, "Su": 6}
_ZAKRES_GODZIN = re.compile(r"^([01]?\d|2[0-4])[:.](\d\d)\s*-\s*([01]?\d|2[0-4])[:.](\d\d)$")


def _godz(m):
    return f"{int(m.group(1)):02d}:{m.group(2)}-{int(m.group(3)):02d}:{m.group(4)}"


def godziny_osm(oh):
    """Prosta składnia OSM opening_hours → {dzień: 'GG:MM-GG:MM' | 'zamkniete'} albo None, gdy nie da się rozłożyć.

    Obsługuje reguły „<dni> <jeden przedział>” i „<dni> off” rozdzielone „;”. Dni niewymienione w żadnej regule są
    zamknięte (semantyka OSM), a święta bez reguły PH pozostają nieznane.
    """
    if not oh:
        return None
    oh = oh.strip()
    if oh == "24/7":
        return {d: "00:00-24:00" for d in DNI + ["swieta"]}
    wynik = {}
    for regula in filter(None, (x.strip() for x in oh.split(";"))):
        regula = re.sub(r",\s+", ",", regula)
        czesci = regula.split(" ", 1)
        if len(czesci) == 1:                       # sam przedział, bez dni = codziennie
            dni_spec, czas = "Mo-Su", czesci[0]
        else:
            dni_spec, czas = czesci
        dni = []
        for tok in dni_spec.split(","):
            if tok == "PH":
                dni.append("swieta")
            elif re.fullmatch(r"(Mo|Tu|We|Th|Fr|Sa|Su)(-(Mo|Tu|We|Th|Fr|Sa|Su))?", tok):
                a, _, b = tok.partition("-")
                i, j = _OSM_DZIEN[a], _OSM_DZIEN[b or a]
                dni += [DNI[k % 7] for k in range(i, (j if j >= i else j + 7) + 1)]
            else:
                return None
        czas = czas.strip()
        if czas in ("off", "closed"):
            wartosc = "zamkniete"
        else:
            m = _ZAKRES_GODZIN.match(czas)
            if not m:
                return None
            wartosc = _godz(m)
        for d in dni:
            wynik[d] = wartosc
    for d in DNI:
        wynik.setdefault(d, "zamkniete")
    return wynik


_PL_DNI_ROBOCZE = re.compile(r"dni powszedni|pon\w*\.?\s*-\s*(pt|piąt)|od poniedziałku do piątku|poniedziałek\s*-\s*piątek", re.I)
_PL_PRZEDZIAL = re.compile(r"(\d{1,2})[.:](\d{2})\s*(?:-|do)\s*(\d{1,2})[.:](\d{2})")


def godziny_tekst(t):
    """Opisy po polsku z wykazów: „całodobowo” albo „dni powszednie 07:00-17:00” → słownik dni albo None."""
    t = (t or "").strip()
    if not t:
        return None
    if re.search(r"całodob|24\s*/\s*7|24h", t, re.I):
        return godziny_osm("24/7")
    m = _PL_PRZEDZIAL.search(t)
    if m and _PL_DNI_ROBOCZE.search(t) and not re.search(r"sobot|niedziel|święt", t, re.I):
        g = f"{int(m.group(1)):02d}:{m.group(2)}-{int(m.group(3)):02d}:{m.group(4)}"
        return {**{d: g for d in DNI[:5]}, "so": "zamkniete", "nd": "zamkniete"}
    return None


def telefon(t):
    """Zapis wg standardu technicznego (pkt 3.2): +48 i 9 cyfr bez spacji. Zwraca (numer, reszta_do_uwag)."""
    t = (t or "").strip()
    if not t:
        return "", ""
    pierwszy = re.split(r"[;,/]| lub ", t)[0]
    cyfry = re.sub(r"\D", "", pierwszy)
    if len(cyfry) == 11 and cyfry.startswith("48"):
        cyfry = cyfry[2:]
    if len(cyfry) == 9:
        return "+48" + cyfry, ("" if pierwszy.strip() == t else f"telefon (źródło): {t}")
    return "", f"telefon (źródło): {t}"


def na_zakres(r):
    """Rekord agregacji → wiersz zgodny z zakresem v0.5. Wartości, których nie da się zapisać w formacie
    zakresu, trafiają do „uwagi” z dopiskiem, skąd pochodzą; w polu zostaje „X”."""
    w = {k: "" for k in POLA_WYJSCIA}
    uwagi = [r["uwagi"]] if r.get("uwagi") else []
    for k in POLA_ZAKRESU:
        if k in r and k not in ("godziny_dostepnosci",):
            w[k] = r[k]
    for k in POLA_DODATKOWE:
        w[k] = r.get(k, "")
    w["id_aed"] = r["id_agregatu"]
    w["duplikat_id_aed"] = r.get("duplikat_z", "")
    w["zrodlo_danych"] = ZRODLO_DANYCH[r["zrodlo"]]
    if r["zrodlo"] == "inpost":
        w["status"] = "sprawny"           # feed InPost zawiera tylko punkty o statusie active
    else:
        w["status"] = "nieznany"
    if r["zrodlo"] in GEOKODOWANE or r["zrodlo"] == "krakow_arcgis_2022":
        w["dokladnosc_polozenia"] = "punkt_adresowy"
    w["szerokosc_geograficzna"] = f'{r["szerokosc_geograficzna"]:.7f}' if r["szerokosc_geograficzna"] != "" else ""
    w["dlugosc_geograficzna"] = f'{r["dlugosc_geograficzna"]:.7f}' if r["dlugosc_geograficzna"] != "" else ""

    # adres: cecha ulicy oddzielnie (standard techniczny, pkt 3.3)
    m = re.match(r"^(ul|al|pl|os)\.\s*(.+)$", str(w["nazwa_ulicy"]), re.I)
    if m:
        w["cecha_ulicy"] = {"ul": "ulica", "al": "aleja", "pl": "plac", "os": "osiedle"}[m.group(1).lower()]
        w["nazwa_ulicy"] = m.group(2)
    kp = re.sub(r"\s", "", str(w["kod_pocztowy"]))
    if re.fullmatch(r"\d{5}", kp):
        kp = f"{kp[:2]}-{kp[2:]}"
    if kp and not re.fullmatch(r"\d{2}-\d{3}", kp):
        uwagi.append(f"kod pocztowy (źródło): {kp}"); kp = ""
    w["kod_pocztowy"] = kp

    # słowniki
    for pole, slownik in (("dostepnosc", "dostepnosc"), ("dostepny_24_7", "tak_nie_ograniczony")):
        if w[pole] and w[pole] not in SLOWNIKI[slownik]:
            uwagi.append(f"{pole} (źródło): {w[pole]}"); w[pole] = ""
    if w["wewnatrz_budynku"] not in ("", "true", "false"):
        uwagi.append(f"wewnatrz_budynku (źródło): {w['wewnatrz_budynku']}"); w["wewnatrz_budynku"] = ""

    # liczby całkowite, daty, URL
    kond = str(w["kondygnacja"]).strip()
    if kond and not re.fullmatch(r"-?\d+", kond):
        uwagi.append(f"kondygnacja (źródło): {kond}"); kond = ""
    w["kondygnacja"] = kond
    dw = str(w["data_weryfikacji"]).strip()
    if dw and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", dw):
        uwagi.append(f"data weryfikacji (źródło): {dw}"); dw = ""
    w["data_weryfikacji"] = dw
    if w["zdjecie_url"] and not re.match(r"https?://", w["zdjecie_url"]):
        uwagi.append(f"zdjęcie (źródło): {w['zdjecie_url']}"); w["zdjecie_url"] = ""

    nr, reszta = telefon(r.get("telefon_kontaktowy"))
    w["telefon_kontaktowy"] = nr
    if reszta:
        uwagi.append(reszta)

    # godziny: osobna kolumna na każdy dzień; przy 24/7 wszystkie „X”
    oh = r.get("godziny_dostepnosci", "")
    dni = godziny_osm(oh) or godziny_tekst(oh)
    if dni and all(dni.get(d) == "00:00-24:00" for d in DNI):
        w["dostepny_24_7"] = "tak"
    elif dni:
        for d, v in dni.items():
            w[f"godziny_{d}"] = v
        if not w["dostepny_24_7"]:
            w["dostepny_24_7"] = "nie"
    elif oh and oh != "24/7":
        uwagi.append(f"godziny (źródło): {oh}")

    w["uwagi"] = "; ".join(u for u in uwagi if u)
    return {k: (ZNAK_BRAKU if v in ("", None) else v) for k, v in w.items()}


# ---------- Deduplikacja ----------

def dist(a, b):
    la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 2 * 6371000 * math.asin(math.sqrt(h))


class Grid:
    S = 0.0015  # ok. 165 m (lat) x 100 m (lon w PL); sąsiedztwo 3x3 pokrywa promień 100 m

    def __init__(self):
        self.g = defaultdict(list)

    def key(self, lat, lon):
        return int(lat // self.S), int(lon // self.S)

    def add(self, lat, lon, item):
        self.g[self.key(lat, lon)].append((lat, lon, item))

    def nearest(self, lat, lon, maxd):
        ki, kj = self.key(lat, lon)
        best = (None, maxd + 1)
        for di in (-1, 0, 1):
            for dj in (-1, 0, 1):
                for la, lo, it in self.g.get((ki + di, kj + dj), ()):
                    d = dist((lat, lon), (la, lo))
                    if d < best[1]:
                        best = (it, d)
        return best if best[1] <= maxd else (None, None)


def main():
    zrodla = [osm, warszawa, inpost, krakow, mikolow, pwr, koszalin, lodz, wykazy]
    wszystkie = []
    for fn in zrodla:
        n0 = len(wszystkie)
        wszystkie.extend(fn())
        print(f"{fn.__name__:10s} {len(wszystkie) - n0:6d}", file=sys.stderr)

    # odrzuć rekordy poza przybliżonym bboxem Polski
    w_pl = lambda r: 48.9 <= r["szerokosc_geograficzna"] <= 55.1 and 14.0 <= r["dlugosc_geograficzna"] <= 24.3
    poza = [r for r in wszystkie if not w_pl(r)]
    wszystkie = [r for r in wszystkie if w_pl(r)]

    for r in wszystkie + BEZ_WSPOLRZEDNYCH:
        r["id_agregatu"] = f'{r["zrodlo"]}:{r["id_zrodlowe"]}'

    g_osm = Grid()
    for r in wszystkie:
        if r["zrodlo"] == "osm":
            g_osm.add(r["szerokosc_geograficzna"], r["dlugosc_geograficzna"], r["id_agregatu"])

    inne = [r for r in wszystkie if r["zrodlo"] != "osm"]
    inne.sort(key=lambda r: PRIORYTET.index(r["zrodlo"]))
    for r in inne:
        promien = PROMIEN_GEOKOD_M if r["zrodlo"] in GEOKODOWANE else PROMIEN_OSM_M
        it, d = g_osm.nearest(r["szerokosc_geograficzna"], r["dlugosc_geograficzna"], promien)
        if it:
            r["duplikat_z"], r["odleglosc_duplikatu_m"] = it, round(d, 1)

    g_inne = Grid()
    for r in inne:
        if r["duplikat_z"]:
            continue
        promien = PROMIEN_GEOKOD_M if r["zrodlo"] in GEOKODOWANE else PROMIEN_INNE_M
        it, d = g_inne.nearest(r["szerokosc_geograficzna"], r["dlugosc_geograficzna"], promien)
        if it and it.split(":")[0] != r["zrodlo"]:
            r["duplikat_z"], r["odleglosc_duplikatu_m"] = it, round(d, 1)
        else:
            g_inne.add(r["szerokosc_geograficzna"], r["dlugosc_geograficzna"], r["id_agregatu"])

    unikalne = [r for r in wszystkie if not r["duplikat_z"]]

    def zapisz_csv(rows, stem):
        # RFC 4180: przecinek, CRLF, UTF-8 bez BOM (standard techniczny, pkt 4.1)
        with open(OUT / f"{stem}.csv", "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, POLA_WYJSCIA, lineterminator="\r\n"); w.writeheader(); w.writerows(rows)

    def zapisz(rows, stem):
        wiersze = [na_zakres(r) for r in rows]
        zapisz_csv(wiersze, stem)
        fc = {"type": "FeatureCollection", "features": [
            {"type": "Feature",
             "geometry": {"type": "Point", "coordinates": [round(r["dlugosc_geograficzna"], 7), round(r["szerokosc_geograficzna"], 7)]},
             "properties": {k: v for k, v in w.items() if k not in ("szerokosc_geograficzna", "dlugosc_geograficzna") and v != ZNAK_BRAKU}}
            for r, w in zip(rows, wiersze)]}
        json.dump(fc, open(OUT / f"{stem}.geojson", "w", encoding="utf-8"), ensure_ascii=False)
        return wiersze

    zapisz(wszystkie, "aed_wszystkie")
    wiersze_unikalne = zapisz(unikalne, "aed_unikalne")
    zapisz_csv([na_zakres(r) for r in BEZ_WSPOLRZEDNYCH], "aed_bez_wspolrzednych")

    # pojazdy Gdańsk
    poj = json.load(open(RAW / "gdansk_pojazdy.json", encoding="utf-8"))["results"]
    aed_poj = [v for v in poj if v.get("aed")]
    with open(OUT / "aed_pojazdy_gdansk.csv", "w", newline="", encoding="utf-8") as fh:
        cols = ["vehicleCode", "carrirer", "transportationType", "brand", "model", "productionYear", "url"]
        w = csv.DictWriter(fh, cols, extrasaction="ignore"); w.writeheader(); w.writerows(aed_poj)

    st = {
        "promien_duplikatu_osm_m": PROMIEN_OSM_M, "promien_duplikatu_inne_m": PROMIEN_INNE_M,
        "odrzucone_poza_polska": len(poza), "odrzucone_bez_geometrii": BEZ_GEOMETRII,
        "rekordy_wg_zrodla": Counter(r["zrodlo"] for r in wszystkie),
        "duplikaty_osm_wg_zrodla": Counter(r["zrodlo"] for r in inne if r["duplikat_z"].startswith("osm:")),
        "duplikaty_miedzy_innymi_wg_zrodla": Counter(r["zrodlo"] for r in inne if r["duplikat_z"] and not r["duplikat_z"].startswith("osm:")),
        "nowe_poza_osm_wg_zrodla": Counter(r["zrodlo"] for r in unikalne if r["zrodlo"] != "osm"),
        "bez_wspolrzednych_wg_zrodla": Counter(r["zrodlo"] for r in BEZ_WSPOLRZEDNYCH),
        "razem_wszystkie": len(wszystkie), "razem_unikalne": len(unikalne),
        "pojazdy_gdansk_z_aed": len(aed_poj), "pojazdy_gdansk_razem": len(poj),
        "wypelnienie_pol_unikalne": {k: sum(1 for w in wiersze_unikalne if w[k] != ZNAK_BRAKU) for k in POLA_WYJSCIA},
    }
    json.dump(st, open(OUT / "statystyki.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps({k: v for k, v in st.items() if k != "wypelnienie_pol_unikalne"}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
