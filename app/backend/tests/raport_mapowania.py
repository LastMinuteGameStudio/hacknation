"""D2: raport jakości mapowania kolumn na fixturach (realne pliki + syntetyczne XLSX).

Uruchomienie (z app/backend):
    .venv/bin/python -m tests.raport_mapowania            # mapowanie
    .venv/bin/python -m tests.raport_mapowania --rekordy  # + porównanie rekordów po normalizacji
    .venv/bin/python -m tests.raport_mapowania --strict   # kod wyjścia 1, gdy plik „wymaga_100” ma < 100%

Oczekiwania: tests/fixtury/oczekiwane/*.json. Próg decyzji o modelu AI: patrz DEMO.md / tablica.
"""

from __future__ import annotations

import argparse
import sys
import traceback

from tests.fixtury import oczekiwania as oc


def _krotko(e: BaseException) -> str:
    if isinstance(e, NotImplementedError):
        return f"NIE ZAIMPLEMENTOWANE ({e})"
    return f"{type(e).__name__}: {e}"


def raport(rekordy: bool = False, verbose: bool = False) -> tuple[list[dict], bool]:
    from aed_core.mapping import suggest_mapping

    sch = oc.schema()
    wyniki, ok_wymagane = [], True
    for exp in oc.wszystkie():
        w = {"plik": exp["plik"], "wymaga_100": exp.get("wymaga_100", False), "procent": None, "blad": None}
        print(f"\n=== {exp['plik']}{'  [WYMAGA 100%]' if w['wymaga_100'] else ''}")
        try:
            t = oc.wczytaj_tabele(exp)
            msgs = "; ".join(f"{m.poziom}:{m.kod}" for m in t.messages)
            print(f"    odczyt: {len(t.columns)} kolumn, {len(t.rows)} wierszy (oczekiwane {exp.get('liczba_wierszy')}), "
                  f"nagłówek w wierszu {t.header_row}{', komunikaty: ' + msgs if msgs else ''}")
            sug = suggest_mapping(t, sch)
            o = oc.ocen_mapowanie(exp, t, sug)
            w["procent"] = o.procent
            print(f"    mapowanie: {o.trafione}/{o.wszystkie} = {o.procent:.0f}%")
            for kol, oczek, got in o.pomylki:
                print(f"      ✗ {kol!r}: oczekiwane {oczek!r}, otrzymane {got!r}")
            if o.nadmiarowe:
                print(f"      ? kolumny spoza oczekiwań: {o.nadmiarowe}")
            if rekordy:
                try:
                    rec = oc.normalizuj(exp, t, o.mapowanie, sch)
                    roz = oc.porownaj_rekordy(exp, rec)
                    print(f"    rekordy: {len(rec)} (pominiętych {sum(r.pominiety for r in rec)}), różnic: {len(roz)}")
                    for r in roz:
                        print(f"      ✗ {r}")
                except Exception as e:  # noqa: BLE001
                    print(f"    rekordy: {_krotko(e)}")
                    if verbose and not isinstance(e, NotImplementedError):
                        traceback.print_exc()
        except Exception as e:  # noqa: BLE001
            w["blad"] = _krotko(e)
            print(f"    {w['blad']}")
            if verbose and not isinstance(e, NotImplementedError):
                traceback.print_exc()
        if w["wymaga_100"] and w["procent"] != 100.0:
            ok_wymagane = False
        wyniki.append(w)

    print("\n=== PODSUMOWANIE")
    print(f"{'plik':32} {'wymaga':7} {'trafność':>9}")
    for w in wyniki:
        p = f"{w['procent']:.0f}%" if w["procent"] is not None else "—"
        print(f"{w['plik']:32} {'tak' if w['wymaga_100'] else 'nie':7} {p:>9}  {w['blad'] or ''}")
    policzone = [w["procent"] for w in wyniki if w["procent"] is not None]
    if policzone:
        print(f"średnia trafność: {sum(policzone) / len(policzone):.0f}% na {len(policzone)} plikach")
    print("wymagane pliki (Krosno, Legionowo, Przemyśl, Warszawa) 100%:", "TAK" if ok_wymagane else "NIE")
    return wyniki, ok_wymagane


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--rekordy", action="store_true", help="porównaj też rekordy po normalizacji")
    ap.add_argument("--strict", action="store_true", help="kod wyjścia 1, gdy wymagany plik ma < 100%%")
    ap.add_argument("-v", "--verbose", action="store_true", help="pełne tracebacki")
    a = ap.parse_args()
    _, ok = raport(a.rekordy, a.verbose)
    return 1 if a.strict and not ok else 0


if __name__ == "__main__":
    sys.exit(main())
