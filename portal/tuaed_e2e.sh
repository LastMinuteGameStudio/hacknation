#!/usr/bin/env bash
# TuAED: test end-to-end „wykazu AED” w lokalnym portalu (stack dgp z URUCHOMIENIE-TUAED.md, po danych testowych B).
# Uruchomienie z katalogu portal/:   ./tuaed_e2e.sh
# Zmienne: KONTENER (domyślnie mcod-admin), API (domyślnie http://localhost:8100), TUAED_E2E_TIMEOUT (s, 900).
# Wypisuje PASS/FAIL dla punktów:
#   (1) migracja 0075 (Resource.is_aed_list, AggregatedAEDInfo) zastosowana
#   (2) zasoby z flagą „Wykaz AED” mają wyniki walidacji v0.5 (poprawne → SUCCESS, fundacja BY-NC i gmina → FAILURE)
#   (3) create_main_aed_resource_task (synchronicznie) + finalize_main_aed_resource_task
#   (4) zbiór „Defibrylatory AED: wykaz zbiorczy”: 49 AED, 3 duplikaty, 2 pominięte, CC BY 4.0
#   (5) wykaz pobrany przez API portalu = pokaz scalania A (pokaz/wykaz-zbiorczy.csv) + wykaz szpitala z danych B
# Kod etapów 2–4: mcod/tuaed_e2e.py. Opis i oczekiwania: JURY.md, sekcja 3.
set -uo pipefail
cd "$(dirname "$0")"
KONTENER="${KONTENER:-mcod-admin}"
API="${API:-http://localhost:8100}"
LOG="$(mktemp -t tuaed_e2e.XXXXXX)"
FAILS=0

wynik() { if [ "$1" = 0 ]; then echo "PASS $2"; else echo "FAIL $2"; FAILS=$((FAILS + 1)); fi; }
shell() {
  docker exec -e TUAED_E2E_TIMEOUT="${TUAED_E2E_TIMEOUT:-900}" "$KONTENER" \
    python manage.py shell -c "from mcod.tuaed_e2e import $1; $1()" 2>&1 | tee -a "$LOG" | grep -E '^(PASS|FAIL|INFO|E2E)'
}

echo "== TuAED e2e wykazu AED: kontener $KONTENER, API $API"
if ! docker ps --format '{{.Names}}' | grep -qx "$KONTENER"; then
  echo "FAIL kontener $KONTENER nie działa (docker ps). Uruchom portal według URUCHOMIENIE-TUAED.md."; exit 1
fi

# (1) migracja
docker exec "$KONTENER" python manage.py showmigrations resources 2>&1 | grep -q '\[X\] 0075_'
wynik $? "(1) migracja resources.0075 (is_aed_list, AggregatedAEDInfo) zastosowana"

# przygotowanie: 4 wykazy z pokazu A obok danych testowych B
shell przygotuj

# (2)–(4) w kontenerze
for etap in walidacja scal wykaz; do
  echo "== $etap"
  shell "$etap"
done
grep -q '^FAIL (2)' "$LOG" && FAILS=$((FAILS + 1))
grep -q '^FAIL (3)' "$LOG" && FAILS=$((FAILS + 1))
grep -q '^FAIL (4)' "$LOG" && FAILS=$((FAILS + 1))

# (5) API portalu → porównanie z pokazem
echo "== (5) API"
python3 - "$LOG" "$API" <<'PY'
import csv, io, json, re, sys, urllib.request
log, api = sys.argv[1], sys.argv[2].rstrip("/")
info = None
for linia in open(log, encoding="utf-8"):
    if linia.startswith("E2E ") and '"wykaz"' in linia:
        info = json.loads(linia[4:])["wykaz"]
if not info:
    print("FAIL (5) brak danych wykazu z etapu (4)"); sys.exit(1)

def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "tuaed-e2e/1.0", "Accept": "application/json, */*"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()

