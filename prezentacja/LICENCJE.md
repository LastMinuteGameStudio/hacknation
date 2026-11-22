# Propozycja licencji dla wykazu AED na dane.gov.pl

Wersja robocza (22.11.2026, hacknacja-3f). Mentorzy MC poprosili o propozycję licencji dla zbioru łączącego dane wielu dostawców („Czekamy na Wasze propozycje w tym zakresie”, Discord, 21.11). Fakty, na których się opieramy, są w `zadania/06-mc-misja-aed/RESEARCH.md`.

## Fakty

- Portal dane.gov.pl oferuje tylko CC0 1.0 i licencje CC 4.0: BY, BY-SA, BY-NC, BY-NC-SA, BY-ND, BY-NC-ND (`Dataset.LICENSES` w kodzie portalu). Licencji ODbL nie ma.
- Wśród 500 najnowszych zbiorów na portalu 421 ma CC0 1.0, a 79 CC BY 4.0.
- Istniejące zbiory AED: Krosno i Przemyśl mają CC0 1.0, a Marki i Warszawa CC BY 4.0.
- Ustawa o otwartych danych (art. 14–16) pozwala stawiać tylko warunki obiektywne i proporcjonalne: podanie źródła, informację o przetworzeniu i zakres odpowiedzialności.
- Dane z OpenStreetMap mają licencję ODbL 1.0 z obowiązkiem udostępniania na tej samej licencji (share-alike).
- Za zbiór na portalu odpowiada jego dostawca (mentorzy MC).

## Propozycja

| Co | Licencja | Dlaczego |
|---|---|---|
| **Wykaz AED dostawcy** (to, co publikuje gmina, szkoła, firma) | **CC0 1.0** jako domyślna i zalecana; dopuszczalna **CC BY 4.0** | Najprostsze ponowne wykorzystanie przez aplikacje ratunkowe i mapy. Tak publikuje już większość portalu i połowa obecnych zbiorów AED. TuAED ustawia CC0 i prosi o wyraźną zgodę przed publikacją. |
| **Wykaz zbiorczy AED tworzony przez portal** | **CC BY 4.0**, a gdy wszystkie wykazy źródłowe mają CC0, to **CC0 1.0** | CC BY 4.0 jest zgodna z CC0 i CC BY. Wymóg podania źródła spełniają kolumny pochodzenia przy każdym rekordzie (instytucja dostawcy, URL zasobu, licencja źródła, data aktualizacji). |
| **Do wykazu zbiorczego nie trafiają** zasoby na CC BY-SA, BY-NC, BY-ND ani ich połączeniach | — | NC wyklucza aplikacje komercyjne (np. mapy w telefonach), ND zabrania przetwarzania, a SA wymusza tę samą licencję na całym wykazie. Portal pokazuje dostawcy komunikat, że jego wykaz nie zostanie dołączony z powodu licencji. |
| **Dane z OpenStreetMap** | nie trafiają do wykazu na portalu | ODbL wymaga udostępniania na tej samej licencji, a portal jej nie oferuje. Na stronie TuAED pokazujemy OSM osobno, z atrybucją, jako pokaz skali (`/d/aed-polska.csv` i wersja bez OSM). |
| **Dane ze stron www bez licencji** (tabele HTML, PDF, mapy Google) | nie trafiają do wykazu na portalu | Brak zgody dysponenta. Zamiast tego zachęcamy dysponenta do publikacji przez TuAED. |

## Zasada w jednym zdaniu

Dostawca publikuje swój wykaz na CC0 (albo CC BY 4.0), a portal skleja tylko wykazy na licencjach zgodnych z CC BY 4.0 i przy każdym AED zapisuje, od kogo pochodzi.

## Do potwierdzenia z MC

- Czy MC akceptuje regułę „licencja wykazu zbiorczego zależy od licencji wykazów źródłowych”, czy woli jedną stałą licencję (CC BY 4.0).
- Czy portal może automatycznie pomijać wykazy na licencjach NC, ND i SA.
