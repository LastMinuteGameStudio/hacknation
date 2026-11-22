"""Zrzuty panelu admina lokalnego portalu dane.gov.pl (mcod-backend 2.62.3 + „wykaz AED”, branch portal-aed).

Portal: portal/URUCHOMIENIE-TUAED.md (panel http://localhost:8101, dane testowe: mcod/tuaed_dane_testowe.py,
scalenie: create_main_aed_resource_task). Skrypt tylko czyta i robi zrzuty, niczego w portalu nie zmienia.

Uruchomienie (hasło wyłącznie ze zmiennej środowiskowej, nie w repo):
    python3 -m venv /tmp/pw && /tmp/pw/bin/pip install playwright && /tmp/pw/bin/playwright install chromium
    PORTAL_HASLO='…' /tmp/pw/bin/python prezentacja/zrzuty/zrob_zrzuty_portal.py \
        [--url http://localhost:8101] [--login admin@tuaed.local] [--zasob-z-bledem 'tytuł zasobu']
Kolejność: najpierw test e2e D (portal/tuaed_e2e.sh), który zakłada zasób z błędem słownika, potem ten skrypt.

Ekrany (podpisy w README.md, sekcja „Portal dane.gov.pl: wykaz AED”):
  portal-01-formularz-wykaz-aed      formularz zasobu: pole „Wykaz AED” z opisem
  portal-02a-walidacja-poprawny      zasób-wykaz: wynik walidacji zakresu v0.5 bez błędów
  portal-02b-walidacja-blad-slownika zasób-wykaz z wartością spoza słownika (jeśli jest w portalu)
  portal-03a-zbior-wykaz-zbiorczy    zbiór „Defibrylatory AED: wykaz zbiorczy”
  portal-03b-zasoby-csv-xlsx         zasoby zbioru zbiorczego: CSV i XLSX
  portal-04-wykaz-zbiorczy-raport    „Wykaz zbiorczy AED” (AggregatedAEDInfo): dołączone i pominięte wykazy z powodem
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path
from urllib.parse import quote

from playwright.sync_api import Page, TimeoutError as PwTimeout, sync_playwright

KATALOG = Path(__file__).resolve().parent
MASKA = "••••••••"

# Teksty z portal/mcod (branch portal-aed): forms.py, models.py, settings/base.py, tuaed_dane_testowe.py.
ETYKIETA_WYKAZ = "Wykaz AED"
ZBIOR_DOSTAWCY = "Defibrylatory AED w Przemyślu"
ZBIOR_ZBIORCZY = "Defibrylatory AED: wykaz zbiorczy"
SLOWA_BLEDU = ("błąd", "blad", "błędem", "niepoprawny")
ZASOB_Z_BLEDEM = "Defibrylatory AED: Gmina (pokaz) (CSV)"  # z portal/tuaed_e2e.sh (sesja D)

# Przed każdym zrzutem: tokeny w tekście i atrybutach zamieniamy na maskę, pola haseł czyścimy.
MASKUJ_JS = r"""(maska) => {
  const wzor = /(token[=:]\s*|csrfmiddlewaretoken=|Bearer\s+)[A-Za-z0-9._~+\/=-]{6,}/gi;
  const dlugi = /\b[A-Za-z0-9_-]{32,}\b/g;  // długie losowe ciągi (tokeny, klucze)
  const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  let n = 0;
  while (w.nextNode()) {
    const t = w.currentNode.nodeValue;
    const nowy = t.replace(wzor, (_, p) => p + maska).replace(dlugi, maska);
    if (nowy !== t) { w.currentNode.nodeValue = nowy; n++; }
  }
  for (const a of document.querySelectorAll("a[href*='token'], a[title*='token']")) {
    a.setAttribute("href", "#"); a.removeAttribute("title");
  }
  for (const i of document.querySelectorAll("input[type=password]")) { i.value = ""; }
  return n;
}"""

# Podświetlenie elementu, o który chodzi na zrzucie (ramka w kolorze kampanii).
PODSWIETL_JS = """(el) => { el.style.outline = '4px solid #008c15'; el.style.outlineOffset = '4px';
  el.style.borderRadius = '6px'; el.scrollIntoView({block: 'center'}); }"""

# Raport scalania (JSONField, tylko do odczytu) pokazujemy jako sformatowany JSON.
RAPORT_JS = """() => {
  const el = document.querySelector('.field-report .readonly, .field-report p, .field-report div.readonly');
  if (!el) return false;
  try {
    const dane = JSON.parse(el.textContent);
    const pre = document.createElement('pre');
    pre.textContent = JSON.stringify(dane, null, 2);
    pre.style.cssText = 'white-space:pre-wrap;font:13px/1.45 ui-monospace,Menlo,monospace;max-width:1100px;margin:0';
    el.replaceWith(pre);
    return true;
  } catch (e) { return false; }
}"""


class Portal:
    def __init__(self, page: Page, baza: str):
        self.p = page
        self.baza = baza
        self.zapisane: list[str] = []
        self.pominiete: list[str] = []

    def idz(self, sciezka: str) -> None:
        self.p.goto(self.baza + sciezka, wait_until="domcontentloaded")
        self.p.wait_for_load_state("networkidle", timeout=30_000)

    def zrob(self, nazwa: str, pelna: bool = True) -> None:
        self.p.evaluate(MASKUJ_JS, MASKA)
        plik = KATALOG / f"{nazwa}.png"
        self.p.screenshot(path=str(plik), full_page=pelna, animations="disabled",
                          mask=[self.p.locator("input[type=password]")])
        self.zapisane.append(plik.name)
        print("  zapisano", plik.name)

    def pomin(self, nazwa: str, powod: str) -> None:
        self.pominiete.append(f"{nazwa}: {powod}")
        print(f"  POMINIĘTO {nazwa}: {powod}")

    def zaloguj(self, login: str, haslo: str) -> None:
        self.idz("/login/")
        self.p.fill("#id_username", login)
        self.p.fill("#id_password", haslo)
        self.p.locator("#login-form [type=submit]").click()
        self.p.wait_for_load_state("networkidle")
        if "/login" in self.p.url:
            sys.exit("Logowanie nieudane: sprawdź --login i PORTAL_HASLO (dane testowe w portal/URUCHOMIENIE-TUAED.md).")
        print("zalogowano jako", login)

    def otworz_z_listy(self, lista: str, szukaj: str, tekst_linku: str | re.Pattern) -> bool:
        """Changelist Django admina z wyszukiwaniem (search_fields: title), potem link do obiektu."""
        self.idz(f"{lista}?q={quote(szukaj)}")
        link = self.p.locator("#result_list").get_by_role("link", name=tekst_linku).first
        try:
            link.wait_for(timeout=10_000)
        except PwTimeout:
            return False
        link.click()
        self.p.wait_for_load_state("networkidle")
        return True

    def zakladka(self, nazwa: str) -> bool:
        """Zakładki django-suit (#general, #data, …)."""
        tab = self.p.locator(f".nav-tabs a[href='#{nazwa}'], a[href='#{nazwa}']").first
        if not tab.count():
            return False
        tab.click()
        self.p.wait_for_timeout(500)
        return True


def ekran_formularz_i_walidacja(pt: Portal) -> None:
    print("1, 2a: zasób-wykaz dostawcy (formularz i walidacja)")
    if not pt.otworz_z_listy("/resources/resource/", ZBIOR_DOSTAWCY, re.compile(re.escape(ZBIOR_DOSTAWCY))):
        pt.pomin("portal-01", f"nie ma zasobu „{ZBIOR_DOSTAWCY}” (czy uruchomiono tuaed_dane_testowe.py?)")
        return
    adres_zasobu = pt.p.url.split("#")[0]
    pt.zakladka("general")
    pole = pt.p.locator(".field-is_aed_list, .form-row:has(label:text-is('%s:'))" % ETYKIETA_WYKAZ).first
    if pole.count():
        pt.p.evaluate(PODSWIETL_JS, pole.element_handle())
        pt.p.wait_for_timeout(300)
        pt.zrob("portal-01-formularz-wykaz-aed", pelna=False)
    else:
        pt.pomin("portal-01", f"brak pola „{ETYKIETA_WYKAZ}” w formularzu (migracja 0075 zastosowana?)")

    pt.p.goto(adres_zasobu, wait_until="networkidle")
    if pt.zakladka("data"):
        pt.zrob("portal-02a-walidacja-poprawny")
    else:
        pt.pomin("portal-02a", "brak zakładki walidacji danych (zasób jeszcze się nie pobrał? sprawdź Flower :5555)")


def ekran_blad_slownika(pt: Portal, tytul: str | None) -> None:
    print("2b: zasób-wykaz z błędem słownika")
    if tytul:
        ok = pt.otworz_z_listy("/resources/resource/", tytul, re.compile(re.escape(tytul)))
    else:
        pt.idz("/resources/resource/?q=" + quote("Defibrylatory AED"))
        linki = pt.p.locator("#result_list a").all()
        cel = next((a for a in linki if any(s in (a.inner_text() or "").lower() for s in SLOWA_BLEDU)), None)
        ok = bool(cel)
        if cel:
            cel.click()
            pt.p.wait_for_load_state("networkidle")
    if not ok:
        pt.pomin("portal-02b", "nie znaleziono zasobu-wykazu z błędem słownika; podaj --zasob-z-bledem 'tytuł'")
        return
    if pt.zakladka("data"):
        pt.zrob("portal-02b-walidacja-blad-slownika")
    else:
        pt.pomin("portal-02b", "brak zakładki walidacji danych")


def ekran_zbior_zbiorczy(pt: Portal) -> None:
    print("3: zbiór zbiorczy i jego zasoby")
    if pt.otworz_z_listy("/datasets/dataset/", ZBIOR_ZBIORCZY, ZBIOR_ZBIORCZY):
        pt.zrob("portal-03a-zbior-wykaz-zbiorczy")
    else:
        pt.pomin("portal-03a", f"nie ma zbioru „{ZBIOR_ZBIORCZY}” (uruchom create_main_aed_resource_task)")
    pt.idz("/resources/resource/?q=" + quote(ZBIOR_ZBIORCZY))
    wiersze = pt.p.locator("#result_list tbody tr")
    if wiersze.count():
        pt.zrob("portal-03b-zasoby-csv-xlsx", pelna=False)
    else:
        pt.pomin("portal-03b", "brak zasobów zbioru zbiorczego")


def ekran_raport(pt: Portal) -> None:
    print("4: Wykaz zbiorczy AED (AggregatedAEDInfo)")
    pt.idz("/resources/aggregatedaedinfo/")
    link = pt.p.locator("#result_list tbody tr a").first
    if not link.count():
        pt.pomin("portal-04", "brak wpisu „Wykaz zbiorczy AED” (scalanie jeszcze nie działało)")
        return
    link.click()
    pt.p.wait_for_load_state("networkidle")
    pt.p.evaluate(RAPORT_JS)
    pt.zrob("portal-04-wykaz-zbiorczy-raport")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--url", default=os.environ.get("PORTAL_URL", "http://localhost:8101"))
    ap.add_argument("--login", default=os.environ.get("PORTAL_LOGIN", "admin@tuaed.local"))
    # Zasób z błędem słownika zakłada test e2e D (portal/tuaed_e2e.sh): dostepnosc = „dla wszystkich”.
    ap.add_argument("--zasob-z-bledem", default=os.environ.get("PORTAL_ZASOB_Z_BLEDEM", ZASOB_Z_BLEDEM))
    a = ap.parse_args()
    haslo = os.environ.get("PORTAL_HASLO")
    if not haslo:
        sys.exit("Ustaw PORTAL_HASLO (hasło konta testowego z portal/URUCHOMIENIE-TUAED.md). Hasła nie trzymamy w repo.")

    with sync_playwright() as pw:
        przegl = pw.chromium.launch(args=["--lang=pl-PL"])
        ctx = przegl.new_context(viewport={"width": 1440, "height": 900}, locale="pl-PL", device_scale_factor=2)
        pt = Portal(ctx.new_page(), a.url.rstrip("/"))
        pt.zaloguj(a.login, haslo)
        for krok in (ekran_formularz_i_walidacja, lambda p: ekran_blad_slownika(p, a.zasob_z_bledem),
                     ekran_zbior_zbiorczy, ekran_raport):
            try:
                krok(pt)
            except Exception as e:  # jeden ekran nie blokuje pozostałych
                pt.pomin(getattr(krok, "__name__", "ekran"), f"{type(e).__name__}: {e}")
        przegl.close()

    print("\nzapisane:", ", ".join(pt.zapisane) or "brak")
    if pt.pominiete:
        print("pominięte:\n  " + "\n  ".join(pt.pominiete))
        sys.exit(1)


if __name__ == "__main__":
    main()
