# Wykorzystanie sztucznej inteligencji

Regulamin zadania (TRESC.md, pkt 5) dopuszcza AI, „pod warunkiem jednak, że finalnie praca będzie efektem analizy
i pracy człowieka i będzie autorskim rozwiązaniem zespołu”. Poniżej piszemy wprost, do czego używaliśmy AI, co
zrobili i postanowili ludzie i jak sprawdzaliśmy wynik.

## Narzędzie

**Claude Code** (model Claude Opus 5.5, Anthropic), czyli asystent programisty uruchamiany w terminalu. Pracowało
kilka sesji naraz, każda we własnym klonie repo i na swojej ścieżce: A rdzeń konwersji i wykaz AED w portalu,
B API i uruchomienie portalu, C front i zrzuty, D testy i instrukcja dla jury, a jedna sesja koordynowała.
Sesje wymieniały ustalenia przez wspólną tablicę (plik poza repo). Każdy commit przygotowany z AI ma w opisie
`Co-Authored-By: Claude`. Takich commitów jest 213 na 251 w repo.

## Do czego używaliśmy AI

- **Research:** przegląd źródeł danych o AED w Polsce, wzorców zagranicznych (Francja, Géo'DAE) i wymagań
  dane.gov.pl. Wyniki są w `zadania/06-mc-misja-aed/` (RESEARCH.md, ZRODLA-DANYCH.md, WZORCE-ZAGRANICZNE.md), każdy
  z linkiem do źródła.
- **Kod:** backend i front AEDane (`app/`), skrypty agregacji (`dane/`) i zmiany w kodzie portalu dane.gov.pl
  (`portal/`, wykaz AED na wzór wykazu DGA).
- **Testy i kontrola jakości:** testy automatyczne, testy end-to-end, audyt WCAG (axe-core, Lighthouse),
  sprawdzenie linków w dokumentacji.
- **Dokumentacja i prezentacja:** README, JURY.md, opisy w `portal/` i generator slajdów
  (`prezentacja/generator/`).

## Co zrobili i postanowili ludzie

- **Wybór zadania i kierunek rozwiązania.** Najważniejsza decyzja należała do zespołu: dysponent sam publikuje
  swoje dane przez kreator, a portal dane.gov.pl scala wykazy wszystkich dostawców. Zapadła po rozmowie z mentorem
  Ministerstwa Cyfryzacji (`ROZMOWA-MENTOR.md`).
- **Wnioski i decyzje projektowe:** 43 podpisane notatki zespołu w `NOTATKI-ZESPOLU.md` (Grzan, Wojtek), m.in.
  grupa docelowa, kreator w 3 krokach, podział pracy, technologia frontu, hosting, zasady dla brakujących danych.
- **Pytania do organizatora i mentora** (`PYTANIA-DO-ORGANIZATORA.md`) oraz rozmowa z mentorem.
- **Identyfikacja wizualna:** nazwa AEDane, hasło „Daj dane, daj życie”, logotyp i księga znaku (`visual/`, autor:
  Kuba).
- **Infrastruktura demo:** serwer i domena prototypu (Wojtek).
- **Nadzór nad pracą AI:** ludzie zatwierdzali zmiany, budowę i uruchomienie portalu, scalanie branchy, usuwanie
  danych i każdy push, a odrzucali propozycje niezgodne z kierunkiem.

## Jak sprawdzaliśmy wynik

- Testy automatyczne: 223 w aplikacji, testy wykazu AED w kontenerze portalu, test end-to-end scalania.
- Sprawdzenie kodu przez inną sesję niż autorka zmiany: niezależne uruchomienie testów, przejście instrukcji dla
  jury krok po kroku jak juror.
- Dostępność: axe-core 0 naruszeń, Lighthouse 100, przy szerokości od 320 px.
- Fakty z researchu mają link do źródła. Czego nie dało się potwierdzić, opisujemy jako niepotwierdzone.

## AI w samym produkcie

**AEDane w działaniu nie korzysta z AI.** Mapowanie kolumn pliku dysponenta działa na regułach: synonimy zebrane z
prawdziwych plików i analiza zawartości kolumn. Dane dysponentów nie trafiają do żadnego modelu językowego ani
zewnętrznej usługi AI. Ten sam plik zawsze daje ten sam wynik, a gdy dopasowanie jest niejednoznaczne, decyduje
użytkownik.

## Prawa

Kod i dokumenty w repo są wynikiem pracy zespołu z użyciem narzędzia AI. Według warunków Anthropic prawa do
wyników przysługują użytkownikowi. Wyjątkiem jest kod portalu w `portal/`: to kod mcod-backend (mirror publicznego
repozytorium portalu dane.gov.pl, opis w `portal/POMINIETE.md`), do którego dopisaliśmy własne zmiany. Pierwszy
commit z tym kodem jest niezmieniony, żeby nasze zmiany dało się odróżnić.
