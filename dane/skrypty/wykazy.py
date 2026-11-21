#!/usr/bin/env python3
"""Parsuje wykazy AED bez współrzędnych (HTML/PDF) i geokoduje adresy przez Nominatim (OSM).

Wejście:  dane/surowe/wykazy/*.html, lublin.txt (tekst z PDF, patrz README)
Wyjście:  dane/surowe/wykazy/wykazy_geokod.json  (lista rekordów z lat/lon albo bez, gdy geokodowanie zawiodło)
Cache:    dane/surowe/wykazy/geokod_cache.json  (zapytanie -> wynik), żeby nie pytać Nominatim ponownie.

Zasady Nominatim: max 1 zapytanie/s, identyfikujący User-Agent.
"""
import html, json, re, sys, time, urllib.parse, urllib.request
from html.parser import HTMLParser
from pathlib import Path

W = Path(__file__).resolve().parent.parent / "surowe" / "wykazy"
CACHE_F = W / "geokod_cache.json"
UA = "aed-agregacja-hackathon/0.1 (+https://wiki.openstreetmap.org/wiki/Nominatim)"


class Tabele(HTMLParser):
    def __init__(s):
        super().__init__(); s.tables = []; s.cell = None; s.row = None

    def handle_starttag(s, t, a):
        if t == "table": s.tables.append([])
        elif t == "tr" and s.tables: s.row = []
        elif t in ("td", "th") and s.row is not None: s.cell = []
        elif t == "br" and s.cell is not None: s.cell.append(" ")

    def handle_endtag(s, t):
        if t in ("td", "th") and s.cell is not None:
            s.row.append(" ".join("".join(s.cell).split())); s.cell = None
        elif t == "tr" and s.row is not None:
            s.tables[-1].append(s.row); s.row = None

    def handle_data(s, d):
        if s.cell is not None: s.cell.append(d)


def tabele(name):
    p = Tabele(); p.feed((W / name).read_text(encoding="utf-8", errors="ignore")); return p.tables


def r(zrodlo, i, nazwa, adres, miasto, **kw):
    return dict(zrodlo=zrodlo, id_zrodlowe=str(i), nazwa_obiektu=nazwa.strip(), adres=adres.strip(), miejscowosc=miasto, **kw)


ULICA = re.compile(r"((?:ul\.|al\.|aleja|aleje|pl\.|plac|os\.|osiedle)\s*[^,()]+?\d+[A-Za-z]?(?:/\d+)?)", re.I)


def ulica(txt):
    m = ULICA.search(txt)
    return m.group(1) if m else txt


def gdansk():
    for row in tabele("gdansk.html")[0][1:]:
        if len(row) < 3 or not row[0].isdigit():
            continue
        adr = row[1]
        zew = row[3].lower() if len(row) > 3 else ""
        nazwa = re.search(r"\(([^)]+)\)", adr)
        yield r("gdansk_um_2022", row[0], nazwa.group(1) if nazwa else adr, ulica(re.sub(r"\([^)]*\)", "", adr)), "Gdańsk",
                opis_lokalizacji=row[2], wewnatrz_budynku="false" if "zewn" in zew else ("true" if "wewn" in zew else ""),
                godziny_dostepnosci=row[4] if len(row) > 4 else "")


def gliwice():
    for row in tabele("gliwice.html")[0][2:]:
        if len(row) < 6 or not row[0].isdigit():
            continue
        szcz = row[4].lower()
        yield r("gliwice_crg", row[0], row[1], row[3], "Gliwice", dzielnica=row[2], opis_lokalizacji=row[4],
                wewnatrz_budynku="false" if "zewn" in szcz else ("true" if "wewn" in szcz else ""),
                godziny_dostepnosci=row[5], dostepny_24_7="tak" if "całodob" in row[5].lower() else "")


