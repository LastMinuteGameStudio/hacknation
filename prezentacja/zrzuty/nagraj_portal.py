"""Nagranie (MP4, ok. 100 s) przejścia przez wykaz AED w panelu lokalnego portalu dane.gov.pl (branch portal-aed).

Scenariusz (podpisy na dole ekranu):
  1. logowanie jako redaktor instytucji (dostawca danych),
  2. formularz zasobu: zaznaczone pole „Wykaz AED”,
  3. zakładka „Walidacja danych”: SUCCESS (wykaz zgodny z zakresem v0.5),
  4. wylogowanie, logowanie jako administrator portalu (wykaz zbiorczy i raport widzi tylko superuser),
     wykaz z błędem słownika (FAILURE z numerem wiersza),
  5. zbiór „Defibrylatory AED: wykaz zbiorczy” i jego zasoby CSV/XLSX,
  6. „Wykaz zbiorczy AED” (AggregatedAEDInfo): liczby i raport scalania.
Skrypt tylko czyta (nie zapisuje formularzy). Hasła wyłącznie ze zmiennych środowiskowych.

Uruchomienie (venv z playwright i imageio-ffmpeg):
    PORTAL_HASLO='…' [PORTAL_HASLO_REDAKTOR='…'] python prezentacja/zrzuty/nagraj_portal.py \
        [--url http://localhost:8101] [--redaktor redaktor.przemysl@tuaed.local] [--admin admin@tuaed.local]
Wynik: prezentacja/zrzuty/portal-nagranie.mp4
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import quote

from playwright.sync_api import Page, sync_playwright

sys.path.insert(0, str(Path(__file__).resolve().parent))
from zrob_zrzuty_portal import (ETYKIETA_WYKAZ, KATALOG, MASKA, MASKUJ_JS, PODSWIETL_JS, RAPORT_JS,  # noqa: E402
                                ZASOB_Z_BLEDEM, ZBIOR_DOSTAWCY, ZBIOR_ZBIORCZY, statyczne_z_ponowieniem)

WYNIK = KATALOG / "portal-nagranie.mp4"
ROZMIAR = {"width": 1440, "height": 900}

# Pasek z podpisem na dole ekranu (kolor kampanii AEDane).
PODPIS_JS = """(tekst) => {
  let el = document.getElementById('aedane-podpis');
  if (!el) {
    el = document.createElement('div');
    el.id = 'aedane-podpis';
    el.style.cssText = 'position:fixed;left:0;right:0;bottom:0;z-index:99999;background:#008c15;color:#fff;' +
      'font:600 26px/1.35 "Helvetica Neue",Arial,sans-serif;padding:18px 40px;text-align:center;' +
      'box-shadow:0 -2px 12px rgba(0,0,0,.25)';
    document.body.appendChild(el);
  }
  el.textContent = tekst;
}"""

# Kursor widoczny na nagraniu (headless Chromium nie rysuje kursora).
KURSOR_JS = """() => {
  if (document.getElementById('aedane-kursor')) return;
  const k = document.createElement('div');
  k.id = 'aedane-kursor';
  k.style.cssText = 'position:fixed;width:22px;height:22px;border-radius:50%;background:rgba(0,140,21,.55);' +
    'border:2px solid #fff;z-index:100000;pointer-events:none;left:-50px;top:-50px;transform:translate(-50%,-50%)';
  document.body.appendChild(k);
  document.addEventListener('mousemove', e => { k.style.left = e.clientX + 'px'; k.style.top = e.clientY + 'px'; });
}"""


class Nagranie:
    def __init__(self, page: Page, baza: str):
        self.p = page
        self.baza = baza
        self.podpis_tekst = ""

    def przygotuj(self) -> None:
        self.p.evaluate(MASKUJ_JS, MASKA)
        self.p.evaluate(KURSOR_JS)
        if self.podpis_tekst:
            self.p.evaluate(PODPIS_JS, self.podpis_tekst)

    def idz(self, sciezka: str) -> None:
        self.p.goto(self.baza + sciezka, wait_until="load")
        self.przygotuj()

    def podpis(self, tekst: str, pauza: int = 0) -> None:
        self.podpis_tekst = tekst
        self.p.evaluate(PODPIS_JS, tekst)
        if pauza:
            self.p.wait_for_timeout(pauza)

    def klik(self, lokator, pauza: int = 1200) -> None:
        lokator.scroll_into_view_if_needed()
        box = lokator.bounding_box()
        if box:
            self.p.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2, steps=25)
            self.p.wait_for_timeout(400)
        lokator.click()
        self.p.wait_for_load_state("load")
        self.przygotuj()
        self.p.wait_for_timeout(pauza)

    def przewin(self, dy: int, kroki: int = 30, pauza: int = 40) -> None:
        for _ in range(kroki):
            self.p.mouse.wheel(0, dy / kroki)
            self.p.wait_for_timeout(pauza)

    def zaloguj(self, login: str, haslo: str) -> None:
        self.idz("/login/")
        self.p.wait_for_timeout(800)
        self.p.locator("#id_username").click()
        self.p.keyboard.type(login, delay=45)
        self.p.locator("#id_password").click()
        self.p.keyboard.type(haslo, delay=30)
        self.p.wait_for_timeout(500)
        self.klik(self.p.locator("#login-form [type=submit]"), pauza=1500)
        if "/login" in self.p.url:
            sys.exit(f"Logowanie {login} nieudane: sprawdź hasło w zmiennej środowiskowej.")

    def wyloguj(self) -> None:
        link = self.p.locator("a[href*='logout']").first
        if link.count():
            self.klik(link, pauza=800)
        else:
            self.idz("/logout/")

    def otworz_z_listy(self, lista: str, szukaj: str, nazwa: str | re.Pattern) -> bool:
        self.idz(f"{lista}?q={quote(szukaj)}")
        self.p.wait_for_timeout(1500)
        link = self.p.locator("#result_list").get_by_role("link", name=nazwa).first
        if not link.count():
            return False
        self.klik(link)
        return True

    def zakladka(self, nazwa: str) -> bool:
        tab = self.p.locator(f".nav-tabs a[href='#{nazwa}']").first
        if not tab.count():
            return False
        self.klik(tab, pauza=600)
        return True


def scenariusz(n: Nagranie, redaktor: str, haslo_red: str, admin: str, haslo_adm: str) -> None:
    n.podpis_tekst = "Dostawca danych (np. urząd gminy) loguje się do panelu dane.gov.pl"
    n.zaloguj(redaktor, haslo_red)
    n.p.wait_for_timeout(1500)

    n.podpis("Otwiera swój zasób z wykazem defibrylatorów (plik CSV)", 0)
    if not n.otworz_z_listy("/resources/resource/", ZBIOR_DOSTAWCY, re.compile(re.escape(ZBIOR_DOSTAWCY))):
        sys.exit(f"Redaktor {redaktor} nie widzi zasobu „{ZBIOR_DOSTAWCY}”.")
    adres_zasobu = n.p.url.split("#")[0]
    n.p.wait_for_timeout(1500)

    pole = n.p.locator(".field-is_aed_list, .form-row:has(label:text-is('%s:'))" % ETYKIETA_WYKAZ).first
    n.podpis("Jedno nowe pole w formularzu: „Wykaz AED” = Tak", 0)
    n.p.evaluate("(el) => el.scrollIntoView({behavior: 'smooth', block: 'center'})", pole.element_handle())
    n.p.wait_for_timeout(1500)
    n.p.evaluate(PODSWIETL_JS, pole.element_handle())
    tak = pole.locator("input").first
    box = tak.bounding_box()
    if box:
        n.p.mouse.move(box["x"] + 8, box["y"] + 8, steps=25)
    n.p.wait_for_timeout(5000)
    n.podpis("Portal sam sprawdza plik ze wzorcowym zakresem danych o AED (v0.5)", 4500)

    n.p.goto(adres_zasobu, wait_until="load")
    n.przygotuj()
    n.podpis("Zakładka „Walidacja danych”: wykaz zgodny z zakresem, SUCCESS", 0)
    n.zakladka("data")
    n.p.wait_for_timeout(5500)

    n.podpis("Co noc portal scala poprawne wykazy wszystkich dostawców w jeden", 0)
    n.wyloguj()
    n.podpis_tekst = "Administrator portalu widzi wynik scalania"
    n.zaloguj(admin, haslo_adm)

    n.podpis_tekst = "Wykaz z błędem dostaje komunikat z numerem wiersza i podpowiedzią, co poprawić"
    if n.otworz_z_listy("/resources/resource/", ZASOB_Z_BLEDEM, re.compile(re.escape(ZASOB_Z_BLEDEM))):
        n.zakladka("data")
        n.p.wait_for_timeout(5500)
        n.podpis("Taki wykaz nie trafia do wykazu zbiorczego, dopóki dostawca go nie poprawi", 4000)

    n.podpis_tekst = "Zbiór „Defibrylatory AED: wykaz zbiorczy”, tworzony przez portal"
    if n.otworz_z_listy("/datasets/dataset/", ZBIOR_ZBIORCZY, ZBIOR_ZBIORCZY):
        n.p.wait_for_timeout(3000)
        n.przewin(500)
        n.p.wait_for_timeout(2500)

    n.podpis_tekst = "Ten sam wykaz zbiorczy w CSV i XLSX, odświeżany po każdym scaleniu"
    n.idz("/resources/resource/?q=" + quote(ZBIOR_ZBIORCZY))
    n.p.wait_for_timeout(6000)

    n.podpis_tekst = "„Wykaz zbiorczy AED”: liczba AED, dołączone i pominięte wykazy, duplikaty, licencja"
    n.idz("/resources/aggregatedaedinfo/")
    n.p.wait_for_timeout(2500)
    link = n.p.locator("#result_list tbody tr a").first
    if link.count():
        n.klik(link, pauza=1000)
        n.p.evaluate(RAPORT_JS)
        n.przygotuj()
        n.p.wait_for_timeout(4000)
        n.podpis("Raport scalania: każdy pominięty wykaz ma podany powód (np. licencja BY-NC)", 0)
        n.przewin(900, kroki=60, pauza=60)
        n.p.wait_for_timeout(3000)
        n.przewin(900, kroki=60, pauza=60)
        n.p.wait_for_timeout(3000)
    n.podpis("AEDane: jeden otwarty wykaz defibrylatorów w Polsce, na dane.gov.pl", 4000)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--url", default=os.environ.get("PORTAL_URL", "http://localhost:8101"))
    ap.add_argument("--redaktor", default="redaktor.przemysl@tuaed.local")
    ap.add_argument("--admin", default="admin@tuaed.local")
    ap.add_argument("--crf", default="30", help="jakość H.264 (wyżej = mniejszy plik)")
    a = ap.parse_args()
    haslo_adm = os.environ.get("PORTAL_HASLO")
    haslo_red = os.environ.get("PORTAL_HASLO_REDAKTOR", haslo_adm)
    if not haslo_adm:
        sys.exit("Ustaw PORTAL_HASLO (i ewentualnie PORTAL_HASLO_REDAKTOR). Haseł nie trzymamy w repo.")
    try:
        import imageio_ffmpeg
        ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        ffmpeg = shutil.which("ffmpeg") or sys.exit("Potrzebny ffmpeg z H.264: pip install imageio-ffmpeg")

    with tempfile.TemporaryDirectory() as tmp:
        with sync_playwright() as pw:
            przegl = pw.chromium.launch(args=["--lang=pl-PL"])
            ctx = przegl.new_context(viewport=ROZMIAR, locale="pl-PL", record_video_dir=tmp,
                                     record_video_size=ROZMIAR)
            ctx.route("**/static/**", statyczne_z_ponowieniem)
            strona = ctx.new_page()
            try:
                scenariusz(Nagranie(strona, a.url.rstrip("/")), a.redaktor, haslo_red, a.admin, haslo_adm)
            finally:
                ctx.unroute_all(behavior="ignoreErrors")
                ctx.close()
                przegl.close()
        webm = next(Path(tmp).glob("*.webm"))
        subprocess.run([ffmpeg, "-y", "-loglevel", "error", "-i", str(webm), "-c:v", "libx264", "-preset", "slow",
                        "-crf", a.crf, "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-an", str(WYNIK)],
                       check=True)
    print(f"zapisano {WYNIK.name}: {WYNIK.stat().st_size / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
