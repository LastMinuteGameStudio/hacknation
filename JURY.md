# Jak sprawdzić AEDane (dla jury)

Wystarczy przeglądarka. Nic nie trzeba instalować.

## 1. Prototyp: dysponent publikuje dane o AED (5 minut)

1. Pobierz plik urzędu: [przemysl_2024.csv](https://raw.githubusercontent.com/LastMinuteGameStudio/hacknation/main/app/backend/tests/fixtury/przemysl_2024.csv)
   (prawdziwy eksport z CMS Przemyśla, nieuporządkowany).
2. Wejdź na **https://tuaed.wkrynski.dev** i kliknij „Zacznij”.
3. Wpisz nazwę, np. `Urząd Miejski w Przemyślu (jury)`, i kliknij „Dalej”.
4. Wgraj plik. Kolumny dopasują się same.
5. W „Ustaw dla wszystkich AED” wybierz: wewnątrz budynku „Nie”, dostęp „Dostępny dla każdego”, całą dobę „Tak”.
6. Kliknij „Sprawdź dane”, a potem „Opublikuj”. Wynik: stały link do pliku CSV oraz instrukcja, jak dodać go na
   dane.gov.pl z „Aktualizacją automatyczną” i polem „Wykaz AED”.
7. Zobacz efekt: **[Mapa AED](https://tuaed.wkrynski.dev/mapa)** i **[Zebrane dane](https://tuaed.wkrynski.dev/dane)**.

## 2. Portal dane.gov.pl z naszą zmianą: scalanie wykazów AED (3 minuty)

Dopisaliśmy do kodu portalu „wykaz AED”. Dostawca zaznacza pole przy zasobie, portal sprawdza dane, a co noc
łączy wykazy wszystkich dostawców w jeden ogólnopolski zbiór.

1. Wejdź na **https://unto-attend-uncle-adopt.trycloudflare.com**. Login: `jury@tuaed.local`, hasło jest w
   formularzu zgłoszenia.
2. Zasoby → „Defibrylatory AED w Przemyślu (CSV)”: pole **„Wykaz AED”** jest zaznaczone, a zakładka walidacji pokazuje
   wynik sprawdzenia danych.
3. Scalony zbiór pobierzesz bez logowania:
   **[wykaz zbiorczy CSV](https://package-colours-charitable-database.trycloudflare.com/media/resources/20261122/wykaz-zbiorczy-aed-20261122.csv)**
   (3 dostawców, 45 AED, 1 duplikat oznaczony w kolumnie `duplikat_id_aed`).

Portal działa na komputerze zespołu. Jeśli link nie działa, zobacz
[nagranie panelu (101 s)](prezentacja/zrzuty/portal-nagranie.mp4) i [zrzuty](prezentacja/zrzuty/README.md) (pliki `portal-*`).

## 3. Pozostałe elementy zadania

| Wymaganie | Gdzie |
|---|---|
| Prezentacja | [AEDane-Misja-AED.pptx](prezentacja/AEDane-Misja-AED.pptx) |
| Wzorcowy zakres danych (xlsx) | [wzorcowy-zakres-danych-AED.xlsx](zakres-danych/wzorcowy-zakres-danych-AED.xlsx) |
| Nazwa, hasło, logotyp, księga znaku | **AEDane**, „Daj dane, daj życie”, [visual/](visual/) ([księga znaku PDF](visual/podstawowa_ksiega_znaku.pdf)) |
| Zgodność z dane.gov.pl | [DOWOD-URL.md](prezentacja/zrzuty/DOWOD-URL.md) |
| WCAG i responsywność | [AUDYT-WCAG.md](prezentacja/AUDYT-WCAG.md) (axe 0 naruszeń, Lighthouse 100, od 320 px) |
| Kod: aplikacja i zmiany w portalu | [app/](app/), [portal/WYKAZ-AED.md](portal/WYKAZ-AED.md) |
| Wykorzystanie AI | [WYKORZYSTANIE-AI.md](WYKORZYSTANIE-AI.md) |

Kroki z alternatywami bez demo i uruchomienie lokalne: [JURY-SZCZEGOLY.md](JURY-SZCZEGOLY.md).
