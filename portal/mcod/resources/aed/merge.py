"""Scalanie wykazów AED od różnych dostawców w jeden wykaz zbiorczy (czysta funkcja, bez bazy).

Zasady (decyzje zespołu, NOTATKI-ZESPOLU.md „wykaz AED w portalu”, prezentacja/LICENCJE.md):
- do wykazu trafia wykaz dostawcy bez błędów walidacji zakresu v0.5 (ostrzeżenia nie blokują),
- tylko licencje CC0 1.0 i CC BY 4.0; inne (BY-SA, BY-NC, BY-ND i połączenia) są pomijane z powodem,
- kolumny: pola publiczne zakresu v0.5 + kolumny pochodzenia (instytucja, id zasobu, URL, data aktualizacji,
  licencja źródła),
- duplikaty między dostawcami zostają oba; rekord z wykazu przetwarzanego później dostaje
  `duplikat_id_aed` = id_aed rekordu wcześniejszego, gdy mają ten sam numer seryjny albo leżą do 30 m od siebie
  (duplikatów w obrębie jednego dostawcy nie oznaczamy: to błąd walidacji jego wykazu),
- licencja wykazu zbiorczego: CC0 1.0, gdy wszystkie dołączone wykazy mają CC0, w przeciwnym razie CC BY 4.0.
"""

import csv
import io
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from mcod.resources.aed.reader import Tabela
from mcod.resources.aed.schema import Zakres
from mcod.resources.aed.validation import Komunikat, bledy, odleglosc_m, validate_table, wspolrzedne

LICENCJA_CC0 = "CC0 1.0"
LICENCJA_CC_BY = "CC BY 4.0"
DOZWOLONE_LICENCJE = (LICENCJA_CC0, LICENCJA_CC_BY)
DUPLIKAT_M = 30.0
_KOMORKA = 0.0005  # stopnie; ok. 55 m szerokości i 32–36 m długości w Polsce, więc ±1 komórka pokrywa 30 m

KOLUMNY_POCHODZENIA = [
    "zrodlo_instytucja",
    "zrodlo_zasob_id",
    "zrodlo_url",
    "zrodlo_data_aktualizacji",
    "licencja_zrodla",
]


@dataclass
class ZrodloWykazu:
    instytucja: str
    zasob_id: int
    url: str
    data_aktualizacji: str  # ISO 8601
    licencja: str  # nazwa z Dataset.LICENSES, np. „CC0 1.0”
    tabela: Tabela


@dataclass
class Pominiety:
    zrodlo: ZrodloWykazu
    powod: str
    komunikaty: List[Komunikat] = field(default_factory=list)


@dataclass
class WynikScalania:
    kolumny: List[str]
    rekordy: List[Dict[str, str]]
    dolaczone: List[ZrodloWykazu]
    pominiete: List[Pominiety]
    licencja: str
    liczba_duplikatow: int


def kolumny_wykazu(zakres: Zakres) -> List[str]:
    return zakres.publiczne + KOLUMNY_POCHODZENIA


def powod_licencji(licencja: str) -> Optional[str]:
    """Powód pominięcia z powodu licencji albo None, gdy licencja pozwala dołączyć wykaz."""
    if licencja in DOZWOLONE_LICENCJE:
        return None
    return (f"Wykaz nie zostanie dołączony do wykazu zbiorczego AED z powodu licencji zbioru ({licencja or 'brak'}). "
            f"Dozwolone: {' albo '.join(DOZWOLONE_LICENCJE)}.")


def _nr_seryjny(r: Dict[str, str]) -> str:
    return "".join((r.get("numer_seryjny") or "").split()).lower()


