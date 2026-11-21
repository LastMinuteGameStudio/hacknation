# Research: 06 Misja AED

Wyniki researchu (tylko fakty). Każdy temat ma status i autora sesji. Pełne wpisy ze źródłami są też na tablicy `~/Desktop/hacknation-wspolne/TABLICA.md`.

Inne pliki z researchem:
- [ZRODLA-DANYCH.md](ZRODLA-DANYCH.md): źródła danych o lokalizacji AED poza dane.gov.pl, Pierwszy Ratownik, Yanosik
- [CHECKLISTA.md](CHECKLISTA.md): wymagania organizatora

- **06 Misja AED:** „Zgodność z zasadami działania portalu dane.gov.pl”. Sprawdzić, jakie to są zasady.
  - ✅ **GOTOWE (sesja hacknacja):** źródła to rozporządzenie RM w sprawie portalu danych (Dz.U. 2022 poz. 2415: metadane §6–7, sposoby udostępniania §4, automatyczna weryfikacja §10), ustawa o otwartych danych (Dz.U. 2021 poz. 1641, rozdz. 7), standard techniczny (5 gwiazdek, CSV wg RFC 4180, ISO 8601, adresy w osobnych polach), standard API (JSON:API), DCAT-AP-PL 2.1.0 i instrukcja zasilania XML. Publiczne API działa bez klucza. Na portalu są już zbiory AED (np. Krosno, Marki, Przemyśl, Legionowo) i każdy ma inne kolumny. Linki są na tablicy.
- **06 Misja AED:** wymóg WCAG. Treść zadania: „zgodności z aktualną wersją WCAG oraz responsywności, tj. poprawne działanie na komputerach i urządzeniach mobilnych a także o zgodności z zasadami UX”. Sprawdzić aktualną wersję WCAG i jej wymagania.
  - ✅ **GOTOWE (sesja kvba):** aktualna wersja W3C to WCAG 2.2 (3.0 to wciąż szkic). Polskie prawo dla podmiotów publicznych wymaga WCAG 2.1 AA przez EN 301 549 V3.2.1. EN 301 549 V4.1.1 z WCAG 2.2 wyszła 2.09.2026, ale nie jest jeszcze zharmonizowana. Podmioty publiczne publikują też deklarację dostępności (HTML). Szczegóły i źródła są na tablicy `~/Desktop/hacknation-wspolne/TABLICA.md`. **Pytanie do organizatora:** jaki poziom i wersję WCAG sprawdza jury?
    - **Wersje a prawo:** WCAG 2.2 jest wstecznie zgodna z 2.1. W3C traktuje usunięte 4.1.1 Parsing jako spełnione również dla 2.1. Spełnienie WCAG 2.2 AA oznacza więc spełnienie 2.1 AA, czyli obu wariantów odpowiedzi organizatora. Zadanie nie podaje poziomu (A/AA/AAA) i nie definiuje „zasad UX”.
    - **EN 301 549 V4.1.1** (WCAG 2.2 AA, opublikowana 2.09.2026): stan na 21.11.2026 to brak cytowania w Dz.Urz. UE. Prognozy: ok. 30.11.2026 (AccessibilityTeam.eu) albo 16.12.2026 (irlandzki NDA). Do tego czasu domniemanie zgodności daje V3.2.1 (WCAG 2.1 AA). Polska ustawa z 2019 (po nowelizacji, Dz.U. 2023 poz. 511) wskazuje konkretnie V3.2.1:2021. Polskiej PN V4.1.1 nie znaleziono.
    - **Nowe kryteria AA w WCAG 2.2:** 2.4.11 Focus Not Obscured, 2.5.7 Dragging Movements (przeciąganie musi mieć alternatywę jednym wskaźnikiem bez przeciągania), 2.5.8 Target Size (min. 24×24 CSS px lub odstęp), 3.3.8 Accessible Authentication. Na poziomie A doszły 3.2.6 Consistent Help i 3.3.7 Redundant Entry.
    - **Kryteria AA istotne dla responsywności i mobile:** 1.3.4 Orientation, 1.4.10 Reflow (320 CSS px bez przewijania w dwóch wymiarach), 1.4.4 Resize Text (200%), 1.4.12 Text Spacing, 1.4.3 / 1.4.11 kontrast (4.5:1 tekst, 3:1 elementy UI), 2.5.1 Pointer Gestures, 1.4.13 Content on Hover or Focus.
    - **Deklaracja dostępności dane.gov.pl** (źródło: CMS API portalu `https://cms.dane.gov.pl/api/pages/page/deklaracja-dostepnosci/`, przegląd 2026-03-27):
      - status „częściowo zgodna” z ustawą z 2019;
      - jedyne wyłączenie to dane od podmiotów zewnętrznych („nie leży w gestii” administratora portalu);
      - podstawą jest samoocena pracowników MC, bez audytu zewnętrznego;
      - z udogodnień wymienia tylko standardowe skróty klawiaturowe;
      - nie podaje wersji WCAG ani normy;
      - nie wspomina o aplikacji mobilnej.
    - **Przy okazji:** strony dane.gov.pl renderują się w JS, ale treści portalu (baza wiedzy, aktualności, strony) są dostępne jako JSON przez publiczne CMS API `https://cms.dane.gov.pl/api/pages/`.
    - **Dalsze pytania do organizatora** (przekazane do zbiorczej listy Wojtka):
      - czym jury sprawdza WCAG (narzędzia automatyczne, audyt ręczny, samoocena);
      - czy WCAG obejmuje też dostarczane pliki (xlsx, dane, PDF księgi znaku);
      - czy jest punkt odniesienia dla „zasad UX”;
      - czy wystarczy responsywna aplikacja webowa, czy oczekiwana jest też mobilna;
      - perspektywa ustawy z 2019 czy EAA.
