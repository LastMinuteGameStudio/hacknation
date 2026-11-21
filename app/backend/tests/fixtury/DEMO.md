# Demo od początku do końca: Przemyśl

Jeden przykład, który pokazuje cały pomysł: miasto ma dane o AED, ale w formacie, z którego nikt nie
skorzysta. Po kilku minutach w kreatorze ma stały URL z CSV zgodnym z v0.5, a aktualizację robi wgraniem
nowego pliku pod ten sam adres.

## Dlaczego Przemyśl

- Urząd Miejski w Przemyślu opublikował zbiór AED na dane.gov.pl (ds 4581, licencja CC0 1.0) jako link
  do eksportu z CMS (przemysl.skycms.com.pl). Deklarowana częstotliwość aktualizacji to „Codziennie”.
- Portal trzyma kopię z **2024-11-06** i jej nie odświeża, bo zasób dodano ręcznie, bez „Aktualizacji
  automatycznej” (RESEARCH.md). Źródło na żywo zmieniło się od tamtej pory: inny format geometrii.
  Zbiór jest w praktyce porzucony.
- Plik jest źle sformatowany dla odbiorcy: separator `;`, BOM, 17 kolumn, z czego połowa to pola CMS
  (`category`, `gallery`, `youtube_url`, `links`…), `description` to ten sam akapit marketingowy w każdym
  wierszu, a współrzędne siedzą w komórce jako JSON. Brak informacji, czy AED jest w budynku,
  kto ma dostęp i w jakich godzinach.

Pliki: `przemysl_2024.csv` (kopia z dane.gov.pl, geometria `{"lat":"49.78","long":"22.77"}`) i
`przemysl.csv` (źródło na żywo z 21.11.2026, geometria `[22.77, 49.78]`). Poza geometrią różnią się
tylko apostrofem z Excela w jednym telefonie (`'+48166779500`).

## Scenariusz (ok. 3 minuty)

**Krok 0. Problem (slajd).** Pokaż `przemysl_2024.csv` w edytorze: średniki, akapit marketingowy w każdym
wierszu, JSON w komórce. Pokaż stronę zbioru na dane.gov.pl: „Codziennie”, a dane z 2024.

**Krok 1. Dysponent.** Nazwa: `Urząd Miejski w Przemyślu`, typ: `jst` (Jednostka samorządu terytorialnego).

**Krok 2. Wgranie `przemysl_2024.csv`.** Kreator sam proponuje mapowanie (bez poprawek):

| Kolumna | Pole v0.5 |
|---|---|
| `id` | `id_zrodlowe` |
| `name` | `nazwa_obiektu` |
| `city`, `street`, `home_number`, `postcode` | `miejscowosc`, `nazwa_ulicy`, `nr_budynku`, `kod_pocztowy` |
| `phone`, `email` | `telefon_kontaktowy`, `email_kontaktowy` (niepubliczne) |
| `geometry` | `_geometria` → `szerokosc_geograficzna` + `dlugosc_geograficzna` |
| `description`, `category`, `www`, `youtube_url`, `panorama_url`, `gallery`, `attachments`, `links` | nie importuj |

Pola obowiązkowe bez kolumny ustawiamy raz dla całego pliku („ustaw dla wszystkich AED”):
`wewnatrz_budynku = false`, `dostepnosc = publiczny`, `dostepny_24_7 = tak` (wartości przyjęte do demo).

**Krok 2b. Walidacja.** 21 rekordów, 0 błędów, ostrzeżenia, które warto pokazać, bo uczą dostawcę:
`WYGENEROWANO_ID` (stały identyfikator z treści rekordu), `DOMYSLNY_STATUS` (brak stanu urządzenia →
`nieznany`), `DOMYSLNA_DATA_WERYFIKACJI` (brak daty sprawdzenia → data wgrania). Telefon i e-mail
nie trafiają do pliku publicznego.

**Krok 3. Publikacja.** Zgoda na CC0 1.0 → stały URL `…/d/<slug>.csv` (+ `.json`, CSVW) i prywatny link
edycji. Pokaż CSV: przecinki, UTF-8 bez BOM, kolumny v0.5 w kolejności zakresu, współrzędne z kropką.
Ten URL wkleja się na dane.gov.pl z „Aktualizacją automatyczną” (instrukcja w kroku 3).

**Krok 4. Aktualizacja (puenta).** Miasto zmieniło CMS i eksport ma inny format geometrii. Otwórz prywatny
link edycji i wgraj `przemysl.csv`. Mapowanie podpowiada się z poprzedniej wersji, walidacja przechodzi,
publikacja **podmienia dane pod tym samym URL**, a `id_aed` wszystkich 21 AED są **takie same jak
wcześniej**. Portal przy następnym pobraniu dostaje świeże dane bez żadnej zmiany po stronie dane.gov.pl.

## Co sprawdzają testy

| Test | Co gwarantuje |
|---|---|
| `test_realne_mapowanie.py::test_mapowanie_100_procent[przemysl*.csv]` | mapowanie z kroku 2 bez poprawek |
| `test_realne_normalizacja.py::*[przemysl_2024.csv]` | wartości rekordów (`oczekiwane/przemysl_2024.json`), brak błędów |
| `test_realne_e2e.py::test_rdzen_plik_do_csv[przemysl_2024.csv]` | CSV RFC 4180 i formaty v0.5 |
| `test_realne_e2e.py::test_api_upload_walidacja_publikacja_csv[przemysl_2024.csv]` | kroki 1–3 przez API |
| `test_realne_demo.py::test_demo_rdzen_oba_formaty_geometrii_daja_te_same_rekordy` | oba formaty geometrii → identyczne rekordy |
| `test_realne_demo.py::test_demo_api_aktualizacja_pod_tym_samym_url` | krok 4: ten sam slug, URL i `id_aed` |

Przed prezentacją: `cd app/backend && .venv/bin/python -m pytest -q tests/test_realne_demo.py tests/test_realne_e2e.py`
oraz `.venv/bin/python -m tests.raport_mapowania --rekordy`.

## Zapas, gdyby coś nie działało

- Marki (`marki.csv`): plik uszkodzony (cały wiersz w jednym polu, zamienione współrzędne). Pokazuje, że
  kreator **wykrywa i naprawia** albo jasno mówi, co jest nie tak (`ROZBITO_WIERSZE`, `ZAMIENIONE_WSPOLRZEDNE`).
- Warszawa 19115 (`warszawa_19115.geojson`): skala, 708 AED, mapowanie 20/20 kolumn.
