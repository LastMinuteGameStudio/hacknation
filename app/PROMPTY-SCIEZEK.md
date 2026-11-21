# Prompty dla sesji ścieżek A–D

Każdą ścieżkę uruchamiasz w osobnym oknie tmux, w osobnym klonie repo (albo `git worktree`), jako nową sesję Claude. Wklej odpowiedni prompt. Deadline kodowania: **22.11, godz. 11:00**.

Wspólny wstęp dla każdej sesji (już zawarty w promptach): czytaj tylko to, co wskazane, żeby kontekst był mały.

---

## A: rdzeń konwersji

```
Jesteś sesją ścieżki A (rdzeń konwersji) w projekcie hackathonowym 06 Misja AED. Pracujesz na branchu app-a-rdzen (utwórz go z main).
Przeczytaj TYLKO: app/README.md, app/KONTRAKT.md (sekcje 3 i 4), app/PLAN.md (sekcja 5 „Mapowanie kolumn i normalizacja”), backend/aed_core/types.py, backend/aed_core/schema.py oraz nagłówek zakres-danych/zakres-pol.csv i zakres-danych/slowniki.csv. Fixtury do ręcznych prób: app/backend/tests/fixtury/ (opis w ZRODLA.md).
Zadania w kolejności (każde z testami jednostkowymi w backend/tests/test_core_*.py):
A2 parsers.read_table (CSV: separator, utf-8/cp1250, BOM, wiersz nagłówka nie zawsze pierwszy, przypadek Marki z całym wierszem w jednym polu; XLSX przez openpyxl, wartości jako tekst bez utraty precyzji współrzędnych; limity 10 MB i 20 000 wierszy),
A3 mapping.suggest_mapping + synonimy.py (heurystyka: znormalizowane nazwy, podobieństwo, analiza zawartości; geometria → "_geometria"; adres w jednym polu → "_adres_pelny"),
A4 normalize.normalize_table (formaty v0.5, pola stałe i domyślne z ostrzeżeniami, rozbijanie adresu i geometrii, godziny, zamiana lat/lon),
A5 validate.validate_records, A6 export (CSV RFC 4180, JSON, CSVW), A7 geocode.GugikGeocoder (GUGiK UUG, cache, niejednoznaczności; Nominatim jako zapas).
Pola specjalne "_geometria" i "_adres_pelny" są wartościami mapowania (nie polami v0.5). Jeśli dodajesz nowe, dopisz je do KONTRAKT.md.
Zasady: edytujesz tylko pliki ścieżki A z app/README.md. Zmiany types.py lub kontraktu zgłaszasz najpierw na ~/Desktop/hacknation-wspolne/TABLICA.md. Ścieżka D buduje testy na realnych plikach i będzie zgłaszać problemy przez SendMessage: traktuj je priorytetowo. Po każdym ukończonym zadaniu: testy zielone (cd app/backend && .venv/bin/python -m pytest -q), commit, push na app-a-rdzen, merge do main (git pull --rebase origin main przed). Wpisz ZAJMUJĘ/GOTOWE na tablicy.
Zacznij od wpisu ZAJMUJĘ na tablicy, potem A2.
```

## B: API i baza

```
Jesteś sesją ścieżki B (API i baza) w projekcie hackathonowym 06 Misja AED. Pracujesz na branchu app-b-api (utwórz go z main).
Przeczytaj TYLKO: app/README.md, app/KONTRAKT.md (całość), app/PLAN.md (sekcja 3 „Architektura” i tabela zadań B), backend/app/*.py, backend/aed_core/types.py.
Zadania: B1 baza (db.py jest szkicem, popraw w razie potrzeby; Postgres w dockerze), B2 endpointy import → walidacja → publikacja oraz edycja przez prywatny link (token: losowy, w bazie tylko hash; publikacja importu powiązanego ze zbiorem zastępuje rekordy pod tym samym slugiem), B3 pliki publiczne /d/{slug}.csv|.json|.csv-metadata.json i szablony, B4 agregat /d/aed-polska.csv i /d/aed-polska-bez-osm.csv (dane/wynik/aed_unikalne.csv + zbiory z bazy, kolumny pochodzenia przy każdym rekordzie; zobacz dane/README.md).
Rdzeń aed_core robi ścieżka A równolegle. Dopóki jej funkcja zgłasza NotImplementedError, używaj atrap z app/mock.py (MOCK=auto), żeby front (C) mógł działać. Gdy rdzeń zadziała, wyłącz atrapy dla danej funkcji.
Testy API w backend/tests/test_api_*.py (TestClient; baza testowa: SQLite przez DATABASE_URL=sqlite:///… albo Postgres w dockerze). Docker: uruchom Docker Desktop, cd app && cp .env.example .env && docker compose up --build. Sprawdź, że całość wstaje.
Zasady: edytujesz tylko pliki ścieżki B z app/README.md. Zmiany kontraktu zgłaszasz najpierw na ~/Desktop/hacknation-wspolne/TABLICA.md i do sesji C przez SendMessage. Po każdym zadaniu: testy zielone, commit, push na app-b-api, merge do main (git pull --rebase origin main przed). Wpisz ZAJMUJĘ/GOTOWE na tablicy.
Zacznij od wpisu ZAJMUJĘ na tablicy, potem B1 i B2.
```

## C: front

