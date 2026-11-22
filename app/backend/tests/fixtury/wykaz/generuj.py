"""Wykaz drugiego dostawcy do testu e2e wykazu AED w portalu (JURY.md, sekcja 3).

„Szpital Wojewódzki w Przemyślu (test TuAED)”: 3 AED w zakresie v0.5, przepuszczone przez rdzeń TuAED.
- SZP-1 leży 15 m od „ADM Centrum” z wykazu Przemyśla (kznsks42) → duplikat (próg 30 m),
- SZP-2 leży 45 m od „I Liceum” z wykazu Przemyśla → nie duplikat,
- SZP-3 bez odpowiednika.
Każdy ma numer_seryjny (pole niepubliczne: jest w pliku pełnym, nie trafia do wykazu zbiorczego).

    cd app/backend && .venv/bin/python -m tests.fixtury.wykaz.generuj
"""

import csv
import io
from datetime import date
from pathlib import Path

from aed_core.export import to_csv
from aed_core.mapping import suggest_mapping
from aed_core.normalize import normalize_table
from aed_core.parsers import read_table
from aed_core.types import Provider
from aed_core.validate import validate_records
from tests.fixtury import oczekiwania as oc

KATALOG = Path(__file__).resolve().parent
M = 111320.0  # metrów na stopień szerokości
ZRODLO = [
    ("SZP-1", "Szpital Wojewódzki – wejście od ul. Słowackiego", 49.7812096 + 15 / M, 22.7750936, "Juliusza Słowackiego", "12"),
    ("SZP-2", "Szpital Wojewódzki – izba przyjęć", 49.7806393 + 45 / M, 22.7771083, "Juliusza Słowackiego", "21"),
    ("SZP-3", "Szpital Wojewódzki – budynek główny", 49.7905, 22.7630, "Monte Cassino", "18"),
]
DOSTAWCA = Provider(nazwa="Szpital Wojewódzki w Przemyślu (test TuAED)", typ="ochrona_zdrowia", slug="szpital-przemysl-test")


def main():
    sch = oc.schema()
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\r\n")
    w.writerow(["id", "nazwa", "lat", "lon", "ulica", "nr", "kod", "miasto", "wewnatrz", "dostep", "24h", "seryjny"])
    for i, n, la, lo, u, nr in ZRODLO:
        w.writerow([i, n, f"{la:.7f}", f"{lo:.7f}", u, nr, "37-700", "Przemyśl", "tak", "publiczny", "tak", f"SN-{i}"])
    (KATALOG / "szpital_przemysl_zrodlo.csv").write_text(buf.getvalue(), encoding="utf-8", newline="")
    t = read_table(buf.getvalue().encode(), "szpital_przemysl_zrodlo.csv")
    mapowanie = {s.kolumna: s.pole for s in suggest_mapping(t, sch)}
    rek = normalize_table(t, mapowanie, sch, DOSTAWCA, date(2026, 11, 22), geocoder=None, fixed={})
    bledy = [m for m in validate_records(rek, sch) if m.poziom == "blad"]
    assert not bledy, bledy
    rekordy = [r.record for r in rek if not r.pominiety]
    (KATALOG / "szpital_przemysl_v05.csv").write_bytes(to_csv(rekordy, sch))
    (KATALOG / "szpital_przemysl_v05_pelny.csv").write_bytes(to_csv(rekordy, sch, public_only=False))
    print(f"{len(rekordy)} rekordów → szpital_przemysl_v05.csv (publiczny) i szpital_przemysl_v05_pelny.csv")


if __name__ == "__main__":
    main()
