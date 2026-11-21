# Wnioski z analizy zadań (21.11.2026)

## Odrzucone

- **01** Attack Surface Intelligence (AGH)
- **07** OSINTowy Łapacz Cyfrowych Śladów (MF / KAS)
- **09** Prawdowid (MSZ)
- **11** Radar innowacji (PCI)
- **12** #InvestWatch (UKNF)
- **15** Przewodnik przyszłego rodzica (ZUS)

## Nadal w analizie

02 COI, 03 KPRM, 04 KOWR, 05 MC Kompas, 06 MC AED, 08 MFiPR, 10 NASK, 13 UM Bydgoszcz, 14 UZP

## Notatki zespołu

- **Grzan:** 08 Risk Miner raczej odpada, bo wymaga zbyt wielu modułów.
- **Grzan:** 06 Misja AED potencjalnie na plus, bo duża część zadania to otoczka nieprogramistyczna (logo, księga znaku, pitch).
- **Grzan:** 06 Misja AED ma najlepszy zakres, bo po zebraniu odpowiednich danych zostaje już tylko ich prezentacja i marketing samego rozwiązania.
- **Grzan:** 06 Misja AED: wymagana responsywność, czyli poprawne działanie zarówno na telefonach, jak i na komputerach.
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
- **06 Misja AED:** wymóg WCAG. Treść zadania: „zgodności z aktualną wersją WCAG oraz responsywności, tj. poprawne działanie na komputerach i urządzeniach mobilnych a także o zgodności z zasadami UX”. Sprawdzić aktualną wersję WCAG i jej wymagania.

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
