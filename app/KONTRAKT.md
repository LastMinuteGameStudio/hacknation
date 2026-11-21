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
  wiersz: number | null;    // numer wiersza w pliku dostawcy (1 = pierwszy wiersz danych), null = cały plik
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
- `kolumna` w mapowaniu to dokładna nazwa kolumny z pliku. Specjalne wartości mapowania (nie są polami v0.5): `_geometria` dla kolumny z geometrią (JSON lub WKT, rozbijana na szerokość i długość) oraz `_adres_pelny` dla adresu w jednym polu (rozbijany na ulicę, numer, kod pocztowy i miejscowość).
- `pole: null` znaczy „nie importuj”.
- `pewnosc` mieści się w przedziale 0–1.

### POST `/api/importy/{import_id}/walidacja`
Body:
```json
{"mapowanie": {"Długość geograficzna": "dlugosc_geograficzna", "Numer Id": null},
 "dysponent": {"nazwa": "Urząd Miasta Krosna", "typ": "jst", "telefon": null, "email": null}}
```
Tutaj następuje normalizacja, geokodowanie (GUGiK) i walidacja. Odpowiedź `WalidacjaOut`:
```json
{
  "liczba_rekordow": 21, "liczba_bledow": 0, "liczba_ostrzezen": 5,
  "komunikaty": [{"poziom": "ostrzezenie", "kod": "DOMYSLNY_STATUS", "komunikat": "...", "wiersz": null, "pole": "status"}],
  "podglad_wyniku": [{"id_aed": "...", "szerokosc_geograficzna": "49.718809", "...": "..."}],
  "mozna_publikowac": true
}
```
`podglad_wyniku` zawiera maks. 20 rekordów i tylko pola publiczne, jako tekst sformatowany jak w CSV. `mozna_publikowac` jest `false`, gdy jest choć jeden błąd.

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

### Pliki publiczne
| GET | Zawartość |
|---|---|
| `/d/{slug}.csv` | pola publiczne v0.5 w kolejności z zakresu; RFC 4180: UTF-8 bez BOM, przecinek, CRLF, cudzysłowy tylko gdy potrzebne; daty ISO 8601; kropka dziesiętna; `Content-Type: text/csv; charset=utf-8` |
| `/d/{slug}.json` | `{"metadane": {...}, "rekordy": [ {pole: wartość} ]}` |
| `/d/{slug}.csv-metadata.json` | CSVW (wzór: `zakres-danych/szablon-aed-publiczny.csv-metadata.json`), `url` wskazuje na CSV |
| `/d/aed-polska.csv` | agregat: `dane/wynik/aed_unikalne.csv` (z OSM) + zbiory z bazy; kolumny pochodzenia przy każdym rekordzie |
| `/d/aed-polska-bez-osm.csv` | jak wyżej, bez rekordów z OSM |
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
                          provider: Provider, today: date, geocoder: Geocoder | None) -> list[RecordResult]
validate.validate_records(records: list[RecordResult], schema: Schema) -> list[Message]
export.to_csv(records: list[dict[str, str]], schema: Schema, public_only: bool = True) -> bytes
export.to_json(records, schema, metadata: dict) -> bytes
export.csvw_metadata(schema: Schema, csv_url: str, title: str) -> dict
geocode.GugikGeocoder(cache: GeocodeCache).geocode(query: AddressQuery) -> GeoResult | None
```
- Rekord to `dict[str, str]`: pole v0.5 → wartość już sformatowana jak w CSV (pusty string = brak).
- `normalize_table` uzupełnia pola stałe: `dysponent_*` z `Provider`, `zrodlo_danych`, `data_aktualizacji`; wartości domyślne (`id_aed`, `status = nieznany`, `data_weryfikacji = today`) razem z ostrzeżeniami.
- `validate_records` sprawdza wymagalność O/Z, formaty, słowniki, współrzędne w Polsce i duplikaty.

## 4. Kody komunikatów

| Kod | Poziom | Kiedy |
|---|---|---|
| `NIEOBSLUGIWANY_FORMAT` | błąd (HTTP 415) | plik inny niż CSV i XLSX |
| `ZA_DUZY_PLIK` / `ZA_DUZO_WIERSZY` | błąd (HTTP 413) | powyżej 10 MB lub 20 000 wierszy |
| `PUSTY_PLIK` | błąd | brak wierszy danych |
| `BRAK_POLA_OBOWIAZKOWEGO` | błąd | puste pole O |
| `BRAK_POLA_ZALECANEGO` | ostrzeżenie | puste pole Z (jeden komunikat na pole z liczbą wierszy) |
| `ZLY_FORMAT` | błąd (pole O) / ostrzeżenie (Z, F) | wartość niezgodna z formatem |
| `WARTOSC_SPOZA_SLOWNIKA` | błąd (O) / ostrzeżenie | nieznany kod słownika |
| `POZA_POLSKA` | błąd | współrzędne poza Polską |
| `ZAMIENIONE_WSPOLRZEDNE` | ostrzeżenie | wykryto zamianę szerokości z długością, poprawiono |
| `DUPLIKAT_ID` / `DUPLIKAT_NR_SERYJNEGO` | błąd | powtórzone w pliku |
| `BLISKIE_PUNKTY` | ostrzeżenie | dwa AED bliżej niż 5 m |
| `GEOKODOWANIE_OK` | info | współrzędne ustalone z adresu (dokładność: adres budynku) |
| `GEOKODOWANIE_NIEJEDNOZNACZNE` / `GEOKODOWANIE_BRAK` | ostrzeżenie / błąd | adres niejednoznaczny / nie znaleziono |
| `ZA_DUZO_DO_GEOKODOWANIA` | ostrzeżenie | ponad 200 adresów bez współrzędnych |
| `WYGENEROWANO_ID` | ostrzeżenie | brak `id_aed`, nadano automatycznie |
| `DOMYSLNY_STATUS` | ostrzeżenie | brak `status`, ustawiono `nieznany` |
| `DOMYSLNA_DATA_WERYFIKACJI` | ostrzeżenie | brak `data_weryfikacji`, ustawiono datę wgrania |
| `ROZBITO_ADRES` / `NIE_ROZBITO_ADRESU` | info / ostrzeżenie | adres z jednego pola rozbity na części / nieudane |
| `NIEZROZUMIALE_GODZINY` | ostrzeżenie | godziny w wolnym tekście, przeniesione do `uwagi` |
| `SA_BLEDY` | HTTP 409 | publikacja przy błędach |
| `ZLY_TOKEN` | HTTP 403 | zły token edycji |
| `NIE_ZNALEZIONO` | HTTP 404 | brak importu lub zbioru |

## 5. Decyzje, które implementuje kontrakt
Licencja zbioru: stała CC0 1.0. Ponowne wgranie przez prywatny link pod ten sam URL. Geokoder GUGiK UUG (Nominatim jako zapas). Limity: 10 MB i 20 000 wierszy. Agregat w dwóch plikach (z OSM i bez OSM) z kolumnami pochodzenia. Źródło: `zadania/06-mc-misja-aed/NOTATKI-ZESPOLU.md`.
