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
- **Grzan (cel i zakres prototypu, doprecyzowanie architektury):**
  - Cel na teraz: **strona, na którą dostawca wgrywa dane o AED.** Z tych danych powstaje URL, który osoba z kontem dostawcy na dane.gov.pl może dodać na portalu.
  - Przepływ:
    1. Użytkownik wgrywa dane w swoim formacie.
    2. Backend przekształca je do **naszego ustandaryzowanego formatu** (wzorcowy schemat).
    3. Po udanej konwersji dane trafiają pod **unikalny URL**. Jeśli konwersja się nie uda, użytkownik dostaje błąd z listą braków.
    4. Użytkownik na dane.gov.pl dodaje nowe źródło danych (zasób) z tym URL.
  - Sytuacja idealna (poza minimum):
    - logowanie na naszej stronie, żeby modyfikować wgrane dane (URL bez zmian, aktualizuje się treść);
    - przyjmowanie danych w kilku formatach: co najmniej .csv i .xlsx, a do tego inne, w których urzędy i instytucje trzymają takie dane.
- **Grzan (sytuacja idealna: synchronizacja ze źródłem zewnętrznym):** Platforma pozwala podpiąć zewnętrzne źródło, np. plik CSV na stronie urzędu, nawet źle sformatowany. Nasza strona cyklicznie pobiera go, automatycznie przekształca do naszego formatu i wystawia poprawione dane pod naszym URL.
  - Fakt z researchu na przykładzie: Przemyśl udostępnia dane na żywo (przemysl.skycms.com.pl/open-data/…, CSV z `;` i geometrią jako JSON w komórce). Między 2024-11 a 21.11.2026 zmienił się w nim format geometrii z obiektu `{lat,long}` na tablicę `[lon,lat]`. Taki przypadek synchronizacja musi wykryć.
- **Grzan (doszczegółowienie, 22.11 ok. 01:10):**
  - Podział pracy: różne agenty odpowiadają za różne części, żeby każdy miał jak najmniejszy i najtańszy kontekst. Maksymalne zrównoleglenie.
  - Front: Vite + React + TypeScript, własny CSS (bez biblioteki komponentów).
  - Hosting u znajomego: szczegóły jeszcze nieznane. Docker-compose ma mieć konfigurowalny bazowy URL (zmienna środowiskowa).
- **Wojtek (podział pracy, 22.11):** Każda ścieżka z app/PLAN.md (A rdzeń, B API, C front, D testy) ma osobną sesję Claude we własnym klonie, a ludzie nadzorują sesje.
- **Wojtek (front, 22.11):** Vite + React + TypeScript z własnym CSS, bez biblioteki komponentów. Kolory jako tokeny w zmiennych CSS, do podmiany na kolory kampanii.
- **Wojtek (hosting, 22.11):** Serwera na razie nie ma, demo pokazujemy lokalnie (docker compose). Bazowy URL do linków /d/{slug}.csv ustawiamy zmienną środowiskową.
- **Wojtek (T0 i merge, 22.11):** Jedna sesja robi T0 (szkielet app/ i kontrakt API), a pozostałe czekają, aż T0 trafi do main. Potem każda ścieżka pracuje na własnym branchu (app-a-rdzen, app-b-api, app-c-front, app-d-testy) i często merguje do main małymi PR-ami.
- **Wojtek (data_weryfikacji, 22.11):** Gdy plik nie ma `data_weryfikacji`, wpisujemy datę wgrania i dodajemy ostrzeżenie z prośbą o realną datę przeglądu.
- **Wojtek (id_aed, 22.11):** Gdy plik nie ma `id_aed`, generujemy `<kod_terc>-<numer>` (albo `<slug>-<numer>`, gdy brak TERC) i dodajemy ostrzeżenie, że przy ponownym wgraniu identyfikatory mogą się zmienić.
- **Wojtek (status, 22.11):** Gdy plik nie ma `status`, wpisujemy `nieznany` i dodajemy ostrzeżenie.
- **Wojtek (duplikaty w pliku, 22.11):** Powtórzone `id_aed` albo numer seryjny w jednym pliku to błąd, który blokuje publikację. Bardzo bliskie współrzędne dają tylko ostrzeżenie, bo w jednym budynku może być kilka AED.
- **Wojtek (licencja, 22.11):** Zbiór wynikowy ma stałą licencję CC0 1.0. Dostawca jej nie wybiera.
- **Wojtek (ponowne wgranie w MVP, 22.11):** Po publikacji dostawca dostaje drugi, prywatny link edycji z tokenem. Przez ten link wgrywa nowy plik pod ten sam slug, więc publiczny URL się nie zmienia, a portal z „Aktualizacją automatyczną” pobiera nową treść. Logowanie (S3) zostaje poza MVP.
- **Grzan (zasady danych, 22.11 ok. 01:25):** data_weryfikacji: data wgrania + ostrzeżenie; brak id_aed: generujemy; brak statusu: `nieznany` + ostrzeżenie; duplikaty: błąd tylko przy tym samym id_aed albo numerze seryjnym, przy bliskich punktach ostrzeżenie; limity pliku: 10 MB i 20 000 wierszy (geokodowanie max ok. 200 adresów na plik). Do tego miejsca zgodnie z Wojtkiem.
- **Grzan (licencja, 22.11):** Dostawca wybiera w kroku 1 CC0 1.0 albo CC BY 4.0, domyślnie CC0. Agregat ma CC BY 4.0 z kolumnami źródła i licencji przy każdym rekordzie. (Fakty: portal nie wymaga CC0, licencję ustawia dostawca w metadanych zbioru na dane.gov.pl. Wśród 500 najnowszych zbiorów 421 ma CC0, a 79 CC BY 4.0.)
- **Grzan (ponowne wgranie w MVP, 22.11):** Nowy URL przy każdym wgraniu.
- ⚠️ **SPÓR do rozstrzygnięcia (Grzan i Wojtek):**
  1. **Licencja:** Wojtek ustalił stałą CC0, Grzan wybór CC0/CC BY 4.0 z domyślną CC0.
  2. **Ponowne wgranie:** Wojtek ustalił prywatny link edycji z tokenem (ten sam URL), Grzan nowy URL przy każdym wgraniu.
  Dopóki tego nie rozstrzygniecie, app/PLAN.md zawiera wersję Wojtka.
