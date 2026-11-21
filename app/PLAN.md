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
| Edycja | **prywatny link edycji z tokenem**: ponowne wgranie pliku pod ten sam slug, publiczny URL bez zmian (Wojtek) | logowanie dostawcy i edycja rekordów |
| Wynik | URL z CSV (pola publiczne), JSON, metadane CSVW | — |
| Agregat | **połączenie (decyzja 22.11):** `/d/aed-polska.csv` to cały agregat (`dane/wynik` łącznie z OSM + zbiory dostawców), a `/d/aed-polska-bez-osm.csv` to wersja bez OSM. **Każdy rekord ma kolumny pochodzenia:** `dysponent_nazwa`, `zrodlo_danych`, `licencja_zrodla`, `data_aktualizacji`, żeby dało się odsiać dane niewiarygodne i nieaktualne | mapa |
| Mapowanie | heurystyka + słownik synonimów + analiza zawartości kolumn | model AI jako wsparcie, jeśli testy pokażą, że heurystyka nie wystarcza |
| Geokodowanie | adres bez współrzędnych: **geokoder GUGiK UUG** (decyzja 22.11; bez klucza, `https://services.gugik.gov.pl/uug/?request=GetAddress&address=…&srid=4326`) z cache, uzupełnia TERC/SIMC/ULIC i kod pocztowy; przy wielu wynikach zawężamy kodem pocztowym lub gminą; oznaczenie dokładności i ostrzeżenie; >200 adresów bez współrzędnych → ostrzeżenie „dodaj współrzędne” | Nominatim jako zapas, gdy GUGiK nie znajdzie adresu |
| Limity | plik do 10 MB i **20 000 wierszy** (decyzja 22.11), powyżej komunikat z prośbą o kontakt (Wojtek) | — |
| Wygląd | neutralny, kolory w zmiennych CSS (czekamy na identyfikację kampanii) | podmiana na kolory i logo akcji |
| Hosting | docker compose na dowolnej maszynie z **tunelem Cloudflare** (`cloudflared` jako serwis w compose); tunel nazwany na domenie Wojtka; ruch przychodzący wyłącznie przez tunel, wychodzący bez ograniczeń; bazowy URL w `BASE_URL` (Wojtek) | — |

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
  │    geocode.py       GUGiK UUG + cache w DB (TERC/SIMC/ULIC/kod pocztowy przy okazji)
  │    validate.py      O = błąd, Z = ostrzeżenie, formaty, współrzędne w Polsce
  │    export.py        CSV RFC 4180 (UTF-8, CRLF, przecinek), JSON, CSVW
  ├─ api/               endpointy, sesje importu
  └─ db/                PostgreSQL (SQLAlchemy + Alembic albo SQL na start)
        ▼
PostgreSQL (docker)
```

`docker-compose.yml`: `db` (postgres:16) + `app` (FastAPI + statyczny front) + `tunnel` (cloudflared). Jedno `docker compose up` dla jury.

### Wdrożenie i sieć (decyzja Wojtka, 22.11)

- Wszystkie nasze komponenty działają jako kontenery w jednym `docker-compose.yml`. Usługi zewnętrzne (geokoder) są wyjątkiem.
- **Ruch przychodzący z internetu trafia do aplikacji wyłącznie przez tunel Cloudflare.** Żaden serwis nie publikuje portów (`ports:`) w głównym pliku compose. Ruch wychodzący nie jest ograniczony: kontenery mają zwykły dostęp do internetu (geokoder, pobieranie źródeł), bo to demo (Wojtek).
- Jedna domyślna sieć compose: `tunnel` → `http://app:8000`, `app` → `db`.
- `tunnel` (`cloudflare/cloudflared`, wersja przypięta, nie `latest`): tunel nazwany z `TUNNEL_TOKEN` w `.env` (nie commitujemy). Wojtek podpina tunel do swojej domeny i przypisuje mu adres (public hostname → `http://app:8000`) w dashboardzie Cloudflare.
- `BASE_URL` = adres przypisany tunelowi w Cloudflare, więc linki `/d/{slug}.csv` są stałe.
- Lokalna praca bez tunelu: opcjonalny `docker-compose.dev.yml` publikuje `app` wyłącznie na `127.0.0.1:8000`.