```
Jesteś sesją ścieżki C (front) w projekcie hackathonowym 06 Misja AED. Pracujesz na branchu app-c-front (utwórz go z main).
Przeczytaj TYLKO: app/README.md, app/KONTRAKT.md (sekcje 1, 2), app/PLAN.md (sekcja 4 „Kreator”), frontend/src/**. Paleta i logo kampanii: plik „hacknation paleta.svg” w katalogu głównym repo (tokeny są już w src/styles/tokens.css).
Stos: Vite + React + TypeScript, własny CSS, bez bibliotek komponentów. Node: jeśli brak, `brew install node`. Backend z atrapami: cd app/backend && python3.12 -m venv .venv && .venv/bin/pip install -r requirements.txt && .venv/bin/uvicorn app.main:app --reload. Front: cd app/frontend && npm install && npm run dev (proxy /api → :8000).
Zadania: C1 layout, logo, strona startowa (po co to jest, szablony do pobrania), C2 krok 1 Dysponent (nazwa, typ ze słownika dysponent_typ z /api/schemat, opcjonalny telefon i e-mail z dopiskiem „nie publikujemy”), C3 krok 2 Dane (upload CSV/XLSX, wybór arkusza, tabela mapowania kolumna → pole v0.5 z podpowiedzią i pewnością, lista komunikatów po walidacji pogrupowana po polach z numerami wierszy; błędy blokują dalej), C4 krok 3 Publikacja (URL z przyciskiem Kopiuj, prywatny link edycji z ostrzeżeniem „zachowaj, nie udostępniaj”, instrukcja dla dane.gov.pl: dodaj zasób → link → wklej URL → zaznacz „Aktualizacja automatyczna”, „powtarzać co: dziennie”; licencja CC0 1.0), plus ścieżka /edycja/{slug}?token=… (pomija krok 1, wgrywa nowy plik pod ten sam URL).
Wymagania: responsywność od 320 px, WCAG 2.2 AA (etykiety, komunikaty błędów powiązane z polami aria-describedby, fokus po zmianie kroku na nagłówek, kontrast, cele dotyku min. 24 px, nawigacja klawiaturą), język polski, prosto i krótko.
Zasady: edytujesz tylko frontend/** (poza src/api/types.ts, który jest wspólny). Zmiany kontraktu zgłaszasz na ~/Desktop/hacknation-wspolne/TABLICA.md i do sesji B przez SendMessage. Po każdym kroku: npm run build bez błędów, commit, push na app-c-front, merge do main (git pull --rebase origin main przed). Wpisz ZAJMUJĘ/GOTOWE na tablicy.
Zacznij od wpisu ZAJMUJĘ na tablicy, potem C1.
```

## D: testy na realnych danych

```
Jesteś sesją ścieżki D (testy na realnych danych) w projekcie hackathonowym 06 Misja AED. Pracujesz na branchu app-d-testy (utwórz go z main).
Przeczytaj TYLKO: app/README.md, app/KONTRAKT.md (sekcje 3 i 4), app/PLAN.md (sekcja 5 i tabela zadań D), backend/aed_core/types.py, backend/tests/fixtury/ZRODLA.md oraz zakres-danych/zakres-pol.csv.
Zadania:
D1 fixtury: są już krosno.csv, marki.csv, marki.xlsx, legionowo.csv, przemysl.csv, przemysl_2024.csv, warszawa_19115.geojson. Dla każdej przygotuj oczekiwane mapowanie (kolumna → pole v0.5 albo null) i oczekiwane wartości kilku rekordów po normalizacji (backend/tests/fixtury/oczekiwane/*.json). Dodaj 2–3 syntetyczne „urzędowe” XLSX (tytuł nad tabelą, scalone komórki, przecinek dziesiętny, adres w jednym polu, „24h” w godzinach, kolumny w dziwnej kolejności), generowane skryptem w tests/fixtury/generuj_syntetyczne.py (openpyxl).
D2 raport jakości mapowania: backend/tests/raport_mapowania.py (uruchamialny: python -m tests.raport_mapowania) wypisuje dla każdej fixtury % trafionych kolumn i listę pomyłek. Test test_realne_mapowanie.py: Krosno, Legionowo, Przemyśl i Warszawa muszą mieć 100% bez ręcznych poprawek (decyzja zespołu), a Marki musi zostać rozpoznane i naprawione albo jasno zgłoszone.
D3 testy end-to-end: plik → normalize → validate → export.to_csv: CSV zgodny z RFC 4180 i zakresem v0.5; test API upload → walidacja → publikacja → GET /d/{slug}.csv (gdy ścieżka B skończy B2–B3).
Do tego przygotuj JEDEN bardzo wyraźny przykład demo od początku do końca (propozycja: Przemyśl, źle sformatowany plik miejski, który miasto opublikowało w 2024 i porzuciło) z opisem kroków w backend/tests/fixtury/DEMO.md.
Rdzeń robi ścieżka A równolegle. Twoje testy będą na początku czerwone (NotImplementedError), co jest w porządku. Oznacz je i uruchamiaj w miarę postępu A. Każdy znaleziony problem z mapowaniem lub normalizacją zgłaszaj sesji A przez SendMessage (konkretnie: plik, kolumna, oczekiwane, otrzymane). Jeśli raport D2 pokaże, że heurystyka nie wystarcza, zgłoś to na tablicy jako decyzję do podjęcia (model AI jako wsparcie).
Zasady: edytujesz tylko pliki ścieżki D z app/README.md (nie kod aed_core). Po każdym zadaniu: commit, push na app-d-testy, merge do main (git pull --rebase origin main przed). Wpisz ZAJMUJĘ/GOTOWE na tablicy.
Zacznij od wpisu ZAJMUJĘ na tablicy, potem D1.
```