- **Wojtek (agregat, 22.11):** Zbiorczy URL `/d/aed-polska.csv` zawiera cały agregat z `dane/wynik`, także dane z OSM. Licencja na razie nas nie interesuje. Wiemy, co wynika z ODbL, ale w prototypie używamy tych danych do prezentacji: duży zbiór pokazuje, że umiemy go zagregować i przetworzyć do wzorcowego formatu.
- **Wojtek (geokodowanie, 22.11):** W prototypie Nominatim z cache w bazie, własnym User-Agentem i limitem 1 zapytanie/s. Gdy w pliku jest ponad ok. 200 adresów bez współrzędnych, pokazujemy ostrzeżenie z prośbą o dodanie współrzędnych. Docelowo (slajd) geokoder GUGiK.
- **Wojtek (limity, 22.11):** Plik do 10 MB i 10 000 wierszy. Większy plik dostaje komunikat z prośbą o kontakt.
- **Wojtek (fixtury, 22.11):** Bez ręcznych poprawek mapowania muszą przejść Krosno, Legionowo, Przemyśl i Warszawa 19115.
- **Wojtek (testowy XLSX, 22.11):** Nie mamy realnego „urzędowego” XLSX. Sesja D przygotuje syntetyczne pliki (D1).
- **Wojtek (zrzuty dane.gov.pl, 22.11):** Nikt z nas nie ma konta dostawcy ani kontaktu w MC, więc prosimy organizatora (PYTANIA-DO-ORGANIZATORA.md). Do czasu odpowiedzi instrukcja w kroku 3 opisuje kroki na podstawie kodu portalu i Przewodnika dla dostawców v1.23.
- **Wojtek (otwarte, decyduje Grzan):** Kto robi slajdy i na kiedy potrzebuje działającej wersji. Kto robi kampanię (nazwa, hasło, logo, księga znaku) i kiedy front dostanie kolory.
- **Grzan (agregat, 22.11 ok. 01:40):** Dane na start (jeszcze niezatwierdzone): dwa pliki zbiorcze, główny bez OSM (zbiory od dostawców i źródła miejskie na CC0 lub CC BY) i osobny „podgląd z OSM (ODbL)”. **Każdy rekord musi mieć wyraźnie oznaczone pochodzenie** (kto podał dane, z jakiego źródła i kiedy), żeby dało się odsiać dane niewiarygodne i nieaktualne.
- **Grzan (geokoder, 22.11):** Geokoder GUGiK (państwowy). Fakt sprawdzony 22.11: usługa UUG `https://services.gugik.gov.pl/uug/?request=GetAddress&address=…&srid=4326` działa bez klucza i zwraca współrzędne, kod TERYT gminy (6 cyfr), SIMC, ULIC, kod pocztowy i `accuracy`. Przy wielu trafieniach (np. dwa „Krosno, Jasna”) trzeba zawęzić wynik kodem pocztowym albo gminą.
- **Grzan (testy, 22.11):** Najpierw 5 miast z dane.gov.pl (Krosno, Marki, Legionowo, Przemyśl, Warszawa 19115). Jeśli starczy czasu: pliki z dane/surowe i syntetyczne „urzędowe” XLSX. **Potrzebny jest jeden bardzo wyraźny przykład, że narzędzie działa.**
- ⚠️ **SPÓR, cd. (tematy 11–13 też przeszły obie sesje):**
  3. **Agregat:** Wojtek: jeden plik `/d/aed-polska.csv` z całym `dane/wynik` łącznie z OSM (licencję świadomie pomijamy w prototypie). Grzan: dwa pliki, główny bez OSM i osobny „podgląd z OSM (ODbL)”, a przy każdym rekordzie wyraźne pochodzenie. (Wspólne: pochodzenie rekordu i tak jest w kolumnach `zrodlo_danych` / `licencja_zrodla` w dane/.)
  4. **Geokoder:** Wojtek: Nominatim w prototypie, GUGiK docelowo (slajd). Grzan: GUGiK od razu (działa bez klucza i zwraca TERYT).
  5. **Limit wierszy:** Wojtek 10 000, Grzan 20 000 (obaj 10 MB).
  Zgodne: fixtury startowe (Grzan dodaje do nich Marki), syntetyczne XLSX przygotowuje sesja D.
