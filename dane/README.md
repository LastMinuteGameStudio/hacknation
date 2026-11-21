# Zagregowane dane o AED w Polsce

Stan: pobrano 21.11.2026 (dokładny czas w `surowe/POBRANO.txt`). Opis źródeł: [zadania/06-mc-misja-aed/ZESTAWIENIE-ZRODEL.md](../zadania/06-mc-misja-aed/ZESTAWIENIE-ZRODEL.md).

## Pliki

| Plik | Zawartość |
|---|---|
| `wynik/aed_unikalne.csv` / `.geojson` | **Główny wynik.** Wszystkie punkty OSM oraz rekordy z innych źródeł, które nie mają odpowiednika w OSM ani w innym źródle |
| `wynik/aed_wszystkie.csv` (`.geojson` generuje skrypt, poza gitem) | Każdy rekord z każdego źródła. Duplikaty mają wypełnione pola `duplikat_z` (id rekordu, z którym się pokrywają) i `odleglosc_duplikatu_m` |
| `wynik/aed_bez_wspolrzednych.csv` | Pozycje z wykazów, których nie udało się zgeokodować |
| `wynik/aed_pojazdy_gdansk.csv` | Pojazdy ZTM Gdańsk z AED, bez stałej lokalizacji. Pozycja na żywo: `ckan2.multimediagdansk.pl/gpsPositions?v=2`, łączenie po `vehicleCode` |
| `wynik/statystyki.json` | Liczby rekordów, duplikatów i wypełnienia pól |
| `surowe/` | Surowe pliki ze źródeł, bez zmian |
| `skrypty/pobierz.sh` → `skrypty/wykazy.py` → `skrypty/agreguj.py` | Kolejność odświeżania danych (tylko biblioteka standardowa Pythona) |

## Schemat

Nazwy pól są podzbiorem wzorcowego zakresu danych (branch `wojtek`, `zakres-danych/zakres-pol.csv`). Dodatkowe pola:
- `id_agregatu` = `<zrodlo>:<id_zrodlowe>`
- `licencja_zrodla`
- `duplikat_z`, `odleglosc_duplikatu_m`
- `dzielnica`

Słowniki są uproszczone:
- `dostepnosc`: publiczny / klienci / pracownicy / prywatny / ograniczony
- `dostepny_24_7`: tak / nie / ograniczony
- `wewnatrz_budynku`: true / false

Gdy wartości nie da się przypisać do słownika, pole zawiera surową wartość ze źródła.

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

Wypełnienie pól w `aed_unikalne` (na 18 858): opis_lokalizacji 17 363, dostepnosc 17 291, wewnatrz_budynku 16 417, dostepny_24_7 7 171, data_weryfikacji 6 344, dysponent_nazwa 6 026, telefon 4 626, kondygnacja 4 057, zdjecie_url 2 171, nazwa_obiektu 1 364, producent 702, adres (ulica) 636. Pełne liczby: `wynik/statystyki.json`.

## Czego tu nie ma (brak danych do pobrania)

- Pierwszy Ratownik (ok. 8 500–10 000 AED) i Fundacja Ratuj Życie (ratujzsercem.pl): bazy zamknięte.
- Kraków „IMPULS ŻYCIA” (krakow.pl): lista w HTML z paginacją. Jest częściowo pokryta przez `krakow_arcgis*`.
- Gliwice MSIP i GAMA: nie znaleźliśmy endpointu warstwy, użyliśmy tabeli HTML.
- Toruń (2016) i Siedlce (2017): wykazy nieaktualne, pominięte.
- AED w pojazdach poza Gdańskiem (Wrocław, Kraków, Rzeszów): brak list numerów taborowych.
