# Dowód: plik pod stałym URL pobierany tak jak przez dane.gov.pl

Wygenerowane przez `prezentacja/zrzuty/sprawdz_url.py` (2026-11-22 06:21 UTC). Zbiór demo z dysponentem „Urząd Miejski w Przemyślu (demo)”, opublikowany przez `zrob_zrzuty.py` z pliku `przemysl_2024.csv`.

## Zapytanie

```
curl -sS -D - -A 'Mozilla/5.0 (compatible; harvester-test)' 'https://tuaed.wkrynski.dev/d/kznsks42.csv'
```

Bez ciasteczek, bez logowania i bez tokenu, tak jak harvester portalu przy „Aktualizacji automatycznej”.

## Nagłówki odpowiedzi

```
HTTP 200
content-type: text/csv; charset=utf-8
content-disposition: inline; filename="aed-kznsks42.csv"
access-control-allow-origin: *
cache-control: max-age=14400
last-modified: Sun, 22 Nov 2026 06:21:55 GMT
```

## Pierwsze wiersze (surowo, `\r\n` na końcu linii)

```csv
id_aed,id_zrodlowe,osm_id,szerokosc_geograficzna,dlugosc_geograficzna,dokladnosc_polozenia,nazwa_obiektu,cecha_ulicy,nazwa_ulicy,nr_budynku,nr_lokalu,kod_pocztowy,miejscowosc,kod_terc,kod_simc,kod_ulic,adres_uniwersalny,wewnatrz_budynku,kondygnacja,opis_lokalizacji,zdjecie_url,zdjecie_licencja,dostepnosc,dostepny_24_7,godziny_pn,godziny_wt,godziny_sr,godziny_cz,godziny_pt,godziny_so,godziny_nd,godziny_swieta,zabezpieczenie,instrukcja_dostepu,dostepnosc_wozek,tryb_pediatryczny,status,data_weryfikacji,data_instalacji,data_przegladu,data_waznosci_elektrod_doroslych,data_waznosci_elektrod_pediatrycznych,data_waznosci_baterii,przeglad_co_miesiecy,dysponent_nazwa,dysponent_typ,dysponent_regon,zrodlo_danych,data_aktualizacji,status_walidacji,duplikat_id_aed,uwagi
kznsks42-9c48a7,744,,49.7812096,22.7750936,,Defibrylator (AED 9485) w ADM Centrum,,Juliusza Słowackiego,12,,37-700,Przemyśl,,,,,false,,,,,publiczny,tak,X,X,X,X,X,X,X,X,,,,,nieznany,2026-11-22,,,,,,,Urząd Miejski w Przemyślu (demo),jst,,dysponent,2026-11-22T00:24:38,,,
kznsks42-5afe42,745,,49.7806393,22.7771083,,Defibrylator (AED 9556) w I Liecum Ogólnokształcącym w Przemyślu,,Juliusza Słowackiego,21,,37-700,Przemyśl,,,,,false,,,,,publiczny,tak,X,X,X,X,X,X,X,X,,,,,nieznany,2026-11-22,,,,,,,Urząd Miejski w Przemyślu (demo),jst,,dysponent,2026-11-22T00:24:38,,,
kznsks42-ceb227,746,,49.7972693,22.7582092,,Defibrylator (AED 9579) w Szkole Podstawowej Nr 6 w Przemyślu,,Generała Mieczysława Boruty Spiechowicza,1,,37-700,Przemyśl,,,,,false,,,,,publiczny,tak,X,X,X,X,X,X,X,X,,,,,nieznany,2026-11-22,,,,,,,Urząd Miejski w Przemyślu (demo),jst,,dysponent,2026-11-22T00:24:38,,,
```

## Walidacja: 21/21

| | Sprawdzenie |
|---|---|
| ✅ | HTTP 200 bez ciasteczek i logowania |
| ✅ | serwer nie ustawia ciasteczek |
| ✅ | Content-Type: text/csv; charset=utf-8 |
| ✅ | CORS `*` (pobranie z przeglądarki, np. mapa w JS) |
| ✅ | Content-Disposition: inline; filename="aed-kznsks42.csv" |
| ✅ | poprawne UTF-8 (dekodowanie ścisłe) |
| ✅ | bez BOM |
| ✅ | ostatni wiersz zakończony CRLF |
| ✅ | separator wierszy wyłącznie CRLF (poza polami w cudzysłowie) |
| ✅ | 21 rekordów, każdy ma 52 pól jak nagłówek |
| ✅ | cudzysłowy tylko tam, gdzie trzeba, `"` podwojone (identyczny zapis RFC 4180) |
| ✅ | nazwy kolumn unikalne |
| ✅ | metadane CSVW pod `https://tuaed.wkrynski.dev/d/kznsks42.csv-metadata.json` (HTTP 200) |
| ✅ | `url` w metadanych wskazuje ten plik |
| ✅ | dialekt: UTF-8, przecinek, wiersz nagłówka |
| ✅ | kolumny w metadanych = nagłówek pliku (52, ta sama kolejność) |
| ✅ | nagłówek zgodny z `titles` (CSVW §5.5.1, sprawdza to np. csvlint) |
| ✅ | pola `required` wypełnione |
| ✅ | wartości zgodne z `datatype`/`format` |
| ✅ | `primaryKey` (id_aed) unikalny |
| ✅ | licencja w metadanych: https://creativecommons.org/publicdomain/zero/1.0/ |

Sprawdzenia RFC 4180: kodowanie, CRLF, stała liczba pól, cytowanie (zapis porównany bajt po bajcie z `csv.writer(QUOTE_MINIMAL)`). CSVW: metadane z `/d/{slug}.csv-metadata.json` (W3C Tabular Data), wartości `X` i puste traktowane jako brak, zgodnie z `tableSchema.null`.
