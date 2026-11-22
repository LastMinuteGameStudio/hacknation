# Instrukcja dla jury: TuAED (06 Misja AED)

Ta instrukcja prowadzi krok po kroku przez prototyp i wskazuje, gdzie sprawdzić każde wymaganie z treści
zadania ([TRESC.md](zadania/06-mc-misja-aed/TRESC.md), punkty 2–5). Każdy krok ma dwie drogi:

- **Demo:** publiczny prototyp https://tuaed.wkrynski.dev (wystarczy przeglądarka, bez logowania).
- **Bez demo:** gdy adres jest zablokowany w Waszej sieci, ten sam stan pokazuje zrzut ekranu albo plik w repo.
  Prototyp można też uruchomić lokalnie (Docker, krok 0).

Zrzuty są w [prezentacja/zrzuty/](prezentacja/zrzuty/README.md), każdy w wersji na komputer (`-1440.png`) i
telefon (`-320.png`). Niżej podajemy wersję 1440.

## 0. Przygotowanie (tylko jeśli demo nie działa)

1. Zainstaluj Dockera i sklonuj repo: `git clone --depth 1 https://github.com/LastMinuteGameStudio/hacknation`.
2. `cd hacknation/app && cp .env.example .env`, a potem w `.env` ustaw `BASE_URL=http://localhost:8000`. Bez tej
   zmiany linki do opublikowanych plików wskazywałyby demo.
3. `docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build -d` (pierwsza budowa trwa kilka minut).
4. Otwórz http://localhost:8000. W dalszych krokach zamiast `https://tuaed.wkrynski.dev` wpisuj
   `http://localhost:8000`. Mapa i agregat lokalnie zawierają tylko zbiory wgrane na tym komputerze.
5. Testy automatyczne (opcjonalnie, **Python 3.12**; na starszym Pythonie nie zainstaluje się sterownik bazy):
   `cd app/backend && python3.12 -m venv .venv && .venv/bin/pip install -r requirements.txt && .venv/bin/python -m pytest -q`
   Wynik: **223 passed**, w tym testy na 10 prawdziwych i syntetycznych plikach dysponentów.

## 1. Prototyp od początku do końca (ok. 5 minut)

Scenariusz: Urząd Miejski w Przemyślu ma 21 AED w eksporcie z CMS. Plik ma średniki, opis marketingowy w każdym
wierszu i współrzędne zapisane jako JSON w komórce. Tak wygląda kopia z dane.gov.pl, której portal nie
odświeża od 2024 r.

