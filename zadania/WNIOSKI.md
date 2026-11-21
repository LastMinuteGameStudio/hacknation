# Wnioski z analizy zadań (21.11.2026)

## ✅ Decyzja

Zespół wybrał **06 Misja AED (MC)**.

## Odrzucone

- **01** Attack Surface Intelligence (AGH)
- **07** OSINTowy Łapacz Cyfrowych Śladów (MF / KAS)
- **09** Prawdowid (MSZ)
- **11** Radar innowacji (PCI)
- **12** #InvestWatch (UKNF)
- **15** Przewodnik przyszłego rodzica (ZUS)

## Analizowane, niewybrane

02 COI, 03 KPRM, 04 KOWR, 05 MC Kompas, 08 MFiPR, 10 NASK, 13 UM Bydgoszcz, 14 UZP

## Notatki zespołu

- **Grzan:** 08 Risk Miner raczej odpada, bo wymaga zbyt wielu modułów.
- **Grzan:** 06 Misja AED potencjalnie na plus, bo duża część zadania to otoczka nieprogramistyczna (logo, księga znaku, pitch).
- **Grzan:** 06 Misja AED ma najlepszy zakres, bo po zebraniu odpowiednich danych zostaje już tylko ich prezentacja i marketing samego rozwiązania.
- **Grzan:** 06 Misja AED: wymagana responsywność, czyli poprawne działanie zarówno na telefonach, jak i na komputerach.
- **Wojtek / Grzan:** 06 Misja AED: Wojtek proponował, żeby użytkownicy mogli zgłaszać lokalizacje defibrylatorów. Ten pomysł już ktoś realizował. W Pierwszym Ratowniku (ZOSP RP) bazę tworzą sami użytkownicy razem z ZOSP RP: zalogowana osoba może dodać AED, zaktualizować go albo zgłosić, że zniknął (dodawanie nowych jest obecnie wyłączone, wg FAQ). Podobnie działają OSM, Yanosik, aplikacja Ratownik i formularz „Zgłoś urządzenie AED” w Warszawie 19115. Szczegóły: [06-mc-misja-aed/ZRODLA-DANYCH.md](06-mc-misja-aed/ZRODLA-DANYCH.md).
- **Grzan:** 06 Misja AED kładzie ogromny nacisk na potencjał promocyjny. Kryteria oceny („przykładowe”):
  - Zgodność z zasadami działania portalu dane.gov.pl: 30%
  - Kreatywność i innowacyjność rozwiązania: 15%
  - Zgodność z tematem wyzwania: 15%
  - Wzorcowy zakres danych o defibrylatorach: 10%
  - Prezentacja wypracowanego i kompletnego rozwiązania: 5%
  - Logotyp i hasło (proste i zrozumiałe, zgodne z tematyką wyzwania, nowoczesne, kreatywne, z potencjałem promocyjnym): 25%
- **Grzan:** 05 Kompas kompetencji: potencjalny problem to asystent AI, bo fajnie, żeby nie był zwykłym wrapperem wokół Claude'a czy innego modelu.
- **Grzan:** 05 Kompas kompetencji: narzędzie ma łączyć różne dziedziny, m.in. analitykę i umiejętności interpersonalne.
- **Grzan:** 05 Kompas kompetencji: użytkownikiem jest urzędnik, czyli osoba nietechniczna. Narzędzie nie zdejmuje z niego odpowiedzialności za ocenę.
- **Grzan:** 05 Kompas kompetencji: trzeba zrobić samo narzędzie i dodatkowo asystenta AI.
- **Grzan:** 05 Kompas kompetencji: regulamin mówi: „Zespoły przygotowujące rozwiązanie mogą korzystać na tym etapie wyłącznie z darmowych narzędzi AI.”

## Do zresearchowania