def scal_wykazy(zrodla: List[ZrodloWykazu], zakres: Zakres) -> WynikScalania:
    kolumny = kolumny_wykazu(zakres)
    rekordy: List[Dict[str, str]] = []
    dolaczone: List[ZrodloWykazu] = []
    pominiete: List[Pominiety] = []

    # indeksy rekordów już dołączonych: numer seryjny i siatka współrzędnych → (instytucja, id_aed rekordu głównego)
    po_numerze: Dict[str, Tuple[str, str]] = {}
    siatka: Dict[Tuple[int, int], List[Tuple[Tuple[float, float], str, str]]] = defaultdict(list)
    duplikatow = 0

    for z in sorted(zrodla, key=lambda z: (z.instytucja.lower(), z.zasob_id)):
        powod = powod_licencji(z.licencja)
        if powod:
            pominiete.append(Pominiety(z, powod))
            continue
        komunikaty = validate_table(z.tabela, zakres)
        if bledy(komunikaty):
            pominiete.append(Pominiety(z, f"Liczba błędów walidacji zakresu v0.5: {len(bledy(komunikaty))}.",
                                       bledy(komunikaty)))
            continue
        dolaczone.append(z)
        nowe: List[Tuple[Dict[str, str], str, Optional[Tuple[float, float]]]] = []
        for w in z.tabela.wiersze:
            r = {k: (w.get(k) or "") for k in zakres.publiczne}
            r.update({
                "zrodlo_instytucja": z.instytucja,
                "zrodlo_zasob_id": str(z.zasob_id),
                "zrodlo_url": z.url,
                "zrodlo_data_aktualizacji": z.data_aktualizacji,
                "licencja_zrodla": z.licencja,
            })
            glowny = _znajdz_duplikat(w, z.instytucja, po_numerze, siatka)
            if glowny and not r.get("duplikat_id_aed"):
                r["duplikat_id_aed"] = glowny
                duplikatow += 1
            rekordy.append(r)
            nowe.append((r, _nr_seryjny(w), wspolrzedne(w)))
        # indeksujemy po całym wykazie, żeby nie porównywać rekordów tego samego dostawcy
        for r, nr, xy in nowe:
            glowny_id = r.get("duplikat_id_aed") or r.get("id_aed", "")
            if nr and nr not in po_numerze:
                po_numerze[nr] = (z.instytucja, glowny_id)
            if xy:
                siatka[(int(xy[0] / _KOMORKA), int(xy[1] / _KOMORKA))].append((xy, z.instytucja, glowny_id))

    licencja = LICENCJA_CC0 if dolaczone and all(z.licencja == LICENCJA_CC0 for z in dolaczone) else LICENCJA_CC_BY
    return WynikScalania(kolumny, rekordy, dolaczone, pominiete, licencja, duplikatow)


def _znajdz_duplikat(w: Dict[str, str], instytucja: str, po_numerze: Dict[str, Tuple[str, str]],
                     siatka: Dict[Tuple[int, int], List[Tuple[Tuple[float, float], str, str]]]) -> Optional[str]:
    nr = _nr_seryjny(w)
    if nr and nr in po_numerze and po_numerze[nr][0] != instytucja:
        return po_numerze[nr][1]
    xy = wspolrzedne(w)
    if not xy:
        return None
    ki, kj = int(xy[0] / _KOMORKA), int(xy[1] / _KOMORKA)
    najblizszy: Optional[Tuple[float, str]] = None
    for di in (-1, 0, 1):
        for dj in (-1, 0, 1):
            for p, inst, glowny_id in siatka.get((ki + di, kj + dj), []):
                if inst == instytucja:
                    continue
                d = odleglosc_m(xy, p)
                if d <= DUPLIKAT_M and (najblizszy is None or d < najblizszy[0]):
                    najblizszy = (d, glowny_id)
    return najblizszy[1] if najblizszy else None


def to_csv_bytes(wynik: WynikScalania) -> bytes:
    """CSV RFC 4180: UTF-8 bez BOM, przecinek, CRLF, cudzysłowy tylko gdy potrzebne."""
    buf = io.StringIO(newline="")
    w = csv.writer(buf, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL, lineterminator="\r\n")
    w.writerow(wynik.kolumny)
    for r in wynik.rekordy:
        w.writerow([r.get(k, "") for k in wynik.kolumny])
    return buf.getvalue().encode("utf-8")


def to_xlsx_bytes(wynik: WynikScalania, arkusz: str = "Wykaz AED") -> bytes:
    """XLSX z tymi samymi kolumnami; wszystkie komórki tekstowe (kody TERC i współrzędne bez zmian)."""
    from openpyxl import Workbook
    from openpyxl.styles import Font

    wb = Workbook()
    ws = wb.active
    ws.title = arkusz
    ws.append(wynik.kolumny)
    for c in ws[1]:
        c.font = Font(bold=True)
    for r in wynik.rekordy:
        ws.append([r.get(k, "") for k in wynik.kolumny])
    for wiersz in ws.iter_rows(min_row=2):
        for c in wiersz:
            c.number_format = "@"
    ws.freeze_panes = "A2"
    out = io.BytesIO()
    wb.save(out)
    return out.getvalue()
