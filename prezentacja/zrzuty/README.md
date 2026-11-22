# Zrzuty ekranu i dowody do prezentacji (E1)

Zrzuty z publicznego demo https://tuaed.wkrynski.dev, scenariusz z `app/backend/tests/fixtury/DEMO.md`:
Przemyśl, plik `przemysl_2024.csv`, dysponent **„Urząd Miejski w Przemyślu (demo)”**. Słowo „(demo)” pozwala
odróżnić te zbiory w agregacie. Każdy zrzut jest w dwóch szerokościach: `-1440.png` (komputer) i `-320.png`
(telefon, WCAG 1.4.10 Reflow), z gęstością pikseli 2×. Numer na początku nazwy to numer slajdu z
`prezentacja/SZKIC-SLAJDOW.md`.

| Plik | Slajd | Podpis |
|---|---|---|
| `09-start` | 9 | Strona startowa: trzy kroki, szablony CSV i XLSX do pobrania, informacja o CC0. |
| `09-krok1-dysponent` | 9 | Krok 1: dysponent (nazwa i typ ze słownika). Kontakt jest opcjonalny i niepubliczny. |
| `09-krok2-mapowanie` | 9 | Krok 2: plik wgrany, początek tabeli mapowania z przykładami wartości z pliku i pewnością podpowiedzi. |
| `09-krok2-mapowanie-tabela` | 9 | Krok 2: pełna tabela mapowania 17 kolumn Przemyśla. Pola CMS (opis marketingowy, galeria, linki) są oznaczone „nie importuj”, a `geometry` z JSON-em jako współrzędne. |
| `09-krok2-wartosci-stale` | 9 | Krok 2: „Ustaw dla wszystkich AED w pliku”, czyli pola obowiązkowe, których brak w pliku (wewnątrz budynku, dostęp, 24/7). |
| `09-krok2-walidacja` | 9 | Krok 2: wynik sprawdzenia: 21 do publikacji, 0 błędów, ostrzeżenia zbiorcze, które uczą dostawcę. |
| `09-krok2-podglad-wyniku` | 9 | Krok 2: podgląd rekordów po normalizacji. |
| `09-krok3-zgoda` | 9 | Krok 3: zgoda na licencję CC0 1.0 przed publikacją. |
| `09-krok3-publikacja` | 9, 8 | Krok 3: stały URL pliku CSV, prywatny link edycji (token zamaskowany) i instrukcja dodania zasobu na dane.gov.pl z „Aktualizacją automatyczną”. |
| `09-edycja-zrodlo-automatyczne` | 9 | Strona aktualizacji (`/edycja/{slug}`, prywatny link): sekcja „Źródło automatyczne” i ręczne wgranie nowej wersji. |
| `09-edycja-zrodlo-automatyczne-sekcja` | 9 | Sama sekcja „Źródło automatyczne”: adres pliku na stronie urzędu i częstotliwość pobierania. |
| `08-csv-w-przegladarce` | 8 | Wynikowy CSV pobrany bez logowania: nagłówki HTTP (`text/csv; charset=utf-8`, CORS `*`) i pierwsze wiersze w zakresie v0.5. |
| `10-docs-api` | 10 | Dokumentacja API (OpenAPI, `/docs`) dla odbiorców i integratorów. |
| `10-mapa` | 10 | Mapa AED (`/mapa`): wszystkie AED albo bez OpenStreetMap, liczby według pochodzenia. Skrypt `zrob_zrzuty_strony.py` (nic nie publikuje). |
| `10-dane` | 10 | „Zebrane dane” (`/dane`): zbiory dostawców z plikami CSV, JSON, GeoJSON i CSVW. |

### Synchronizacja z URL źródła (S1), zbiór `kznsks42`

Źródło udające eksport z CMS miasta to plik w publicznym repo:
`https://raw.githubusercontent.com/LastMinuteGameStudio/hacknation/demo-zrodlo/demo/przemysl.csv` (branch
`demo-zrodlo`, bez merge do main). Między etapami podmieniamy go commitami. Synchronizacja zostaje
**włączona** (raz dziennie, stan „Aktywna”) na prezentację.

| Plik | Slajd | Podpis |
|---|---|---|
| `09-sync-0-csv-przed` | 9 | CSV `/d/kznsks42.csv` przed synchronizacją (dane z wgranego `przemysl_2024.csv`): `id_aed` i `data_aktualizacji`. |
| `09-sync-1-ustawienie` | 9 | Dysponent wkleja adres pliku na stronie urzędu i wybiera „raz dziennie”. |
| `09-sync-2-aktywna` | 9 | Po „Włącz i pobierz teraz”: stan „Aktywna”, ZSYNCHRONIZOWANO, 21 AED. |
| `09-sync-3-zsynchronizowano` | 9 | CMS zmienił format geometrii z `{"lat","long"}` na `[lon, lat]`. „Synchronizuj teraz”: ZSYNCHRONIZOWANO bez żadnej ręcznej poprawki. |
| `09-sync-4-csv-po` | 9, 8 | Ten sam URL i te same `id_aed` co na `09-sync-0`, nowa `data_aktualizacji`. Portal pobiera świeże dane bez zmian po swojej stronie. |
| `09-sync-5-wstrzymana` | 9 | Z eksportu zniknęła kolumna `geometry`: stan „Wstrzymana”, ZMIANA_STRUKTURY („brak kolumn: geometry”). Opublikowane dane zostają bez zmian. |
| `09-sync-6-przywrocona` (+ `-strona`) | 9 | Plik naprawiony, „Zapisz i pobierz teraz”: znów „Aktywna” (BEZ_ZMIAN). |

