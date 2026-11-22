# Kontrakt API i interfejs rdzenia: 06 Misja AED

**Jedno źródło prawdy dla ścieżek A (rdzeń), B (API), C (front) i D (testy).** Zmiana kontraktu wymaga uzgodnienia na tablicy i jednoczesnej poprawki w:
- `backend/app/api_models.py` (Pydantic),
- `frontend/src/api/types.ts` (TypeScript),
- tym pliku.

Wszystkie teksty dla użytkownika są po polsku. Nazwy pól danych są takie jak w zakresie v0.5 (`zakres-danych/zakres-pol.csv`).

## 1. Typy wspólne

```ts
type Poziom = "blad" | "ostrzezenie" | "info";

interface Komunikat {
  poziom: Poziom;
  kod: KodKomunikatu;       // lista w sekcji 4
  komunikat: string;        // po polsku, zrozumiały dla urzędnika
  wiersz: number | null;    // numer wiersza tak, jak widzi go dostawca w arkuszu (nagłówek w wierszu 1 → pierwszy wiersz danych = 2), null = cały plik
  pole: string | null;      // nazwa pola v0.5 albo null
}

interface Dysponent {
  nazwa: string;                     // → dysponent_nazwa (O)
  typ: string;                       // kod ze słownika dysponent_typ
  telefon?: string | null;           // → telefon_kontaktowy (niepubliczne)
  email?: string | null;             // → email_kontaktowy (niepubliczne)
}
```

## 2. Endpointy

Bazowy URL publicznych linków pochodzi ze zmiennej `BASE_URL` (np. `http://localhost:8000`). Błędy HTTP mają postać `{"detail": {"kod": "...", "komunikat": "..."}}`.

### GET `/api/schemat`
```json
{
  "wersja": "0.5",
  "pola": [{"pole": "szerokosc_geograficzna", "nazwa": "Szerokość geograficzna", "grupa": "Lokalizacja",
            "typ": "liczba dziesiętna", "format": "WGS84 ...", "wymagalnosc": "O", "publiczne": true,
            "opis": "...", "przyklad": "52.395198", "slownik": null}],
  "slowniki": {"dostepnosc": [{"kod": "publiczny", "znaczenie": "Dostępny dla każdego ..."}]}
}
```
`wymagalnosc`: `O` = obowiązkowe (brak = błąd), `Z` = zalecane (brak = ostrzeżenie), `F` = fakultatywne. `slownik` to nazwa słownika, gdy typ pola to „słownik”.

### POST `/api/importy`  (multipart: `plik`, opcjonalnie `arkusz`)
Przyjmuje CSV i XLSX, do 10 MB i 20 000 wierszy. Odpowiedź `ImportOut`:
```json
{
  "import_id": "uuid",
  "plik_nazwa": "aed.csv",
  "liczba_wierszy": 21,
  "arkusze": ["Arkusz1"],
  "kolumny": [{"indeks": 0, "nazwa": "Długość geograficzna", "przyklady": ["21.72", "21.71", "21.71"]}],
  "podglad": [["21.72", "49.71", "Defibrylator", "..."]],
  "mapowanie_propozycja": [{"kolumna": "Długość geograficzna", "pole": "dlugosc_geograficzna", "pewnosc": 0.95, "powod": "nazwa kolumny"}],
  "komunikaty": []
}
```
- `podglad`: maks. 10 pierwszych wierszy, wartości jako tekst.
- `kolumna` w mapowaniu to dokładna nazwa kolumny z pliku. Specjalne wartości mapowania (nie są polami v0.5): `_geometria` dla kolumny z geometrią (JSON lub WKT, rozbijana na szerokość i długość) `_adres_pelny` dla adresu w jednym polu (rozbijany na ulicę, numer, kod pocztowy i miejscowość) oraz `_godziny` dla godzin w jednym polu (OSM `opening_hours`, „pn-pt 8-16”, „24h”; rozbijane na `dostepny_24_7` i `godziny_pn`…`godziny_swieta`).
- Kolumny o powtórzonej nazwie dostają dopisek ` (2)`, ` (3)`, a puste nagłówki nazwę `Kolumna N` (N = numer kolumny od 1). Wiersz nagłówka jest wykrywany automatycznie (pomijane są wiersze tytułowe nad tabelą).
- Jedno pole v0.5 może mieć przypisaną najwyżej jedną kolumnę (front blokuje drugi wybór).
- `pole: null` znaczy „nie importuj”.
- `pewnosc` mieści się w przedziale 0–1.