- ✅ **Grzan (rozstrzygnięcie sporów 1–5, 22.11 ok. 02:00):** 1) licencja: **stała CC0** (wersja Wojtka); 2) ponowne wgranie: **prywatny link z tokenem, ten sam URL** (wersja Wojtka); 3) agregat: **połączenie**: `/d/aed-polska.csv` z OSM i `/d/aed-polska-bez-osm.csv` bez OSM, a przy każdym rekordzie kolumny pochodzenia (dysponent, źródło, licencja źródła, data aktualizacji); 4) geokoder: **GUGiK UUG**, Nominatim jako zapas; 5) limit: **10 MB i 20 000 wierszy**. Zmiany wprowadzone w app/PLAN.md.
- **Grzan (organizacja, 22.11 ok. 02:10):** Ścieżki A, B, C, D to osobne sesje Claude w osobnych oknach tmux, działające równolegle. Komunikują się jak dotychczas (tablica + SendMessage). Logo i paleta do frontu są w repo (`hacknation paleta.svg`, od Kuby). Slajdy powstaną rano. Na odpowiedź MC nie czekamy.
- **Grzan (doprecyzowanie backendu, 22.11):**
  1. Brak kolumny dla pól O `wewnatrz_budynku`, `dostepnosc`, `dostepny_24_7`: kreator pokazuje „ustaw dla wszystkich AED w pliku”; do wyboru wartości jest błąd. Kontrakt: w body `/walidacja` nowe pole `wartosci_stale: {pole: wartość}`.
  2. Współrzędne z mniej niż 6 miejscami po przecinku: zapisujemy bez zmian (bez dopisywania zer), poniżej 5 miejsc ostrzeżenie `NISKA_PRECYZJA`.
  3. Nowe pola specjalne mapowania `_adres` i `_godziny` (jak `_geometria`); rdzeń rozbija je na części.
  4. Adres nieznaleziony przez geokoder: ostrzeżenie, rekord pominięty w publikacji (nie blokuje pliku). W `WalidacjaOut` nowe pole `liczba_pominietych`.
  5. Wygenerowany `id_aed` z treści rekordu (skrót z numeru seryjnego albo współrzędnych ~10 m + nazwy), stabilny przy ponownym wgraniu.
  6. Agregat: rekord dostawcy jest główny; rekordy z `dane/wynik` bliżej niż ~30 m dostają `duplikat_id_aed` = id rekordu dostawcy (nic nie znika).
  7. Geokodowanie synchronicznie w `/walidacja`, równolegle ok. 8 zapytań z cache; kontrakt bez zmian.
  8. Z zakresu v0.5: brak ulicy → `nazwa_ulicy` = miejscowość + info.
  Paleta TuAED: #008c15 ma kontrast 4,41:1 na białym (poniżej AA 4,5:1) → na tekst i przyciski ciemniejszy odcień; #5bc500 i #78d64b tylko dekoracyjnie.
