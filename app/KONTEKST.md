# Kontekst projektu dla agentów: 06 Misja AED

Ten plik wyjaśnia, **co budujemy i dlaczego**. Przeczytaj go, zanim odpowiesz na pytania o projekt, zaczniesz doszczegóławiać plan albo pisać kod. Stan: 22.11.2026, ok. 01:00. Zespół (Grzan i znajomi) właśnie doszczegóławia projekt, więc **decyzje mogą się zmieniać**. Nowsze ustalenia mają pierwszeństwo przed tym plikiem.

## W jednym zdaniu

Strona, na którą instytucja (gmina, urząd, OSP, szkoła, firma) wgrywa swój plik z defibrylatorami w dowolnym arkuszu. Strona przekształca go do wspólnego, wzorcowego formatu, sprawdza i wystawia pod stałym URL, który instytucja podpina na dane.gov.pl. Dzięki temu dane o AED od wszystkich dysponentów trafiają na portal w jednym formacie i są aktualizowane.

## Dlaczego tak (najważniejsze ustalenia)

- **Zadanie** (zadania/06-mc-misja-aed/TRESC.md): rozwiązanie ma „ułatwić zebranie w portalu dane.gov.pl” danych o AED od wszystkich dysponentów w jednolity sposób, z wzorcowym zakresem danych (xlsx) i kampanią (logo, hasło, księga znaku). Największe wagi w ocenie: zgodność z zasadami dane.gov.pl 30%, logo i hasło 25%.
- **Mentor** (ROZMOWA-MENTOR.md, mentor jest medykiem i dostawcą AED, nie jest z MC): budujemy **bazę danych i jednolitą „formatkę”, a nie aplikację** dla obywateli. Za dane odpowiadają dostawcy, nie dane.gov.pl. **Nie zbieramy zgłoszeń od obywateli.** Deduplikacja po numerze seryjnym. Godziny dostępności w strukturze, nie wolnym tekstem. Ciągła synchronizacja. Nie przeregulowywać.
- **Decyzje Grzana** (NOTATKI-ZESPOLU.md): agregujemy dane; celem jest, żeby instytucje **chciały** publikować na dane.gov.pl; **AED w pojazdach są poza zakresem**.
- **Jak publikuje się na dane.gov.pl** (RESEARCH.md): API portalu służy tylko do odczytu, więc publikuje wyłącznie konto dostawcy. Dostawca może dodać zasób jako **URL**. Po włączeniu „Aktualizacji automatycznej” (dziennie, tygodniowo, miesięcznie) portal sam ponownie pobiera plik (potwierdzone w kodzie portalu). Bez tej opcji trzyma kopię z chwili dodania. Istnieje też automatyczny import XML (deweloperzy), często przez pośredników, ale jego rejestracja dla AED jest niepotwierdzona.
- **Format:** czysty CSV według standardu dane.gov.pl (RFC 4180, UTF-8, przecinek, ISO 8601, adres w osobnych polach) to 3★. Z metadanymi CSVW lub JSON-LD to 4★. 5★ (dane połączone) to tylko 0,03% portalu, więc nie jest celem.

## Źródła prawdy (nie duplikuj, odwołuj się)

| Co | Gdzie |
|---|---|
| Plan aplikacji: zakres MVP, architektura, kontrakt API, zadania i równoległość | `app/PLAN.md` |
| Wzorcowy zakres danych v0.5 (58 pól, O/Z/F, publiczne i niepubliczne), słowniki, szablony CSV/XLSX, CSVW | `zakres-danych/` (`zakres-pol.csv`, `slowniki.csv`) |
| Zagregowane dane AED (ok. 19 tys., 15 źródeł) i skrypty | `dane/` (README tam) |
| Decyzje i pomysły zespołu (z podpisem) | `zadania/06-mc-misja-aed/NOTATKI-ZESPOLU.md` |
| Research: zasady dane.gov.pl, Francja (Géo'DAE), publikacja przez URL, odświeżanie | `zadania/06-mc-misja-aed/RESEARCH.md` |
| Rozmowa z mentorem | `zadania/06-mc-misja-aed/ROZMOWA-MENTOR.md` |
| Pytania do organizatora (MC) | `zadania/06-mc-misja-aed/PYTANIA-DO-ORGANIZATORA.md` |
| Źródła danych AED | `ZRODLA-DANYCH.md`, `ZESTAWIENIE-ZRODEL.md` |

## Decyzje techniczne (z sesji planowania, 22.11 ok. 00:45)

- Backend: **FastAPI** (Python). Baza: **PostgreSQL w dockerze**. Front: lekki **React**, mało ekranów, **responsywny**, WCAG 2.2 AA.
- Hosting: lokalnie (docker-compose). Serwera znajomego na razie nie ma (Wojtek, 22.11), demo pokazujemy lokalnie.
- Wejście w MVP: **CSV i XLSX z mapowaniem kolumn** oraz nasz szablon. Jeśli starczy czasu: **synchronizacja z URL źródła** (demo: Przemyśl), potem formularz ręczny.
- Mapowanie kolumn: **heurystyka + słownik synonimów**. Model AI tylko wtedy, gdy testy na realnych danych pokażą, że heurystyka nie wystarcza. **Testy na realnych plikach są ważne.**
- Brak współrzędnych: **geokodowanie z potwierdzeniem** (Nominatim, oznaczenie dokładności, ostrzeżenie).
- Edycja i logowanie: **nie w MVP**. Poprawka w MVP to ponowne wgranie pliku przez **prywatny link edycji** pod ten sam URL (Wojtek, 22.11), żeby „Aktualizacja automatyczna” na dane.gov.pl miała sens.
- Agregat: **tylko URL zbiorczego CSV**, mapa jeśli starczy czasu.
- Krok 1 kreatora: nazwa i typ dysponenta oraz opcjonalny kontakt służbowy (kontaktu nie publikujemy). Dostawcy nie weryfikujemy, bo robi to dane.gov.pl przy publikacji.
- Wygląd: **czekamy na identyfikację kampanii**, kolory w zmiennych CSS.
- Podział pracy: na razie bez osobnych sesji. Plan jest rozpisany tak, żeby maksymalnie zrównoleglić pracę.

## Otwarte (do doszczegółowienia z zespołem)

- ~~Brak `data_weryfikacji`~~: data wgrania + ostrzeżenie (Wojtek, 22.11).
- ~~Licencja zbioru wynikowego~~: stała CC0 1.0 (Wojtek, 22.11). Nadal otwarte: ODbL dla danych z OSM w agregacie (pytanie do MC).
- Rejestracja URL do importu XML i limity odświeżania (pytania do MC).
- ~~Kto robi którą ścieżkę~~: osobna sesja Claude na ścieżkę, T0 najpierw przez jedną sesję, branch na ścieżkę (Wojtek, 22.11). Nadal otwarte: które osoby nadzorują które sesje.
- Identyfikacja wizualna i nazwa akcji (25% oceny), poza aplikacją.

## Jak pracować przy doszczegóławianiu

- Nowe decyzje ludzi zapisuj w `NOTATKI-ZESPOLU.md` z podpisem autora. Zmiany planu technicznego wprowadzaj w `app/PLAN.md`, a ten plik aktualizuj tylko wtedy, gdy zmienia się „dlaczego” albo kierunek.
- Zanim zaczniesz kodować którąś ścieżkę, wpisz `ZAJMUJĘ` na tablicy (`~/Desktop/hacknation-wspolne/TABLICA.md`).
- Nie proponuj ponownie rzeczy już odrzuconych: AED w pojazdach, zgłoszenia od obywateli, aplikacja zamiast bazy, 5★.
