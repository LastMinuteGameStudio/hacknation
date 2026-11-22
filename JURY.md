# Instrukcja dla jury: TuAED (06 Misja AED)

Ta instrukcja prowadzi krok po kroku przez prototyp i wskazuje, gdzie sprawdzić każde wymaganie z treści
zadania ([TRESC.md](zadania/06-mc-misja-aed/TRESC.md), punkty 2–5). Każdy krok ma dwie drogi:

- **Demo:** publiczny prototyp https://tuaed.wkrynski.dev (wystarczy przeglądarka, bez logowania).
- **Bez demo:** gdy adres jest zablokowany w Waszej sieci, ten sam stan pokazuje zrzut ekranu albo plik w repo.
  Prototyp można też uruchomić lokalnie (Docker, krok 0).

Zrzuty są w [prezentacja/zrzuty/](prezentacja/zrzuty/README.md), każdy w wersji na komputer (`-1440.png`) i
telefon (`-320.png`). Niżej podajemy wersję 1440.

## 0. Przygotowanie (tylko jeśli demo nie działa)

1. Zainstaluj Dockera i sklonuj repo: `git clone https://github.com/LastMinuteGameStudio/hacknation`.
2. `cd hacknation/app && cp .env.example .env && docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build`
3. Otwórz http://localhost:8000. W dalszych krokach zamiast `https://tuaed.wkrynski.dev` wpisuj
   `http://localhost:8000`.
