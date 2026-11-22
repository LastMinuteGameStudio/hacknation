# AEDane: opublikuj dane o defibrylatorach na dane.gov.pl w 3 prostych krokach

**Hasło akcji: „Daj dane, daj życie”**

Projekt na hackathon HackNation 2026, zadanie **06 Misja AED: Dane na ratunek** (Ministerstwo Cyfryzacji).

- **Instrukcja dla jury (krok po kroku, każde wymaganie):** [JURY.md](JURY.md)
- **Prototyp:** https://tuaed.wkrynski.dev (kreator dla dostawcy, mapa AED, zebrane dane, API w `/docs`)
- **Prezentacja:** [prezentacja/AEDane-Misja-AED.pptx](prezentacja/AEDane-Misja-AED.pptx)
- **Wzorcowy zakres danych (xlsx):** [zakres-danych/wzorcowy-zakres-danych-AED.xlsx](zakres-danych/wzorcowy-zakres-danych-AED.xlsx)

> Wersja robocza opisu (22.11.2026). Uzupełniamy ją do końca hackathonu.

## Problem

Przy nagłym zatrzymaniu krążenia liczy się każda minuta, a defibrylatora AED może użyć każdy. Trzeba jednak wiedzieć, gdzie jest najbliższe urządzenie, czy jest dostępne i czy działa. W Polsce nie ma krajowego rejestru AED. Dane są rozproszone u wielu dysponentów (gminy, urzędy, OSP, szkoły, firmy) i publikowane w różnych formach: API z tokenem, mapy Google, tabele HTML, PDF, CSV z własnym układem kolumn. Na dane.gov.pl jest kilka zbiorów AED, każdy w innym schemacie, a część nie jest aktualizowana. Za jakość danych na portalu odpowiada dostawca, więc rozwiązanie musi ułatwić publikację samym dysponentom, a nie publikować dane za nich.

## Rozwiązanie

**AEDane** to akcja i narzędzie dla dysponentów AED. Dysponent wgrywa swój arkusz, AEDane zamienia go na wspólny, wzorcowy format i wystawia pod stałym adresem, który dysponent dodaje na dane.gov.pl jako zasób z „Aktualizacją automatyczną”. Dzięki temu dane o AED od wszystkich dostawców trafiają na portal w jednym formacie i pozostają aktualne.

1. **Wzorcowy zakres danych v0.5:** 58 pól (14 obowiązkowych, 18 zalecanych, 26 fakultatywnych), słowniki, szablony CSV i XLSX, metadane CSVW. 52 pola są publiczne, 6 zostaje w ewidencji dysponenta. Godziny dostępności są w strukturze, nie w wolnym tekście.
2. **Kreator w 3 krokach:** dysponent, wgranie pliku (CSV, XLSX, GeoJSON) z automatycznym mapowaniem kolumn i walidacją, publikacja. Wynik: CSV (RFC 4180, UTF-8), JSON, GeoJSON i CSVW na licencji CC0 1.0 pod stałym URL oraz instrukcja dodania zasobu na dane.gov.pl.
3. **Aktualizacja bez zmiany adresu:** prywatny link edycji albo synchronizacja z URL źródła (np. eksport z CMS miasta). Przy zmianie struktury pliku synchronizacja się wstrzymuje, a opublikowane dane zostają bez zmian.
4. **Agregat ogólnopolski:** `/d/aed-polska.csv` i `.geojson` łączą 18 858 unikalnych AED z 15 źródeł (z OpenStreetMap i bez niego) oraz zbiory wgrane przez dostawców. Przy każdym rekordzie są kolumny pochodzenia (źródło, licencja, data, status weryfikacji).
5. **Strona dla odbiorców:** mapa AED i tabela z wyszukiwaniem i filtrami.

### Wykaz AED w portalu dane.gov.pl

Za zbiór na portalu odpowiada dostawca, a dostawców AED jest wielu. Dlatego dopisaliśmy do kodu portalu (mcod-backend 2.62.3) **wykaz AED** na wzór istniejącego wykazu chronionych danych (DGA). Dostawca zaznacza przy swoim zasobie pole „Wykaz AED”, portal sprawdza plik według zakresu v0.5, a raz dziennie scala poprawne wykazy wszystkich dostawców w jeden zbiór **„Defibrylatory AED: wykaz zbiorczy”** (CSV i XLSX). Przy każdym AED zapisuje, od kogo pochodzi. AED zgłoszone przez dwóch dostawców zostają oba, a drugi rekord dostaje `duplikat_id_aed`. Dołączane są tylko wykazy na CC0 1.0 albo CC BY 4.0 ([propozycja licencji](prezentacja/LICENCJE.md)).

