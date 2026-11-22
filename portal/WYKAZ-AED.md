# Wykaz AED w portalu dane.gov.pl

Zmiana w kodzie portalu (mcod-backend 2.62.3). Dostawcy, czyli gminy, szpitale, uczelnie i firmy, publikują własne wykazy AED. Portal sprawdza każdy wykaz według wzorcowego zakresu danych o AED v0.5. Raz dziennie scala poprawne wykazy w jedną standardową listę, czyli zbiór **„Defibrylatory AED: wykaz zbiorczy”**.

Mechanizm jest wzorowany na istniejącym w portalu wykazie chronionych danych DGA: `Resource.contains_protected_data`, `create_main_dga_resource_task`, `AggregatedDGAInfo`. Robi jednak coś, czego DGA nie robi: scala wykazy **rekord po rekordzie** we wspólnym zakresie danych, opisuje pochodzenie każdego rekordu i oznacza AED zgłoszone przez dwóch dostawców.

## Jak to wygląda dla dostawcy

1. Redaktor instytucji dodaje w panelu zasób z plikiem CSV albo XLSX w zakresie v0.5. Taki plik przygotowuje kreator TuAED. Albo podaje link do pliku, na przykład stały adres TuAED `/d/{slug}.csv` z automatyczną aktualizacją.
2. Zaznacza **„Wykaz AED: Tak”**. Opis pola w formularzu wyjaśnia, co to oznacza.
3. Przy zapisie portal od razu sprawdza format pliku i kolumny pól obowiązkowych. Jeśli są błędy, pokazuje je przy polu.
4. Po publikacji pełna walidacja zakresu v0.5 jest częścią zwykłej walidacji danych zasobu. Błędy widać w panelu w tym samym miejscu i w tej samej formie co inne błędy walidacji danych, razem z numerem wiersza, nazwą kolumny i zaleceniem.
5. Następnej nocy (o 3:45) poprawny wykaz trafia do wykazu zbiorczego.

## Reguły scalania

| Reguła | Szczegóły |
|---|---|
| Co trafia do wykazu zbiorczego | Opublikowane zasoby z flagą „Wykaz AED” od **wszystkich** dostawców. Tylko wykazy dostawców: bez OpenStreetMap i bez danych zebranych przez TuAED ze stron miast (decyzja zespołu). |
| Wykaz z błędami | Wykaz z co najmniej jednym błędem walidacji zakresu v0.5 jest pomijany w całości. Ostrzeżenia, np. brak pól zalecanych, nie blokują dołączenia. |
| Licencja | Dołączane są tylko zbiory z licencją CC0 1.0 albo CC BY 4.0. Wykaz z inną licencją (BY-SA, BY-NC, BY-ND i ich połączenia) jest pomijany, a w walidacji zasobu pojawia się komunikat, że nie zostanie dołączony z powodu licencji. |
| Licencja wykazu zbiorczego | CC0 1.0, gdy wszystkie dołączone wykazy mają CC0. W przeciwnym razie CC BY 4.0. |
| Kolumny | Pola publiczne zakresu v0.5 w kolejności zakresu oraz kolumny pochodzenia: `zrodlo_instytucja`, `zrodlo_zasob_id`, `zrodlo_url`, `zrodlo_data_aktualizacji`, `licencja_zrodla`. Pola niepubliczne, np. `numer_seryjny` i `telefon_kontaktowy`, nie trafiają do wykazu. Kolumny spoza zakresu też nie, a portal ostrzega o nich przy walidacji. |
| Duplikaty między dostawcami | Oba rekordy zostają. Rekord z wykazu przetwarzanego później dostaje `duplikat_id_aed` = `id_aed` rekordu wcześniejszego, gdy oba mają ten sam numer seryjny (bez różnicy wielkości liter i spacji) albo leżą do 30 m od siebie. Kolejny duplikat wskazuje ten sam rekord główny. Duplikatów w wykazie jednego dostawcy scalanie nie oznacza, bo walidacja zgłasza je jako błąd tego wykazu (powtórzony id_aed albo numer seryjny). |
| Kolejność | Wykazy są przetwarzane według nazwy instytucji, a w obrębie instytucji według id zasobu. Wynik jest powtarzalny. |
| Formaty | Plik główny CSV (RFC 4180: UTF-8 bez BOM, przecinek, CRLF) i plik dodatkowy XLSX z tymi samymi kolumnami. W XLSX wszystkie komórki są tekstowe, więc kod TERC „0201011” i współrzędna „49.785100” nie tracą zer. |
| Podmiana wykazu | Nowy zasób wykazu zbiorczego zastępuje stary dopiero wtedy, gdy przejdzie walidację portalu (plik, link, dane). Jeśli walidacja się nie uda, nowy zasób jest usuwany, a stary zostaje (jak w DGA). Gdy nie ma żadnego poprawnego wykazu, nic się nie zmienia. |

