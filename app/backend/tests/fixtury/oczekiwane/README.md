# Oczekiwane wyniki dla fixtur (ścieżka D)

Jeden plik JSON na fixturę. Używają go `tests/raport_mapowania.py` (D2) i `tests/test_realne_*.py`.

## Format

```jsonc
{
  "plik": "krosno.csv",            // nazwa w tests/fixtury/
  "arkusz": null,                  // arkusz XLSX albo null
  "wymaga_100": true,              // true = mapowanie musi być w 100% trafne bez poprawek (decyzja zespołu)
  "dostawca": {"nazwa": "...", "typ": "jst"},
  "wartosci_stale": {...},         // wartosci_stale dla pól O bez kolumny (krok 2 kreatora)
  "liczba_wierszy": 21,            // wierszy danych po odczycie
  "mapowanie": {                   // kolumna (po strip()) → oczekiwane pole
    "Długość geograficzna": "dlugosc_geograficzna",
    "Nazwa": null,                 // null = nie importować
    "id": ["id_zrodlowe", "id_aed"] // lista = każda z wartości jest trafieniem
  },
  "rekordy": [                     // wybrane rekordy po normalize_table
    {"wiersz": 2, "pola": {
      "nazwa_ulicy": "Jasna",                 // dokładna wartość
      "nr_budynku": ["28a", "28A"],          // lista = dowolna z wartości
      "id_aed": {"regex": "^krosno-[0-9a-f]{6}$"}
    }}
  ],
  "komunikaty": {                  // kody, których oczekujemy w wyniku (normalize + validate)
    "musza_byc": ["WYGENEROWANO_ID"],
    "nie_moze_byc": ["POZA_POLSKA"]
  },
  "uwagi": "dlaczego tak"
}
```

Klucze `mapowanie` porównujemy po `strip()`, bo parser może (ale nie musi) obcinać spacje z nagłówków.