def wopr():
    miasta = ["Szczecin", "Koszalin", "Świnoujście", "Stargard", "Kołobrzeg"]  # kolejność nagłówków nad tabelami
    for t, miasto in zip(tabele("wopr_zp.html"), miasta):
        for row in t[1:]:
            if len(row) < 3 or not row[1]:
                continue
            yield r("wopr_zachodniopomorskie", f"{miasto}-{row[0].rstrip('.')}", row[1], row[2], miasto)


def lublin():
    seen = set()
    for line in (W / "lublin.txt").read_text(encoding="utf-8").splitlines():
        m = re.match(r"\s*(\d+)\.\s+(.*)", line)
        if not m:
            continue
        txt = " ".join(m.group(2).split())
        key = re.sub(r"\W", "", ulica(txt).lower())   # duplikaty po adresie
        if key in seen:          # PDF ma powtórzone pozycje (np. Radio Lublin, AGRO II)
            continue
        seen.add(key)
        adr = ulica(txt)
        nazwa = txt.replace(adr, "").strip(" ,:-") or txt
        yield r("lublin_um", m.group(1), nazwa, adr, "Lublin")


def chelm():
    s = (W / "chelm.html").read_text(encoding="utf-8", errors="ignore")
    t = html.unescape(re.sub(r"<[^>]+>", "\n", s))
    i = 0
    for line in t.splitlines():
        m = re.match(r"\s*([^-–]+?)\s+-\s+(.+?),\s*(.+?)[,.]?\s*$", line)
        if m and ("ul." in line or "al." in line):
            i += 1
            yield r("chelm_um", i, m.group(2), ulica(m.group(3)) if ULICA.search(m.group(3)) else m.group(3), "Chełm",
                    dzielnica=m.group(1))


def nominatim(q, cache):
    if q in cache:
        return cache[q]
    url = "https://nominatim.openstreetmap.org/search?" + urllib.parse.urlencode(
        {"q": q, "format": "jsonv2", "countrycodes": "pl", "limit": 1, "addressdetails": 0})
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "pl"})
    time.sleep(1.1)
    try:
        res = json.load(urllib.request.urlopen(req, timeout=30))
    except Exception as e:
        print("  błąd", q, e, file=sys.stderr); return None
    cache[q] = res[0] if res else None
    return cache[q]


def oczysc(adr):
    a = re.sub(r"\b(ul\.|al\.|ulica)\s*", "", adr, flags=re.I)
    a = re.sub(r"\b(parter|PARTER)\b.*", "", a)
    return " ".join(a.split()).strip(" ,")


def main():
    cache = json.loads(CACHE_F.read_text()) if CACHE_F.exists() else {}
    out = []
    for fn in (gdansk, gliwice, wopr, lublin, chelm):
        rows = list(fn())
        print(f"{fn.__name__:8s} {len(rows)}", file=sys.stderr)
        out += rows
    ok = 0
    for i, x in enumerate(out):
        q1 = f'{oczysc(x["adres"])}, {x["miejscowosc"]}'
        g = nominatim(q1, cache)
        tryb = "adres"
        if not g:                                      # druga próba: nazwa obiektu + miasto
            g = nominatim(f'{x["nazwa_obiektu"]}, {x["miejscowosc"]}', cache); tryb = "nazwa"
        if g:
            ok += 1
            x.update(lat=float(g["lat"]), lon=float(g["lon"]), geokod_tryb=tryb,
                     geokod_typ=f'{g.get("category", "")}/{g.get("type", "")}', geokod_nazwa=g.get("display_name", ""))
        if i % 25 == 0:
            CACHE_F.write_text(json.dumps(cache, ensure_ascii=False))
            print(f"  {i}/{len(out)} ok={ok}", file=sys.stderr)
    CACHE_F.write_text(json.dumps(cache, ensure_ascii=False))
    (W / "wykazy_geokod.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))
    print(f"razem {len(out)}, zgeokodowane {ok}", file=sys.stderr)


if __name__ == "__main__":
    main()