- **06 Misja AED:** „Zgodność z zasadami działania portalu dane.gov.pl”. Sprawdzić, jakie to są zasady.
  - ✅ **GOTOWE (sesja hacknacja):** źródła to rozporządzenie RM w sprawie portalu danych (Dz.U. 2022 poz. 2415: metadane §6–7, sposoby udostępniania §4, automatyczna weryfikacja §10), ustawa o otwartych danych (Dz.U. 2021 poz. 1641, rozdz. 7), standard techniczny (5 gwiazdek, CSV wg RFC 4180, ISO 8601, adresy w osobnych polach), standard API (JSON:API), DCAT-AP-PL 2.1.0 i instrukcja zasilania XML. Publiczne API działa bez klucza. Na portalu są już zbiory AED (np. Krosno, Marki, Przemyśl, Legionowo) i każdy ma inne kolumny. Linki są na tablicy.
- **06 Misja AED:** wymóg WCAG. Treść zadania: „zgodności z aktualną wersją WCAG oraz responsywności, tj. poprawne działanie na komputerach i urządzeniach mobilnych a także o zgodności z zasadami UX”. Sprawdzić aktualną wersję WCAG i jej wymagania.
  - ✅ **GOTOWE (sesja kvba):** aktualna wersja W3C to WCAG 2.2 (3.0 to wciąż szkic). Polskie prawo dla podmiotów publicznych wymaga WCAG 2.1 AA przez EN 301 549 V3.2.1. EN 301 549 V4.1.1 z WCAG 2.2 wyszła 2.09.2026, ale nie jest jeszcze zharmonizowana. Podmioty publiczne publikują też deklarację dostępności (HTML). Szczegóły i źródła są na tablicy `~/Desktop/hacknation-wspolne/TABLICA.md`. **Pytanie do organizatora:** jaki poziom i wersję WCAG sprawdza jury?

## Ranking trudności (pozostałe zadania)

Ocena wynika tylko z wymagań organizatorów: ile trzeba oddać, czy dane są gotowe i jak dokładna jest specyfikacja.

### Najłatwiejsze

- **14 Odwołania2JSON (UZP)**: najwęższy zakres (3 typy dokumentów → JSON), dane treningowe i oczekiwane wyniki są na GitHubie, nie trzeba rozbudowanej aplikacji. Utrudnienia: tylko otwarte modele, bez GPU, w preselekcji liczy się wyłącznie F1.
- **13 Asystent urzędnika (UM Bydgoszcz)**: najbardziej szczegółowa specyfikacja (6 kroków testu jury), przykładowe wnioski z odpowiedziami. Utrudnienia: kilka modułów (kalendarz, archiwum, projekt pisma, anonimizacja) plus film i prezentacja.

### Średnie

- **05 Kompas kompetencji (MC)**: jasny cel, są materiały, wolno korzystać z gotowych modeli i zewnętrznych API. Utrudnienia: **wyłącznie darmowe narzędzia AI**, przepisy i model kompetencji, jury sprawdza odpowiedzi chatbota.
- **06 Misja AED (MC)**: mało programowania. Utrudnienia: źródła danych o AED trzeba znaleźć samemu, logo z księgą znaku ma 25% wagi.
- **02 Cyfryzacja formularzy (COI)**: jasne wejście i wyjście, są przykłady. Utrudnienia: wiele formatów razem ze skanami, zakaz modeli przez API, wymagania „produkcyjne” (Docker, JWT, walidacje).
- **10 Kolekcjoner fejków (NASK)**: UI nieoceniane, są przykładowe dane. Utrudnienia: wynik zależy od jakości grupowania na ukrytym zbiorze.

### Najtrudniejsze

- **03 Asystent ocen okresowych (KPRM)**: cały proces oceny (arkusze A/B/C) plus moduł HR, dużo materiału.
- **08 Risk Miner (MFiPR)**: automatyczne pobieranie z wielu publicznych baz, ekstrakcja, wyszukiwanie podobnych projektów, panel eksperta.
- **04 Zatrzymaj wodę (KOWR)**: brak dostarczonych danych, trzeba samemu zebrać satelitarne, meteo i glebowe z 10 lat, potrzebna wiedza rolnicza.

## Pytania do organizatora: 06 Misja AED (na spotkanie)

Kolejność według wagi w ocenie. ⭐ = najważniejsze, zadać na pewno.

