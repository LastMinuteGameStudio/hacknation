"""Pokaz scalania wykazów AED bez uruchamiania portalu (bez Django i bazy).

Przepuszcza wykazy „dostawców” przez tę samą logikę, której używa zadanie create_main_aed_resource_task
(mcod/resources/aed/), i zapisuje wynik w portal/pokaz/:
  wykaz-zbiorczy.csv, wykaz-zbiorczy.xlsx, raport.json, zrodla/ (kopie wejściowych wykazów).

Źródła:
  1. Urząd Miejski w Przemyślu: https://tuaed.wkrynski.dev/d/kznsks42.csv (CC0 1.0)
  2. Urząd Miasta Krosna: https://tuaed.wkrynski.dev/d/qy7g6px5.csv (CC0 1.0)
  3–6. wykazy pokazowe (fikcyjne, przygotowane tu): uczelnia (CC0), szpital (CC BY 4.0) z duplikatem po numerze
       seryjnym i duplikatem do 30 m, fundacja z licencją CC BY-NC 4.0 (pominięta), gmina z błędem walidacji
       (pominięta).

Uruchomienie (z katalogu portal/, Python ≥ 3.8 z openpyxl):
  python tuaed_pokaz_scalania.py            # pobiera wykazy 1–2 z TuAED, przy braku sieci bierze kopie z pokaz/zrodla/
  python tuaed_pokaz_scalania.py --offline  # tylko kopie z pokaz/zrodla/
"""

import argparse
import csv
import io
import json
import sys
import types
import urllib.request
from pathlib import Path

PORTAL = Path(__file__).resolve().parent
POKAZ = PORTAL / "pokaz"
ZRODLA = POKAZ / "zrodla"

# mcod/__init__.py i mcod/resources/__init__.py importują Django; pakiet aed go nie potrzebuje,
# więc rejestrujemy puste pakiety nadrzędne wskazujące na prawdziwe katalogi.
for nazwa, katalog in (("mcod", PORTAL / "mcod"), ("mcod.resources", PORTAL / "mcod" / "resources")):
    if nazwa not in sys.modules:
        m = types.ModuleType(nazwa)
        m.__path__ = [str(katalog)]
        sys.modules[nazwa] = m

from mcod.resources.aed.merge import (  # noqa: E402
    ZrodloWykazu,
    scal_wykazy,
    to_csv_bytes,
    to_xlsx_bytes,
)
from mcod.resources.aed.reader import read_table  # noqa: E402
from mcod.resources.aed.schema import load_zakres  # noqa: E402
from mcod.resources.aed.validation import bledy, validate_table  # noqa: E402

TUAED = "https://tuaed.wkrynski.dev/d/{}.csv"
DATA = "2026-11-22T06:00:00"


def _rekord(id_aed, lat, lon, nazwa, ulica, nr, miejscowosc, dysponent, **kw):
    r = {
        "id_aed": id_aed, "szerokosc_geograficzna": lat, "dlugosc_geograficzna": lon,
        "dokladnosc_polozenia": "pomiar_przy_urzadzeniu", "nazwa_obiektu": nazwa, "cecha_ulicy": "ulica",
        "nazwa_ulicy": ulica, "nr_budynku": nr, "miejscowosc": miejscowosc, "wewnatrz_budynku": "true",
        "dostepnosc": "publiczny", "dostepny_24_7": "tak", "status": "sprawny", "data_weryfikacji": "2026-11-15",
        "numer_seryjny": "", "dysponent_nazwa": dysponent, "dysponent_typ": "ochrona_zdrowia",
        "zrodlo_danych": "dysponent", "data_aktualizacji": DATA, "uwagi": "Rekord pokazowy (fikcyjny).",
    }
    r.update(kw)
    return r


def _csv(rekordy):
    kolumny = list(rekordy[0].keys())
    buf = io.StringIO(newline="")
    w = csv.DictWriter(buf, fieldnames=kolumny, lineterminator="\r\n")
    w.writeheader()
    w.writerows(rekordy)
    return buf.getvalue().encode("utf-8")


def wykazy_pokazowe(krosno_pierwszy):
    """Wykazy 3–6. Duplikat do 30 m liczymy względem pierwszego AED z wykazu Krosna."""
    lat0, lon0 = float(krosno_pierwszy["szerokosc_geograficzna"]), float(krosno_pierwszy["dlugosc_geograficzna"])
    uczelnia = [
        _rekord("uczelnia-przemysl-1", "49.786100", "22.773900", "Uczelnia (pokaz), budynek A", "Książąt Lubomirskich", "6",
                "Przemyśl", "Uczelnia (pokaz)", dysponent_typ="edukacja", numer_seryjny="SN-PL-2024-0001"),
    ]
    szpital = [
        # ten sam numer seryjny co AED uczelni: urządzenie zgłoszone przez dwóch dysponentów
        _rekord("szpital-krosno-1", "49.692700", "21.766300", "Szpital (pokaz), izba przyjęć", "Korczyńska", "57",
                "Krosno", "Szpital (pokaz)", numer_seryjny="sn-pl-2024-0001"),
        # ok. 15 m na północ od pierwszego AED z wykazu Krosna
        _rekord("szpital-krosno-2", f"{lat0 + 0.000135:.6f}", f"{lon0:.6f}", "Szpital (pokaz), punkt przy pływalni",
                krosno_pierwszy.get("nazwa_ulicy") or "Bursaki", krosno_pierwszy.get("nr_budynku") or "1", "Krosno",
                "Szpital (pokaz)"),
        _rekord("szpital-krosno-3", "49.695500", "21.770100", "Szpital (pokaz), poradnia", "Korczyńska", "57",
                "Krosno", "Szpital (pokaz)"),
    ]
    fundacja = [
        _rekord("fundacja-1", "49.780000", "22.770000", "Fundacja (pokaz), siedziba", "Mickiewicza", "1", "Przemyśl",
                "Fundacja (pokaz)", dysponent_typ="ngo"),
    ]
    gmina_zle = [
        _rekord("gmina-1", "49.900000", "22.100000", "Gmina (pokaz), urząd", "Rynek", "1", "Wieś Pokazowa",
                "Gmina (pokaz)", dysponent_typ="jst", dostepnosc="dla wszystkich"),
    ]
    return [
        ("Uczelnia (pokaz)", 103, "CC0 1.0", "pokaz-uczelnia.csv", _csv(uczelnia)),
        ("Wojewódzki Szpital (pokaz)", 104, "CC BY 4.0", "pokaz-szpital.csv", _csv(szpital)),
        ("Fundacja (pokaz)", 105, "CC BY-NC 4.0", "pokaz-fundacja.csv", _csv(fundacja)),
        ("Gmina (pokaz)", 106, "CC0 1.0", "pokaz-gmina-z-bledem.csv", _csv(gmina_zle)),
    ]


