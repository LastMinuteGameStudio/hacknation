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
- **06 Misja AED:** Francja jako punkt odniesienia (Géo'DAE, krajowy schemat danych AED).
  - ✅ **GOTOWE (sesja hacknacja, Grzan, 21.11.2026):**
    - **Schemat:** `atlasante/schema-dae` v1.0.8 (zmieniony 2026-03-20), format Table Schema (Frictionless, maszynowa walidacja CSV). Autor: Ministère des Solidarités et de la Santé (DGS). https://schema.data.gouv.fr/schemas/atlasante/schema-dae/1.0.8/schema.json , README: https://gitlab.com/arsante/atlasante/schema-dae
    - **Podstawa prawna (wg README schematu, tekstów na Légifrance nie udało się pobrać, HTTP 403):** loi n°2018-527 z 28.06.2018 o defibrylatorach, décret n°2018-1259 z 27.12.2018 o krajowej bazie AED, arrêté z 29.10.2019 o funkcjonowaniu bazy. Obowiązek wyposażenia budynków publicznych (ERP) w AED był wprowadzany etapami: kat. 1–3 od 2020, kat. 4 od 2021, część kat. 5 od 2022 (ANSM: https://ansm.sante.fr/dossiers-thematiques/defibrillateurs-cardiaques-externes/lemplacement-du-dae-et-sa-signaletique ).
    - **Kto zgłasza:** „exploitant”, czyli każda osoba fizyczna lub prawna, która jest właścicielem AED i udostępnia go innym (gmina, firma, centrum handlowe) albo używa go w działalności. Kto ma mało urządzeń, zgłasza przez formularz na portalu GéoDAE (https://geodae.atlasante.fr ), kto ma dużo, przesyła plik zgodny ze schematem. Konsolidacją zajmuje się ministerstwo (DGS). Aplikacje obywatelskie rozpowszechniają dane i mogą je „podważać”.
    - **45 pól schematu, 18 wymaganych:** nom, lat/long, acc (wewnątrz/na zewnątrz), acc_lib (wolny dostęp), tel1, etat_fonct (sprawny / niesprawny / usunięty / chwilowo nieobecny / nieznany), fab_rais, modele, num_serie, dermnt (data ostatniego przeglądu), expt_siren, expt_rais, expt_tel1, expt_email, dispo_horaires (format OSM `opening_hours`). Opcjonalne: adres (numer, ulica, kod pocztowy, kod INSEE gminy), piętro, opis dojścia, AED mobilny, 2 zdjęcia jako URL („libre de droit”), daty ważności elektrod (dorosłych i dziecięcych) i baterii, częstotliwość przeglądów, serwisant, zdalny monitoring, UDI.
    - **Otwarte dane:** „Géo'DAE - Base Nationale des Défibrillateurs” na data.gouv.fr (wydawca Atlasanté, Licence Ouverte 2.0, aktualizacja kilka razy dziennie). Pliki CSV ok. 81 MB i JSON ok. 221 MB. https://www.data.gouv.fr/datasets/geodae-base-nationale-des-defibrillateurs
      - Policzone z CSV z 21.11.2026: **192 453 AED.** Status: 177 436 zwalidowane, 14 800 oczekuje na walidację, 39 podważonych. Stan działania: 191 215 sprawnych, 746 chwilowo nieobecnych, 325 niesprawnych. 5 298 oznaczonych jako duplikaty. Zdjęcie ma 8 526. Godziny i data przeglądu są w każdym rekordzie (pola wymagane), ale 79 341 rekordów ma ostatni przegląd przed 2025.
      - **Open data to podzbiór schematu.** Nie publikuje się 13 pól: telefonów, e-maili (tel1, tel2, site_email, expt_tel1/2, expt_email), producenta, modelu, numeru seryjnego, UDI i serwisanta. Publiczne są: lokalizacja, adres, dostęp, godziny, stan, daty przeglądu i ważności, nazwa i SIREN dysponenta.
      - Dodatkowe kolumny techniczne w open data: status walidacji (`c_etat_valid`), flaga duplikatu (`c_doublon`), data aktualizacji danych, dokładność położenia.
