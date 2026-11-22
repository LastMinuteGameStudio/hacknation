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

Dowód zgodności pliku z wymaganiami portalu (nagłówki, RFC 4180, UTF-8, CSVW): [`DOWOD-URL.md`](DOWOD-URL.md).

## Jak odtworzyć

```bash
python3 -m venv /tmp/pw && /tmp/pw/bin/pip install playwright && /tmp/pw/bin/playwright install chromium
/tmp/pw/bin/python prezentacja/zrzuty/zrob_zrzuty.py          # publikuje nowy zbiór „(demo)” i robi 26 PNG
python3 prezentacja/zrzuty/sprawdz_url.py                      # DOWOD-URL.md dla ostatniego zbioru
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
