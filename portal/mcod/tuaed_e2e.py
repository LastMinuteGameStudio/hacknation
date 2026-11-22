"""TuAED: test end-to-end „wykazu AED” w lokalnym portalu (uruchamia go portal/tuaed_e2e.sh, opis w JURY.md, sekcja 3).

Etapy (każdy wywoływany osobno przez `manage.py shell -c`, wypisuje linie `PASS|FAIL|INFO …` i `E2E {json}`):
- przygotuj(): do danych testowych B (mcod/tuaed_dane_testowe.py: Przemyśl, Krosno, Szpital w Przemyślu) dokłada
  4 wykazy z pokazu A (portal/pokaz/zrodla/): uczelnia (CC0), szpital (CC BY 4.0), fundacja (CC BY-NC 4.0, ma być
  pominięta z powodu licencji) i gmina (wartość spoza słownika, ma być pominięta z powodu błędu walidacji). Zasoby
  są linkami do plików na branchu portal-aed, z flagą „Wykaz AED”. Idempotentne (po tytule).
- walidacja(): czeka, aż portal zwaliduje wszystkie zasoby z flagą, i sprawdza wynik: poprawne → SUCCESS,
  fundacja i gmina → FAILURE z błędem wykazu AED.
- scal(): uruchamia create_main_aed_resource_task synchronicznie i czeka na finalize_main_aed_resource_task
  (AggregatedAEDInfo z nowym zasobem).
- wykaz(): sprawdza zbiór „Defibrylatory AED: wykaz zbiorczy”: liczba AED, duplikaty (pary id), pominięte wykazy,
  licencja. Wypisuje adres pliku CSV do porównania z pokazem po stronie hosta.
"""

from __future__ import annotations

import json
import os
import time

RAW = os.environ.get(
    "TUAED_E2E_RAW", "https://raw.githubusercontent.com/LastMinuteGameStudio/hacknation/portal-aed/portal/pokaz/zrodla/"
)
POKAZ = [
    # instytucja (nazwy jak w pokazie A, bo kolejność scalania zależy od nazwy), plik, licencja, czy ma przejść
    ("Uczelnia (pokaz)", "pokaz-uczelnia.csv", "CC0 1.0", True),
    ("Wojewódzki Szpital (pokaz)", "pokaz-szpital.csv", "CC BY 4.0", True),
    ("Fundacja (pokaz)", "pokaz-fundacja.csv", "CC BY-NC 4.0", False),
    ("Gmina (pokaz)", "pokaz-gmina-z-bledem.csv", "CC0 1.0", False),
]
OCZEKIWANE = {
    # dane testowe B (21 + 21 + 3) + pokaz A (1 + 3); fundacja i gmina pominięte
    "records_count": 49,
    "sources_count": 5,
    "skipped_count": 2,
    "license_name": "CC BY 4.0",
    "duplikaty": {
        "szpital-krosno-1": "uczelnia-przemysl-1",  # ten sam numer seryjny (pokaz A)
        "szpital-krosno-2": "qy7g6px5-26c91c",  # ok. 15 m (pokaz A)
        "kznsks42-9c48a7": "szpital-przemysl-test-0c95af",  # 15 m (wykaz szpitala z danych B, plik od D)
    },
    "pominiete": {"Fundacja (pokaz)": "licencj", "Gmina (pokaz)": "walidacji"},
}
TIMEOUT_S = int(os.environ.get("TUAED_E2E_TIMEOUT", "900"))


def _wypisz(ok, opis):
    print(f"{'PASS' if ok else 'FAIL'} {opis}", flush=True)
    return bool(ok)


def _licencja_kod(Dataset, nazwa):
    return {
        "CC0 1.0": Dataset.LICENSE_CC0,
        "CC BY 4.0": Dataset.LICENSE_CC_BY,
        "CC BY-NC 4.0": Dataset.LICENSE_CC_BY_NC,
    }[nazwa]


def przygotuj() -> None:
    import datetime

    from mcod.categories.models import Category
    from mcod.datasets.models import Dataset
    from mcod.organizations.models import Organization
    from mcod.resources.models import Resource

    kat = Category.objects.filter(code="HEAL").first()
    for instytucja, plik, licencja, _ in POKAZ:
        org = Organization.objects.filter(title=instytucja).first() or Organization(title=instytucja)
        org.slug = "e2e-" + plik.replace(".csv", "")
        org.institution_type = Organization.INSTITUTION_TYPE_LOCAL
        org.email = f"{org.slug}@tuaed.test"
        org.status = "published"
        org.save()
        tytul = f"Defibrylatory AED: {instytucja}"
        ds = Dataset.objects.filter(title=tytul, organization=org).first() or Dataset(title=tytul, organization=org)
        ds.notes = "Wykaz pokazowy (fikcyjny) do testu e2e wykazu AED (portal/tuaed_e2e.sh)."
        ds.update_frequency = "daily"
        ds.license_chosen = _licencja_kod(Dataset, licencja)
        ds.has_dynamic_data = ds.has_high_value_data = ds.has_research_data = False
        ds.status = "published"
        ds.save()
        if kat:
            ds.categories.add(kat)
        res = Resource.objects.filter(dataset=ds, title=f"{tytul} (CSV)").first() or Resource(dataset=ds, title=f"{tytul} (CSV)")
        res.description = "Plik CSV w zakresie v0.5 z pokazu scalania (portal/pokaz/zrodla/)."
        res.link = RAW + plik
        res.type = "file"
        res.format = "csv"
        res.has_dynamic_data = res.has_high_value_data = res.has_research_data = False
        res.data_date = datetime.date.today()
        res.is_aed_list = True
        res.status = "published"
        res.save()
        print(f"INFO {instytucja} ({licencja}): zbiór #{ds.pk}, zasób #{res.pk} → {res.link}", flush=True)


