"""E1: zrzuty stron dla odbiorców (/mapa, /dane) z publicznego demo. Niczego nie publikuje.

    /tmp/pw/bin/python prezentacja/zrzuty/zrob_zrzuty_strony.py [--url https://tuaed.wkrynski.dev]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).resolve().parent))
from zrob_zrzuty import Zrzuty  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="https://tuaed.wkrynski.dev")
    baza = ap.parse_args().url.rstrip("/")
    with sync_playwright() as pw:
        przegl = pw.chromium.launch(args=["--lang=pl-PL"])
        page = przegl.new_context(viewport={"width": 1440, "height": 900}, locale="pl-PL", device_scale_factor=2).new_page()
        z = Zrzuty(page)
        page.goto(baza + "/mapa")
        page.locator(".leaflet-marker-icon, .marker-cluster").first.wait_for(timeout=60_000)
        page.wait_for_timeout(1500)
        z.zrob("10-mapa", pelna=False)
        page.goto(baza + "/dane")
        page.get_by_role("heading", name="Zbiory dostawców").wait_for(timeout=60_000)
        page.wait_for_timeout(1500)
        z.zrob("10-dane", pelna=False)
        przegl.close()
    print("zrzuty:", z.zapisane)


if __name__ == "__main__":
    main()
