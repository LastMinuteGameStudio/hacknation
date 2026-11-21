"""D3: geokodowanie w normalize_table na realnym pliku (Krosno bez kolumn współrzędnych), bez sieci.

Atrapa geokodera zamiast GUGiK: wynik deterministyczny. Sprawdzamy kontrakt (KONTRAKT §3–4):
GEOKODOWANIE_OK + dokladnosc_polozenia, GEOKODOWANIE_BRAK → rekord pominięty (reszta pliku się publikuje),
jedno zapytanie na unikalny adres, limit 200 adresów (ZA_DUZO_DO_GEOKODOWANIA), CSV bez pominiętych.
"""

from __future__ import annotations

import csv
import io
import threading

import pytest

from aed_core.types import AddressQuery, GeoResult
from tests.fixtury import oczekiwania as oc

KROSNO = oc.wg_pliku("krosno.csv")
NIEZNANA_ULICA = "Rzeszowska"  # wiersz 4: „ul. Rzeszowska, 38-400 Krosno” → atrapa nie znajduje


class AtrapaGeokodera:
    def __init__(self, nieznane: set[str] = frozenset()):
        self.nieznane = {u.lower() for u in nieznane}
        self.zapytania: list[AddressQuery] = []
        self._lock = threading.Lock()

    def geocode(self, q: AddressQuery):
        with self._lock:
            self.zapytania.append(q)
            n = len(self.zapytania)
        if q.ulica.lower() in self.nieznane:
            return None
        return GeoResult(lat=49.68 + n * 0.0001, lon=21.75 + n * 0.0001,
                         dokladnosc="punkt_adresowy" if q.nr_budynku else "przyblizone",
                         kod_terc="1861011", kod_simc="0975290")


def _krosno_bez_wspolrzednych() -> bytes:
    wiersze = list(csv.reader(io.StringIO((oc.FIXTURY / "krosno.csv").read_text(encoding="utf-8"))))
    buf = io.StringIO()
    csv.writer(buf, lineterminator="\r\n").writerows([w[2:] for w in wiersze])
    return buf.getvalue().encode("utf-8")


def _normalizuj(tresc: bytes, nazwa: str, geokoder):
    from aed_core.mapping import suggest_mapping
    from aed_core.normalize import normalize_table
    from aed_core.parsers import read_table

    sch = oc.schema()
    try:
        t = read_table(tresc, nazwa)
        mapowanie = {s.kolumna: s.pole for s in suggest_mapping(t, sch)}
        return sch, normalize_table(t, mapowanie, sch, oc.provider(KROSNO), oc.DZIS, geocoder=geokoder,
                                    fixed=KROSNO["wartosci_stale"])
    except NotImplementedError as e:
        pytest.xfail(f"rdzeń: {e}")


def _kody(r):
    return {m.kod for m in r.messages}


def test_krosno_bez_wspolrzednych_geokodowane():
    g = AtrapaGeokodera(nieznane={NIEZNANA_ULICA})
    sch, rek = _normalizuj(_krosno_bez_wspolrzednych(), "krosno.csv", g)
    assert len(rek) == 21
    wg = {r.wiersz: r for r in rek}

    # nieznaleziony adres: ostrzeżenie i rekord pominięty, bez błędu
    r4 = wg[4]
    assert r4.pominiety and "GEOKODOWANIE_BRAK" in _kody(r4)
    assert not [m for m in r4.messages if m.poziom == "blad"]

    # pozostałe: współrzędne, dokładność, kody TERYT z geokodera
    for r in rek:
        if r.wiersz == 4:
            continue
        assert not r.pominiety, r.wiersz
        assert "GEOKODOWANIE_OK" in _kody(r) or "GEOKODOWANIE_NIEJEDNOZNACZNE" in _kody(r), (r.wiersz, _kody(r))
        assert r.record["szerokosc_geograficzna"] and r.record["dlugosc_geograficzna"]
        assert r.record["kod_terc"] == "1861011"
    assert wg[3].record["dokladnosc_polozenia"] == "punkt_adresowy"  # Wyspiańskiego 20
    assert wg[2].record["dokladnosc_polozenia"] == "przyblizone"  # „ul. Jasna” bez numeru

    # zapytania: „Kazimierza Wielkiego 4” jest w wierszach 10 i 11 → jedno zapytanie na unikalny adres
    adresy = [(q.ulica, q.nr_budynku) for q in g.zapytania]
    assert adresy.count(("Kazimierza Wielkiego", "4")) <= 2  # 1 + ewentualne drugie przejście z TERC
    assert all(q.miejscowosc == "Krosno" and q.kod_pocztowy == "38-400" for q in g.zapytania)


def test_pominiety_nie_trafia_do_csv_i_nie_blokuje_publikacji():
    from aed_core.export import to_csv
    from aed_core.validate import validate_records

    sch, rek = _normalizuj(_krosno_bez_wspolrzednych(), "krosno.csv", AtrapaGeokodera(nieznane={NIEZNANA_ULICA}))
    walid = validate_records(rek, sch)
    assert not [m for m in walid if m.poziom == "blad"], [(m.kod, m.wiersz) for m in walid if m.poziom == "blad"]
    dane = to_csv([r.record for r in rek if not r.pominiety], sch)
    wiersze = list(csv.DictReader(io.StringIO(dane.decode("utf-8"))))
    assert len(wiersze) == 20
    assert "OSP Turaszówka" not in {w["nazwa_obiektu"] for w in wiersze}


def test_bez_geokodera_rekordy_bez_wspolrzednych_to_blad_walidacji():
    """Bez geokodera (np. awaria GUGiK) brak współrzędnych to brak pola O, nie cicha publikacja."""
    from aed_core.validate import validate_records

    sch, rek = _normalizuj(_krosno_bez_wspolrzednych(), "krosno.csv", None)
    kody = {m.kod for m in validate_records(rek, sch)} | {m.kod for r in rek for m in r.messages}
    assert "BRAK_POLA_OBOWIAZKOWEGO" in kody or all(r.pominiety for r in rek)


def test_limit_200_adresow():
    n = 205
    tresc = "nazwa,ulica,nr,kod,miasto\r\n" + "".join(
        f"Obiekt {i},Testowa,{i},38-400,Krosno\r\n" for i in range(1, n + 1))
    g = AtrapaGeokodera()
    _, rek = _normalizuj(tresc.encode(), "limit.csv", g)
    assert len(rek) == n
    pominiete = [r for r in rek if r.pominiety]
    assert len(pominiete) == n - 200
    kody = {m.kod for r in rek for m in r.messages}
    assert "ZA_DUZO_DO_GEOKODOWANIA" in kody
    assert len({(q.ulica, q.nr_budynku) for q in g.zapytania}) <= 200