def _zasoby():
    from mcod.resources.aed_utils import get_aed_source_resources

    return list(get_aed_source_resources())


def _bledy_zasobu(res):
    t = res.data_tasks.order_by("-id").first() if hasattr(res, "data_tasks") else None
    wynik = getattr(t, "result", "") or ""
    return str(wynik)[:300]


def walidacja() -> None:
    koniec = time.time() + TIMEOUT_S
    while True:
        zasoby = _zasoby()
        for r in zasoby:
            r.refresh_from_db()
        czekaja = [r for r in zasoby if r.data_tasks_last_status in ("", "PENDING", "STARTED", None)]
        if not czekaja or time.time() > koniec:
            break
        print(f"INFO czekam na walidację {len(czekaja)} z {len(zasoby)} zasobów…", flush=True)
        time.sleep(15)
    oczekiwane_bledne = {i for i, _, _, ok in POKAZ if not ok}
    wszystko = True
    for r in zasoby:
        inst = r.institution.title
        st = r.data_tasks_last_status or "(brak)"
        if inst in oczekiwane_bledne:
            tekst = _bledy_zasobu(r)
            ok = st == "FAILURE" and ("aed" in tekst.lower() or "licencj" in tekst.lower() or "dostepnosc" in tekst)
            wszystko &= _wypisz(ok, f"walidacja v0.5: {inst} (zasób #{r.pk}) → {st}, oczekiwany błąd: {tekst[:160]}")
        else:
            wszystko &= _wypisz(st == "SUCCESS", f"walidacja v0.5: {inst} (zasób #{r.pk}) → {st}")
    _wypisz(wszystko and len(zasoby) >= 7, f"(2) wyniki walidacji zasobów z flagą „Wykaz AED”: {len(zasoby)} zasobów")


def scal() -> None:
    from mcod.resources.models import AggregatedAEDInfo
    from mcod.resources.tasks import create_main_aed_resource_task

    wynik = create_main_aed_resource_task.apply().result or {}
    print("E2E " + json.dumps({"scal": wynik}, ensure_ascii=False, default=str), flush=True)
    rid = wynik.get("resource_id")
    if not rid:
        _wypisz(False, f"(3) create_main_aed_resource_task nie utworzył zasobu: {wynik}")
        return
    koniec = time.time() + TIMEOUT_S
    info = None
    while time.time() < koniec:
        # update_aggregated_aed_info aktualizuje ostatni wiersz, więc czekamy, aż wskaże nowy zasób
        info = AggregatedAEDInfo.objects.filter(resource_id=rid).first()
        if info:
            break
        print(f"INFO czekam na finalize_main_aed_resource_task (zasób #{rid})…", flush=True)
        time.sleep(15)
    _wypisz(info is not None, f"(3) scalanie i finalizacja: zasób wykazu zbiorczego #{rid}"
            + ("" if info else f" (brak AggregatedAEDInfo po {TIMEOUT_S} s: walidacja portalu nie skończyła się?)"))


def wykaz() -> None:
    from mcod.resources.aed_utils import get_aggregated_aed_info, read_aed_resource_table

    info = get_aggregated_aed_info()
    if not info or not info.resource:
        _wypisz(False, "(4) brak wykazu zbiorczego (AggregatedAEDInfo)")
        return
    res = info.resource
    ds = res.dataset
    raport = info.report if isinstance(getattr(info, "report", None), (dict, list)) else {}
    ok = True
    ok &= _wypisz(ds.title.startswith("Defibrylatory AED: wykaz zbiorczy"), f"zbiór: „{ds.title}” (#{ds.pk})")
    for pole in ("records_count", "sources_count", "skipped_count", "license_name"):
        ok &= _wypisz(getattr(info, pole) == OCZEKIWANE[pole], f"{pole} = {getattr(info, pole)} (oczekiwane {OCZEKIWANE[pole]})")
    tabela = read_aed_resource_table(res)
    wiersze = tabela.wiersze
    dup = {w["id_aed"]: w["duplikat_id_aed"] for w in wiersze if w.get("duplikat_id_aed")}
    ok &= _wypisz(dup == OCZEKIWANE["duplikaty"], f"duplikaty w pliku: {dup}")
    ok &= _wypisz(info.duplicates_count == len(OCZEKIWANE["duplikaty"]), f"duplicates_count = {info.duplicates_count}")
    pominiete = {}
    for p in (raport.get("pominiete") or raport.get("skipped") or []) if isinstance(raport, dict) else []:
        pominiete[p.get("instytucja") or p.get("institution")] = p.get("powod") or p.get("reason") or ""
    for inst, slowo in OCZEKIWANE["pominiete"].items():
        ok &= _wypisz(slowo in pominiete.get(inst, "").lower(), f"pominięty: {inst}: {pominiete.get(inst, '(brak w raporcie)')}")
    ok &= _wypisz(ds.license_name == OCZEKIWANE["license_name"], f"licencja zbioru wykazu zbiorczego: {ds.license_name}")
    _wypisz(ok, "(4) zbiór „Defibrylatory AED: wykaz zbiorczy”")
    print("E2E " + json.dumps({"wykaz": {"dataset_id": ds.pk, "resource_id": res.pk, "file_url": res.file_url,
                                        "liczba_wierszy": len(wiersze)}}, ensure_ascii=False), flush=True)
