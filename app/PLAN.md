# Plan aplikacji: 06 Misja AED

Stan: 22.11.2026, przed kodowaniem. Deadline kodowania: **22.11, godz. 11:00**. Plan na podstawie decyzji Grzana (NOTATKI-ZESPOLU.md) i odpowiedzi z sesji planowania.

## 1. Cel

Strona, na którą dostawca (gmina, urząd, OSP, szkoła, firma) wgrywa swój plik z AED. Aplikacja:
1. przekształca dane do **wzorcowego zakresu v0.5** (`zakres-danych/zakres-pol.csv`),
2. waliduje je: brak pól obowiązkowych to błąd, a brak zalecanych to ostrzeżenie,
3. wystawia czysty CSV pod **stałym, unikalnym URL**,
4. pokazuje instrukcję: dodaj ten URL na dane.gov.pl jako zasób i włącz „Aktualizację automatyczną: dziennie”.

Dodatkowo aplikacja wystawia **zbiorczy URL ogólnopolski**: agregat z `dane/wynik` plus wszystkie zbiory wgrane przez dostawców.

Rdzeń to dane i ich jakość, frontu ma być mało (mentor: „budujecie bazę danych, nie aplikację”).

## 2. Zakres

| | MVP (do 11:00) | Jeśli starczy czasu (kolejność) |
|---|---|---|
| Wejście | CSV i XLSX z **mapowaniem kolumn**; nasz szablon CSV/XLSX przechodzi bez mapowania | 1) **synchronizacja z URL źródła** (demo: Przemyśl); 2) ODS, GeoJSON; 3) formularz ręczny |
| Edycja | brak, poprawka przez ponowne wgranie pliku (nowy zbiór) | logowanie dostawcy i edycja (URL bez zmian) |
| Wynik | URL z CSV (pola publiczne), JSON, metadane CSVW | — |
| Agregat | URL zbiorczego CSV | mapa |
| Mapowanie | heurystyka + słownik synonimów + analiza zawartości kolumn | model AI jako wsparcie, jeśli testy pokażą, że heurystyka nie wystarcza |
| Geokodowanie | adres bez współrzędnych: Nominatim z cache, oznaczenie dokładności, ostrzeżenie | — |
| Wygląd | neutralny, kolory w zmiennych CSS (czekamy na identyfikację kampanii) | podmiana na kolory i logo akcji |
| Hosting | lokalnie (docker-compose), demo lokalne; bazowy URL w zmiennej środowiskowej `BASE_URL` (Wojtek: serwera na razie nie ma) | publiczny serwer, jeśli się pojawi |

Poza zakresem: AED w pojazdach, zgłoszenia od obywateli, aplikacja mobilna natywna.

## 3. Architektura

```
przeglądarka (React, responsywny, WCAG 2.2 AA)
        │  REST/JSON
        ▼
FastAPI (Python 3.12) ─── serwuje też zbudowany front (jeden kontener aplikacji)
  ├─ aed_core/          czysta biblioteka, bez I/O sieciowego poza geokoderem
  │    schema.py        wczytuje zakres-pol.csv + slowniki.csv (jedno źródło prawdy)
  │    parsers.py       CSV (separator, kodowanie, BOM) i XLSX → tabela
  │    mapping.py       podpowiedź mapowania kolumn → pola v0.5
  │    normalize.py     wartości → format v0.5 (liczby, daty, bool, słowniki, godziny, współrzędne)
  │    geocode.py       Nominatim + cache w DB, 1 zapytanie/s
  │    validate.py      O = błąd, Z = ostrzeżenie, formaty, współrzędne w Polsce
  │    export.py        CSV RFC 4180 (UTF-8, CRLF, przecinek), JSON, CSVW
  ├─ api/               endpointy, sesje importu
  └─ db/                PostgreSQL (SQLAlchemy + Alembic albo SQL na start)
        ▼
PostgreSQL (docker)
```

`docker-compose.yml`: `db` (postgres:16) + `app` (FastAPI + statyczny front). Jedno `docker compose up` dla jury.

### Model danych (PostgreSQL)

- `zbior`: id, `slug` (losowy, w URL), `dysponent_nazwa`, `dysponent_typ`, `telefon_kontaktowy`, `email_kontaktowy` (niepubliczne), `utworzono`, `zaktualizowano`, `zrodlo_url` (synchronizacja, później), `status`.
- `rekord`: id, `zbior_id`, `id_aed`, `dane` JSONB (pola v0.5), `ostrzezenia` JSONB.
- `import`: id, `zbior_id` (null do zatwierdzenia), `plik_nazwa`, `kolumny` JSONB, `podglad` JSONB, `mapowanie` JSONB, `wynik_walidacji` JSONB, `utworzono`.
- `geokod_cache`: `zapytanie` PK, `lat`, `lon`, `dokladnosc`, `utworzono`.

### Kontrakt API (ustalić na starcie, front i backend pracują równolegle)