### Model danych (PostgreSQL)

- `zbior`: id, `slug` (losowy, w URL), `dysponent_nazwa`, `dysponent_typ`, `telefon_kontaktowy`, `email_kontaktowy` (niepubliczne), `token_edycji_hash` (niepubliczny), `utworzono`, `zaktualizowano`, `zrodlo_url` (synchronizacja, później), `status`.
- `rekord`: id, `zbior_id`, `id_aed`, `dane` JSONB (pola v0.5), `ostrzezenia` JSONB.
- `import`: id, `zbior_id` (null do zatwierdzenia), `plik_nazwa`, `kolumny` JSONB, `podglad` JSONB, `mapowanie` JSONB, `wynik_walidacji` JSONB, `utworzono`.
- `geokod_cache`: `zapytanie` PK, `lat`, `lon`, `dokladnosc`, `utworzono`.

### Kontrakt API (ustalić na starcie, front i backend pracują równolegle)

| Metoda | Ścieżka | Co robi |
|---|---|---|
| GET | `/api/schemat` | pola v0.5 (nazwa, opis, typ, wymagalność, publiczne) i słowniki, dla frontu i formularza mapowania |
| POST | `/api/importy` | multipart: plik → `{import_id, kolumny[], podglad[10 wierszy], mapowanie_propozycja{kolumna: pole, pewnosc}}` |
| POST | `/api/importy/{id}/walidacja` | body: `{mapowanie, dysponent{nazwa, typ, telefon?, email?}}` → `{liczba_rekordow, bledy[], ostrzezenia[], podglad_wyniku[]}` (geokodowanie tutaj) |
| POST | `/api/importy/{id}/publikacja` | tylko gdy brak błędów → `{slug, url_csv, url_json, url_metadane, url_edycji}`; gdy import powstał z linku edycji, podmienia rekordy w istniejącym zbiorze (ten sam slug) |
| GET | `/api/zbiory/{slug}?token=…` | dane dysponenta i mapowanie dla linku edycji; zły token → 403 |
| POST | `/api/zbiory/{slug}/importy?token=…` | jak `/api/importy`, ale import jest powiązany z istniejącym zbiorem |
| GET | `/d/{slug}.csv` | CSV z polami publicznymi (RFC 4180, UTF-8, CRLF) |
| GET | `/d/{slug}.json` | to samo w JSON |
| GET | `/d/{slug}.csv-metadata.json` | CSVW (wzór: `zakres-danych/szablon-aed-publiczny.csv-metadata.json`) |
| GET | `/d/aed-polska.csv` | agregat: `dane/wynik/aed_unikalne.csv` (łącznie z OSM) + wszystkie opublikowane zbiory; kolumny pochodzenia przy każdym rekordzie |
| GET | `/d/aed-polska-bez-osm.csv` | to samo bez rekordów z OSM (ODbL) |
| GET | `/szablon.csv`, `/szablon.xlsx` | szablony z `zakres-danych/` |

Format błędu walidacji: `{wiersz, pole, kod, komunikat}` z komunikatem po polsku, zrozumiałym dla urzędnika.

## 4. Kreator (front)

Przed wgraniem pliku strona startowa krótko tłumaczy, po co to jest, pozwala pobrać szablon i przejść do „Zacznij”.