### POST `/api/importy/{import_id}/walidacja`
Body:
```json
{"mapowanie": {"Długość geograficzna": "dlugosc_geograficzna", "Numer Id": null},
 "dysponent": {"nazwa": "Urząd Miasta Krosna", "typ": "jst", "telefon": null, "email": null},
 "wartosci_stale": {"wewnatrz_budynku": "true", "dostepnosc": "publiczny", "dostepny_24_7": "nie"}}
```
`wartosci_stale` (opcjonalne, domyślnie `{}`): wartość pola v0.5 ustawiona dla wszystkich AED w pliku. Front pokazuje ją dla pól O bez zmapowanej kolumny (co najmniej `wewnatrz_budynku`, `dostepnosc`, `dostepny_24_7`), z listą ze słownika. Wartość stała nie nadpisuje niepustej wartości z kolumny. Dopóki pole O nie ma ani kolumny, ani wartości stałej, walidacja zwraca `BRAK_POLA_OBOWIAZKOWEGO` (jeden komunikat na pole, `wiersz: null`).

Tutaj następuje normalizacja, geokodowanie (GUGiK) i walidacja. Odpowiedź `WalidacjaOut`:
```json
{
  "liczba_rekordow": 21, "liczba_pominietych": 0, "liczba_bledow": 0, "liczba_ostrzezen": 5,
  "komunikaty": [{"poziom": "ostrzezenie", "kod": "DOMYSLNY_STATUS", "komunikat": "...", "wiersz": null, "pole": "status"}],
  "podglad_wyniku": [{"id_aed": "...", "szerokosc_geograficzna": "49.718809", "...": "..."}],
  "mozna_publikowac": true
}
```
`podglad_wyniku` zawiera maks. 20 rekordów i tylko pola publiczne, jako tekst sformatowany jak w CSV. `mozna_publikowac` jest `false`, gdy jest choć jeden błąd. `liczba_pominietych` to rekordy, które nie trafią do publikacji (adres nieznaleziony przez geokoder albo ponad limit 200 geokodowań); `liczba_rekordow` ich nie obejmuje.

Ten sam kod dotyczący wielu wierszy: gdy dotyczy więcej niż 20 wierszy, zamiast osobnych komunikatów jest jeden z `wiersz: null` i listą pierwszych numerów wierszy w treści („…w 57 wierszach, m.in. 2, 5, 9”).

### POST `/api/importy/{import_id}/publikacja`
Wymaga wcześniejszej walidacji bez błędów, inaczej zwraca 409 `{"kod": "SA_BLEDY"}`. Odpowiedź `PublikacjaOut`:
```json
{"slug": "k7q2m9xa", "token_edycji": "długi-losowy-token",
 "url_csv": "{BASE_URL}/d/k7q2m9xa.csv", "url_json": "{BASE_URL}/d/k7q2m9xa.json",
 "url_metadane": "{BASE_URL}/d/k7q2m9xa.csv-metadata.json",
 "url_edycji": "{BASE_URL}/edycja/k7q2m9xa?token=..."}
```
Token pokazujemy tylko raz. W bazie trzymamy wyłącznie jego hash.

### Edycja przez prywatny link (ten sam slug i URL)
- GET `/api/zbiory/{slug}?token=…` → `{"slug", "dysponent": Dysponent, "utworzono", "zaktualizowano", "liczba_rekordow", "mapowanie"}`. Zły token zwraca 403 `{"kod": "ZLY_TOKEN"}`.
- POST `/api/zbiory/{slug}/importy?token=…` (multipart jak wyżej) → `ImportOut`. Import jest powiązany ze zbiorem, a propozycja mapowania uwzględnia mapowanie z poprzedniej wersji.
- Dalej `walidacja` i `publikacja` bez zmian. Publikacja importu powiązanego ze zbiorem **zastępuje rekordy pod tym samym slugiem** i zwraca te same URL (bez nowego tokenu: `token_edycji = null`).

