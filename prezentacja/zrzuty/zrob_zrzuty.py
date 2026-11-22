"""E1: zrzuty ekranu kreatora TuAED z publicznego demo (scenariusz z app/backend/tests/fixtury/DEMO.md).

Uruchomienie (ponownie w dowolnym momencie, nadpisuje PNG):
    python3 -m venv /tmp/pw && /tmp/pw/bin/pip install playwright && /tmp/pw/bin/playwright install chromium
    /tmp/pw/bin/python prezentacja/zrzuty/zrob_zrzuty.py [--url https://tuaed.wkrynski.dev]

Każde uruchomienie publikuje NOWY zbiór z dysponentem „Urząd Miejski w Przemyślu (demo)”.
Token edycji nie trafia do repo ani na zrzuty: przed każdym zrzutem podmieniamy go w DOM na „••••”.
Jeśli potrzebny jest link edycji (np. do usunięcia zbioru), ustaw ZRZUTY_TOKEN_PLIK=/ścieżka/poza/repo.
"""

from __future__ import annotations

import argparse
import html
import json
import os
import re
from pathlib import Path

from playwright.sync_api import Page, sync_playwright

KATALOG = Path(__file__).resolve().parent
REPO = KATALOG.parents[1]
PLIK_DEMO = REPO / "app/backend/tests/fixtury/przemysl_2024.csv"
DYSPONENT = "Urząd Miejski w Przemyślu (demo)"
STALE = {"wewnatrz_budynku": "false", "dostepnosc": "publiczny", "dostepny_24_7": "tak"}
SZEROKOSCI = (1440, 320)
MASKA = "••••••••"

CSV_HTML = """<!doctype html><meta charset="utf-8"><title>CSV</title>
<style>body{{font:14px/1.45 ui-monospace,Menlo,monospace;margin:24px;color:#111}}
h1{{font:600 18px system-ui;margin:0 0 8px}} .n{{color:#555;margin:0 0 16px;white-space:pre-wrap}}
pre{{white-space:pre;overflow:hidden;background:#f6f8f6;border:1px solid #cfd8cf;padding:12px;font-size:12px}}</style>
<h1>GET {url} → {status}</h1><p class="n">{naglowki}</p><pre>{csv}</pre>"""

MASKUJ_JS = """(token) => {
  if (!token) return 0;
  let n = 0;
  const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  while (w.nextNode()) {
    const t = w.currentNode;
    if (t.nodeValue.includes(token)) { t.nodeValue = t.nodeValue.split(token).join('%s'); n++; }
  }
  for (const el of document.querySelectorAll('input, textarea')) {
    if (el.value && el.value.includes(token)) { el.value = el.value.split(token).join('%s'); n++; }
  }
  for (const a of document.querySelectorAll('a[href]')) {
    if (a.href.includes(token)) { a.setAttribute('href', a.href.split(token).join('ukryty')); n++; }
  }
  return n;
}""" % (MASKA, MASKA)