1. **Dysponent:** nazwa instytucji, typ (słownik `dysponent_typ`), opcjonalnie telefon i e-mail. Kontaktu nie publikujemy, co jest wprost napisane przy polu.
2. **Dane:** wgranie CSV/XLSX → tabela mapowania (kolumna z pliku → pole v0.5, podpowiedź z oznaczeniem pewności, lista rozwijana) → „Sprawdź” → lista błędów i ostrzeżeń pogrupowana po polach, z numerami wierszy. Błędy blokują przejście dalej, ostrzeżenia nie.
3. **Publikacja:** URL do skopiowania (przycisk „Kopiuj”), prywatny link edycji z wyraźnym ostrzeżeniem „zachowaj, nie udostępniaj” (wejście przez ten link pomija krok 1 i zapisuje dane pod ten sam URL), instrukcja krok po kroku dla dane.gov.pl („dodaj zasób → link → wklej URL → zaznacz Aktualizacja automatyczna, powtarzać co: dziennie”), linki do JSON i metadanych.

Wymagania przekrojowe: responsywność (od 320 px), WCAG 2.2 AA (kontrast, fokus, etykiety, komunikaty błędów powiązane z polami, cele dotyku min. 24 px), język polski.

## 5. Mapowanie kolumn i normalizacja: reguły

- Synonimy per pole (plik `aed_core/synonimy.py`), zebrane z realnych źródeł: Krosno/Marki („Długość geograficzna”, „ Nazwa”), Legionowo (`dlugosc_geograficzna`), Przemyśl (`street`, `home_number`, `geometry`), Warszawa (`location_street`, `device_availability`…), OSM (`indoor`, `access`, `opening_hours`), Géo'DAE (`adr_voie`, `acc`…).
- Porównanie nazw po normalizacji (małe litery, bez polskich znaków, spacji i podkreśleń), potem podobieństwo tekstu.
- Analiza zawartości: liczby 49–55 to szerokość, 14–24.2 to długość, `NN-NNN` to kod pocztowy, wartości tak/nie to bool, GG:MM-GG:MM to godziny, JSON z `lat`/`long` lub `coordinates` to geometria (rozbijana na dwa pola).
- Wykrywanie zamienionych lat/lon (przypadek Marek) i przecinka dziesiętnego.
- Adres w jednym polu („ul. Jasna 5, 38-400 Krosno”, pole specjalne `_adres_pelny`) rozbijany na ulicę, numer, kod pocztowy i miejscowość. Gdy się nie uda, ostrzeżenie. Brak ulicy → `nazwa_ulicy` = miejscowość (zasada z zakresu v0.5) + info.
- Współrzędne z precyzją z pliku, bez dopisywania zer; poniżej 5 miejsc po przecinku ostrzeżenie `NISKA_PRECYZJA` (Grzan, 22.11).
- Nagłówek wykrywany automatycznie (pomijamy wiersze tytułowe), powtórzone nazwy kolumn dostają ` (2)`, numery wierszy w komunikatach jak w arkuszu dostawcy.
- Godziny (kolumna z godzinami: pole specjalne `_godziny`): „24h”, „całodobowo”, „24/7” → `dostepny_24_7 = tak` i `X` w polach godzin. Format OSM `opening_hours` → pola `godziny_pn`…`godziny_nd`. Wolny tekst, którego nie da się sparsować → ostrzeżenie i `uwagi`.
- Pola stałe dla całego pliku: `dysponent_*` z kroku 1, `zrodlo_danych`, `data_aktualizacji` = teraz, `data_weryfikacji` (gdy brak: data wgrania + ostrzeżenie, decyzja Wojtka), `status` (gdy brak: `nieznany` + ostrzeżenie, potwierdzone przez Wojtka), `licencja` stała: CC0 1.0 (Wojtek), `id_aed` (gdy brak: generowany `<kod_terc lub slug>-<6 hex>` ze skrótu numeru seryjnego albo współrzędnych i nazwy, więc stały przy ponownym wgraniu, + ostrzeżenie; Grzan, 22.11).
- Pola O bez kolumny w pliku (`wewnatrz_budynku`, `dostepnosc`, `dostepny_24_7`): kreator pokazuje „ustaw dla wszystkich AED w pliku” (`wartosci_stale`); do wyboru jest błąd (Grzan, 22.11).
- Wartości słownikowe normalizowane synonimami wartości (np. „czynny” → `sprawny`, „ogólnodostępny” → `publiczny`).
- Geokodowanie synchronicznie w `/walidacja`, do 8 zapytań równolegle z cache. Adres nieznaleziony → ostrzeżenie, **rekord pominięty** w publikacji, reszta pliku się publikuje (Grzan, 22.11).
- Agregat: rekord dostawcy jest główny, rekordy z `dane/wynik` bliżej niż 30 m dostają `duplikat_id_aed` (nic nie usuwamy; Grzan, 22.11). Szczegóły w `KONTRAKT.md`.