### Synchronizacja z URL źródła (S1)
Zbiór może być odświeżany z pliku pod stałym adresem (np. CSV na stronie urzędu). Wszystkie wywołania z `?token=…` jak w edycji.
- GET `/api/zbiory/{slug}/zrodlo` → `SynchronizacjaOut`.
- PUT `/api/zbiory/{slug}/zrodlo`, body `{"url": "https://…" | null, "co_ile_godzin": 24}` (1–720) → `SynchronizacjaOut`. Od razu synchronizuje. `url: null` wyłącza. Zły adres (nie http(s), sieć prywatna) → 422 `ZLY_URL`.
- POST `/api/zbiory/{slug}/synchronizacja[?wymus=true]` → `SynchronizacjaOut`. Synchronizuj teraz; `wymus` pomija kontrolę `ZA_DUZA_ZMIANA` i porównanie skrótu pliku. Brak źródła → 404.
```json
{"url": "https://…/aed.csv", "co_ile_godzin": 24, "status": "aktywna",
 "komunikaty": [{"poziom": "info", "kod": "ZSYNCHRONIZOWANO", "komunikat": "Opublikowano 21 AED z pliku źródła.", "wiersz": null, "pole": null}],
 "ostatnia_proba": "2026-11-22T10:00:00+00:00", "ostatni_sukces": "2026-11-22T10:00:00+00:00", "liczba_rekordow": 21}
```
`status`: `brak` (nie ustawiono), `aktywna`, `wstrzymana` (dane nie zostały podmienione, potrzebna decyzja dostawcy), `blad` (nie udało się pobrać lub odczytać; harmonogram ponowi). Każde odświeżenie to import powiązany ze zbiorem → walidacja z zapamiętanym mapowaniem, dysponentem i wartościami stałymi → publikacja pod tym samym slugiem. Harmonogram w aplikacji sprawdza zaległe zbiory co 5 minut. Wznowienie po wstrzymaniu: PUT z adresem albo POST z `wymus=true` (dla `ZA_DUZA_ZMIANA`), albo zwykłe wgranie przez link edycji z nowym mapowaniem.

### Pliki publiczne
| GET | Zawartość |
|---|---|
| `/d/{slug}.csv` | pola publiczne v0.5 w kolejności z zakresu; RFC 4180: UTF-8 bez BOM, przecinek, CRLF, cudzysłowy tylko gdy potrzebne; daty ISO 8601; kropka dziesiętna; `Content-Type: text/csv; charset=utf-8` |
| `/d/{slug}.json` | `{"metadane": {...}, "rekordy": [ {pole: wartość} ]}` |
| `/d/{slug}.geojson` | S2: `AedFeatureCollection` (RFC 7946) z polami publicznymi w `properties`, plus `metadane` jak w `.json` (foreign member) |
| `/d/{slug}.csv-metadata.json` | CSVW (wzór: `zakres-danych/szablon-aed-publiczny.csv-metadata.json`), `url` wskazuje na CSV |
| `/d/aed-polska.csv` | agregat: `dane/wynik/aed_unikalne.csv` (z OSM) + zbiory z bazy; kolumny pochodzenia przy każdym rekordzie |
| `/d/aed-polska-bez-osm.csv` | jak wyżej, bez rekordów z OSM (`zrodlo == "osm"` w `dane/wynik`) |
| `/d/aed-polska.geojson`, `/d/aed-polska-bez-osm.geojson` | S2: te same rekordy co w CSV agregatu (ta sama kolejność i liczba), `AedFeatureCollection` z kolumnami agregatu w `properties` |

Agregat: kolumny to pola publiczne v0.5 + `zrodlo` i `licencja_zrodla` (dla zbiorów z bazy: `zrodlo = "tuaed:<slug>"`, `licencja_zrodla = "CC0 1.0"`, `status_walidacji = "oczekuje"`, bo dostawców nie weryfikujemy; Wojtek, 22.11). Rekord dostawcy jest główny: rekord z `dane/wynik` bliżej niż 30 m od rekordu dostawcy dostaje `duplikat_id_aed` = jego `id_aed` (nic nie jest usuwane). W agregacie `id_aed` rekordów z bazy ma prefiks `<slug>:`, żeby identyfikatory różnych dostawców się nie zderzały.