class Zrzuty:
    def __init__(self, page: Page):
        self.page = page
        self.token: str | None = None
        self.zapisane: list[str] = []

    def _przygotuj(self):
        p = self.page
        p.evaluate(MASKUJ_JS, self.token)
        if self.token:
            tekst = p.evaluate("document.body.innerText + [...document.querySelectorAll('input')].map(i=>i.value).join(' ')")
            assert self.token not in tekst, "token widoczny na stronie"
        # bez migającego kursora i fokusu (rama fokusu po zmianie kroku wygląda na zrzucie jak błąd)
        p.evaluate("document.activeElement && document.activeElement.blur && document.activeElement.blur()")

    def zakres(self, nazwa: str, od: str, do: str, margines: int = 16):
        """Zrzut wycinka strony od górnej krawędzi elementu `od` do dolnej krawędzi `do` (oba szerokości)."""
        p = self.page
        for szer in SZEROKOSCI:
            p.set_viewport_size({"width": szer, "height": 900})
            p.wait_for_timeout(250)
            self._przygotuj()
            a = p.locator(od).first.bounding_box()
            b = p.locator(do).first.bounding_box()
            sy = p.evaluate("window.scrollY")
            y0 = max(0, a["y"] + sy - margines)
            y1 = b["y"] + sy + b["height"] + margines
            plik = KATALOG / f"{nazwa}-{szer}.png"
            p.screenshot(path=str(plik), full_page=True, animations="disabled",
                         clip={"x": 0, "y": y0, "width": szer, "height": y1 - y0})
            self.zapisane.append(plik.name)
        p.set_viewport_size({"width": SZEROKOSCI[0], "height": 900})

    def zrob(self, nazwa: str, element: str | None = None, pelna: bool = True):
        """Zrzut w obu szerokościach. nazwa bez sufiksu, np. '09-krok2-mapowanie'."""
        p = self.page
        for szer in SZEROKOSCI:
            p.set_viewport_size({"width": szer, "height": 900})
            p.wait_for_timeout(250)
            self._przygotuj()
            plik = KATALOG / f"{nazwa}-{szer}.png"
            if element:
                loc = p.locator(element).first
                loc.scroll_into_view_if_needed()
                loc.screenshot(path=str(plik), animations="disabled")
            else:
                p.screenshot(path=str(plik), full_page=pelna, animations="disabled")
            self.zapisane.append(plik.name)
        p.set_viewport_size({"width": SZEROKOSCI[0], "height": 900})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="https://tuaed.wkrynski.dev")
    ap.add_argument("--headed", action="store_true")
    a = ap.parse_args()
    baza = a.url.rstrip("/")

    with sync_playwright() as pw:
        przegl = pw.chromium.launch(headless=not a.headed, args=["--lang=pl-PL"])
        ctx = przegl.new_context(viewport={"width": 1440, "height": 900}, locale="pl-PL", device_scale_factor=2)
        page = ctx.new_page()
        z = Zrzuty(page)

        publikacja: dict = {}

        def przechwyc(resp):
            if re.search(r"/api/importy/[^/]+/publikacja$", resp.url) and resp.status == 200:
                publikacja.update(resp.json())

        page.on("response", przechwyc)

        # Strona startowa
        page.goto(baza + "/")
        page.get_by_role("button", name="Zacznij").wait_for()
        z.zrob("09-start")

        # Krok 1: dysponent
        page.get_by_role("button", name="Zacznij").click()
        page.locator("#d-nazwa").fill(DYSPONENT)
        page.locator("#d-typ option[value='jst']").wait_for(state="attached")
        page.locator("#d-typ").select_option("jst")
        z.zrob("09-krok1-dysponent")

        # Krok 2: wgranie, mapowanie, wartości stałe
        page.get_by_role("button", name="Dalej: dane").click()
        page.locator("#plik").set_input_files(str(PLIK_DEMO))
        page.get_by_role("button", name="Wgraj plik").click()
        page.locator("table.mapowanie").wait_for(timeout=60_000)
        z.zrob("09-krok2-mapowanie-tabela", element="table.mapowanie")
        for pole, wartosc in STALE.items():
            page.locator(f"#stala-{pole}").select_option(wartosc)
        z.zakres("09-krok2-wartosci-stale", "h2:has-text('Ustaw dla wszystkich AED')", "button:has-text('Sprawdź dane')")
        z.zakres("09-krok2-mapowanie", "h1#naglowek-kroku", "table.mapowanie tbody tr:nth-child(2)")

        # Krok 2b: walidacja i komunikaty
        page.get_by_role("button", name="Sprawdź dane").click()
        page.get_by_role("heading", name="Wynik sprawdzenia").wait_for(timeout=180_000)
        page.wait_for_timeout(300)
        z.zakres("09-krok2-walidacja", "h2:has-text('Wynik sprawdzenia')", "details summary:has-text('Podgląd wyniku')")
        page.locator("details summary:has-text('Podgląd wyniku')").click()
        z.zrob("09-krok2-podglad-wyniku", element="details:has(summary:has-text('Podgląd wyniku'))")

        # Krok 3: zgoda i publikacja
        page.get_by_role("button", name="Dalej: publikacja").click()
        page.locator("#zgoda-cc0").check()
        z.zrob("09-krok3-zgoda")
        page.get_by_role("button", name="Opublikuj").click()
        page.get_by_role("heading", name="Dane opublikowane").wait_for(timeout=60_000)
        page.wait_for_timeout(300)
        assert publikacja.get("token_edycji"), "brak odpowiedzi publikacji"
        z.token = publikacja["token_edycji"]
        slug, url_csv, url_edycji = publikacja["slug"], publikacja["url_csv"], publikacja["url_edycji"]
        z.zrob("09-krok3-publikacja")

        if os.environ.get("ZRZUTY_TOKEN_PLIK"):
            Path(os.environ["ZRZUTY_TOKEN_PLIK"]).write_text(url_edycji + "\n", encoding="utf-8")

        # Edycja przez prywatny link: sekcja „Źródło automatyczne”
        page.goto(url_edycji)
        page.get_by_role("heading", name="Źródło automatyczne (opcjonalnie)").wait_for(timeout=30_000)
        page.locator(".zrodlo .ramka").first.wait_for()
        z.zrob("09-edycja-zrodlo-automatyczne")
        z.zrob("09-edycja-zrodlo-automatyczne-sekcja", element="section.zrodlo")

        # Wynikowy CSV w przeglądarce (tak, jak go widzi każdy odbiorca)
        # Serwer wysyła CSV jako plik do pobrania (Content-Disposition), więc przeglądarka go nie wyświetla.
        # Pobieramy go bez ciasteczek i pokazujemy surowy tekst w <pre> z adresem i nagłówkami odpowiedzi.
        odp = pw.request.new_context().get(url_csv)
        naglowki = {k: v for k, v in odp.headers.items() if k in ("content-type", "content-disposition", "access-control-allow-origin")}
        tekst = odp.body().decode("utf-8")
        page.set_content(CSV_HTML.format(
            url=html.escape(url_csv), status=odp.status,
            naglowki=html.escape("\n".join(f"{k}: {v}" for k, v in naglowki.items())),
            csv=html.escape("\n".join(tekst.splitlines()[:12]))))
        z.zrob("08-csv-w-przegladarce")

        # Dokumentacja API
        page.goto(baza + "/docs")
        page.locator(".swagger-ui .opblock").first.wait_for(timeout=30_000)
        z.zrob("10-docs-api", pelna=False)

        przegl.close()

    (KATALOG / "ostatnie_uruchomienie.json").write_text(json.dumps({
        "demo": baza, "slug": slug, "url_csv": url_csv, "dysponent": DYSPONENT,
        "plik": str(PLIK_DEMO.relative_to(REPO)), "zrzuty": z.zapisane,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"slug={slug}\nurl_csv={url_csv}\nzrzutów: {len(z.zapisane)} w {KATALOG.relative_to(REPO)}")


if __name__ == "__main__":
    main()