4. Testy automatyczne (opcjonalnie): `cd app/backend && python -m venv .venv && .venv/bin/pip install -r requirements.txt && .venv/bin/python -m pytest -q`
   Wynik: **222 passed**, w tym testy na 10 prawdziwych i syntetycznych plikach dysponentów.

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
| 1.1 | Otwórz https://tuaed.wkrynski.dev | Strona startowa: 3 kroki, szablony CSV i XLSX do pobrania, przycisk „Zacznij” | [09-start](prezentacja/zrzuty/09-start-1440.png) |
| 1.2 | „Zacznij”. Wpisz nazwę, np. `Urząd Miejski w Przemyślu (jury)`, typ „Jednostka samorządu terytorialnego”, „Dalej: dane” | Formularz dysponenta. Telefon i e-mail są opcjonalne i oznaczone „nie publikujemy” | [09-krok1-dysponent](prezentacja/zrzuty/09-krok1-dysponent-1440.png) |
| 1.3 | Wybierz pobrany `przemysl_2024.csv`, „Wgraj plik” | Tabela „Dopasuj kolumny”: dla 17 kolumn podpowiedź pola z pewnością. `geometry` → współrzędne, a 8 kolumn CMS (opis, galeria, linki…) → „nie importuj” | [09-krok2-mapowanie](prezentacja/zrzuty/09-krok2-mapowanie-1440.png), [cała tabela](prezentacja/zrzuty/09-krok2-mapowanie-tabela-1440.png) |
| 1.4 | W „Ustaw dla wszystkich AED w pliku” wybierz: wewnątrz budynku „Nie”, dostęp „Dostępny dla każdego”, całą dobę „Tak” | Pola obowiązkowe, których nie ma w pliku, ustawia się raz dla całego pliku | [09-krok2-wartosci-stale](prezentacja/zrzuty/09-krok2-wartosci-stale-1440.png) |
| 1.5 | „Sprawdź dane” | „Do publikacji: 21, Błędy: 0”, ostrzeżenia zbiorcze z opisem po polsku (np. „Cecha ulicy w 18 wierszach”). Rozwiń „Podgląd wyniku” | [09-krok2-walidacja](prezentacja/zrzuty/09-krok2-walidacja-1440.png), [podgląd](prezentacja/zrzuty/09-krok2-podglad-wyniku-1440.png) |
| 1.6 | „Dalej: publikacja”, zaznacz zgodę na CC0 1.0, „Opublikuj” | Stały adres `…/d/<slug>.csv`, prywatny link do aktualizacji i instrukcja dodania zasobu na dane.gov.pl z „Aktualizacją automatyczną”. Linki JSON i CSVW | [09-krok3-zgoda](prezentacja/zrzuty/09-krok3-zgoda-1440.png), [09-krok3-publikacja](prezentacja/zrzuty/09-krok3-publikacja-1440.png) |
| 1.7 | Kliknij „Dane w CSV” | Plik CSV: przecinki, UTF-8, kolumny wzorcowego zakresu v0.5 w stałej kolejności, telefon i e-mail usunięte | [08-csv-w-przegladarce](prezentacja/zrzuty/08-csv-w-przegladarce-1440.png) |
| 1.8 | Otwórz prywatny link do aktualizacji (skopiuj go z kroku 1.6) | Strona „Wgraj nową wersję danych” i sekcja „Źródło automatyczne” | [09-edycja-zrodlo-automatyczne](prezentacja/zrzuty/09-edycja-zrodlo-automatyczne-1440.png) |
| 1.9 | Wgraj [przemysl.csv](https://raw.githubusercontent.com/LastMinuteGameStudio/hacknation/main/app/backend/tests/fixtury/przemysl.csv) (eksport z 2026 r., inny format geometrii), sprawdź i opublikuj | Mapowanie podpowiada się samo, a publikacja podmienia dane **pod tym samym adresem** z **tymi samymi `id_aed`** | [przed](prezentacja/zrzuty/09-sync-0-csv-przed-1440.png) i [po](prezentacja/zrzuty/09-sync-4-csv-po-1440.png) (te same `id_aed`) |
| 1.10 | (opcjonalnie) W „Źródło automatyczne” wklej adres pliku na stronie urzędu i „Włącz i pobierz teraz” | Stan „Aktywna”, ZSYNCHRONIZOWANO. Zmiana kolumn w źródle wstrzymuje synchronizację i nie psuje danych | [ustawienie](prezentacja/zrzuty/09-sync-1-ustawienie-1440.png), [aktywna](prezentacja/zrzuty/09-sync-2-aktywna-1440.png), [nowy format](prezentacja/zrzuty/09-sync-3-zsynchronizowano-1440.png), [wstrzymana](prezentacja/zrzuty/09-sync-5-wstrzymana-1440.png) |
| 1.11 | Otwórz https://tuaed.wkrynski.dev/mapa | Mapa AED z całej Polski z popupem szczegółów. Wybór: wszystkie AED albo bez OpenStreetMap | [mapa](prezentacja/audyt/zrzuty/mapa-popup-1440.png), [telefon](prezentacja/audyt/zrzuty/mapa-320.png) |
| 1.12 | Otwórz https://tuaed.wkrynski.dev/dane | Zebrane dane: liczba AED według pochodzenia, tabela z wyszukiwaniem, „Zbiory dostawców” i pliki CSV i GeoJSON do pobrania | [dane](prezentacja/audyt/zrzuty/dane-1440.png), [telefon](prezentacja/audyt/zrzuty/dane-karty-320.png) |

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
2. Logotyp w plikach .jpg, .png, .pdf i formacie otwartym oraz księga znaku .pdf: _w przygotowaniu, ścieżka
   zostanie uzupełniona_.

### 2.8 Wymagania formalne (pkt 4)

| Wymaganie | Gdzie |
|---|---|
| Tytuł i szczegółowy opis | [README.md](README.md) |
| Prezentacja (min. 5 slajdów, zrzuty, kroki użytkownika, ograniczenia) | [prezentacja/TuAED-Misja-AED.pptx](prezentacja/TuAED-Misja-AED.pptx), zrzuty: [prezentacja/zrzuty/](prezentacja/zrzuty/README.md) |
| Prototyp | https://tuaed.wkrynski.dev, sekcja 1 tej instrukcji |
| Wzorcowy zakres danych (xlsx) | [zakres-danych/wzorcowy-zakres-danych-AED.xlsx](zakres-danych/wzorcowy-zakres-danych-AED.xlsx) |
| Kod źródłowy | to repozytorium: [app/](app/) (TuAED), [dane/skrypty/](dane/skrypty/) (agregacja), portal: sekcja 3 |
| Logotyp i księga znaku | 2.7 |

## 3. Zmiany w portalu dane.gov.pl (wykaz AED)

_Szkielet: sekcję uzupełnimy, gdy będą gotowe `portal/WYKAZ-AED.md` i `portal/URUCHOMIENIE-TUAED.md`._

Pomysł: na wzór wykazu DGA w kodzie portalu (mcod-backend 2.62.3) dostawca oznacza zasób flagą **„wykaz AED”**.
Portal waliduje go względem zakresu v0.5, a zadanie okresowe scala wykazy wszystkich dostawców w jeden zbiór.
Duplikat (ten sam numer seryjny albo do 30 m) nie jest usuwany, tylko dostaje `duplikat_id_aed`.

1. Uruchomienie lokalnego portalu: _(portal/URUCHOMIENIE-TUAED.md)_
2. Panel admina: dodanie zasobu z flagą „wykaz AED”: _(zrzut)_
3. Dwóch dostawców publikuje wykazy, a zadanie scalające tworzy jeden zbiór: _(zrzut, wynik testu e2e)_
4. Duplikat między dostawcami z `duplikat_id_aed`: _(zrzut, fragment pliku)_
5. Kod zmian i testy: _(portal/WYKAZ-AED.md, ścieżki do plików)_

## 4. Ograniczenia

- Publikacji na produkcyjnym dane.gov.pl nie sprawdziliśmy, bo nie mamy konta dostawcy. Wykaz AED w portalu
  działa w lokalnej kopii portalu (sekcja 3).
- Prototyp nie ma logowania. Zgubionego prywatnego linku do aktualizacji nie da się odzyskać.
- Geokodujemy (GUGiK) do 200 adresów bez współrzędnych na plik. W agregacie 63 AED nie ma współrzędnych.
- Dane OpenStreetMap mają licencję ODbL, więc agregat ma też wersję bez OSM.
- Demo działa na tunelu z komputera zespołu. Jeśli jest niedostępne, prosimy o drogę „bez demo” albo krok 0.
- AED w pojazdach są poza zakresem.