- **06 Misja AED:** licencje źródeł danych AED i możliwość łączenia ich w jeden zbiór. Regulamin §4 ust. 2: „Uczestnicy zapewniają, że opracowane rozwiązanie jest wolne od wad prawnych oraz nie narusza praw osób trzecich”.
  - ✅ **GOTOWE (sesja kvba):** pełny wpis ze źródłami jest na tablicy („GOTOWE: licencje źródeł danych AED”). To nie jest porada prawna.
    - **Licencje zbiorów AED na dane.gov.pl** (API `api.dane.gov.pl/1.4/datasets`, 21.11.2026):
      - Krosno (3624): CC0 1.0
      - Przemyśl (4581): CC0 1.0
      - Marki (4955): CC BY 4.0
      - Warszawa (39512, tylko link do API miasta): CC BY 4.0
      - Katalog Warszawy (Stołeczne Centrum Bezpieczeństwa): CC BY
      - Endpoint 19115, Pierwszy Ratownik, Fundacja Ratuj Życie: licencji nie podano.
    - **Licencje oferowane przez dane.gov.pl:** backend portalu (mirror `github.com/olekstomek/mcod-backend-dane.gov.pl`, `mcod/datasets/models.py`, `Dataset.LICENSES`, commit z 16.10.2026) zna tylko CC0 1.0 i CC 4.0: BY, BY-SA, BY-NC, BY-NC-SA, BY-ND, BY-NC-ND. **ODbL nie ma.**
    - **Ustawa o otwartych danych** (t.j. Dz.U. 2023 poz. 1524):
      - art. 14 ust. 1: ISP udostępnia się „bezwarunkowo, z wyjątkiem przypadków określonych w ustawie”;
      - art. 14 ust. 2: warunki dotyczą informacji będących utworem lub bazą danych (ustawa z 27.07.2001 o ochronie baz danych);
      - art. 15: możliwe warunki to źródło, informacja o przetworzeniu i zakres odpowiedzialności; można je określić „stosując standardowe otwarte licencje”;
      - art. 16: warunki muszą być „obiektywne, proporcjonalne, niedyskryminacyjne”;
      - art. 12: warunki w portalu to oferta, a ponowne wykorzystanie oznacza jej przyjęcie.
    - **OSM / OpenAEDMap (ODbL 1.0):**
      - 4.4: publicznie używana Derivative Database musi być na ODbL lub licencji zgodnej (share-alike);
      - 4.5: Collective Database i Produced Work (np. mapa) nie podlegają share-alike, ale wymagają noty o źródle (4.3);
      - 4.6: przy publicznym użyciu bazy pochodnej trzeba udostępnić ją całą albo plik zmian;
      - strona openstreetmap.org/copyright wymaga atrybucji OpenStreetMap i wskazania licencji ODbL.
    - **Wytyczne OSMF (Collective Database Guideline):** dane z OSM i spoza OSM są niezależne tylko wtedy, gdy dany typ danych w danym regionie pochodzi w całości z jednego źródła i zbiory nie odwołują się do siebie (klucz, join). Uzupełnianie warstwy OSM danymi spoza OSM uruchamia share-alike (Horizontal Layers Guideline).
    - **Licence Compatibility (OSMF):** CC0 jest „in general compatible” jako wejście do OSM. CC BY bez wyraźnego zrzeczenia (waiver) jest niezgodna z OSM.
    - **Odczyt sesji kvba (do potwierdzenia):**
      - jeden zbiór AED łączący rekordy z OSM z innymi źródłami to najpewniej Derivative Database na ODbL, a dane.gov.pl nie oferuje ODbL;
      - CC0 i CC BY 4.0 można łączyć, z atrybucją źródeł CC BY;
      - dane bez licencji nie mają jasnej podstawy do ponownego użycia, z możliwym wyjątkiem ISP z art. 14 ust. 1 (niezweryfikowane).
    - **Pytania do organizatora** (w [PYTANIA-DO-ORGANIZATORA.md](PYTANIA-DO-ORGANIZATORA.md) na branchu wojtek):
      - czy dane z OSM (ODbL) mogą trafić do zbioru na dane.gov.pl;
      - jakiej licencji MC oczekuje dla wzorcowego zbioru (CC0 czy CC BY 4.0).
