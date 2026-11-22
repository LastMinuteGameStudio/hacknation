"""E1: dowód dla portalu. Pobiera /d/{slug}.csv tak jak harvester dane.gov.pl (bez ciasteczek, prosty
User-Agent), sprawdza RFC 4180, UTF-8 i zgodność z metadanymi CSVW, wynik zapisuje w DOWOD-URL.md.

    python3 prezentacja/zrzuty/sprawdz_url.py [https://tuaed.wkrynski.dev/d/<slug>.csv]

Bez argumentu bierze url_csv z ostatnie_uruchomienie.json (zrob_zrzuty.py). Tylko biblioteka standardowa.
"""

from __future__ import annotations

import csv
import io
import json
import re
import sys
import urllib.request
from datetime import date, datetime, timezone
from pathlib import Path

KATALOG = Path(__file__).resolve().parent
UA = "Mozilla/5.0 (compatible; harvester-test)"
POKAZ_NAGLOWKI = ("content-type", "content-length", "content-disposition", "access-control-allow-origin",
                  "cache-control", "last-modified", "etag", "link", "set-cookie")


def pobierz(url: str):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.status, {k.lower(): v for k, v in r.headers.items()}, r.read()


def zgodny_tytul(kolumna: dict, naglowek: str) -> bool:
    """CSVW (tabular-metadata §5.5.1): kolumna z nagłówka pliku nie ma `name`, więc musi mieć wspólny tytuł."""
    t = kolumna.get("titles")
    if t is None:
        return True  # brak tytułów: walidator nie ma czego porównywać
    if isinstance(t, str):
        t = [t]
    elif isinstance(t, dict):
        t = [x for v in t.values() for x in (v if isinstance(v, list) else [v])]
    return naglowek in t


TYPY = {
    "decimal": lambda v: re.fullmatch(r"-?\d+(\.\d+)?", v),
    "double": lambda v: re.fullmatch(r"-?\d+(\.\d+)?([eE]-?\d+)?", v),
    "integer": lambda v: re.fullmatch(r"-?\d+", v),
    "boolean": lambda v: v in ("true", "false"),
    "date": lambda v: date.fromisoformat(v),
    "dateTime": lambda v: datetime.fromisoformat(v),
}


def sprawdz_typ(dt, v: str) -> bool:
    baza = dt.get("base") if isinstance(dt, dict) else dt
    fmt = dt.get("format") if isinstance(dt, dict) else None
    try:
        if baza in TYPY and not TYPY[baza](v):
            return False
    except ValueError:
        return False
    if fmt and baza in ("string", None) and not re.fullmatch(fmt, v):
        return False
    return True