| Metoda | Ścieżka | Co robi |
|---|---|---|
| GET | `/api/schemat` | pola v0.5 (nazwa, opis, typ, wymagalność, publiczne) i słowniki, dla frontu i formularza mapowania |
| POST | `/api/importy` | multipart: plik → `{import_id, kolumny[], podglad[10 wierszy], mapowanie_propozycja{kolumna: pole, pewnosc}}` |
| POST | `/api/importy/{id}/walidacja` | body: `{mapowanie, dysponent{nazwa, typ, telefon?, email?}}` → `{liczba_rekordow, bledy[], ostrzezenia[], podglad_wyniku[]}` (geokodowanie tutaj) |
| POST | `/api/importy/{id}/publikacja` | tylko gdy brak błędów → `{slug, url_csv, url_json, url_metadane}` |
| GET | `/d/{slug}.csv` | CSV z polami publicznymi (RFC 4180, UTF-8, CRLF) |
| GET | `/d/{slug}.json` | to samo w JSON |
| GET | `/d/{slug}.csv-metadata.json` | CSVW (wzór: `zakres-danych/szablon-aed-publiczny.csv-metadata.json`) |
| GET | `/d/aed-polska.csv` | agregat: `dane/wynik/aed_unikalne.csv` + wszystkie opublikowane zbiory |
| GET | `/szablon.csv`, `/szablon.xlsx` | szablony z `zakres-danych/` |

Format błędu walidacji: `{wiersz, pole, kod, komunikat}` z komunikatem po polsku, zrozumiałym dla urzędnika.

## 4. Kreator (front)

Przed wgraniem pliku strona startowa krótko tłumaczy, po co to jest, pozwala pobrać szablon i przejść do „Zacznij”.

1. **Dysponent:** nazwa instytucji, typ (słownik `dysponent_typ`), opcjonalnie telefon i e-mail. Kontaktu nie publikujemy, co jest wprost napisane przy polu.
2. **Dane:** wgranie CSV/XLSX → tabela mapowania (kolumna z pliku → pole v0.5, podpowiedź z oznaczeniem pewności, lista rozwijana) → „Sprawdź” → lista błędów i ostrzeżeń pogrupowana po polach, z numerami wierszy. Błędy blokują przejście dalej, ostrzeżenia nie.
3. **Publikacja:** URL do skopiowania (przycisk „Kopiuj”), instrukcja krok po kroku dla dane.gov.pl („dodaj zasób → link → wklej URL → zaznacz Aktualizacja automatyczna, powtarzać co: dziennie”), linki do JSON i metadanych.

Wymagania przekrojowe: responsywność (od 320 px), WCAG 2.2 AA (kontrast, fokus, etykiety, komunikaty błędów powiązane z polami, cele dotyku min. 24 px), język polski.

## 5. Mapowanie kolumn i normalizacja: reguły

- Synonimy per pole (plik `aed_core/synonimy.py`), zebrane z realnych źródeł: Krosno/Marki („Długość geograficzna”, „ Nazwa”), Legionowo (`dlugosc_geograficzna`), Przemyśl (`street`, `home_number`, `geometry`), Warszawa (`location_street`, `device_availability`…), OSM (`indoor`, `access`, `opening_hours`), Géo'DAE (`adr_voie`, `acc`…).
- Porównanie nazw po normalizacji (małe litery, bez polskich znaków, spacji i podkreśleń), potem podobieństwo tekstu.
- Analiza zawartości: liczby 49–55 to szerokość, 14–24.2 to długość, `NN-NNN` to kod pocztowy, wartości tak/nie to bool, GG:MM-GG:MM to godziny, JSON z `lat`/`long` lub `coordinates` to geometria (rozbijana na dwa pola).
- Wykrywanie zamienionych lat/lon (przypadek Marek) i przecinka dziesiętnego.
- Adres w jednym polu („ul. Jasna 5, 38-400 Krosno”) rozbijany na ulicę, numer, kod pocztowy i miejscowość. Gdy się nie uda, ostrzeżenie.
- Godziny: „24h”, „całodobowo”, „24/7” → `dostepny_24_7 = tak`. Format OSM `opening_hours` → pola `godziny_pn`…`godziny_nd`. Wolny tekst, którego nie da się sparsować → ostrzeżenie i `uwagi`.
- Pola stałe dla całego pliku: `dysponent_*` z kroku 1, `zrodlo_danych`, `data_aktualizacji` = teraz, `data_weryfikacji` (gdy brak: ostrzeżenie i data wgrania? **decyzja do testów**), `status` (gdy brak: `nieznany` + ostrzeżenie), `id_aed` (gdy brak: generowany `<kod_terc lub slug>-<nr>`).

## 6. Zadania i równoległość

Ścieżki A–E mogą iść równolegle po zadaniu T0. Szacunki są orientacyjne.