## 6. Zadania i równoległość

Ścieżki A–E mogą iść równolegle po zadaniu T0. Szacunki są orientacyjne.

| # | Zadanie | Ścieżka | Zależy od | Szac. |
|---|---|---|---|---|
| T0 | Szkielet repo `app/`: struktura, docker-compose (db + app + tunnel cloudflared, konfiguracja wg §3 „Wdrożenie i sieć”, bez publikowanych portów), FastAPI „hello”, Vite + React + TypeScript (własne CSS, bez biblioteki komponentów), kontrakt API jako typy (Pydantic + TS) | — | — | 45 min |
| A1 | `schema.py`: wczytanie zakres-pol.csv i slowniki.csv | A: rdzeń | T0 | 20 min |
| A2 | `parsers.py`: CSV (sniff separatora, kodowania cp1250/utf-8, BOM, cudzysłowy) i XLSX (openpyxl) | A | T0 | 45 min |
| A3 | `mapping.py` + `synonimy.py`: propozycja mapowania z pewnością | A | A1, A2 | 1,5 h |
| A4 | `normalize.py`: liczby, daty, bool, słowniki, godziny, geometria, adres w jednym polu, zamiana lat/lon | A | A1 | 2 h |
| A5 | `validate.py`: O/Z/F, formaty, współrzędne w Polsce; duplikat `id_aed` lub numeru seryjnego w pliku = błąd, bliskie współrzędne = ostrzeżenie | A | A1, A4 | 1 h |
| A6 | `export.py`: CSV RFC 4180 (pola publiczne), JSON, CSVW | A | A1 | 45 min |
| A7 | `geocode.py`: GUGiK UUG z cache, rozstrzyganie niejednoznaczności (kod pocztowy, gmina), uzupełnianie TERC/SIMC/ULIC, `dokladnosc_polozenia` | A | A4 | 1 h |
| B1 | Schemat bazy + migracja | B: API | T0 | 30 min |
| B2 | Endpointy importu, walidacji i publikacji | B | B1, A2–A6 | 1,5 h |
| B3 | Endpointy publiczne `/d/{slug}.*`, szablony | B | B1, A6 | 30 min |
| B4 | Agregat `/d/aed-polska.csv` i `/d/aed-polska-bez-osm.csv` (dane/wynik + zbiory z bazy, kolumny pochodzenia) | B | B3 | 1 h |
| C1 | Layout, zmienne CSS, dostępność, strona startowa | C: front | T0 | 1 h |
| C2 | Krok 1: dysponent | C | C1 | 30 min |
| C3 | Krok 2: upload, tabela mapowania, wyniki walidacji | C | C1, kontrakt | 2 h |
| C4 | Krok 3: URL, kopiowanie, instrukcja dane.gov.pl | C | C1 | 45 min |
| D1 | **Zestaw testowy z realnych danych**. MVP: 5 miast z dane.gov.pl (Krosno, Marki uszkodzony, Legionowo, Przemyśl, Warszawa 19115). Jeśli starczy czasu: pliki z dane/surowe i syntetyczne „urzędowe” XLSX. Do tego **jeden bardzo wyraźny przykład demo** od początku do końca | D: testy | — | 1 h |
| D2 | Test jakości mapowania: dla każdej fixtury oczekiwane mapowanie, raport % trafień. Próg decyzji, czy potrzebny model AI | D | A3, D1 | 45 min |
| D3 | Testy jednostkowe normalizacji i walidacji + test end-to-end API (upload → URL → CSV zgodny z RFC 4180) | D | A4–A6, B2 | 1 h |
| E1 | Instrukcja dla dostawcy (treść kroku 3) + zrzuty ekranu do prezentacji (min. 5 slajdów z dowodami) | E: dokumentacja | C4 | 45 min |
| E2 | Audyt WCAG (axe/Lighthouse) i responsywności, poprawki | E | C2–C4 | 45 min |
| E3 | **Schemat i user story do prezentacji** (Grzan, 22.11): diagram przepływu (źródła i dysponenci → TuAED: mapowanie, walidacja, geokodowanie → stały URL → dane.gov.pl z „Aktualizacją automatyczną” → odbiorcy) i historia użytkownika dysponenta krok po kroku (urzędnik z plikiem XLSX → URL na dane.gov.pl → poprawka przez link edycji). Do slajdów 3 i 9 (`prezentacja/SZKIC-SLAJDOW.md`) | E | architektura (§3), kreator (§4) | 45 min |
| S1 | Synchronizacja z URL źródła (demo Przemyśl): zapamiętane mapowanie, cykliczne pobieranie, wstrzymanie przy zmianie struktury | stretch | MVP | 2 h |
| S2 | Mapa agregatu (Leaflet + OSM) | stretch | B4 | 1 h |
| S3 | Logowanie i edycja | stretch | MVP | 2 h+ |
| S4 | Formularz ręczny | stretch | C | 1,5 h |

