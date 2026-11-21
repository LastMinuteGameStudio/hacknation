# Wybór zadania (21.11.2026)

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

## Pliki zadania 06 Misja AED

- [Notatki zespołu](06-mc-misja-aed/NOTATKI-ZESPOLU.md)
- [Research (dane.gov.pl, WCAG)](06-mc-misja-aed/RESEARCH.md)
- [Źródła danych o AED](06-mc-misja-aed/ZRODLA-DANYCH.md)
- [Pytania do organizatora](06-mc-misja-aed/PYTANIA-DO-ORGANIZATORA.md)
- [Checklista wymagań](06-mc-misja-aed/CHECKLISTA.md)

## Notatki o innych zadaniach

- **Grzan:** 08 Risk Miner raczej odpada, bo wymaga zbyt wielu modułów.
- **Grzan:** 05 Kompas kompetencji: potencjalny problem to asystent AI, bo fajnie, żeby nie był zwykłym wrapperem wokół Claude'a czy innego modelu.
- **Grzan:** 05 Kompas kompetencji: narzędzie ma łączyć różne dziedziny, m.in. analitykę i umiejętności interpersonalne.
- **Grzan:** 05 Kompas kompetencji: użytkownikiem jest urzędnik, czyli osoba nietechniczna. Narzędzie nie zdejmuje z niego odpowiedzialności za ocenę.
- **Grzan:** 05 Kompas kompetencji: trzeba zrobić samo narzędzie i dodatkowo asystenta AI.
- **Grzan:** 05 Kompas kompetencji: regulamin mówi: „Zespoły przygotowujące rozwiązanie mogą korzystać na tym etapie wyłącznie z darmowych narzędzi AI.”

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