Kod jest w katalogu [portal/](portal/) (rozwijany na branchu `portal-aed`): pierwszy commit to niezmieniony kod portalu, kolejne to nasze zmiany. Opis zmian: [portal/WYKAZ-AED.md](portal/WYKAZ-AED.md), uruchomienie: [portal/URUCHOMIENIE-TUAED.md](portal/URUCHOMIENIE-TUAED.md). Portal z tą zmianą uruchomiliśmy lokalnie w Dockerze (admin, API, Celery). Scalenie wykazów 3 testowych dostawców: 45 AED, 1 duplikat, licencja wykazu CC BY 4.0; testy wykazu AED w kontenerze portalu: 26 passed (stan na 22.11, 09:15).

Mapowanie kolumn działa bez AI (synonimy z realnych plików i analiza zawartości) i trafia w 100% na 10 plikach testowych. Brakujące współrzędne uzupełnia geokoder GUGiK. Front spełnia WCAG 2.2 AA (axe-core: 0 naruszeń, Lighthouse: 100) i działa od 320 px szerokości.

## Gdzie co jest

Ponumerowane kroki sprawdzenia każdego wymagania, także bez dostępu do demo: **[JURY.md](JURY.md)**.

| Wymaganie z treści zadania | Gdzie |
|---|---|
| Prototyp | https://tuaed.wkrynski.dev, kod w [app/](app/) ([app/README.md](app/README.md)) |
| Prezentacja (zrzuty, kroki użytkownika, ograniczenia) | [prezentacja/](prezentacja/), zrzuty w [prezentacja/zrzuty/](prezentacja/zrzuty/README.md) |
| Wzorcowy zakres danych (xlsx) | [zakres-danych/](zakres-danych/) |
| Dane zebrane z wielu źródeł | [dane/](dane/) (skrypty i wynik agregacji) |
| Zgodność z dane.gov.pl | [prezentacja/zrzuty/DOWOD-URL.md](prezentacja/zrzuty/DOWOD-URL.md), [zadania/06-mc-misja-aed/RESEARCH.md](zadania/06-mc-misja-aed/RESEARCH.md) |
| WCAG i responsywność | [prezentacja/AUDYT-WCAG.md](prezentacja/AUDYT-WCAG.md) |
| Logotyp i księga znaku | [visual/](visual/) (logo JPG, PNG, PDF, SVG; księga znaku [PDF](visual/podstawowa_ksiega_znaku.pdf)) |
| Zmiany w portalu dane.gov.pl (wykaz AED) | [portal/](portal/), opis w [portal/WYKAZ-AED.md](portal/WYKAZ-AED.md) |
| Kod źródłowy | to repozytorium |

## Uruchomienie

Wymaga Dockera.

```bash
cd app
cp .env.example .env
docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build
```

Aplikacja działa pod http://localhost:8000. Szczegóły (wersja z tunelem, uruchomienie bez Dockera, testy): [app/README.md](app/README.md).

## Ograniczenia

- Publikacji na produkcyjnym dane.gov.pl nie sprawdziliśmy, bo nie mamy konta dostawcy. Działanie „Aktualizacji automatycznej” znamy z kodu portalu.
- Geokodujemy do 200 adresów na plik. W agregacie 63 AED nie ma współrzędnych.
- Dane z OpenStreetMap mają licencję ODbL, dlatego agregat ma też wersję bez OSM.
- Duplikaty między zbiorami różnych dostawców nie są jeszcze oznaczane.
- Zgubionego linku edycji nie da się odzyskać (prototyp nie ma logowania).
- AED w pojazdach są poza zakresem.

## Materiały robocze

- [Treść zadania i checklista wymagań](zadania/06-mc-misja-aed/)
- [Notatki i decyzje zespołu](zadania/06-mc-misja-aed/NOTATKI-ZESPOLU.md)
- [Źródła danych o AED](zadania/06-mc-misja-aed/ZESTAWIENIE-ZRODEL.md)
- [Plan i kontrakt API aplikacji](app/PLAN.md), [app/KONTRAKT.md](app/KONTRAKT.md)
- [Przegląd wszystkich zadań hackathonu](zadania/README.md)

## Zespół

_Do uzupełnienia._