# wyszukanie pliku CSV wykazu zbiorczego przez publiczne API portalu (JSON:API)
url_csv = None
for sciezka in (f"/1.4/datasets/{info['dataset_id']}/resources", f"/1.4/resources/{info['resource_id']}"):
    try:
        dane = json.loads(get(api + sciezka))
    except Exception as e:  # noqa: BLE001
        print(f"INFO {sciezka}: {e}"); continue
    tekst = json.dumps(dane)
    for kandydat in re.findall(r'"(https?://[^"]+?\.csv)"', tekst):
        url_csv = kandydat; break
    if url_csv:
        print(f"INFO API {sciezka} → {url_csv}"); break
if not url_csv:
    url_csv = info["file_url"]; print(f"INFO API nie podało pliku CSV, używam file_url zasobu: {url_csv}")
url_csv = re.sub(r"^https?://[^/]+", api, url_csv) if "localhost" not in url_csv and "127.0.0.1" not in url_csv else url_csv
try:
    surowe = get(url_csv)
except Exception as e:  # noqa: BLE001
    print(f"FAIL (5) nie udało się pobrać {url_csv}: {e}"); sys.exit(1)

ok = True
def sprawdz(warunek, opis):
    global ok
    ok &= bool(warunek); print(("PASS " if warunek else "FAIL ") + opis)

tekst = surowe.decode("utf-8")
sprawdz(not tekst.startswith("﻿") and tekst.endswith("\r\n"), "CSV z API: UTF-8 bez BOM, wiersze zakończone CRLF")
portal = {w["id_aed"]: w for w in csv.DictReader(io.StringIO(tekst, newline=""))}
pokaz = {w["id_aed"]: w for w in csv.DictReader(open("pokaz/wykaz-zbiorczy.csv", encoding="utf-8", newline=""))}
# pk zasobów, adresy i daty nadaje portal; data_aktualizacji pochodzi z żywego pliku TuAED (pokaz ma kopię)
POCHODZENIE = {"zrodlo_zasob_id", "zrodlo_url", "zrodlo_data_aktualizacji", "data_aktualizacji"}
NAZWA = lambda v: v.replace(" (test TuAED)", "")  # dane B mają nazwy z dopiskiem, pokaz bez
DOPUSZCZALNE = {"kznsks42-9c48a7": {"duplikat_id_aed"}}  # w portalu duplikat wykazu szpitala z danych B
braki = sorted(set(pokaz) - set(portal))
dodatkowe = sorted(set(portal) - set(pokaz))
sprawdz(not braki, f"wszystkie {len(pokaz)} AED z pokazu są w wykazie z portalu" + (f" (brak: {braki[:5]})" if braki else ""))
sprawdz(all(i.startswith("szpital-przemysl-test-") for i in dodatkowe),
        f"dodatkowe AED w portalu to tylko wykaz szpitala z danych B: {dodatkowe}")
roznice = []
for i, w in pokaz.items():
    p = portal.get(i)
    if not p:
        continue
    for k in w:
        if k in POCHODZENIE or k in DOPUSZCZALNE.get(i, set()):
            continue
        if k == "zrodlo_instytucja" and NAZWA(p.get(k, "")) == w[k]:
            continue
        if p.get(k, "") != w[k]:
            roznice.append((i, k, w[k], p.get(k)))
sprawdz(not roznice, "id_aed, pola v0.5, zrodlo_instytucja, licencja_zrodla i duplikat_id_aed jak w pokazie"
        + (f": {roznice[:5]}" if roznice else ""))
sprawdz(list(next(iter(portal.values())).keys()) == list(next(iter(pokaz.values())).keys()), "kolumny i ich kolejność jak w pokazie")
print(("PASS" if ok else "FAIL") + f" (5) wykaz zbiorczy z API portalu ({len(portal)} AED) zgodny z pokazem scalania A")
sys.exit(0 if ok else 1)
PY
wynik $? "(5) porównanie z pokazem"

echo "== log: $LOG"
if [ "$FAILS" = 0 ]; then echo "WYNIK: PASS (wszystkie punkty)"; else echo "WYNIK: FAIL ($FAILS)"; exit 1; fi