**Plik testowy do pobrania:** [przemysl_2024.csv](https://raw.githubusercontent.com/LastMinuteGameStudio/hacknation/main/app/backend/tests/fixtury/przemysl_2024.csv)
(w repo: [app/backend/tests/fixtury/przemysl_2024.csv](app/backend/tests/fixtury/przemysl_2024.csv)).
Inne pliki do wypróbowania: [krosno.csv](https://raw.githubusercontent.com/LastMinuteGameStudio/hacknation/main/app/backend/tests/fixtury/krosno.csv)
(czysty CSV miasta), [syntetyczny_gmina.xlsx](https://raw.githubusercontent.com/LastMinuteGameStudio/hacknation/main/app/backend/tests/fixtury/syntetyczny_gmina.xlsx)
(„urzędowy” arkusz z tytułem, scalonymi komórkami i przecinkiem dziesiętnym).

| # | Co zrobić | Co powinno być widać | Bez demo |
|---|---|---|---|
| 1.1 | Otwórz https://tuaed.wkrynski.dev | Strona startowa „Opublikuj dane o defibrylatorach na dane.gov.pl, w 3 prostych krokach”: szablony CSV i XLSX do pobrania, przycisk „Zacznij”. U góry nawigacja: „Opublikuj dane”, „Mapa AED”, „Zebrane dane” | [09-start](prezentacja/zrzuty/09-start-1440.png) |
| 1.2 | „Zacznij”. Wpisz nazwę, np. `Urząd Miejski w Przemyślu (jury)`, typ „Jednostka samorządu terytorialnego”, „Dalej: dane” | Formularz dysponenta. Telefon i e-mail są opcjonalne i oznaczone „nie publikujemy” | [09-krok1-dysponent](prezentacja/zrzuty/09-krok1-dysponent-1440.png) |
| 1.3 | Wybierz pobrany `przemysl_2024.csv`, „Wgraj plik” | Tabela „Dopasuj kolumny”: dla 17 kolumn podpowiedź pola z pewnością. `geometry` → współrzędne, a 8 kolumn CMS (opis, galeria, linki…) → „nie importuj” | [09-krok2-mapowanie](prezentacja/zrzuty/09-krok2-mapowanie-1440.png), [cała tabela](prezentacja/zrzuty/09-krok2-mapowanie-tabela-1440.png) |
| 1.4 | W „Ustaw dla wszystkich AED w pliku” wybierz: wewnątrz budynku „Nie”, dostęp „Dostępny dla każdego”, całą dobę „Tak” | Pola obowiązkowe, których nie ma w pliku, ustawia się raz dla całego pliku | [09-krok2-wartosci-stale](prezentacja/zrzuty/09-krok2-wartosci-stale-1440.png) |
| 1.5 | „Sprawdź dane” | „Do publikacji: 21, Błędy: 0”, ostrzeżenia zbiorcze z opisem po polsku (np. „Cecha ulicy w 18 wierszach”). Rozwiń „Podgląd wyniku” | [09-krok2-walidacja](prezentacja/zrzuty/09-krok2-walidacja-1440.png), [podgląd](prezentacja/zrzuty/09-krok2-podglad-wyniku-1440.png) |
| 1.6 | „Dalej: publikacja”, zaznacz zgodę na CC0 1.0, „Opublikuj” | Stały adres `…/d/<slug>.csv`, prywatny link do aktualizacji, instrukcja dodania zasobu na dane.gov.pl („link”, „Aktualizacja automatyczna: dziennie”, pole **„Wykaz AED”**, licencja CC0 1.0), „Metadane zbioru do skopiowania” (tytuł, opis, słowa kluczowe, kategoria Zdrowie) i linki JSON i CSVW | [09-krok3-zgoda](prezentacja/zrzuty/09-krok3-zgoda-1440.png), [09-krok3-publikacja](prezentacja/zrzuty/09-krok3-publikacja-1440.png) |
| 1.7 | Kliknij „Dane w CSV” (przeglądarka otworzy albo pobierze plik) | Plik CSV: przecinki, UTF-8, kolumny wzorcowego zakresu v0.5 w stałej kolejności, telefon i e-mail usunięte | [08-csv-w-przegladarce](prezentacja/zrzuty/08-csv-w-przegladarce-1440.png) |
| 1.8 | Otwórz prywatny link do aktualizacji (skopiuj go z kroku 1.6) | Strona „Wgraj nową wersję danych” i sekcja „Źródło automatyczne” | [09-edycja-zrodlo-automatyczne](prezentacja/zrzuty/09-edycja-zrodlo-automatyczne-1440.png) |
| 1.9 | Wgraj [przemysl.csv](https://raw.githubusercontent.com/LastMinuteGameStudio/hacknation/main/app/backend/tests/fixtury/przemysl.csv) (eksport z 2026 r., inny format geometrii). Ustaw ponownie trzy wartości z kroku 1.4, bo strona ich nie pamięta. Potem „Sprawdź dane”, zgoda i „Opublikuj” | Mapowanie kolumn podpowiada się samo, a publikacja podmienia dane **pod tym samym adresem** z **tymi samymi `id_aed`** | [przed](prezentacja/zrzuty/09-sync-0-csv-przed-1440.png) i [po](prezentacja/zrzuty/09-sync-4-csv-po-1440.png) (te same `id_aed`) |
| 1.10 | (opcjonalnie) W „Źródło automatyczne” wklej adres pliku na stronie urzędu i „Włącz i pobierz teraz” | Stan „Aktywna”, ZSYNCHRONIZOWANO. Zmiana kolumn w źródle wstrzymuje synchronizację i nie psuje danych | [ustawienie](prezentacja/zrzuty/09-sync-1-ustawienie-1440.png), [aktywna](prezentacja/zrzuty/09-sync-2-aktywna-1440.png), [nowy format](prezentacja/zrzuty/09-sync-3-zsynchronizowano-1440.png), [wstrzymana](prezentacja/zrzuty/09-sync-5-wstrzymana-1440.png) |
| 1.11 | Otwórz https://tuaed.wkrynski.dev/mapa | Mapa AED z całej Polski z popupem szczegółów. Wybór: wszystkie AED albo bez OpenStreetMap | [10-mapa](prezentacja/zrzuty/10-mapa-1440.png), [telefon](prezentacja/zrzuty/10-mapa-320.png), [popup](prezentacja/audyt/zrzuty/mapa-popup-1440.png) |
| 1.12 | Otwórz https://tuaed.wkrynski.dev/dane | „Zebrane dane o AED”: „Zbiory dostawców” (każdy z plikami CSV, JSON, GeoJSON i CSVW), liczba AED według pochodzenia, tabela „Wszystkie AED” z wyszukiwaniem i pliki zbiorcze | [10-dane](prezentacja/zrzuty/10-dane-1440.png), [telefon](prezentacja/zrzuty/10-dane-320.png) |

Zbiór na prezentację z włączoną synchronizacją: https://tuaed.wkrynski.dev/d/kznsks42.csv. Zbiory, które
opublikujecie, będą widoczne w agregacie, dlatego prosimy o dopisek „(jury)” w nazwie dysponenta.

## 2. Wymagania z treści zadania: gdzie je sprawdzić

### 2.1 Dane z wielu rozproszonych źródeł w jednym zbiorze (pkt 2 i 3)

1. Otwórz [dane/README.md](dane/README.md), sekcja „Wyniki”: 15 źródeł (OSM, Warszawa 19115, Kraków, Łódź,
   Gliwice, InPost, WOPR…), **18 858 unikalnych AED** po deduplikacji (do 50 m od OSM, do 30 m między innymi źródłami).
2. Demo: pobierz https://tuaed.wkrynski.dev/d/aed-polska.csv (ok. 19 870 wierszy). Ostatnie kolumny to
   pochodzenie rekordu: `zrodlo`, `licencja_zrodla`, `duplikat_id_aed`, `status_walidacji`. Wersja bez danych
   OSM (licencja ODbL): `/d/aed-polska-bez-osm.csv`, mapa: `/d/aed-polska.geojson`.
   Bez demo: [dane/wynik/aed_unikalne.csv](dane/wynik/aed_unikalne.csv), [statystyki.json](dane/wynik/statystyki.json).
3. Zbiory wgrane przez dysponentów w kreatorze trafiają do tego samego agregatu (krok 1.12, lista zbiorów).
4. Scalanie wykazów od wielu dostawców **w kodzie portalu dane.gov.pl**: sekcja 3.

### 2.2 Wzorcowy zakres danych, plik xlsx (pkt 2 i 4)

1. Otwórz [zakres-danych/wzorcowy-zakres-danych-AED.xlsx](zakres-danych/wzorcowy-zakres-danych-AED.xlsx).
   Zakres v0.5 ma 58 pól (obowiązkowe, zalecane, fakultatywne), słowniki, formaty i przykłady. 52 pola są
   publiczne, a 6 zostaje w ewidencji dysponenta.
2. Szablony do wypełnienia: [szablon-aed.csv](zakres-danych/szablon-aed.csv) (pełna ewidencja) i
   [szablon-aed-publiczny.csv](zakres-danych/szablon-aed-publiczny.csv) z metadanymi CSVW
   ([.csv-metadata.json](zakres-danych/szablon-aed-publiczny.csv-metadata.json)). Demo: `/szablon.csv`, `/szablon.xlsx`.
3. Wersja maszynowa zakresu: [zakres-pol.csv](zakres-danych/zakres-pol.csv), [slowniki.csv](zakres-danych/slowniki.csv),
   a w API https://tuaed.wkrynski.dev/api/schemat.

### 2.3 Format odczytywalny maszynowo (pkt 5)

1. Każdy opublikowany zbiór ma CSV (RFC 4180, UTF-8), JSON, GeoJSON i metadane CSVW. Demo: `/d/kznsks42.csv`,
   `.json`, `.geojson`, `.csv-metadata.json`. Nie publikujemy PDF ani DOC.
2. Dowód z walidacją: [prezentacja/zrzuty/DOWOD-URL.md](prezentacja/zrzuty/DOWOD-URL.md) (21/21: kodowanie,
   CRLF, cytowanie, stała liczba pól, typy i wymagane pola wg CSVW). Sprawdzenie można powtórzyć:
   `python3 prezentacja/zrzuty/sprawdz_url.py https://tuaed.wkrynski.dev/d/kznsks42.csv`.
3. Testy: `app/backend/tests/test_realne_e2e.py` sprawdza CSV z 6 prawdziwych plików pod kątem RFC 4180 i
   formatów zakresu v0.5.

### 2.4 Zgodność z zasadami działania portalu dane.gov.pl (pkt 5, 30% oceny)

1. **Publikuje dostawca, nie my:** dysponent dodaje stały URL jako zasób z „Aktualizacją automatyczną”
   (krok 1.6, instrukcja na ekranie). Zasady portalu: [RESEARCH.md](zadania/06-mc-misja-aed/RESEARCH.md).
2. **Plik pobierany jak przez harvester portalu** (bez ciasteczek i logowania, `text/csv; charset=utf-8`,
   CORS): nagłówki HTTP w [DOWOD-URL.md](prezentacja/zrzuty/DOWOD-URL.md).
3. **Licencja z listy portalu:** CC0 1.0, wybierana świadomie w kroku 1.6 i zapisana w metadanych CSVW.
4. **Aktualność:** ten sam URL po aktualizacji (krok 1.9) i synchronizacja ze źródła (krok 1.10). To odpowiedź
   na problem Przemyśla, gdzie portal trzyma kopię z 2024 r.
5. **Wykaz AED w kodzie portalu:** sekcja 3.

### 2.5 WCAG, responsywność i UX (pkt 5)

1. Otwórz [prezentacja/AUDYT-WCAG.md](prezentacja/AUDYT-WCAG.md): **WCAG 2.2 AA**, axe-core 0 naruszeń na 33
   ekranach (320, 768 i 1440 px), Lighthouse Accessibility 100. Opisane są też klawiatura i kontrast.
   Raporty: [prezentacja/audyt/](prezentacja/audyt/).
2. Demo: zmniejsz okno do 320 px (albo otwórz na telefonie) i przejdź krok 1. Nie ma poziomego przewijania.
   Bez demo: każdy zrzut w [prezentacja/zrzuty/](prezentacja/zrzuty/README.md) ma wersję `-320.png`.
3. UX: komunikaty walidacji są po polsku i zbiorcze („w 18 wierszach”) zamiast jednego błędu na wiersz.
   Pola obowiązkowe ustawia się raz dla pliku. Podpowiedzi mapowania pokazują pewność i przykłady z pliku.
   Opis kroków użytkownika: [prezentacja/USER-STORY.md](prezentacja/USER-STORY.md).

### 2.6 Użytkownicy: służby ratunkowe i każdy z nas (pkt 2)

1. Obywatel: mapa `/mapa` (krok 1.11).
2. Służby i integratorzy: API z dokumentacją https://tuaed.wkrynski.dev/docs
   ([zrzut](prezentacja/zrzuty/10-docs-api-1440.png)), agregat CSV i GeoJSON (2.1).

### 2.7 Akcja: nazwa, hasło, logotyp, księga znaku (pkt 2 i 4, 25% oceny)

1. Nazwa akcji: **TuAED**. Logo jest w nagłówku prototypu ([kod SVG](app/frontend/src/components/Logo.tsx)).
2. Logotyp i księga znaku są na branchu `kvba`, w katalogu [visual/](https://github.com/LastMinuteGameStudio/hacknation/tree/kvba/visual). Na `main` trafią po decyzji zespołu.
   - JPG: [Logo.jpg](https://github.com/LastMinuteGameStudio/hacknation/blob/kvba/visual/Logo.jpg)
   - PNG: [Logo.png](https://github.com/LastMinuteGameStudio/hacknation/blob/kvba/visual/Logo.png), wersje z tłem i bez tła, poziome i pionowe (`logo_*.png`)
   - PDF: [Logo.pdf](https://github.com/LastMinuteGameStudio/hacknation/blob/kvba/visual/Logo.pdf)
   - format otwarty SVG: [Logo.svg](https://github.com/LastMinuteGameStudio/hacknation/blob/kvba/visual/Logo.svg), wersje monochromatyczne, negatywowe i pionowe (`logo_*.svg`)
   - księga znaku PDF: [podstawowa_ksiega_znaku.pdf](https://github.com/LastMinuteGameStudio/hacknation/blob/kvba/visual/podstawowa_ksiega_znaku.pdf)
   - kolory (#008C15, #1A4E8A) i czcionka (Noto Sans): [GRAPHICS.md](https://github.com/LastMinuteGameStudio/hacknation/blob/kvba/visual/GRAPHICS.md)

### 2.8 Wymagania formalne (pkt 4)

| Wymaganie | Gdzie |
|---|---|
| Tytuł i szczegółowy opis | [README.md](README.md) |
| Prezentacja (min. 5 slajdów, zrzuty, kroki użytkownika, ograniczenia) | [prezentacja/TuAED-Misja-AED.pptx](prezentacja/TuAED-Misja-AED.pptx), zrzuty: [prezentacja/zrzuty/](prezentacja/zrzuty/README.md) |
| Prototyp | https://tuaed.wkrynski.dev, sekcja 1 tej instrukcji |
| Wzorcowy zakres danych (xlsx) | [zakres-danych/wzorcowy-zakres-danych-AED.xlsx](zakres-danych/wzorcowy-zakres-danych-AED.xlsx) |
| Kod źródłowy | to repozytorium: [app/](app/) (TuAED), [dane/skrypty/](dane/skrypty/) (agregacja), portal: sekcja 3 |
| Logotyp i księga znaku | 2.7 (branch `kvba`, [visual/](https://github.com/LastMinuteGameStudio/hacknation/tree/kvba/visual)) |

## 3. Zmiany w portalu dane.gov.pl (wykaz AED)

Kod portalu (mcod-backend 2.62.3) z naszymi zmianami jest na branchu `portal-aed`, w katalogu `portal/`. Pierwszy
commit to czysty kod portalu, kolejne to zmiany. Opis zmian: [portal/WYKAZ-AED.md](https://github.com/LastMinuteGameStudio/hacknation/blob/portal-aed/portal/WYKAZ-AED.md).
Uruchomienie: [portal/URUCHOMIENIE-TUAED.md](https://github.com/LastMinuteGameStudio/hacknation/blob/portal-aed/portal/URUCHOMIENIE-TUAED.md).

Na wzór istniejącego w portalu wykazu DGA dostawca zaznacza na zasobie **„Wykaz AED: Tak”** (`Resource.is_aed_list`).
Portal waliduje taki zasób według zakresu v0.5. Codziennie o 3:45 zadanie `create_main_aed_resource_task` scala
poprawne wykazy wszystkich dostawców w zbiór **„Defibrylatory AED: wykaz zbiorczy”** (CSV i XLSX). AED zgłoszony
przez dwóch dostawców (ten sam numer seryjny albo do 30 m) nie jest usuwany, tylko dostaje `duplikat_id_aed`.

Dane testowe: trzech dostawców, każdy z zasobem-linkiem z „Aktualizacją automatyczną”.

| Dostawca | Wykaz | Licencja |
|---|---|---|
| Urząd Miejski w Przemyślu (test TuAED) | https://tuaed.wkrynski.dev/d/kznsks42.csv (21 AED) | CC0 1.0 |
| Urząd Miasta Krosna (test TuAED) | https://tuaed.wkrynski.dev/d/qy7g6px5.csv (21 AED) | CC0 1.0 |
| Szpital Wojewódzki w Przemyślu (test TuAED) | [szpital_przemysl_v05.csv](app/backend/tests/fixtury/wykaz/szpital_przemysl_v05.csv) (3 AED: jeden 15 m od AED Przemyśla, jeden 45 m od innego) | CC BY 4.0 |

1. Uruchom portal lokalnie według URUCHOMIENIE-TUAED.md i wczytaj dane testowe. Panel: http://localhost:8101.
2. Zaloguj się jako redaktor szpitala i otwórz zasób jego zbioru. Pole „Wykaz AED: Tak” ma opis; błędy zakresu
   v0.5 widać w wynikach walidacji zasobu. _(zrzut)_
3. Uruchom scalanie: `python manage.py shell -c "from mcod.resources.tasks import create_main_aed_resource_task as t; print(t.apply().result)"`.
4. Oczekiwany wynik: **45 AED, 1 duplikat**, licencja wykazu zbiorczego **CC BY 4.0** (jeden dostawca ma CC BY).
   Rekord „ADM Centrum” z wykazu Przemyśla ma `duplikat_id_aed` wskazujący AED szpitala. Wykazy są
   przetwarzane alfabetycznie według instytucji, więc oznaczony jest rekord z wykazu przetworzonego później. AED
   oddalony o 45 m nie jest oznaczony. Kolumny pochodzenia: `zrodlo_instytucja`, `zrodlo_zasob_id`, `zrodlo_url`,
   `zrodlo_data_aktualizacji`, `licencja_zrodla`. _(zrzut, fragment pliku)_
5. Panel: Zasoby → „Wykaz zbiorczy AED”. Raport pokazuje, które wykazy dołączono, a które pominięto i dlaczego
   (błędy walidacji albo licencja spoza CC0 i CC BY 4.0). _(zrzut)_

**Bez uruchamiania portalu (pokaz scalania, ok. 1 minuta):**

1. `git clone --depth 1 -b portal-aed https://github.com/LastMinuteGameStudio/hacknation hacknation-portal && cd hacknation-portal/portal`
2. `python3 -m venv .venv && .venv/bin/pip install openpyxl && .venv/bin/python tuaed_pokaz_scalania.py --offline`
   (Python ≥ 3.8, bez Django i bazy). Bez
   `--offline` skrypt pobiera wykazy Przemyśla i Krosna z demo. Skrypt używa tego samego kodu, który wywołuje
   zadanie portalu ([mcod/resources/aed/](https://github.com/LastMinuteGameStudio/hacknation/blob/portal-aed/portal/mcod/resources/aed/)).
3. Oczekiwany wynik: **46 AED z 4 wykazów, licencja CC BY 4.0.**
   - 2 duplikaty, oba rekordy zostają: `szpital-krosno-1 → uczelnia-przemysl-1` (ten sam numer seryjny) i
     `szpital-krosno-2 → qy7g6px5-26c91c` (ok. 15 m).
   - 2 wykazy pominięte: „Fundacja (pokaz)” z powodu licencji CC BY-NC 4.0 i „Gmina (pokaz)”, bo wartość
     „dla wszystkich” jest spoza słownika `dostepnosc`.
4. Pliki wynikowe: [wykaz-zbiorczy.csv](https://github.com/LastMinuteGameStudio/hacknation/blob/portal-aed/portal/pokaz/wykaz-zbiorczy.csv) (RFC 4180, UTF-8 bez BOM, 52 pola publiczne
   i 5 kolumn pochodzenia, bez numerów seryjnych i telefonów), [wykaz-zbiorczy.xlsx](https://github.com/LastMinuteGameStudio/hacknation/blob/portal-aed/portal/pokaz/wykaz-zbiorczy.xlsx)
   i [raport.json](https://github.com/LastMinuteGameStudio/hacknation/blob/portal-aed/portal/pokaz/raport.json) (co dołączono, co pominięto i dlaczego). Opis: WYKAZ-AED.md, sekcja „Pokaz
   bez uruchamiania portalu”.
5. Testy kodu portalu: 18 testów czystej logiki ([test_aed_merge.py](https://github.com/LastMinuteGameStudio/hacknation/blob/portal-aed/portal/mcod/resources/tests/test_aed_merge.py))
   i testy z bazą w stylu wykazu DGA ([test_aed_list.py](https://github.com/LastMinuteGameStudio/hacknation/blob/portal-aed/portal/mcod/resources/tests/test_aed_list.py)).

## 4. Ograniczenia

- Publikacji na produkcyjnym dane.gov.pl nie sprawdziliśmy, bo nie mamy konta dostawcy. Wykaz AED w portalu
  działa w lokalnej kopii portalu (sekcja 3).
- Prototyp nie ma logowania. Zgubionego prywatnego linku do aktualizacji nie da się odzyskać.
- Geokodujemy (GUGiK) do 200 adresów bez współrzędnych na plik. W agregacie 63 AED nie ma współrzędnych.
- Dane OpenStreetMap mają licencję ODbL, więc agregat ma też wersję bez OSM.
- Demo działa na tunelu z komputera zespołu. Jeśli jest niedostępne, prosimy o drogę „bez demo” albo krok 0.
- AED w pojazdach są poza zakresem.

## Przebieg kontrolny (22.11.2026, ścieżka D)

Instrukcję przeszliśmy jak juror. Sprawdzone:
- **Linki:** wszystkie 75 linków w tym pliku (pliki na `main` i `portal-aed`, adresy raw, adresy demo) działają.
  Ścieżki demo z sekcji 2 (`/d/…`, `/szablon.*`, `/api/schemat`, `/docs`, `/mapa`, `/dane`) dają HTTP 200.
- **Sekcja 1:** przejście automatem (Playwright) z etykietami jak w tabeli, na lokalnym stacku z kroku 0: 23 z 24
  oczekiwań spełnione. Jedyna różnica: przy aktualizacji (1.9) strona nie pamięta wartości z kroku 1.4, więc
  w opisie kroku jest teraz polecenie, żeby ustawić je ponownie. Zrzuty kreatora odświeżone na demo
  (nowa nawigacja, „Wykaz AED” i metadane w kroku 3), zrzuty mapy i `/dane` dodane.
- **Krok 0:** świeży klon, `docker compose` z `.env.example`: działa. Dopisana zmiana `BASE_URL` (bez niej linki
  wskazują demo). Testy: na Pythonie 3.12 **223 passed**. Na systemowym 3.9 nie instaluje się `psycopg-binary`,
  stąd uwaga o wersji.
- **Sekcja 2:** `DOWOD-URL.md` 21/21 dla `kznsks42`, agregat `/d/aed-polska.csv` ma 19 871 wierszy.
- **Sekcja 3:** `python tuaed_pokaz_scalania.py` ze świeżego klonu `portal-aed`, online i `--offline`: **46 AED z 4
  wykazów, 2 duplikaty, 2 wykazy pominięte, CC BY 4.0**, zgodnie z opisem. Portalu w Dockerze jeszcze nie
  uruchamialiśmy, więc kroki 1–5 sekcji 3 i ich zrzuty czekają.