Wykaz czytamy z surowego pliku zasobu, a nie z `tabular_data` portalu. Rzutowanie typów w portalu zamieniłoby kod TERC „0201011” na liczbę, a „49.785100” na „49.7851”.

## Co i gdzie zmieniono

| Plik | Zmiana |
|---|---|
| `mcod/resources/aed/` (nowy) | Czysta logika bez Django: `schema.py` (zakres v0.5 z kopii `zakres/zakres-pol.csv` i `zakres/slowniki.csv`), `reader.py` (odczyt CSV/XLSX jako tekst), `validation.py` (walidacja przeniesiona z rdzenia TuAED `aed_core/validate.py` i rozszerzona o kontrolę nagłówka), `merge.py` (scalanie, duplikaty, licencje, eksport CSV/XLSX). |
| `mcod/resources/aed_utils.py` (nowy) | Integracja z modelami, odpowiednik `dga_utils.py`: wybór zasobów, walidacja zasobu, tworzenie zbioru i zasobu wykazu zbiorczego, zapis `AggregatedAEDInfo`, sprzątanie. |
| `mcod/resources/tasks/aed.py` (nowy) | `create_main_aed_resource_task` (scalanie, pliki, nowy zasób) i `finalize_main_aed_resource_task` (czeka na walidację portalu z ponawianiem, potem podmienia wykaz). Odpowiednik `tasks/dga.py`. |
| `mcod/resources/models.py` | Pole `Resource.is_aed_list` („Wykaz AED”) i model `AggregatedAEDInfo` (zasób, liczba wykazów, pominiętych, AED, duplikatów, licencja, raport JSON). |
| `mcod/resources/migrations/0075_resource_is_aed_list_aggregatedaedinfo.py` (nowa) | Migracja obu zmian. |
| `mcod/resources/forms.py` | Pole „Wykaz AED” z opisem. Przy wgraniu pliku z flagą: kontrola formatu i kolumn pól obowiązkowych. W formularzu inline pole jest ukryte, jak flaga DGA. |
| `mcod/resources/admin.py` | Pole „Wykaz AED” w formularzu zasobu (dodawanie i edycja) oraz podgląd „Wykaz zbiorczy AED” (`AggregatedAEDInfo`, tylko do odczytu, dla administratora) z raportem: które wykazy dołączono, a które pominięto i dlaczego. |
| `mcod/resources/tasks/process_resource_file_data.py` | Dla zasobu z flagą, po walidacji goodtables, uruchamia walidację zakresu v0.5. Błędy trafiają do wyników walidacji danych zasobu jako `ResourceDataValidationError`. |
| `mcod/resources/error_mappings.py` | Zalecenia dla kodów błędów `aed-*`, wyświetlane w panelu obok błędu. |
| `mcod/resources/tasks/__init__.py`, `mcod/settings/base.py`, `mcod/celeryapp.py` | Rejestracja zadań, kolejka `resources`, ustawienia `MAIN_AED_*` i harmonogram `aed_main_resource_creation`: codziennie o 3:45, po DGA. |
| `mcod/resources/tests/test_aed_merge.py` (nowy) | 18 testów czystej logiki bez bazy: odczyt, walidacja, dwóch dostawców, duplikat po numerze seryjnym, duplikat po odległości (22 m tak, 45 m nie), duplikat trzeciego dostawcy, zasób z błędem walidacji pominięty, zasób z licencją BY-NC pominięty, licencja wykazu, eksport CSV/XLSX. |
| `mcod/resources/tests/test_aed_list.py` (nowy) | Testy z bazą w stylu `test_main_dga.py`: wybór zasobów, scalanie trzech dostawców (jeden z BY-NC), walidacja licencji zasobu, zadanie tworzące wykaz zbiorczy, podmiana starego zasobu i brak zmian, gdy nie ma poprawnych wykazów. |

## Konfiguracja

| Ustawienie | Znaczenie |
|---|---|
| `MAIN_AED_DATASET_OWNER_ORGANIZATION_PK` (zmienna środowiskowa) | **Wymagane.** Id instytucji, która jest właścicielem zbioru „Defibrylatory AED: wykaz zbiorczy”. Odpowiednik `MAIN_DGA_DATASET_OWNER_ORGANIZATION_PK`. |
| `MAIN_AED_DATASET_UPDATE_NOTIFICATION_EMAIL` (zmienna środowiskowa, opcjonalna) | Adres powiadomień o aktualizacji zbioru. |
| `MAIN_AED_DATASET_CATEGORIES_TITLES`, `MAIN_AED_DATASET_TAGS_NAMES` | Kategoria „Zdrowie” oraz tagi „AED”, „defibrylator” i „wykaz AED”. |