Skrypt: `zrob_zrzuty_sync.py --etap zrodlo|nowy-format|wstrzymana|przywroc` (link edycji z `ZRZUTY_TOKEN_PLIK`).
Przed każdym etapem trzeba podmienić plik na branchu i poczekać, aż raw.githubusercontent.com przestanie
podawać starą wersję z cache (u nas ok. 5 minut).

Dowód zgodności pliku z wymaganiami portalu (nagłówki, RFC 4180, UTF-8, CSVW): [`DOWOD-URL.md`](DOWOD-URL.md).

## Jak odtworzyć

```bash
python3 -m venv /tmp/pw && /tmp/pw/bin/pip install playwright && /tmp/pw/bin/playwright install chromium
/tmp/pw/bin/python prezentacja/zrzuty/zrob_zrzuty.py          # publikuje nowy zbiór „(demo)” i robi 26 PNG
python3 prezentacja/zrzuty/sprawdz_url.py https://tuaed.wkrynski.dev/d/kznsks42.csv   # DOWOD-URL.md
```

- Każde uruchomienie `zrob_zrzuty.py` publikuje **nowy** zbiór demo. Slug ostatniego jest w
  `ostatnie_uruchomienie.json`.
- Token edycji nie jest zapisywany w repo. Przed każdym zrzutem skrypt podmienia go w DOM na `••••••••`
  i sprawdza, że nie ma go na stronie. Link edycji można zapisać poza repo zmienną
  `ZRZUTY_TOKEN_PLIK=/ścieżka`.
- `08-csv-w-przegladarce`: Chromium w trybie headless traktuje `text/csv` jako pobranie pliku, choć serwer wysyła
  `Content-Disposition: inline`. Skrypt pobiera więc plik bez ciasteczek i pokazuje surowy tekst w `<pre>` razem
  z adresem i nagłówkami odpowiedzi.
- Przycisk wyboru pliku ma napis „Choose File”, bo pochodzi z interfejsu Chromium, nie z aplikacji. W polskiej
  przeglądarce będzie „Wybierz plik”.

## Zbiory na publicznym demo

| Slug | Rola | Do posprzątania? |
|---|---|---|
| `kznsks42` | Zbiór na prezentację: synchronizacja z `demo-zrodlo` włączona, zrzuty `09-sync-*`, `DOWOD-URL.md` | nie |
| `qps44qst` | Ostatnie uruchomienie `zrob_zrzuty.py` (zrzuty kreatora z nową nawigacją i „Wykaz AED” w kroku 3) | tak, po prezentacji |
| `gh4e9uju` | Wcześniejsze uruchomienie `zrob_zrzuty.py` | tak |
| `cfseuu37`, `r9ba4cvw` | Próbne przebiegi skryptu | tak |

Wszystkie mają dysponenta „Urząd Miejski w Przemyślu (demo)”. Sprzątanie należy do Grzana. Skrypty niczego nie usuwają.

### Portal dane.gov.pl: wykaz AED (panel admina lokalnego portalu, branch `portal-aed`)

Skrypt `zrob_zrzuty_portal.py` (Playwright, tylko czyta). Portal i dane testowe: `portal/URUCHOMIENIE-TUAED.md`
(panel `http://localhost:8101`, konto `admin@tuaed.local`). Hasło podajemy tylko w zmiennej środowiskowej:

```bash
PORTAL_HASLO='…' /tmp/pw/bin/python prezentacja/zrzuty/zrob_zrzuty_portal.py [--zasob-z-bledem 'tytuł zasobu']
```

Uruchamiamy po teście e2e sesji D (`portal/tuaed_e2e.sh`): to on zakłada zasób z błędem słownika
„Defibrylatory AED: Gmina (pokaz) (CSV)” (`dostepnosc` = „dla wszystkich”), domyślny dla ekranu `portal-02b`.

Przed każdym zrzutem tokeny (`token=…`, długie losowe ciągi) są zamieniane na „••••••••”, a pola haseł czyszczone.
Zrzuty 1440 px, gęstość 2×. Ekran, którego nie ma w portalu (np. brak zasobu z błędem), jest pomijany z powodem
w wyniku skryptu, a pozostałe powstają.

| Plik | Podpis |
|---|---|
| `portal-01-formularz-wykaz-aed` | Formularz zasobu w panelu dostawcy: pole „Wykaz AED” (TAK/NIE) z opisem. TAK oznacza wykaz w formacie zakresu v0.5, który portal sprawdzi i co noc dołączy do zbioru „Defibrylatory AED: wykaz zbiorczy”. |
| `portal-02a-walidacja-poprawny` | Zakładka walidacji danych zasobu-wykazu: plik zgodny z zakresem v0.5, bez błędów. |
| `portal-02b-walidacja-blad-slownika` | Ten sam widok dla wykazu z wartością spoza słownika (np. `dostepnosc`): komunikat z numerem wiersza i podpowiedzią „Użyj jednej z wartości słownika zakresu v0.5”. Taki wykaz nie trafia do wykazu zbiorczego. |
| `portal-03a-zbior-wykaz-zbiorczy` | Zbiór „Defibrylatory AED: wykaz zbiorczy” utworzony przez portal (instytucja-właściciel, kategoria Zdrowie, słowa kluczowe AED, defibrylator, wykaz AED). |
| `portal-03b-zasoby-csv-xlsx` | Zasoby zbioru zbiorczego: ten sam wykaz w CSV i XLSX, odświeżany po każdym scaleniu. |
| `portal-04-wykaz-zbiorczy-raport` | „Wykaz zbiorczy AED” (wzór: wykaz DGA): liczba AED, dołączone wykazy dostawców, pominięte wykazy z powodem (licencja, błędy walidacji), oznaczone duplikaty i licencja wykazu. |
