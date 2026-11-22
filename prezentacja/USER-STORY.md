# Historie użytkownika: TuAED (E3, do slajdów 3 i 9)

Schemat przepływu: [`schemat-przeplywu.svg`](schemat-przeplywu.svg) (ręczny SVG 1920×1080, ten plik jest też źródłem).

Kolumna 📷 wskazuje zrzuty ścieżki D w [`zrzuty/`](zrzuty/README.md). Numer w nazwie to numer slajdu z
`SZKIC-SLAJDOW.md`, a każdy zrzut jest w wersji `-1440.png` i `-320.png`. Zrzuty kreatora zrobiono na pliku
Przemyśla, więc ilustrują kroki obu historii. Zrzuty synchronizacji (`09-sync-*`) pochodzą z publicznego demo
(zbiór `kznsks42`, źródło podmieniane commitami: format 2024 → nowy format geometrii → zmiana struktury → naprawa).

Obie historie działają w prototypie (także na demo https://tuaed.wkrynski.dev). Historia 1 korzysta z pliku
`app/backend/tests/fixtury/syntetyczny_gmina.xlsx`, historia 2 z plików Przemyśla (`przemysl_2024.csv` → `przemysl.csv`).
Krok na dane.gov.pl wykonuje się w panelu portalu.

---

## Historia 1: gmina z arkuszem XLSX

**Persona.** Anna, inspektorka ds. zarządzania kryzysowego w Urzędzie Gminy Przykładowo. Prowadzi
„Wykaz defibrylatorów AED na terenie gminy” w Excelu: tytuł nad tabelą, scalone komórki z miejscowością,
godziny wpisane po swojemu („24h”, „pn-pt 7:30-15:30”, „w godzinach otwarcia ośrodka”) i stopka „Sporządził: …”.
Nie zna CSV ani schematów danych. Chce, żeby AED z gminy były widoczne dla dyspozytorów i w aplikacjach.

**Cel.** Opublikować wykaz na dane.gov.pl tak, żeby dalej poprawiać go w Excelu, a nie w kolejnym systemie.

| # | Co robi Anna | Co robi TuAED | 📷 |
|---|---|---|---|
| 0 | Wchodzi na stronę TuAED. Może pobrać szablon CSV/XLSX, ale ma już swój arkusz | Strona startowa: trzy kroki, szablony do pobrania | [`09-start`](zrzuty/09-start-1440.png) |
| 1 | **Krok 1, Dysponent:** wpisuje „Urząd Gminy Przykładowo”, wybiera typ „Jednostka samorządu terytorialnego”, podaje służbowy telefon i e-mail | Kontakt oznacza jako niepubliczny: nie trafia do pliku na dane.gov.pl | [`09-krok1-dysponent`](zrzuty/09-krok1-dysponent-1440.png) |
| 2 | **Krok 2, Dane:** wgrywa swój plik XLSX bez żadnych zmian | Sam znajduje nagłówek w 4. wierszu, pomija tytuł i stopkę, wpisuje scaloną miejscowość do każdego wiersza | [`09-krok2-mapowanie`](zrzuty/09-krok2-mapowanie-1440.png) |
| 3 | Przegląda propozycję mapowania. Nic nie poprawia | Proponuje pole v0.5 dla 9 z 10 kolumn, każde z pewnością i powodem. „Lp.” to liczba porządkowa, więc jej nie importuje | [`09-krok2-mapowanie-tabela`](zrzuty/09-krok2-mapowanie-tabela-1440.png) |
| 4 | Czyta wynik walidacji: **0 błędów**, kilka ostrzeżeń | Rozbija adres „ul. Rynek 1, 34-100 Przykładowo” na pola. „24h” i „całodobowo” to dostęp 24/7, a „na zewnątrz, przy wejściu” to `wewnatrz_budynku = false`. Ostrzega o tym, co ustawił sam: status „nieznany”, data weryfikacji = dziś, identyfikatory nadane automatycznie, a „w godzinach otwarcia ośrodka” przeniesione do uwag | [`09-krok2-walidacja`](zrzuty/09-krok2-walidacja-1440.png), [`09-krok2-podglad-wyniku`](zrzuty/09-krok2-podglad-wyniku-1440.png) |
| 5 | **Krok 3, Publikacja:** zaznacza zgodę na licencję CC0 1.0 i klika „Opublikuj” | Daje stały adres `/d/{slug}.csv` oraz JSON i metadane CSVW. Prywatny link edycji pokazuje tylko raz i przypomina, żeby go zapisać | [`09-krok3-zgoda`](zrzuty/09-krok3-zgoda-1440.png), [`09-krok3-publikacja`](zrzuty/09-krok3-publikacja-1440.png) |
| 6 | W panelu dane.gov.pl dodaje zasób jako link do `/d/{slug}.csv` i włącza **„Aktualizacja automatyczna: codziennie”** | Instrukcja krok po kroku jest w kroku 3 kreatora | [`09-krok3-publikacja`](zrzuty/09-krok3-publikacja-1440.png) (instrukcja) |
| 7 | **Po pół roku:** w świetlicy wymieniono AED, a w ośrodku zdrowia zmieniły się godziny. Anna poprawia swój arkusz i otwiera zapisany link edycji | Pamięta poprzednie mapowanie, więc kreator od razu proponuje te same pola | [`09-edycja-zrodlo-automatyczne`](zrzuty/09-edycja-zrodlo-automatyczne-1440.png) |
| 8 | Klika „Opublikuj” | **Adres URL się nie zmienia.** Te same AED mają te same `id_aed`. dane.gov.pl pobiera nową wersję w nocy, bez logowania się do portalu | [`09-sync-0-csv-przed`](zrzuty/09-sync-0-csv-przed-1440.png), [`09-sync-4-csv-po`](zrzuty/09-sync-4-csv-po-1440.png) (ten sam URL i `id_aed` przed i po aktualizacji) |

**Efekt.** Gmina po raz pierwszy publikuje AED w formacie zgodnym ze wzorcowym zakresem v0.5. Aktualizacja to
„popraw Excel i wgraj przez link”: pięć minut raz na jakiś czas, bez znajomości CSV.

---

## Historia 2: miasto z plikiem na swojej stronie (Przemyśl)

**Persona.** Urząd Miejski w Przemyślu ma dane AED w CMS, który sam eksportuje CSV na stronę miasta.
Zbiór jest na dane.gov.pl z deklaracją „Codziennie”. Portal trzyma jednak kopię z 2024 r., bo zasób dodano bez
aktualizacji automatycznej. Plik ma separator `;`, akapit marketingowy w każdym wierszu i współrzędne jako JSON w komórce.
Miasto nie chce zmieniać CMS ani pamiętać o ręcznym wgrywaniu.

| # | Co się dzieje | 📷 |
|---|---|---|
| 1 | Urzędnik raz przechodzi kreator z eksportem z CMS. TuAED mapuje go bez poprawek: rozbija geometrię JSON na szerokość i długość, a 8 kolumn CMS (opis marketingowy, galeria, linki) pomija | [`09-krok2-mapowanie-tabela`](zrzuty/09-krok2-mapowanie-tabela-1440.png), [`09-krok2-wartosci-stale`](zrzuty/09-krok2-wartosci-stale-1440.png) |
| 2 | Publikacja daje stały URL z CSV zgodnym z v0.5 zamiast eksportu z CMS | [`08-csv-w-przegladarce`](zrzuty/08-csv-w-przegladarce-1440.png) |
| 3 | Na stronie edycji (prywatny link), w sekcji **„Źródło automatyczne”**, wkleja adres eksportu z CMS, wybiera częstotliwość (np. „raz dziennie”) i klika „Włącz i pobierz teraz” | [`09-edycja-zrodlo-automatyczne-sekcja`](zrzuty/09-edycja-zrodlo-automatyczne-sekcja-1440.png), [`09-sync-1-ustawienie`](zrzuty/09-sync-1-ustawienie-1440.png) |
| 4 | TuAED od razu pobiera plik i dalej robi to sam według harmonogramu: zapamiętane mapowanie → walidacja → publikacja pod tym samym slugiem. Status „aktywna”, komunikat **ZSYNCHRONIZOWANO**. Gdy plik się nie zmienił: **BEZ_ZMIAN** | [`09-sync-2-aktywna`](zrzuty/09-sync-2-aktywna-1440.png), [`09-sync-3-zsynchronizowano`](zrzuty/09-sync-3-zsynchronizowano-1440.png) |
| 5 | CMS zmienia format geometrii z `{"lat","long"}` na `[lon, lat]`. Przy następnej synchronizacji TuAED rozpoznaje nowy format, a **URL i `id_aed` zostają te same**. Nikt w urzędzie nic nie robi | [`09-sync-0-csv-przed`](zrzuty/09-sync-0-csv-przed-1440.png), [`09-sync-4-csv-po`](zrzuty/09-sync-4-csv-po-1440.png) |
| 6 | Zabezpieczenie: gdy w źródle zniknie zmapowana kolumna albo pojawi się nowa (**ZMIANA_STRUKTURY**) lub zmieni się ponad połowa AED (**ZA_DUZA_ZMIANA**), synchronizacja jest **wstrzymana**, a opublikowane dane zostają bez zmian. Po naprawie pliku w źródle dysponent klika „Zapisz i pobierz teraz” i synchronizacja znów jest aktywna. Przy ZA_DUZA_ZMIANA kreator pyta wprost: „Potwierdź zmianę i opublikuj”. Przy innej strukturze pliku można też wgrać plik z nowym mapowaniem | [`09-sync-5-wstrzymana`](zrzuty/09-sync-5-wstrzymana-1440.png), [`09-sync-6-przywrocona`](zrzuty/09-sync-6-przywrocona-1440.png) |

**Efekt.** Dane z CMS miasta codziennie trafiają na dane.gov.pl w ujednoliconym formacie, bez zmian w systemie
miasta i bez ręcznej pracy. Błędne źródło nie nadpisze dobrych danych.

---

## Jak to działa w środku (slajd techniczny)

1. **Wczytuje pliki z prawdziwych urzędów.** CSV (dowolny separator, UTF-8 lub Windows-1250), XLSX i GeoJSON.
   Radzi sobie z tytułem nad tabelą, scalonymi komórkami, nagłówkiem w dwóch wierszach, stopką i całym wierszem
   w jednej komórce (zbiór z Marek). Limit: 10 MB i 20 000 wierszy.
2. **Mapowanie kolumn bez AI.** Heurystyka łączy znormalizowane nazwy, synonimy z realnych źródeł (miasta,
   OSM, francuski Géo'DAE), podobieństwo tekstu i analizę zawartości (np. liczby 49–55 to szerokość geograficzna,
   NN-NNN to kod pocztowy). **100% trafień na 10 plikach testowych** (7 realnych z 5 miast, 3 „urzędowe” XLSX).
3. **Normalizacja do wzorcowego zakresu v0.5.** Daty do ISO 8601, przecinek dziesiętny, „tak/nie” do true/false,
   słowniki („czynny” → `sprawny`), godziny z wolnego tekstu do pól `godziny_pn…nd`, adres z jednego pola
   rozbity na części. Zamiana szerokości z długością jest wykrywana w każdym wierszu osobno.
4. **Geokodowanie w GUGiK.** Rekordy bez współrzędnych dostają punkt adresowy z państwowego geokodera (UUG),
   z cache i limitem 200 adresów na plik. Niejednoznaczne trafienia rozstrzyga gmina, w której leży reszta pliku.
   Przykład: plik z Krosna bez współrzędnych, 21 adresów ustalonych w mniej niż 1 s.
5. **Walidacja O/Z/F.** Brak pola obowiązkowego to błąd i blokuje publikację. Brak zalecanego to ostrzeżenie.
   Sprawdza też formaty, słowniki, współrzędne w Polsce, duplikaty identyfikatorów i numerów seryjnych
   oraz AED bliżej niż 5 m od siebie. Każdy komunikat ma numer wiersza taki, jak w arkuszu dostawcy.
6. **Formaty dla dane.gov.pl.** CSV zgodny z RFC 4180 (UTF-8 bez BOM, przecinek, CRLF), JSON i metadane CSVW,
   tylko pola publiczne, licencja CC0 1.0. Stały URL działa z „Aktualizacją automatyczną” portalu.
7. **Stabilne identyfikatory.** Gdy plik nie ma `id_aed`, TuAED nadaje `<TERC lub slug>-<6 znaków>` ze skrótu numeru
   seryjnego albo współrzędnych i nazwy. Ponowne wgranie tego samego AED daje ten sam identyfikator, więc
   odbiorcy mogą śledzić zmiany.