def pobierz(slug, offline):
    kopia = ZRODLA / f"{slug}.csv"
    if not offline:
        try:
            zapytanie = urllib.request.Request(TUAED.format(slug), headers={"User-Agent": "tuaed-pokaz-scalania/1.0"})
            with urllib.request.urlopen(zapytanie, timeout=15) as r:
                dane = r.read()
            kopia.write_bytes(dane)
            return dane, TUAED.format(slug)
        except OSError as exc:
            print(f"Nie udało się pobrać {slug} ({exc}), używam kopii {kopia.relative_to(PORTAL)}.", file=sys.stderr)
    return kopia.read_bytes(), TUAED.format(slug)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--offline", action="store_true", help="nie pobieraj z TuAED, użyj kopii z pokaz/zrodla/")
    args = ap.parse_args()
    ZRODLA.mkdir(parents=True, exist_ok=True)
    zakres = load_zakres()

    zrodla = []
    for instytucja, zasob_id, slug in (("Urząd Miejski w Przemyślu", 101, "kznsks42"),
                                       ("Urząd Miasta Krosna", 102, "qy7g6px5")):
        dane, url = pobierz(slug, args.offline)
        zrodla.append(ZrodloWykazu(instytucja, zasob_id, url, DATA, "CC0 1.0", read_table(dane, "csv")))
    for instytucja, zasob_id, licencja, plik, dane in wykazy_pokazowe(zrodla[1].tabela.wiersze[0]):
        (ZRODLA / plik).write_bytes(dane)
        zrodla.append(ZrodloWykazu(instytucja, zasob_id, f"pokaz/zrodla/{plik}", DATA, licencja, read_table(dane, "csv")))

    wynik = scal_wykazy(zrodla, zakres)
    (POKAZ / "wykaz-zbiorczy.csv").write_bytes(to_csv_bytes(wynik))
    (POKAZ / "wykaz-zbiorczy.xlsx").write_bytes(to_xlsx_bytes(wynik))

    raport = {
        "opis": "Wynik scalania wykazów AED tą samą logiką co zadanie portalu create_main_aed_resource_task "
                "(portal/mcod/resources/aed/). Reguły: portal/WYKAZ-AED.md.",
        "zakres": f"wzorcowy zakres danych o AED v{zakres.wersja}",
        "licencja_wykazu": wynik.licencja,
        "liczba_aed": len(wynik.rekordy),
        "liczba_duplikatow": wynik.liczba_duplikatow,
        "dolaczone": [{"instytucja": z.instytucja, "zasob_id": z.zasob_id, "url": z.url, "licencja": z.licencja,
                       "liczba_aed": len(z.tabela.wiersze),
                       "ostrzezenia": len(validate_table(z.tabela, zakres)) - len(bledy(validate_table(z.tabela, zakres)))}
                      for z in wynik.dolaczone],
        "pominiete": [{"instytucja": p.zrodlo.instytucja, "zasob_id": p.zrodlo.zasob_id, "url": p.zrodlo.url,
                       "licencja": p.zrodlo.licencja, "powod": p.powod,
                       "bledy": [k.as_dict()["message"] for k in p.komunikaty]} for p in wynik.pominiete],
        "duplikaty": [{"id_aed": r["id_aed"], "instytucja": r["zrodlo_instytucja"], "duplikat_id_aed": r["duplikat_id_aed"]}
                      for r in wynik.rekordy if r["duplikat_id_aed"]],
    }
    (POKAZ / "raport.json").write_text(json.dumps(raport, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"Wykaz zbiorczy: {len(wynik.rekordy)} AED z {len(wynik.dolaczone)} wykazów, licencja {wynik.licencja}.")
    for d in raport["duplikaty"]:
        print(f"  duplikat: {d['id_aed']} ({d['instytucja']}) → {d['duplikat_id_aed']}")
    for p in raport["pominiete"]:
        print(f"  pominięty: {p['instytucja']}: {p['powod']}")
    print(f"Zapisano: {', '.join(str(p.relative_to(PORTAL)) for p in (POKAZ / 'wykaz-zbiorczy.csv', POKAZ / 'wykaz-zbiorczy.xlsx', POKAZ / 'raport.json'))}")


if __name__ == "__main__":
    main()