### Zgodność z dane.gov.pl (30%)
- ⭐ Co dokładnie jury rozumie przez „zgodność z zasadami działania portalu dane.gov.pl”? Czy chodzi o rozporządzenie Dz.U. 2022/2415, standard techniczny (5★, CSV RFC 4180, ISO 8601), standard API, DCAT-AP-PL, czy o coś innego? Czy jest lista, według której sprawdzacie?
- ⭐ Jaki poziom otwartości (liczba gwiazdek) jest oczekiwany od udostępnianego zbioru?
- Czy rozwiązanie ma faktycznie publikować dane na dane.gov.pl (konto dostawcy, API), czy wystarczy, że dane są przygotowane zgodnie z wymaganiami portalu? Czy na hackathon jest dostępne środowisko testowe lub konto dostawcy?
- Kto w zamyśle MC ma być dostawcą ogólnopolskiego zbioru: jedna instytucja (agregator) czy każdy dysponent osobno?
- Czy metadane zbioru (DCAT-AP-PL) są częścią oceny?

### Wzorcowy zakres danych (10%)
- ⭐ Czy MC ma listę pól, których oczekuje (np. godziny dostępności, stan techniczny, data przeglądu, kontakt)? Czy są pola obowiązkowe lub zakazane, np. ze względu na RODO (dane osoby odpowiedzialnej, telefon prywatny)?
- Czy zakres danych ma się opierać na istniejącym standardzie (np. tagi OSM `emergency=defibrillator`, schematy z innych krajów) czy ma być od zera?
- Czy w xlsx oczekujecie samego opisu pól (nazwa, typ, opis, wymagalność, przykład), czy także przykładowych rekordów?
- Czy kody TERC/SIMC i standard adresowy są wymagane?

### Źródła danych
- ⭐ Czy MC zna lub poleca konkretne źródła danych o AED poza dane.gov.pl (rejestry ratownicze, PRM/KSRG, wojewodowie, NFZ, aplikacje typu Ratunek)? Czy któreś są dla nas udostępnione na czas hackathonu?
- Czy wolno korzystać z danych na licencjach z warunkiem udostępniania na tej samej licencji (np. OpenStreetMap, ODbL) i łączyć je w jednym zbiorze z danymi CC0 / CC BY? Jaka licencja docelowego zbioru jest oczekiwana?
- Czy dopuszczalne jest pobieranie danych ze stron www dysponentów (scraping), jeśli nie mają one licencji otwartej?
- Ilu rekordów lub jakiego pokrycia (gminy, miasta, cała Polska) oczekujecie w prototypie?

### Prototyp i walidacja
- ⭐ Jak jury będzie uruchamiać prototyp: link do działającej wersji, repozytorium + instrukcja, Docker? Na jakich urządzeniach będzie sprawdzane?
- Kto jest głównym użytkownikiem prototypu: dysponent danych (który je przesyła), służby ratownicze czy obywatel szukający AED? Czy wszyscy trzej muszą być obsłużeni?
- ⭐ Jaką wersję i jaki poziom WCAG sprawdzacie (2.1 AA wg ustawy czy 2.2 AA)? Czy wymagana jest deklaracja dostępności?
- Co rozumiecie przez „zgodność z zasadami UX”? Czy jest konkretny standard, np. Gov.pl Design System?
- Czy można korzystać z zewnętrznych usług (mapy, geokodowanie, hosting), czy tylko z rozwiązań otwartych lub darmowych?

### Akcja, logo, księga znaku (25%)
- ⭐ Kto jest odbiorcą akcji: dysponenci danych (gminy, firmy, szkoły), obywatele czy oba?
- Czy logo ma współgrać z identyfikacją dane.gov.pl / MC / gov.pl? Czy są ograniczenia (np. zakaz używania godła, barw MC, symbolu serca ERC)?
- Czy wolno używać fontów i ikon na licencjach otwartych (OFL, CC BY) i czy trzeba to udokumentować w księdze znaku?
- Czy ocena logo dotyczy samego znaku, czy także materiałów promocyjnych (plakat, social media)?

### Formalne
- Czy lista kryteriów („przykładowe kryteria”) jest ostateczna, czy wagi mogą się zmienić?
- Jak długi będzie pitch lub prezentacja w finale i w jakiej formie składamy materiały (format, limit rozmiaru, gdzie)?
- Przeniesienie praw majątkowych: czy dotyczy także zebranego zbioru danych i kodu z bibliotekami open source?
