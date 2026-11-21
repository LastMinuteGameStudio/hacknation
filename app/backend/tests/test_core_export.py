import csv
import io
import json
from pathlib import Path

from aed_core.export import csvw_metadata, to_csv, to_json
from aed_core.schema import load_schema

ZAKRES = Path(__file__).resolve().parents[3] / "zakres-danych"
SCHEMA = load_schema(ZAKRES)


def rec(**kw):
    r = {p: "" for p in SCHEMA.nazwy}
    r.update(kw)
    return r


def test_csv_rfc4180():
    recs = [rec(id_aed="a-1", nazwa_obiektu='Pływalnia "Wodne Piaski"', uwagi="linia1\nlinia2", numer_seryjny="TAJNE",
                telefon_kontaktowy="123456789", opis_lokalizacji="hol, parter")]
    b = to_csv(recs, SCHEMA)
    assert not b.startswith(b"\xef\xbb\xbf")
    tekst = b.decode("utf-8")
    naglowek, _, reszta = tekst.partition("\r\n")
    assert naglowek.split(",") == SCHEMA.publiczne
    assert naglowek == (ZAKRES / "szablon-aed-publiczny.csv").read_text(encoding="utf-8").splitlines()[0]
    assert '"Pływalnia ""Wodne Piaski"""' in reszta and '"hol, parter"' in reszta
    assert "TAJNE" not in tekst and "123456789" not in tekst
    assert tekst.endswith("\r\n")
    wiersze = list(csv.DictReader(io.StringIO(tekst, newline="")))
    assert wiersze[0]["uwagi"] == "linia1\nlinia2"


def test_csv_wszystkie_pola():
    b = to_csv([rec(numer_seryjny="SN1")], SCHEMA, public_only=False).decode()
    assert b.split("\r\n")[0].split(",") == SCHEMA.nazwy and "SN1" in b


def test_json():
    d = json.loads(to_json([rec(id_aed="a-1", email_kontaktowy="x@y.pl")], SCHEMA, {"slug": "abc"}))
    assert d["metadane"] == {"slug": "abc"}
    assert list(d["rekordy"][0]) == SCHEMA.publiczne and d["rekordy"][0]["id_aed"] == "a-1"
    assert "email_kontaktowy" not in d["rekordy"][0]


def test_csvw_zgodny_ze_wzorem():
    wzor = json.loads((ZAKRES / "szablon-aed-publiczny.csv-metadata.json").read_text(encoding="utf-8"))
    m = csvw_metadata(SCHEMA, "https://x/d/abc.csv", "AED Krosno")
    assert m["url"] == "https://x/d/abc.csv" and m["dc:title"] == "AED Krosno"
    assert m["dialect"] == wzor["dialect"]
    assert m["tableSchema"]["null"] == wzor["tableSchema"]["null"]
    for a, b in zip(m["tableSchema"]["columns"], wzor["tableSchema"]["columns"], strict=True):
        assert (a["name"], a["datatype"], a["required"]) == (b["name"], b["datatype"], b["required"])
