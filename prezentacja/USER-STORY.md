# Historie użytkownika: TuAED (E3, do slajdów 3 i 9)

Schemat przepływu: [`schemat-przeplywu.svg`](schemat-przeplywu.svg) (ręczny SVG 1920×1080, ten plik jest też źródłem).

Odwołania 📷 wskazują zrzuty, które robi ścieżka D (`prezentacja/zrzuty/README.md`). Nazwy zrzutów są robocze:
gdy README będzie gotowe, trzeba je dopasować.

Wszystko w historii 1 działa w prototypie na pliku `app/backend/tests/fixtury/syntetyczny_gmina.xlsx`.
Wyjątkiem jest krok na dane.gov.pl, który wykonuje się w portalu. W historii 2 synchronizacja z URL to plan (S1).
Dziś to samo robi się, wgrywając nowy plik przez link edycji.

---

## Historia 1: gmina z arkuszem XLSX

**Persona.** Anna, inspektorka ds. zarządzania kryzysowego w Urzędzie Gminy Przykładowo. Prowadzi
„Wykaz defibrylatorów AED na terenie gminy” w Excelu: tytuł nad tabelą, scalone komórki z miejscowością,
godziny wpisane po swojemu („24h”, „pn-pt 7:30-15:30”, „w godzinach otwarcia ośrodka”) i stopka „Sporządził: …”.
Nie zna CSV ani schematów danych. Chce, żeby AED z gminy były widoczne dla dyspozytorów i w aplikacjach.

**Cel.** Opublikować wykaz na dane.gov.pl tak, żeby dalej poprawiać go w Excelu, a nie w kolejnym systemie.

| # | Co robi Anna | Co robi TuAED | 📷 |
|---|---|---|---|
| 0 | Wchodzi na stronę TuAED. Może pobrać szablon CSV/XLSX, ale ma już swój arkusz | Strona startowa: trzy kroki, szablony do pobrania | `01-start` |
| 1 | **Krok 1, Dysponent:** wpisuje „Urząd Gminy Przykładowo”, wybiera typ „Jednostka samorządu terytorialnego”, podaje służbowy telefon i e-mail | Kontakt oznacza jako niepubliczny: nie trafia do pliku na dane.gov.pl | `02-dysponent` |
| 2 | **Krok 2, Dane:** wgrywa swój plik XLSX bez żadnych zmian | Sam znajduje nagłówek w 4. wierszu, pomija tytuł i stopkę, wpisuje scaloną miejscowość do każdego wiersza | `03-wgranie` |
| 3 | Przegląda propozycję mapowania. Nic nie poprawia | Proponuje pole v0.5 dla 9 z 10 kolumn, każde z pewnością i powodem. „Lp.” to liczba porządkowa, więc jej nie importuje | `04-mapowanie` |
| 4 | Czyta wynik walidacji: **0 błędów**, kilka ostrzeżeń | Rozbija adres „ul. Rynek 1, 34-100 Przykładowo” na pola. „24h” i „całodobowo” to dostęp 24/7, a „na zewnątrz, przy wejściu” to `wewnatrz_budynku = false`. Ostrzega o tym, co ustawił sam: status „nieznany”, data weryfikacji = dziś, identyfikatory nadane automatycznie, a „w godzinach otwarcia ośrodka” przeniesione do uwag | `05-walidacja` |
| 5 | **Krok 3, Publikacja:** zaznacza zgodę na licencję CC0 1.0 i klika „Opublikuj” | Daje stały adres `/d/{slug}.csv` oraz JSON i metadane CSVW. Prywatny link edycji pokazuje tylko raz i przypomina, żeby go zapisać | `06-publikacja` |
| 6 | W panelu dane.gov.pl dodaje zasób jako link do `/d/{slug}.csv` i włącza **„Aktualizacja automatyczna: codziennie”** | Instrukcja krok po kroku jest w kroku 3 kreatora | `07-dane-gov-pl` |
| 7 | **Po pół roku:** w świetlicy wymieniono AED, a w ośrodku zdrowia zmieniły się godziny. Anna poprawia swój arkusz i otwiera zapisany link edycji | Pamięta poprzednie mapowanie, więc kreator od razu proponuje te same pola | `08-edycja` |
| 8 | Klika „Opublikuj” | **Adres URL się nie zmienia.** Te same AED mają te same `id_aed`. dane.gov.pl pobiera nową wersję w nocy, bez logowania się do portalu | `09-ten-sam-url` |

**Efekt.** Gmina po raz pierwszy publikuje AED w formacie zgodnym ze wzorcowym zakresem v0.5. Aktualizacja to
„popraw Excel i wgraj przez link”: pięć minut raz na jakiś czas, bez znajomości CSV.

---

## Historia 2: miasto z plikiem na swojej stronie (Przemyśl)

**Persona.** Urząd Miejski w Przemyślu ma dane AED w CMS i eksportuje je jako CSV na swojej stronie.
Zbiór jest na dane.gov.pl z deklaracją „Codziennie”. Portal trzyma jednak kopię z 2024 r., bo zasób dodano bez
aktualizacji automatycznej. Plik ma separator `;`, akapit marketingowy w każdym wierszu i współrzędne jako JSON w komórce.

| # | Co się dzieje | 📷 |
|---|---|---|
| 1 | Urzędnik wgrywa eksport z CMS. TuAED mapuje go bez poprawek: rozbija geometrię JSON na szerokość i długość, a 8 kolumn CMS (opis marketingowy, galeria, linki) pomija | `10-przemysl-mapowanie` |
| 2 | Publikacja: stały URL z CSV zgodnym z v0.5 zamiast eksportu z CMS | `11-przemysl-csv` |
| 3 | **Dziś (działa):** gdy CMS zmieni format (np. geometria z `{"lat","long"}` na `[lon, lat]`), urzędnik wgrywa nowy eksport przez link edycji. URL i `id_aed` zostają te same. Scenariusz demo: `app/backend/tests/fixtury/DEMO.md` | `12-przemysl-aktualizacja` |
| 4 | **W planie (S1):** zamiast wgrywać plik, urzędnik podaje adres eksportu z CMS. TuAED pobiera go codziennie z zapamiętanym mapowaniem. Gdy zmieni się struktura pliku, wstrzymuje aktualizację i pisze do dysponenta, zamiast opublikować błędne dane | (brak, funkcja w planie) |

**Efekt.** Dane z CMS miasta trafiają na dane.gov.pl w ujednoliconym formacie i są aktualne, a miasto nie musi
zmieniać swojego systemu.

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
