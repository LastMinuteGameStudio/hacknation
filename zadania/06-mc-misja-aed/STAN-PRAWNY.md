# Stan prawny i źródła państwowe AED w Polsce

Stan na 21.11.2026, research subagenta. Wywołania usług i dokumenty sprawdzono curlem albo przeczytano, chyba że oznaczono ❔. Plik zawiera tylko fakty.

## Brak obowiązku i rejestru

- **Ministerstwo Zdrowia** w odpowiedzi na interpelację nr 20763 (13.11.2026):
  - „nie istnieje powszechny obowiązek zgłaszania AED do centralnego rejestru”,
  - MZ „nie prowadziło formalnych prac legislacyjnych”,
  - dane „nie stanowią państwowej ewidencji AED”.

  Nie ma ustawowego zakresu danych ani klasyfikacji dostępności AED.
- **Pismo MZ DBR.055.48.2023.AF z 05.01.2024**, odpowiedź na petycję z 16.10.2023 (gov.pl/attachment/6b98e1da-f278-48b6-9f61-f7d289d6ca2f; data 22.09.2025 to tylko data utworzenia pliku):
  - nie ma obowiązku wyposażania w AED, bo to inicjatywa pracodawców i zarządców;
  - system ochrony zdrowia korzysta z danych publikowanych przez organizacje społeczne;
  - „Centrum e-Zdrowia prowadzi prace nad umożliwieniem lokalizacji AED i udostępnienia tej informacji w aplikacji Na ratunek w MojeIKP”. Wdrożenia nie potwierdziliśmy ❔.
- **Projekty ustaw:** w API Sejmu (IX i X kadencja) nie ma druków z „defibryl”. RCL i Senat sprawdziliśmy tylko wyszukiwarką ❔. Petycji o rejestrze AED nie znaleźliśmy ❔.
- **NIK, RPO, RPP:** nie znaleźliśmy kontroli NIK ani wystąpień dotyczących AED.

## Z czego korzysta państwo: OSM

- **Geoportal GUGiK:** warstwa „Defibrylatory”, ✅ WMS `https://mapy.geoportal.gov.pl/wss/ext/OSM/Defibrylatory` (WMS 1.3.0, układy EPSG:2180/4326/4258/3857).
  - GetMap zwraca PNG. WFS nie istnieje.
  - Warstwa działa od 04.02.2022 na podstawie porozumienia Głównego Geodety Kraju z Stowarzyszeniem OpenStreetMap Polska.
  - Według MZ GUGiK sprawdza tylko poprawność struktury danych, a nie ich aktualność.
- **Dyspozytorzy medyczni:** według MZ (interpelacja 20763) warstwa GUGiK jest w Uniwersalnym Module Mapowym zintegrowanym z SWD PRM.
- **CPR (112/997/998):** MSWiA w odpowiedzi na interpelację 16205 (15.04.2026) pisze, że operatorzy mają podkład z AED „pobierany z openaedmap.org i cyklicznie importowany”. Według MSWiA ogólnopolski standard oznakowania i ewidencji AED oraz integracja z SWD PRM należą do ministra zdrowia.
- **KSRG, PSP, Policja:** nie ma zbiorczych wykazów AED w jednostkach ani pojazdach. Społeczność OSM nie mapuje AED w pojazdach (obiektów ruchomych).

## Interpelacje (X kadencja)

- **nr 10044** (06.2025): AED w szkołach. MZ odpowiada, że nie ma podstawy do ich finansowania i nie ma rządowego programu AED w szkołach.
- **nr 16205** (03.2026, do MSWiA): AED z Programu Ochrony Ludności zamykane w magazynach. Odpowiedź: decyduje samorząd. MSWiA wymienia też aplikację Pierwszy Ratownik.
- **nr 20440** (15.10.2026, do Ministerstwa Cyfryzacji): AED w mObywatelu i projekt Tower of Life Politechniki Wrocławskiej. Odpowiedzi jeszcze nie ma.
- **nr 20763** (29.10.2026, do MZ): jednolita ewidencja AED i obowiązek aktualizacji. Odpowiedź z 13.11.2026 jest opisana wyżej.
- **IX kadencja:** interpelacje 1790 (2020) i 27552 (2021) o AED. Ich treści nie czytaliśmy.