GeoJSON (S2): `Content-Type: application/geo+json`, `Access-Control-Allow-Origin: *`, kompresja gzip (agregat z OSM: ok. 11 MB, po kompresji ok. 1,3 MB). Każdy rekord to `{"type": "Feature", "id": id_aed, "geometry": {"type": "Point", "coordinates": [lon, lat]}, "properties": {pole: wartość}}`. Współrzędne są liczbami w kolejności [długość, szerokość]. W `properties` są tylko pola z wartością: puste i „X” są pomijane (konwencja `dane/wynik/*.geojson`), wartości są tekstem jak w CSV. Rekord bez współrzędnych ma `geometry: null`. Plik agregatu jest w pamięci i odświeża się po każdej publikacji i synchronizacji.
| `/szablon.csv`, `/szablon.xlsx` | `zakres-danych/szablon-aed-publiczny.*` |

### GET `/api/zdrowie`
`{"status": "ok", "baza": true, "wersja_zakresu": "0.5"}`

## 3. Interfejs rdzenia `aed_core` (A ↔ B)

Czyste funkcje bez dostępu do bazy. Typy są w `backend/aed_core/types.py`.

```python
schema.load_schema(zakres_dir: Path) -> Schema
parsers.read_table(content: bytes, filename: str, sheet: str | None = None) -> Table
mapping.suggest_mapping(table: Table, schema: Schema, previous: dict[str, str | None] | None = None) -> list[MappingSuggestion]
normalize.normalize_table(table: Table, mapping: dict[str, str | None], schema: Schema,
                          provider: Provider, today: date, geocoder: Geocoder | None,
                          fixed: dict[str, str] | None = None) -> list[RecordResult]
validate.validate_records(records: list[RecordResult], schema: Schema) -> list[Message]
export.to_csv(records: list[dict[str, str]], schema: Schema, public_only: bool = True) -> bytes
export.to_json(records, schema, metadata: dict) -> bytes
export.csvw_metadata(schema: Schema, csv_url: str, title: str) -> dict
geocode.GugikGeocoder(cache: GeocodeCache).geocode(query: AddressQuery) -> GeoResult | None
```
- `read_table` przy błędzie blokującym cały plik rzuca `parsers.BladPliku(kod, komunikat, status)`: `NIEOBSLUGIWANY_FORMAT` (415), `ZA_DUZY_PLIK` / `ZA_DUZO_WIERSZY` (413), `PUSTY_PLIK` (422), `NIE_ZNALEZIONO` (404, brak podanego arkusza). API zamienia go na HTTP `status` z `detail = {kod, komunikat}`. Poza CSV i XLSX czyta też GeoJSON FeatureCollection (`.geojson`/`.json`: kolumny z `properties` + `geometry` jako JSON). Puste wiersze i stopki („Sporządził: …”) są pomijane; numer wiersza `rows[i]` w arkuszu daje `Table.numer_wiersza(i)` (`Table.row_numbers`). XLSX: scalone komórki dziedziczą wartość, nagłówek dwupoziomowy jest składany, bez podanego arkusza wybieramy arkusz z największą liczbą wierszy danych.
- Rekord to `dict[str, str]`: pole v0.5 → wartość już sformatowana jak w CSV (pusty string = brak).
- `normalize_table` uzupełnia pola stałe: `dysponent_*` z `Provider`, `zrodlo_danych`, `data_aktualizacji`, `wartosci_stale` z `fixed`; wartości domyślne (`id_aed`, `status = nieznany`, `data_weryfikacji = today`) razem z ostrzeżeniami. Rekord z adresem nieznalezionym przez geokoder ma `pominiety = True`.
- Wygenerowany `id_aed` jest stabilny przy ponownym wgraniu: `<kod_terc lub slug>-<6 znaków hex>` (slug jest rezerwowany już przy `POST /api/importy`, a publikacja go aktywuje; Wojtek, 22.11), gdzie hex to skrót SHA-1 z numeru seryjnego, a gdy go brak, ze współrzędnych zaokrąglonych do 4 miejsc i znormalizowanej `nazwa_obiektu`. Kolizja w pliku → dopisek `-2`, `-3`.
- Komunikaty o wartościach domyślnych (`DOMYSLNY_STATUS`, `DOMYSLNA_DATA_WERYFIKACJI`, `WYGENEROWANO_ID`): gdy pole nie ma kolumny ani wartości stałej, jeden komunikat na plik (`wiersz: null`, w `messages` pierwszego rekordu); gdy kolumna jest, a komórka pusta, komunikat per wiersz. `ZA_DUZO_DO_GEOKODOWANIA` też w pierwszym rekordzie. Identyczne adresy geokodujemy raz (limit 200 liczy adresy unikalne). Puste wiersze `Table.rows` nie dają rekordu.
- Brak ulicy przy niepustej miejscowości: `nazwa_ulicy` = miejscowość (zasada z zakresu v0.5) + info `ULICA_Z_MIEJSCOWOSCI`.
- Wartości słownikowe są normalizowane synonimami (np. „czynny”, „sprawny” → `sprawny`; „ogólnodostępny”, „tak” w kolumnie dostępności → `publiczny`; „całodobowo”, „24h”, „24/7” → `dostepny_24_7 = tak`). Przy `dostepny_24_7 = tak` pola godzin dostają `X` (zakres v0.5). `wewnatrz_budynku` to `true`/`false`.
- Współrzędne zapisujemy z precyzją z pliku (bez dopisywania zer); poniżej 5 miejsc po przecinku ostrzeżenie `NISKA_PRECYZJA` (liczy się dokładniejsza z dwóch współrzędnych, bo np. „49.7851” obok „22.772605” to zwykle obcięte zera). `validate_records` pomija rekordy `pominiety`. Braki w polach `godziny_*` dają jedno `BRAK_POLA_ZALECANEGO` z `pole: godziny_pn`. Geokodowanie: niejednoznaczne trafienia (np. „Krosno, Jasna” bez numeru) są ponawiane z kodem TERC gminy dominującej wśród pewnych trafień w pliku; adres bez numeru budynku lub nieznaleziony numer → `dokladnosc_polozenia = przyblizone`.
- Geokodowanie: synchronicznie w `/walidacja`, do 8 zapytań do GUGiK równolegle, z cache, **najwyżej 200 adresów na plik** (limit tunelu Cloudflare ok. 100 s na żądanie). Rekordy ponad limit mają `pominiety = True` (Wojtek, 22.11).
- `validate_records` sprawdza wymagalność O/Z, formaty, słowniki, współrzędne w Polsce i duplikaty.

