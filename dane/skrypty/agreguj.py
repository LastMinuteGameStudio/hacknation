#!/usr/bin/env python3
"""Sprowadza surowe dane o AED (dane/surowe/) do wspólnego schematu i szuka duplikatów.

Wyniki (dane/wynik/):
  aed_wszystkie.csv / .geojson  - każdy rekord z każdego źródła, z oznaczeniem duplikatu
  aed_unikalne.csv / .geojson   - OSM + rekordy spoza OSM bez odpowiednika (bez duplikatów)
  aed_pojazdy_gdansk.csv        - pojazdy ZTM Gdańsk z AED (bez stałej lokalizacji)
  statystyki.json

Nazwy pól są podzbiorem wzorcowego zakresu danych (branch wojtek, zakres-danych/zakres-pol.csv).
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
    "producent", "model", "aed_mobilny",
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

OSM_ACCESS = {"yes": "publiczny", "permissive": "publiczny", "public": "publiczny",
              "customers": "klienci", "private": "prywatny", "no": "prywatny",
              "permit": "ograniczony", "employees": "pracownicy", "staff": "pracownicy"}


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
            aed_mobilny="true" if p.get("mobile") == "yes" else "",
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

    for i, r in enumerate(wszystkie, 1):
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

    def zapisz(rows, stem):
        with open(OUT / f"{stem}.csv", "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, POLA); w.writeheader(); w.writerows(rows)
        fc = {"type": "FeatureCollection", "features": [
            {"type": "Feature",
             "geometry": {"type": "Point", "coordinates": [round(r["dlugosc_geograficzna"], 7), round(r["szerokosc_geograficzna"], 7)]},
             "properties": {k: v for k, v in r.items() if k not in ("szerokosc_geograficzna", "dlugosc_geograficzna") and v != ""}}
            for r in rows]}
        json.dump(fc, open(OUT / f"{stem}.geojson", "w", encoding="utf-8"), ensure_ascii=False)

    zapisz(wszystkie, "aed_wszystkie")
    zapisz(unikalne, "aed_unikalne")
    with open(OUT / "aed_bez_wspolrzednych.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, POLA); w.writeheader(); w.writerows(BEZ_WSPOLRZEDNYCH)

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
        "wypelnienie_pol_unikalne": {k: sum(1 for r in unikalne if r[k] != "") for k in POLA},
    }
    json.dump(st, open(OUT / "statystyki.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps({k: v for k, v in st.items() if k != "wypelnienie_pol_unikalne"}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