**Ścieżka krytyczna:** T0 → A2/A3/A4 → A5 → B2 → C3 → E1. Mapowanie i normalizacja (A3, A4) to najbardziej ryzykowna część i dlatego D1/D2 zaczynamy od razu, równolegle.

**Jak zrównoleglić (decyzja Wojtka):** każda ścieżka A, B, C, D ma osobną sesję Claude we własnym klonie. Najpierw T0 i kontrakt API jako jeden krok, robione przez jedną sesję; pozostałe czekają na T0 w main. Potem branch na ścieżkę (`app-a-rdzen`, `app-b-api`, `app-c-front`, `app-d-testy`), częste małe PR-y do main. Potem równolegle: (1) rdzeń A + testy D, (2) API B, (3) front C na mockach kontraktu. E na koniec.

## 7. Definicja „gotowe” dla MVP

- `docker compose up` uruchamia całość razem z tunelem, a aplikacja odpowiada pod adresem tunelu i nie jest dostępna przez żaden opublikowany port. Na czystej maszynie test: wgranie plików **Krosno, Legionowo, Przemyśl i Warszawa 19115** → mapowanie bez poprawek → URL → CSV zgodny ze schematem v0.5 (Wojtek).
- Plik Marki: aplikacja wykrywa problem (jedna kolumna i zamienione współrzędne) i albo go naprawia, albo jasno komunikuje.
- Raport D2 pokazuje trafność mapowania na wszystkich fixturach.
- Front działa przy 320 px i przechodzi axe bez błędów krytycznych.
- Instrukcja dane.gov.pl w kroku 3 i zrzuty ekranu do prezentacji są gotowe.

## 8. Otwarte kwestie

- ODbL dla danych z OSM w agregacie: w prototypie świadomie pomijamy, bo OSM służy do prezentacji skali (Wojtek). Do produkcji pytanie do MC (PYTANIA-DO-ORGANIZATORA.md). Licencja zbioru wynikowego rozstrzygnięta: stała CC0 1.0 (Wojtek).
- Identyfikacja wizualna kampanii: czekamy (Grzan).
- Slajdy: kto robi i na kiedy potrzebna działająca wersja (decyduje Grzan).
- Zrzuty z panelu dostawcy dane.gov.pl: prośba do organizatora. Do czasu odpowiedzi instrukcja w kroku 3 bazuje na kodzie portalu i Przewodniku v1.23.