| # | Zadanie | Ścieżka | Zależy od | Szac. |
|---|---|---|---|---|
| T0 | Szkielet repo `app/`: struktura, docker-compose (db + app), FastAPI „hello”, Vite + React + TypeScript (własne CSS, bez biblioteki komponentów), kontrakt API jako typy (Pydantic + TS) | — | — | 45 min |
| A1 | `schema.py`: wczytanie zakres-pol.csv i slowniki.csv | A: rdzeń | T0 | 20 min |
| A2 | `parsers.py`: CSV (sniff separatora, kodowania cp1250/utf-8, BOM, cudzysłowy) i XLSX (openpyxl) | A | T0 | 45 min |
| A3 | `mapping.py` + `synonimy.py`: propozycja mapowania z pewnością | A | A1, A2 | 1,5 h |
| A4 | `normalize.py`: liczby, daty, bool, słowniki, godziny, geometria, adres w jednym polu, zamiana lat/lon | A | A1 | 2 h |
| A5 | `validate.py`: O/Z/F, formaty, współrzędne w Polsce, duplikaty id i punktów w pliku | A | A1, A4 | 1 h |
| A6 | `export.py`: CSV RFC 4180 (pola publiczne), JSON, CSVW | A | A1 | 45 min |
| A7 | `geocode.py`: Nominatim z cache i limitem 1/s, `dokladnosc_polozenia` | A | A4 | 45 min |
| B1 | Schemat bazy + migracja | B: API | T0 | 30 min |
| B2 | Endpointy importu, walidacji i publikacji | B | B1, A2–A6 | 1,5 h |
| B3 | Endpointy publiczne `/d/{slug}.*`, szablony | B | B1, A6 | 30 min |
| B4 | Agregat `/d/aed-polska.csv` (dane/wynik + zbiory z bazy) | B | B3 | 45 min |
| C1 | Layout, zmienne CSS, dostępność, strona startowa | C: front | T0 | 1 h |
| C2 | Krok 1: dysponent | C | C1 | 30 min |
| C3 | Krok 2: upload, tabela mapowania, wyniki walidacji | C | C1, kontrakt | 2 h |
| C4 | Krok 3: URL, kopiowanie, instrukcja dane.gov.pl | C | C1 | 45 min |
| D1 | **Zestaw testowy z realnych danych**: fixtury Krosno, Marki (uszkodzony), Legionowo, Przemyśl, Warszawa 19115, Géo'DAE (próbka), plus 2–3 syntetyczne „urzędowe” XLSX z dziwnymi nagłówkami | D: testy | — | 1 h |
| D2 | Test jakości mapowania: dla każdej fixtury oczekiwane mapowanie, raport % trafień. Próg decyzji, czy potrzebny model AI | D | A3, D1 | 45 min |
| D3 | Testy jednostkowe normalizacji i walidacji + test end-to-end API (upload → URL → CSV zgodny z RFC 4180) | D | A4–A6, B2 | 1 h |
| E1 | Instrukcja dla dostawcy (treść kroku 3) + zrzuty ekranu do prezentacji (min. 5 slajdów z dowodami) | E: dokumentacja | C4 | 45 min |
| E2 | Audyt WCAG (axe/Lighthouse) i responsywności, poprawki | E | C2–C4 | 45 min |
| S1 | Synchronizacja z URL źródła (demo Przemyśl): zapamiętane mapowanie, cykliczne pobieranie, wstrzymanie przy zmianie struktury | stretch | MVP | 2 h |
| S2 | Mapa agregatu (Leaflet + OSM) | stretch | B4 | 1 h |
| S3 | Logowanie i edycja | stretch | MVP | 2 h+ |
| S4 | Formularz ręczny | stretch | C | 1,5 h |

**Ścieżka krytyczna:** T0 → A2/A3/A4 → A5 → B2 → C3 → E1. Mapowanie i normalizacja (A3, A4) to najbardziej ryzykowna część i dlatego D1/D2 zaczynamy od razu, równolegle.

**Jak zrównoleglić (decyzja Wojtka):** każda ścieżka A, B, C, D ma osobną sesję Claude we własnym klonie. Najpierw T0 i kontrakt API jako jeden krok. Potem równolegle: (1) rdzeń A + testy D, (2) API B, (3) front C na mockach kontraktu. E na koniec.

## 7. Definicja „gotowe” dla MVP

- `docker compose up` uruchamia całość. Na czystej maszynie test: wgranie pliku Krosno → mapowanie bez poprawek → URL → CSV zgodny ze schematem v0.5.
- Plik Marki: aplikacja wykrywa problem (jedna kolumna i zamienione współrzędne) i albo go naprawia, albo jasno komunikuje.
- Raport D2 pokazuje trafność mapowania na wszystkich fixturach.
- Front działa przy 320 px i przechodzi axe bez błędów krytycznych.
- Instrukcja dane.gov.pl w kroku 3 i zrzuty ekranu do prezentacji są gotowe.

## 8. Otwarte kwestie

- Brak `data_weryfikacji` w pliku: przyjąć datę wgrania czy wymagać od dostawcy? (rozstrzygnąć przy testach)
- Licencja zbioru wynikowego (CC0 albo CC BY 4.0) i ODbL dla danych z OSM w agregacie. Pytania są w PYTANIA-DO-ORGANIZATORA.md.
- Identyfikacja wizualna kampanii: czekamy (Grzan).
- Hosting: serwera na razie nie ma (Wojtek), demo lokalnie. Bazowy URL w `BASE_URL`.
