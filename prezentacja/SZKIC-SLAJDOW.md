# Szkic struktury slajdów: 06 Misja AED

Wersja robocza z 21.11.2026. Wymagania organizatora (pkt 4 treści zadania): co najmniej 5 slajdów, na nich zrzuty ekranu jako dowody spełnienia wymagań technicznych, opis funkcjonalności z krokami użytkownika i lista ograniczeń. Regulamin (§2 ust. 8) wymaga też wskazania, jak używaliśmy AI.

Organizator nie podał limitu slajdów ani czasu pitchu, więc celujemy w 12–14 slajdów. W razie limitu można wyciąć slajdy oznaczone jako opcjonalne.

Legenda statusu: ✅ materiał jest w repo · 🟡 jest częściowo · ❌ trzeba przygotować.

| # | Slajd | Kryterium (waga) | Treść | Dowód lub zrzut | Status |
|---|---|---|---|---|---|
| 1 | Tytuł | Logo i hasło (25%) | nazwa akcji, hasło, logo, nazwa zespołu | logo | ❌ |
| 2 | Problem | Temat (15%) | przykład z treści zadania (Warszawa, 3 marca). Dane o AED są rozproszone, niepełne i niezweryfikowane, a krajowego rejestru nie ma. 5 zbiorów na dane.gov.pl ma 5 różnych schematów | mapa rozproszenia źródeł albo zestawienie schematów | 🟡 |
| 3 | Rozwiązanie w jednym zdaniu | Temat (15%), Kreatywność (15%) | jeden otwarty zbiór AED na dane.gov.pl, który powstaje z wielu źródeł, ma wspólny wzorzec i jest zasilany przez dysponentów. Budujemy bazę danych, nie aplikację (decyzja po rozmowie z mentorem) | schemat przepływu: źródła → agregacja → deduplikacja → dane.gov.pl → odbiorcy (służby, mapy, obywatele) | 🟡 |
| 4 | Agregacja: wyniki | Temat (15%), dane.gov.pl (30%) | 15 źródeł, 19 834 rekordy, **18 858 unikalnych AED**, w tym 559 spoza OSM. Najwięcej nowych punktów: Warszawa 19115 (355), Kraków (73), Gliwice (44) | zrzut mapy lub tabeli z `dane/wynik/` (branch grzan) | ✅ dane, ❌ zrzut |
| 5 | Deduplikacja i jakość | Kreatywność (15%) | dopasowanie po odległości (50 m, a dla geokodowanych 100 m), docelowo po numerze seryjnym. Pole `duplikat_z` i status walidacji | zrzut przykładu duplikatu z dwóch źródeł | 🟡 |
| 6 | Wzorcowy zakres danych | Zakres danych (10%) | 52 pola (obowiązkowe, zalecane, fakultatywne). Godziny dostępności w ustrukturyzowanym formacie. Odpowiedniki pól w Géo'DAE (FR) | zrzut arkusza xlsx | ✅ |
| 7 | Co jest publiczne, a co zostaje w ewidencji | Zakres danych (10%), dane.gov.pl (30%) | 6 pól niepublicznych (producent, model, nr seryjny, serwisant, telefon, e-mail) i uzasadnienie. Szablony: pełna ewidencja i wersja publiczna (CSV + CSVW) | zrzut obu szablonów | ✅ |
| 8 | Zgodność z dane.gov.pl | dane.gov.pl (**30%**) | formaty maszynowe (CSV RFC 4180, GeoJSON, JSON, bez PDF/DOC), licencja z listy portalu (CC0 albo CC BY 4.0), metadane zbioru z § 6 rozporządzenia, poziom otwartości (gwiazdki), daty w ISO 8601, kodowanie UTF-8 | zrzut karty zbioru lub metadanych, wynik walidacji CSV | ❌ |
| 9 | Prototyp: kroki użytkownika (dysponent) | Prezentacja (5%), wymóg formalny | np. 1) dysponent pobiera szablon, 2) wgrywa plik, 3) widzi walidację i duplikaty, 4) publikuje lub eksportuje na dane.gov.pl | zrzut z każdego kroku | ❌ (zależy od prototypu) |
| 10 | Prototyp: odbiorcy danych | Temat (15%) | jak służby i obywatele korzystają ze zbioru: mapa, API, pobranie pliku | zrzut mapy lub wywołania API | ❌ |
| 11 | WCAG, responsywność, UX | wymagania techniczne | wersja WCAG (do potwierdzenia: 2.1 AA czy 2.2 AA), wynik Lighthouse lub axe, kontrast, obsługa klawiaturą | zrzuty: telefon i komputer obok siebie, raport z audytu | ❌ |
| 12 | Akcja: nazwa, hasło, logo | Logo i hasło (**25%**) | koncepcja w 3–5 zdaniach, do kogo mówimy (dysponenci: gminy, urzędy, instytucje), dlaczego im się opłaca publikować | logo i przykładowe zastosowania (plakat, naklejka na szafkę, post) | ❌ |
| 13 | Księga znaku (skrót) | Logo i hasło (25%) | kolorystyka, pole ochronne, minimalna wielkość, niedozwolone użycia | strony z PDF księgi znaku | ❌ |
| 14 | Ograniczenia | wymóg formalny | 63 rekordy bez współrzędnych, geokodowanie Nominatim (ryzyko złego punktu), dane Warszawy dostępne tylko przez API z tokenem, część źródeł bez otwartej licencji, brak krajowego obowiązku zgłaszania AED, AED w pojazdach poza zakresem | — | 🟡 |
| 15 | Użycie AI i dalsze kroki | wymóg z regulaminu | do czego użyliśmy AI (research, kod, teksty) i co zrobili ludzie. Plan: synchronizacja dat ważności baterii i elektrod, zgłoszenia od dysponentów, rozszerzanie źródeł | — | ❌ |

## Uwagi

- Jeśli jury ogranicza liczbę slajdów: połączyć 4 z 5, 6 z 7 i 12 z 13, a slajd 10 usunąć. Zostaje 11 slajdów.
- Każdy slajd z wymaganiem technicznym powinien mieć zrzut ekranu, bo organizator wprost o to prosi.
- Liczby ze slajdów 4 i 14 pochodzą z agregacji z 21.11 (branch grzan, `dane/README.md`). Przed oddaniem trzeba je odświeżyć.
- Do ustalenia z organizatorem: czas pitchu, format pliku, miejsce oddania, sposób sprawdzania WCAG i rozumienie „zgodności z dane.gov.pl” (zob. `zadania/06-mc-misja-aed/PYTANIA-DO-ORGANIZATORA.md`).
