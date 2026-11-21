# Zagregowane dane o AED w Polsce

Stan: pobrano 21.11.2026 (dokładny czas w `surowe/POBRANO.txt`). Opis źródeł: [zadania/06-mc-misja-aed/ZESTAWIENIE-ZRODEL.md](../zadania/06-mc-misja-aed/ZESTAWIENIE-ZRODEL.md).

## Pliki

| Plik | Zawartość |
|---|---|
| `wynik/aed_unikalne.csv` / `.geojson` | **Główny wynik.** Wszystkie punkty OSM oraz rekordy z innych źródeł, które nie mają odpowiednika w OSM ani w innym źródle |
| `wynik/aed_wszystkie.csv` (`.geojson` generuje skrypt, poza gitem) | Każdy rekord z każdego źródła. Duplikaty mają wypełnione pola `duplikat_id_aed` (id rekordu, z którym się pokrywają) i `odleglosc_duplikatu_m` |
| `wynik/aed_bez_wspolrzednych.csv` | Pozycje z wykazów, których nie udało się zgeokodować |
| `wynik/aed_pojazdy_gdansk.csv` | Pojazdy ZTM Gdańsk z AED, bez stałej lokalizacji. Pozycja na żywo: `ckan2.multimediagdansk.pl/gpsPositions?v=2`, łączenie po `vehicleCode` |
| `wynik/statystyki.json` | Liczby rekordów, duplikatów i wypełnienia pól |
| `surowe/` | Surowe pliki ze źródeł, bez zmian |
| `skrypty/pobierz.sh` → `skrypty/wykazy.py` → `skrypty/agreguj.py` | Kolejność odświeżania danych (tylko biblioteka standardowa Pythona) |

## Schemat

Pliki CSV mają **wszystkie 58 kolumn wzorcowego zakresu danych v0.5** (`zakres-danych/zakres-pol.csv`), w tej samej kolejności co `szablon-aed.csv`. Skrypt czyta listę pól i słowniki bezpośrednio z `zakres-danych/`, więc zmiana zakresu nie wymaga zmian w liście kolumn. Za kolumnami zakresu są 4 kolumny agregacji: `zrodlo`, `dzielnica`, `licencja_zrodla`, `odleglosc_duplikatu_m`.

Zasady zgodne z zakresem v0.5 i standardem technicznym dane.gov.pl:
- CSV wg RFC 4180: przecinek, CRLF, UTF-8 bez BOM.
- **Brak wartości to znak „X”**, a nie pusta komórka. W GeoJSON pola z „X” są pomijane.
- `id_aed` = `<zrodlo>:<id_zrodlowe>`. `duplikat_id_aed` to `id_aed` rekordu, z którym rekord się pokrywa (wcześniej kolumna `duplikat_z`).
- Słowniki v0.5:
  - `dostepnosc`: publiczny / klienci / na_prosbe / prywatny. OSM `permit` → na_prosbe, `employees`/`staff` → prywatny.
  - `dostepny_24_7`: tak / nie / ograniczony.
- `zrodlo_danych`: `jst` dla ewidencji urzędów, `dysponent` dla InPost i PWr, `inne` dla OSM i kont o nieznanym właścicielu. OSM to dane poglądowe na ODbL, a w zakresie nie ma osobnej wartości dla OSM.
- `status`: `sprawny` dla InPost (feed zawiera tylko aktywne punkty), dla pozostałych `nieznany`.
- `dokladnosc_polozenia`: `punkt_adresowy` dla współrzędnych z geokodowania, w pozostałych rekordach „X”.
- **Godziny w osobnej kolumnie na każdy dzień** (`godziny_pn` … `godziny_nd`, `godziny_swieta`), w formacie „GG:MM-GG:MM” albo „zamkniete”.
  - Z OSM rozkładana jest prosta składnia `opening_hours`: dni + jeden przedział albo `off`, reguły oddzielone „;”.
  - Z wykazów rozkładane są opisy typu „całodobowo” i „dni powszednie 07:00-17:00”.
  - Przy 24/7 kolumny godzin mają „X”, a `dostepny_24_7` = tak.
  - Godzin, których nie da się rozłożyć (sezonowe, kilka przedziałów, „w godzinach otwarcia”), nie zgadujemy: trafiają do `uwagi` jako `godziny (źródło): …`.
- Telefon zapisany jako `+48` i 9 cyfr. Numery skrócone (112, 998), kolejne numery i inne zapisy trafiają do `uwagi`.
- Tak samo (wartość do `uwagi`, w polu „X”) traktowane są: kondygnacje niecałkowite, daty niepełne (np. `2023-05`), adresy zdjęć bez `http(s)://`, kody pocztowe w innym formacie. Prefiks `ul.`/`al.`/`pl.`/`os.` przechodzi z nazwy ulicy do `cecha_ulicy`.
- Kolumna `aed_mobilny` została usunięta (AED w pojazdach są poza zakresem). Plik `aed_pojazdy_gdansk.csv` jest generowany bez zmian, poza schematem zakresu.