## Uruchomienie

```bash
python manage.py migrate resources
# scalanie od razu, bez czekania na harmonogram (synchronicznie, w powłoce kontenera):
python manage.py shell -c "from mcod.resources.tasks import create_main_aed_resource_task as t; print(t.apply().result)"
# albo przez Celery:
python manage.py shell -c "from mcod.resources.tasks import create_main_aed_resource_task as t; t.delay()"
```

Wynik scalania, czyli liczbę AED, duplikatów i powody pominięcia wykazów, widać w panelu: **Zasoby → Wykaz zbiorczy AED**.

Testy (środowisko testowe portalu):

```bash
python -m pytest mcod/resources/tests/test_aed_merge.py mcod/resources/tests/test_aed_list.py
```

`test_aed_merge.py` nie używa bazy. Moduły `mcod/resources/aed/` nie importują Django, więc te testy przechodzą też poza portalem: na Pythonie 3.8 (wersja portalu) i 3.12, z samym pakietem `aed` i openpyxl.

## Pokaz bez uruchamiania portalu

```bash
cd portal && python tuaed_pokaz_scalania.py   # Python ≥ 3.8 i openpyxl; --offline: bez sieci, z kopii w pokaz/zrodla/
```

Skrypt nie używa Django ani bazy. Przepuszcza wykazy przez ten sam kod (`mcod/resources/aed/`), którego używa zadanie `create_main_aed_resource_task`. Zapisuje `pokaz/wykaz-zbiorczy.csv`, `pokaz/wykaz-zbiorczy.xlsx` i `pokaz/raport.json` (co dołączono, co pominięto i dlaczego, które rekordy są duplikatami), a wejściowe wykazy w `pokaz/zrodla/`.

| Wykaz | Licencja | Wynik |
|---|---|---|
| Urząd Miejski w Przemyślu, `https://tuaed.wkrynski.dev/d/kznsks42.csv` | CC0 1.0 | dołączony, 21 AED |
| Urząd Miasta Krosna, `https://tuaed.wkrynski.dev/d/qy7g6px5.csv` | CC0 1.0 | dołączony, 21 AED |
| Uczelnia (pokaz, fikcyjny) | CC0 1.0 | dołączony, 1 AED z numerem seryjnym SN-PL-2024-0001 |
| Wojewódzki Szpital (pokaz, fikcyjny) | CC BY 4.0 | dołączony, 3 AED. `szpital-krosno-1` ma ten sam numer seryjny co AED uczelni, więc dostaje `duplikat_id_aed = uczelnia-przemysl-1`. `szpital-krosno-2` leży ok. 15 m od pierwszego AED z wykazu Krosna, więc dostaje `duplikat_id_aed = qy7g6px5-26c91c`. |
| Fundacja (pokaz, fikcyjny) | CC BY-NC 4.0 | pominięty z powodu licencji |
| Gmina (pokaz, fikcyjny) | CC0 1.0 | pominięty: wartość „dla wszystkich” spoza słownika `dostepnosc` |

Wynik: 46 AED z 4 wykazów, 2 duplikaty oznaczone (oba rekordy zostają), licencja wykazu CC BY 4.0, bo jeden dołączony wykaz ma CC BY.

Skrypt wysyła własny nagłówek User-Agent, bo Cloudflare przed TuAED odrzuca domyślny User-Agent `Python-urllib` (błąd 403). Portal tego problemu nie ma: pobiera linki biblioteką requests z przeglądarkowym User-Agent (`mcod/resources/link_validation.py`).

## Ograniczenia

- `id_aed` jest unikalny w wykazie dostawcy, ale nie w całym wykazie zbiorczym. Para (`zrodlo_zasob_id`, `id_aed`) jest unikalna. `duplikat_id_aed` wskazuje `id_aed` rekordu głównego, a jego dostawcę podają kolumny pochodzenia rekordu głównego.
- Numer seryjny jest polem niepublicznym. Duplikat po numerze wykryjemy tylko wtedy, gdy dostawca opublikował go w swoim wykazie. Poza tym zostaje kryterium odległości.
- Zakres v0.5 jest w portalu kopią plików z repozytorium projektu (`zakres-danych/`). Nowa wersja zakresu oznacza podmianę dwóch plików w `mcod/resources/aed/zakres/`.