## 4. Kody komunikatów

| Kod | Poziom | Kiedy |
|---|---|---|
| `NIEOBSLUGIWANY_FORMAT` | błąd (HTTP 415) | plik inny niż CSV i XLSX |
| `ZA_DUZY_PLIK` / `ZA_DUZO_WIERSZY` | błąd (HTTP 413) | powyżej 10 MB lub 20 000 wierszy |
| `PUSTY_PLIK` | błąd | brak wierszy danych |
| `ROZBITO_WIERSZE` | ostrzeżenie | cały wiersz był w jednej komórce (np. Marki), rozdzielono na kolumny |
| `POMINIETO_WIERSZE_TYTULOWE` | info | nagłówek tabeli nie w wierszu 1, wiersze nad nim pominięto |
| `NAGLOWEK_DWUPOZIOMOWY` | info | nagłówek w dwóch wierszach (grupy scalone w poziomie), nazwy kolumn z niższego wiersza |
| `BRAK_POLA_OBOWIAZKOWEGO` | błąd | puste pole O (gdy pole nie ma kolumny ani wartości stałej: jeden komunikat na pole) |
| `BRAK_POLA_ZALECANEGO` | ostrzeżenie | puste pole Z (jeden komunikat na pole z liczbą wierszy) |
| `ZLY_FORMAT` | błąd (pole O) / ostrzeżenie (Z, F) | wartość niezgodna z formatem |
| `WARTOSC_SPOZA_SLOWNIKA` | błąd (O) / ostrzeżenie | nieznany kod słownika |
| `POZA_POLSKA` | błąd | współrzędne poza Polską |
| `NISKA_PRECYZJA` | ostrzeżenie | współrzędne z mniej niż 5 miejscami po przecinku (zapisane bez zmian) |
| `ZAMIENIONE_WSPOLRZEDNE` | ostrzeżenie | wykryto zamianę szerokości z długością, poprawiono |
| `DUPLIKAT_ID` / `DUPLIKAT_NR_SERYJNEGO` | błąd | powtórzone w pliku |
| `BLISKIE_PUNKTY` | ostrzeżenie | dwa AED bliżej niż 5 m |
| `GEOKODOWANIE_OK` | info | współrzędne ustalone z adresu (dokładność: adres budynku) |
| `GEOKODOWANIE_NIEJEDNOZNACZNE` | ostrzeżenie | adres niejednoznaczny, wybrano najlepsze trafienie |
| `GEOKODOWANIE_BRAK` | ostrzeżenie | adresu nie znaleziono: **rekord pominięty** w publikacji (nie blokuje pliku) |
| `ZA_DUZO_DO_GEOKODOWANIA` | ostrzeżenie | ponad 200 adresów bez współrzędnych: geokodujemy pierwsze 200, resztę pomijamy w publikacji (jeden komunikat z liczbą pominiętych) |
| `WYGENEROWANO_ID` | ostrzeżenie | brak `id_aed`, nadano automatycznie (stały przy ponownym wgraniu tego samego AED) |
| `ULICA_Z_MIEJSCOWOSCI` | info | brak ulicy, w `nazwa_ulicy` wpisano miejscowość |
| `DOMYSLNY_STATUS` | ostrzeżenie | brak `status`, ustawiono `nieznany` |
| `DOMYSLNA_DATA_WERYFIKACJI` | ostrzeżenie | brak `data_weryfikacji`, ustawiono datę wgrania |
| `ROZBITO_ADRES` / `NIE_ROZBITO_ADRESU` | info / ostrzeżenie | adres z jednego pola rozbity na części / nieudane |
| `NIEZROZUMIALE_GODZINY` | ostrzeżenie | godziny w wolnym tekście, przeniesione do `uwagi` (gdy `dostepny_24_7` puste, ustawiamy `nie`) |
| `WEWNATRZ_Z_OPISU` | info | `wewnatrz_budynku` ustalone z opisu lokalizacji zaczynającego się od „wewnątrz” / „na zewnątrz” |
| `SA_BLEDY` | HTTP 409 | publikacja przy błędach |
| `ZLY_TOKEN` | HTTP 403 | zły token edycji |
| `NIE_ZNALEZIONO` | HTTP 404 | brak importu lub zbioru |
| `ZLY_URL` | HTTP 422 | S1: adres źródła nie jest publicznym http(s) |
| `ZSYNCHRONIZOWANO` / `BEZ_ZMIAN` | info | S1: opublikowano nową wersję / plik źródła się nie zmienił |
| `BLAD_POBIERANIA` | błąd | S1: serwer źródła nie odpowiedział, kod inny niż 200, plik > 10 MB |
| `ZMIANA_STRUKTURY` | błąd | S1: zniknęła zmapowana kolumna albo pojawiła się nowa; synchronizacja wstrzymana |
| `ZA_DUZA_ZMIANA` | ostrzeżenie | S1: zmieniło się > 50% `id_aed` albo rekordów jest o ponad połowę mniej; wstrzymana do potwierdzenia |

## 5. Decyzje, które implementuje kontrakt
Licencja zbioru: stała CC0 1.0. Ponowne wgranie przez prywatny link pod ten sam URL. Geokoder GUGiK UUG (Nominatim jako zapas). Limity: 10 MB i 20 000 wierszy. Agregat w dwóch plikach (z OSM i bez OSM) z kolumnami pochodzenia. Doprecyzowanie backendu (Grzan, 22.11): wartości stałe dla pól O bez kolumny, pola `_adres_pelny` i `_godziny`, rekord z nieznalezionym adresem pomijany, precyzja współrzędnych bez dopisywania zer, stabilny `id_aed` z treści rekordu, w agregacie rekord dostawcy jest główny. Źródło: `zadania/06-mc-misja-aed/NOTATKI-ZESPOLU.md`.
