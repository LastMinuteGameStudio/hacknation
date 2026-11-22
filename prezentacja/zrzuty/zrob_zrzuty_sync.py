"""E1/S1: zrzuty synchronizacji z URL źródła („Źródło automatyczne”) na zbiorze demo.

Scenariusz (README.md, sekcja „Synchronizacja”). Źródło to plik w publicznym repo na branchu `demo-zrodlo`, który
podmieniamy commitami między etapami, i to udaje CMS miasta:
    etap zrodlo      plik = przemysl_2024.csv  → ustawienie URL, „Włącz i pobierz teraz”, stan aktywna
    etap nowy-format plik = przemysl.csv       → „Synchronizuj teraz”: ZSYNCHRONIZOWANO, ten sam URL i id_aed
    etap wstrzymana  plik bez kolumny geometry → „Synchronizuj teraz”: wstrzymana (ZMIANA_STRUKTURY), dane bez zmian
    etap przywroc    plik = przemysl.csv       → „Zapisz i pobierz teraz”: znów aktywna (stan na prezentację)

    ZRZUTY_TOKEN_PLIK=/poza/repo/link.txt python zrob_zrzuty_sync.py --etap zrodlo --zrodlo <raw URL>

Link edycji (z tokenem) czyta z ZRZUTY_TOKEN_PLIK (zapisuje go zrob_zrzuty.py). Token jest maskowany na zrzutach.
"""

from __future__ import annotations

import argparse
import csv
import html
import io
import os
import sys
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).resolve().parent))
from zrob_zrzuty import CSV_HTML, Zrzuty  # noqa: E402

KOLUMNY_CSV = ("id_aed", "id_zrodlowe", "szerokosc_geograficzna", "dlugosc_geograficzna", "nazwa_obiektu",
               "data_aktualizacji")
SEKCJA = "section.zrodlo"


def csv_html(pw, url_csv: str, podpis: str) -> str:
    odp = pw.request.new_context().get(url_csv)
    wiersze = list(csv.DictReader(io.StringIO(odp.body().decode("utf-8"))))
    tab = [",".join(KOLUMNY_CSV)] + [",".join(w[k] for k in KOLUMNY_CSV) for w in wiersze[:8]]
    return CSV_HTML.format(url=html.escape(url_csv), status=odp.status,
                           naglowki=html.escape(f"{podpis}\n{len(wiersze)} rekordów, wybrane kolumny, pierwsze 8"),
                           csv=html.escape("\n".join(tab)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--etap", required=True, choices=["zrodlo", "nowy-format", "wstrzymana", "przywroc"])
    ap.add_argument("--zrodlo", help="URL pliku źródłowego (etap zrodlo)")
    a = ap.parse_args()

    url_edycji = Path(os.environ["ZRZUTY_TOKEN_PLIK"]).read_text().strip()
    u = urlparse(url_edycji)
    baza = f"{u.scheme}://{u.netloc}"
    slug = u.path.rstrip("/").split("/")[-1]
    token = parse_qs(u.query)["token"][0]
    url_csv = f"{baza}/d/{slug}.csv"
    api_zrodlo = f"{baza}/api/zbiory/{slug}/zrodlo?token={token}"

    with sync_playwright() as pw:
        przegl = pw.chromium.launch(args=["--lang=pl-PL"])
        ctx = przegl.new_context(viewport={"width": 1440, "height": 900}, locale="pl-PL", device_scale_factor=2)
        page = ctx.new_page()
        z = Zrzuty(page)
        z.token = token

        def otworz():
            page.goto(url_edycji)
            page.locator(f"{SEKCJA} .ramka").first.wait_for(timeout=30_000)

        def czekaj_na_stan(tekst: str):
            page.locator(f"{SEKCJA} .ramka strong", has_text=tekst).first.wait_for(timeout=180_000)
            page.wait_for_timeout(300)

        def stan_api() -> dict:
            return ctx.request.get(api_zrodlo).json()

        if a.etap == "zrodlo":
            page.set_content(csv_html(pw, url_csv, "Przed synchronizacją: dane z wgranego pliku przemysl_2024.csv"))
            z.zrob("09-sync-0-csv-przed")
            otworz()
            page.locator("#zrodlo-url").fill(a.zrodlo)
            page.locator("#zrodlo-co-ile").select_option("24")
            z.zrob("09-sync-1-ustawienie", element=SEKCJA)
            page.get_by_role("button", name="Włącz i pobierz teraz").click()
            czekaj_na_stan("Aktywna")
            z.zrob("09-sync-2-aktywna", element=SEKCJA)

        elif a.etap == "nowy-format":
            otworz()
            page.get_by_role("button", name="Synchronizuj teraz").click()
            page.locator(f"{SEKCJA}", has_text="Ostatnia próba").wait_for()
            page.wait_for_timeout(1500)
            otworz()
            s = stan_api()
            kody = [k["kod"] for k in s["komunikaty"]]
            assert s["status"] == "aktywna" and "ZSYNCHRONIZOWANO" in kody, (s["status"], kody)
            z.zrob("09-sync-3-zsynchronizowano", element=SEKCJA)
            page.set_content(csv_html(pw, url_csv, "Po synchronizacji pliku w nowym formacie geometrii [lon, lat]: "
                                                   "ten sam URL, te same id_aed, nowa data_aktualizacji"))
            z.zrob("09-sync-4-csv-po")

        elif a.etap == "wstrzymana":
            otworz()
            page.get_by_role("button", name="Synchronizuj teraz").click()
            czekaj_na_stan("Wstrzymana")
            s = stan_api()
            kody = [k["kod"] for k in s["komunikaty"]]
            assert s["status"] == "wstrzymana", (s["status"], kody)
            print("kody:", kody)
            z.zrob("09-sync-5-wstrzymana", element=SEKCJA)

        elif a.etap == "przywroc":
            otworz()
            page.get_by_role("button", name="Zapisz i pobierz teraz").click()
            czekaj_na_stan("Aktywna")
            s = stan_api()
            print("stan:", s["status"], [k["kod"] for k in s["komunikaty"]])
            z.zrob("09-sync-6-przywrocona", element=SEKCJA)
            z.zrob("09-sync-6-przywrocona-strona")

        przegl.close()
    print("zrzuty:", z.zapisane)


if __name__ == "__main__":
    main()