def main():
    url = sys.argv[1] if len(sys.argv) > 1 else json.loads((KATALOG / "ostatnie_uruchomienie.json").read_text())["url_csv"]
    status, nagl, tresc = pobierz(url)
    wyniki: list[tuple[bool, str]] = []

    def ok(warunek, opis):
        wyniki.append((bool(warunek), opis))

    ok(status == 200, f"HTTP {status} bez ciasteczek i logowania")
    ok("set-cookie" not in nagl, "serwer nie ustawia ciasteczek")
    ok(nagl.get("content-type", "").startswith("text/csv") and "utf-8" in nagl.get("content-type", "").lower(),
       f"Content-Type: {nagl.get('content-type')}")
    ok(nagl.get("access-control-allow-origin") == "*", "CORS `*` (pobranie z przeglądarki, np. mapa w JS)")
    ok("inline" in nagl.get("content-disposition", "inline"), f"Content-Disposition: {nagl.get('content-disposition', '(brak)')}")

    # UTF-8
    try:
        tekst = tresc.decode("utf-8", errors="strict")
        ok(True, "poprawne UTF-8 (dekodowanie ścisłe)")
    except UnicodeDecodeError as e:
        tekst = tresc.decode("utf-8", errors="replace")
        ok(False, f"błąd UTF-8: {e}")
    ok(not tekst.startswith("﻿"), "bez BOM")

    # RFC 4180
    ok(tekst.endswith("\r\n"), "ostatni wiersz zakończony CRLF")
    bez_cytatow = re.sub(r'"(?:[^"]|"")*"', "", tekst)
    ok("\n" not in bez_cytatow.replace("\r\n", "") and "\r" not in bez_cytatow.replace("\r\n", ""),
       "separator wierszy wyłącznie CRLF (poza polami w cudzysłowie)")
    wiersze = list(csv.reader(io.StringIO(tekst, newline=""), strict=True))
    naglowek, dane = wiersze[0], wiersze[1:]
    zle = [i + 2 for i, w in enumerate(dane) if len(w) != len(naglowek)]
    ok(not zle, f"{len(dane)} rekordów, każdy ma {len(naglowek)} pól jak nagłówek" + (f" (złe: {zle[:5]})" if zle else ""))
    buf = io.StringIO()
    csv.writer(buf, lineterminator="\r\n", quoting=csv.QUOTE_MINIMAL).writerows(wiersze)
    ok(buf.getvalue() == tekst, "cudzysłowy tylko tam, gdzie trzeba, `\"` podwojone (identyczny zapis RFC 4180)")
    ok(len(set(naglowek)) == len(naglowek), "nazwy kolumn unikalne")

    # CSVW
    url_meta = url + "-metadata.json"
    s2, nagl_meta, meta_b = pobierz(url_meta)
    meta = json.loads(meta_b)
    ok(s2 == 200, f"metadane CSVW pod `{url_meta}` (HTTP {s2})")
    ok(meta.get("url") == url, "`url` w metadanych wskazuje ten plik")
    d = meta.get("dialect", {})
    ok(d.get("encoding", "utf-8").lower() == "utf-8" and d.get("delimiter", ",") == "," and d.get("header", True),
       "dialekt: UTF-8, przecinek, wiersz nagłówka")
    kol = [c for c in meta["tableSchema"]["columns"] if not c.get("virtual")]
    ok([c["name"] for c in kol] == naglowek, f"kolumny w metadanych = nagłówek pliku ({len(kol)}, ta sama kolejność)")
    niezgodne = [c["name"] for c, h in zip(kol, naglowek) if not zgodny_tytul(c, h)]
    ok(not niezgodne, "nagłówek zgodny z `titles` (CSVW §5.5.1, sprawdza to np. csvlint)" +
       (f": {len(niezgodne)} kolumn ma `titles` bez nazwy z nagłówka, np. `{niezgodne[0]}` → "
        f"`{kol[naglowek.index(niezgodne[0])].get('titles')}`" if niezgodne else ""))
    null = meta["tableSchema"].get("null", "")
    nulle = set(null if isinstance(null, list) else [null]) | {""}
    braki, typy = [], []
    for i, w in enumerate(dane):
        for c, v in zip(kol, w):
            if v in nulle:
                if c.get("required"):
                    braki.append((i + 2, c["name"]))
            elif "datatype" in c and not sprawdz_typ(c["datatype"], v):
                typy.append((i + 2, c["name"], v))
    ok(not braki, "pola `required` wypełnione" + (f" (braki: {braki[:5]})" if braki else ""))
    ok(not typy, "wartości zgodne z `datatype`/`format`" + (f" (złe: {typy[:5]})" if typy else ""))
    pk = meta["tableSchema"].get("primaryKey")
    if pk:
        idx = naglowek.index(pk)
        ok(len({w[idx] for w in dane}) == len(dane), f"`primaryKey` ({pk}) unikalny")
    ok(meta.get("dc:license") or meta.get("license"), f"licencja w metadanych: {meta.get('dc:license')}")

    # Raport
    teraz = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    pierwsze = "\r\n".join(tekst.split("\r\n")[:4])
    l = [
        "# Dowód: plik pod stałym URL pobierany tak jak przez dane.gov.pl",
        "",
        f"Wygenerowane przez `prezentacja/zrzuty/sprawdz_url.py` ({teraz}). Zbiór demo z dysponentem "
        "„Urząd Miejski w Przemyślu (demo)”, opublikowany przez `zrob_zrzuty.py` z pliku `przemysl_2024.csv`.",
        "",
        "## Zapytanie",
        "",
        "```",
        f"curl -sS -D - -A '{UA}' '{url}'",
        "```",
        "",
        "Bez ciasteczek, bez logowania i bez tokenu, tak jak harvester portalu przy „Aktualizacji automatycznej”.",
        "",
        "## Nagłówki odpowiedzi",
        "",
        "```",
        f"HTTP {status}",
        *[f"{k}: {nagl[k]}" for k in POKAZ_NAGLOWKI if k in nagl],
        "```",
        "",
        "## Pierwsze wiersze (surowo, `\\r\\n` na końcu linii)",
        "",
        "```csv",
        pierwsze,
        "```",
        "",
        f"## Walidacja: {sum(w for w, _ in wyniki)}/{len(wyniki)}",
        "",
        "| | Sprawdzenie |",
        "|---|---|",
        *[f"| {'✅' if w else '❌'} | {o} |" for w, o in wyniki],
        "",
        "Sprawdzenia RFC 4180: kodowanie, CRLF, stała liczba pól, cytowanie (zapis porównany bajt po bajcie z "
        "`csv.writer(QUOTE_MINIMAL)`). CSVW: metadane z `/d/{slug}.csv-metadata.json` (W3C Tabular Data), "
        f"wartości `{null}` i puste traktowane jako brak, zgodnie z `tableSchema.null`.",
        "",
    ]
    (KATALOG / "DOWOD-URL.md").write_text("\n".join(l), encoding="utf-8")
    for w, o in wyniki:
        print("OK " if w else "ŹLE", o)
    return 0 if all(w for w, _ in wyniki) else 1


if __name__ == "__main__":
    sys.exit(main())
