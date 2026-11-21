# Notatki zespołu: 06 Misja AED

Wnioski i pomysły ludzi z zespołu, każdy podpisany autorem. Nowe notatki dopisuj na końcu jako `- **Autor:** treść`.

- **Grzan:** Zadanie potencjalnie na plus, bo duża część zadania to otoczka nieprogramistyczna (logo, księga znaku, pitch).
- **Grzan:** Zadanie ma najlepszy zakres, bo po zebraniu odpowiednich danych zostaje już tylko ich prezentacja i marketing samego rozwiązania.
- **Grzan:** Wymagana responsywność, czyli poprawne działanie zarówno na telefonach, jak i na komputerach.
- **Wojtek / Grzan:** Wojtek proponował, żeby użytkownicy mogli zgłaszać lokalizacje defibrylatorów. Ten pomysł już ktoś realizował. W Pierwszym Ratowniku (ZOSP RP) bazę tworzą sami użytkownicy razem z ZOSP RP: zalogowana osoba może dodać AED, zaktualizować go albo zgłosić, że zniknął (dodawanie nowych jest obecnie wyłączone, wg FAQ). Podobnie działają OSM, Yanosik, aplikacja Ratownik i formularz „Zgłoś urządzenie AED” w Warszawie 19115. Szczegóły: [ZRODLA-DANYCH.md](ZRODLA-DANYCH.md).
- **Grzan:** Zadanie kładzie ogromny nacisk na potencjał promocyjny. Kryteria oceny („przykładowe”):
  - Zgodność z zasadami działania portalu dane.gov.pl: 30%
  - Kreatywność i innowacyjność rozwiązania: 15%
  - Zgodność z tematem wyzwania: 15%
  - Wzorcowy zakres danych o defibrylatorach: 10%
  - Prezentacja wypracowanego i kompletnego rozwiązania: 5%
  - Logotyp i hasło (proste i zrozumiałe, zgodne z tematyką wyzwania, nowoczesne, kreatywne, z potencjałem promocyjnym): 25%
- **Grzan:** Zakres danych (wstępnie, lista będzie rozszerzana). Docelowe rozwiązanie na pewno przechowuje:
  - lokalizację defibrylatora,
  - słowną nazwę ulicy,
  - opcjonalnie zdjęcie defibrylatora.
- **Grzan:** Pomysł: AED w pojazdach komunikacji miejskiej. Gdy ktoś potrzebuje AED przy przystanku, kierowca pojazdu z AED mógłby dostać o tym informację.
  - Fakty (ZTM Gdańsk, dane na dane.gov.pl, zbiór 1803): „Baza pojazdów” ma pole `aed`, które ma 278 z 503 pojazdów. Feed „Pozycja GPS pojazdów” podaje na żywo `vehicleCode` i lat/lon. Oba łączą się po `vehicleCode`. Test 21.11.2026 ok. 16:50: 222 pojazdy w trasie, w tym 165 z AED. Inne miasta z AED w pojazdach (wg ZRODLA-DANYCH.md): Kraków ok. 25 pojazdów, Warszawa (autobusy, metro, SKM), Katowice. Dla nich nie znaleziono otwartych danych.
- **Grzan (decyzja):** Kierunek projektu:
  - na pewno agregujemy dane o AED;
  - na pewno chcemy, żeby gminy, urzędy miast i inne instytucje **chciały** publikować na dane.gov.pl dane o defibrylatorach, za które odpowiadają;
  - **AED w pojazdach (defibrylatory w ruchu) całkowicie pomijamy**, bo nie mieszczą się w zakresie projektu. Wcześniejszy pomysł z powiadamianiem kierowcy jest odrzucony.
- **Grzan (na podstawie analizy Claude, 21.11 ok. 19:30):** Co budujemy: nie samą bazę, tylko bazę z cienką warstwą wokół. 4 elementy:
  1. **Wzorcowy schemat** (xlsx + definicja w formacie do maszynowej walidacji, jak francuski Table Schema). Pola: od mentora, z Francji i ze standardu dane.gov.pl (adres w osobnych polach, TERYT, ISO 8601). Podział na pola publiczne i niepubliczne. To fundament.
  2. **Agregator:** istniejące źródła (5 zbiorów z dane.gov.pl, Warszawa, ewentualnie OSM, jeśli pozwoli licencja ODbL) → mapowanie na schemat → deduplikacja (numer seryjny i bliskość współrzędnych) → flagi jakości → jeden zbiór w formatach portalu.
  3. **Ścieżka dla dostawcy:** wgranie pliku lub formularz → walidacja → gotowy plik i metadane do dane.gov.pl (albo automatyczny import).
  4. **Raport jakości dla dostawcy:** czego brakuje, żeby można było „odbić się do administratorów”.
  - Jak zachęcić: „potwierdź, zamiast wpisywać” (gmina potwierdza AED, które już są na jej terenie wg TERYT); duzi dostawcy hurtowo (producenci, serwisanci); widoczna korzyść (AED trafia do map i aplikacji); uznanie (mapa pokrycia gmin, znak lub naklejka akcji, co łączy się z logo); kanały: pełnomocnicy ds. otwartości danych, OSP i straż, związki samorządów.
  - Kolejność: najpierw schemat. Kampania może iść równolegle.
- **Grzan (pomysł do dyskusji):** Aplikacja PWA (web i mobile) dla dostawcy, prowadząca w 3 krokach: 1) dane o dostawcy, 2) wgranie danych w naszym formacie i uzupełnienie braków, 3) pobranie danych przekształconych przez nasz backend wraz z instrukcją publikacji na dane.gov.pl. Otwarte pytanie: czy z poziomu naszej aplikacji da się publikować na dane.gov.pl w imieniu dostawcy („podpisane” przez niego)? Odpowiedź z researchu jest w RESEARCH.md („Publikacja z zewnętrznej aplikacji”).
- **Grzan (architektura, wersja robocza):** Dostawca → nasza strona → formularz → wgranie danych o defibrylatorach → walidacja: **wygenerowany URL z danymi** albo **błąd o brakujących kluczowych polach** → dostawca wchodzi na dane.gov.pl i dodaje wygenerowany URL jako zasób w swoim zbiorze.
