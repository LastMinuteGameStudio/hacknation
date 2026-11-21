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