Wszystkie wartości różne od „X” są zgodne z typami i formatami opisu CSVW `szablon-aed.csv-metadata.json`. Pola obowiązkowe (O) często mają „X”, bo źródła ich nie podają, np. nazwa ulicy w OSM, `data_aktualizacji` w żadnym źródle. Ta luka pokazuje, czego brakuje w obecnych danych. Wypełnienie pól: `wynik/statystyki.json`.

## Deduplikacja

1. Rekord spoza OSM uznajemy za duplikat, jeśli najbliższy punkt OSM leży bliżej niż **50 m**. Dla współrzędnych z geokodowania próg wynosi **100 m**.
2. Rekordy spoza OSM, które nie mają odpowiednika w OSM, porównujemy między źródłami z progiem **30 m** (100 m dla geokodowanych). Wygrywa źródło wyżej na liście `PRIORYTET` w `agreguj.py`, a na jej początku jest oficjalny zbiór Warszawy.
3. Rekordów OSM nie łączymy między sobą, bo w jednym budynku bywa kilka AED.

Deduplikacja jest wyłącznie przestrzenna, więc może się mylić w obie strony: dwa różne AED w jednym budynku albo jeden AED opisany w dwóch źródłach z różnym położeniem.

## Geokodowanie

Wykazy HTML i PDF (Gdańsk, Gliwice, WOPR zachodniopomorskie, Lublin, Chełm) podają tylko adresy. Współrzędne pochodzą z Nominatim (OSM), z limitem 1 zapytania na sekundę i zapisem w cache `surowe/wykazy/geokod_cache.json`. Pole `uwagi` zawiera tryb geokodowania (`adres` albo `nazwa`) i typ trafienia. Trafienie typu `highway/...` oznacza, że punkt wskazuje ulicę, a nie budynek, więc dokładność jest niska.

## Licencje (fakty, nie porada prawna)

- OSM: ODbL 1.0, która wymaga atrybucji i udostępniania na tych samych warunkach (share-alike). Pliki `wynik/*` zawierają dane OSM.
- Warszawa: feed 19115 nie podaje licencji. Ten sam zbiór w API Otwarte dane Warszawy jest na CC BY.
- Pozostałe źródła nie podają licencji (szczegóły w kolumnie `licencja_zrodla`). Koszalin: „Wszystkie prawa zastrzeżone”.
- Zgodnie z regułami OSM danych spoza OSM nie wolno importować do OSM bez zgody właściciela.

## Wyniki

Po deduplikacji: **18 858 unikalnych AED** (18 299 z OSM i **559 spoza OSM**), do tego 63 pozycje z wykazów bez współrzędnych i 278 pojazdów ZTM Gdańsk z AED.

| Źródło (`zrodlo`) | Rekordy | Duplikat OSM | Nowe (poza OSM) | Bez współrzędnych |
|---|---|---|---|---|
| osm | 18 299 | – | – | – |
| warszawa_19115 | 708 | 353 | 355 | – |
| lodz_um | 136 | 113 | 23 | – |
| krakow_arcgis (2022, konto prywatne) | 150 | 83 | 64 (+3 duplikaty z innym źródłem) | – |
| krakow_arcgis_2022 | 44 | 35 | 9 | – |
| inpost | 137 | 121 | 16 | – |
| gliwice_crg (geokod.) | 95 | 46 | 44 | 5 |
| gdansk_um_2022 (geokod., stan 2022) | 114 | 70 | 11 | 33 |
| wopr_zachodniopomorskie (geokod.) | 91 | 52 | 20 | 19 |
| lublin_um (geokod.) | 46 | 28 | 12 | 5 |
| koszalin_um | 35 | 34 | 1 | – |
| mikolow_arcgis | 20 (+1 bez geometrii) | 20 | 0 | – |
| pwr, pwr_2023 | 15 | 11 | 3 (+1 duplikat) | – |
| chelm_um (geokod.) | 8 | 6 | 1 | 1 |

Wypełnienie pól w `aed_unikalne` (na 18 858, wartości różne od „X”): opis_lokalizacji 17 363, dostepnosc 17 285, wewnatrz_budynku 16 417, dostepny_24_7 7 187 (w tym 4 236 × całodobowo), data_weryfikacji 6 328, dysponent_nazwa 6 026, telefon 4 164, kondygnacja 4 038, godziny w podziale na dni 2 620, zdjecie_url 2 170, nazwa_obiektu 1 364, producent 702, adres (ulica) 636. Pełne liczby: `wynik/statystyki.json`.

## Czego tu nie ma (brak danych do pobrania)

- Pierwszy Ratownik (ok. 8 500–10 000 AED) i Fundacja Ratuj Życie (ratujzsercem.pl): bazy zamknięte.
- Kraków „IMPULS ŻYCIA” (krakow.pl): lista w HTML z paginacją. Jest częściowo pokryta przez `krakow_arcgis*`.
- Gliwice MSIP i GAMA: nie znaleźliśmy endpointu warstwy, użyliśmy tabeli HTML.
- Toruń (2016) i Siedlce (2017): wykazy nieaktualne, pominięte.
- AED w pojazdach poza Gdańskiem (Wrocław, Kraków, Rzeszów): brak list numerów taborowych.
