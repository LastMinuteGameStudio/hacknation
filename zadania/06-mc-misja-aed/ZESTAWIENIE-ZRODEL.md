# Zestawienie źródeł danych o AED w Polsce (runda 2)

Stan na 21.11.2026. Lista jest jak najszersza: obejmuje wszystko, co znaleźliśmy, także źródła bez danych do pobrania. Zawiera tylko fakty, bez rozwiązań.
Researchu dokonało 7 subagentów (Sonnet/Haiku), a liczby oznaczone ✅ sprawdziła sesja hacknacja-3f (curl lub analiza pliku).
Oznaczenia: ✅ zweryfikowane, ❔ niezweryfikowane (wyszukiwarka, prasa, streszczenie strony).

Pozostałe pliki: [ZRODLA-DANYCH.md](ZRODLA-DANYCH.md) (runda 1: OSM, Pierwszy Ratownik, Yanosik, Warszawa 19115, pojazdy), [WZORCE-ZAGRANICZNE.md](WZORCE-ZAGRANICZNE.md), [STAN-PRAWNY.md](STAN-PRAWNY.md). Zbiory na dane.gov.pl opisuje wpis na tablicy (inwentaryzacja sesji hacknacja-27).

## 1. Źródła z danymi do pobrania maszynowo

| Źródło | Liczba AED | Format / dostęp | Licencja | URL |
|---|---|---|---|---|
| OSM / OpenAEDMap (cała Polska) | ✅ 18 297 | GeoJSON, CSV; Overpass | ODbL | https://openaedmap.org/api/v1/countries/PL.geojson (stary adres `aed.openstreetmap.org.pl/aed_poland.geojson` przekierowuje) |
| Warszawa 19115 / SCB | ✅ 708 | GeoJSON (feed mapy, bez tokena) albo API miasta z tokenem | brak w feedzie; CC BY w API | opis w ZRODLA-DANYCH.md |
| Warszawa, kopia Esri Polska na ArcGIS Online | ✅ 708 | ArcGIS FeatureServer (query JSON/GeoJSON) | źródło: „Urząd m.st. Warszawy, Otwarte dane Warszawy” | https://services.arcgis.com/zg6BBB0wvjzrRBLk/arcgis/rest/services/AED/FeatureServer/0 |
| InPost Helpbox 365 (AED na paczkomatach) | ✅ 137 aktywnych w 98 miejscowościach (39 we Wrocławiu) | GeoJSON, którym zasila się mapa na inpost.pl/aed | brak | https://inpost.pl/aed-points |
| Kraków, mapa „MAPA DEFIBRYLATORÓW” (konto prywatne `wasniowskip`, 2022) | 150 ❔ (policzył subagent) | ArcGIS FeatureServer | brak | https://services6.arcgis.com/w8Sm3ehkmwzR6bQc/arcgis/rest/services/AED_zestawy/FeatureServer/0 |
| Kraków, wersja z 08.2022 (konto `pica_1`) | 44 ❔ | ArcGIS FeatureServer | brak | https://services-eu1.arcgis.com/svTzSt3AvH7sK6q9/arcgis/rest/services/AED_zestawy_2022_sierpien/FeatureServer/0 |
| Mikołów (konto `d.bania`, zmiana 11.2026) | 21 ❔ | ArcGIS FeatureServer, EPSG:2177 | brak, właściciel nieznany | https://services9.arcgis.com/E1ZsJFZqsk2tR9yK/arcgis/rest/services/Defibrylatory_AED/FeatureServer/0 |
| Koszalin „Punkty Życia” (UM, z BO 2021) | 35 w KML (strona podaje 40, w tym 8 mobilnych) ❔ | KML z Google My Maps, bez logowania | „Wszystkie prawa zastrzeżone” | https://www.google.com/maps/d/kml?forcekml=1&mid=1AQwJAfeZsGGB7fhz0-yBSxab83DwyIw |
| Politechnika Wrocławska (kampus) | ❔ | ArcGIS FeatureServer (`Defibrylatory_2023`, `defibrylatory`) | brak | services3.arcgis.com/rrLByHvJ7zuJQDVw |
| ZTM Gdańsk (pojazdy z AED) | 278 z 503 pojazdów | dane.gov.pl ds 1803 + GPS na żywo | dane.gov.pl | opis w ZRODLA-DANYCH.md |
| Geoportal GUGiK, warstwa „Defibrylatory” | to kopia OSM | ✅ tylko WMS (obraz PNG; GetFeatureInfo zadeklarowane). WFS: brak | AccessConstraints = NONE; dane OSM (ODbL) | https://mapy.geoportal.gov.pl/wss/ext/OSM/Defibrylatory |

Wyszukiwanie w ArcGIS Online (`defibrylator*`, typ Feature Service) zwraca ✅ tylko 7 publicznych usług: Warszawa (Esri PL), Kraków, Mikołów oraz 3–4 usługi PWr.

## 2. Wykazy samorządowe bez pliku (HTML, PDF, mapa)

- **Łódź, UM:** „Mapa defibrylatorów AED”, 136–137 stacjonarnych AED, dane z 08.2026 ❔. Strona blokuje automatyczne pobieranie (captcha), więc nie sprawdziliśmy jej technologii ani pól. https://uml.lodz.pl/dla-mieszkancow/zdrowie/mapa-defibrylatorow-aed/
- **Lublin, UM:** ✅ PDF „AED Lublin stan 17.03.2026”, **48 pozycji**. Każda ma tylko nazwę i adres, bez współrzędnych. Są duplikaty, np. Radio Lublin i AGRO II pojawiają się dwa razy. Miasto odsyła też do ratujzsercem.pl. https://lublin.eu/mieszkancy/zdrowie/aktualnosci/aed-w-lublinie,748,1345,1.html
- **Gliwice, Centrum Ratownictwa Gliwice:** tabela HTML z ok. 96 AED ❔.
  - Kolumny: lokalizacja, dzielnica, adres, szczegóły, dostępność (np. „całodobowo”). Brak współrzędnych.
  - Najaktualniejsze dane są w geoportalu MSIP (warstwa „Lokalizacja defibrylatorów AED”, endpointu nie ustaliliśmy) i w aplikacji GAMA.
  - OSM ma 24 punkty z odnośnikiem do geoportalu Gliwic.
  - https://gliwice.eu/aktualnosci/bezpieczne-gliwice/wykaz-defibrylatorow-aed-aktualizowany
- **Gdańsk, UMG (Wydział Bezpieczeństwa i Zarządzania Kryzysowego):** tabela HTML ze **114 pozycjami**, stan na 25.02.2022, miasto zaznacza, że lista jest niepełna. Obejmuje szkoły, słupki zewnętrzne, baseny i pojazdy. Brak współrzędnych. https://www.gdansk.pl/wiadomosci/Defibrylatory,a,216952
- **Zachodniopomorska Sieć Defibrylatorów AED (WOPR i Wojewoda):** tabele HTML z ok. 94 wpisami (Szczecin 76, Świnoujście 9, Stargard 5, Koszalin 3, Kołobrzeg 1). Zgłoszenia przyjmuje aed@wopr.szczecin.pl. OSM ma 26 punktów z tym źródłem. https://woprwz.pl/zachodniopomorska-siec-defibrylatorow-aed/
- **Kraków:** lista HTML i mapa Google, ok. 80 punktów stałych i 25 w pojazdach (stan 1.10.2026). Opis w ZRODLA-DANYCH.md.
- **Toruń:** lista HTML z 14 AED (z 2016). https://um.torun.pl/pl/print/215128
- **Chełm:** strona HTML z 10 lokalizacjami. https://samorzad.gov.pl/web/miasto-chelm/defibrylatory-aed-w-miejskiej-przestrzeni-publicznej
- **Siedlce:** lista z 2017, 11 miejsc, nieaktualna.
- **Sosnowiec:** mapa w aplikacji Sosnowieckiej Karty Miejskiej, kategoria „Defibrylatory AED” ❔.
- **Wrocław:** lista HTML 38 paczkomatów InPost z AED (21.11.2025). Miasto deklaruje ok. 300 AED, ale nie ma własnej mapy i odsyła do ratujzsercem.pl.
- **Płock:** ponad 50 AED według artykułu miasta. Brak wykazu, miasto odsyła do ratujzsercem.pl.
- **Poznań:** ok. 60 AED, 8 z BO i 3 planowane, wg Radia Poznań (03.2026). Wykazu miasta nie znaleźliśmy. dane.poznan.pl blokuje curl.
- **Nie znaleziono wykazu ani mapy (sprawdzone wyszukiwarką, domenami miast, ArcGIS Online i CKAN):**
  - Gdynia (CKAN: 0 wyników dla „defibrylator”), Sopot, Bydgoszcz, Olsztyn, Elbląg, Legnica, Wałbrzych, Leszno, Gorzów Wlkp.
  - Białystok, Rzeszów, Kielce, Katowice, Bytom, Tychy, Częstochowa, Radom, Zamość, Opole, Rybnik, Bielsko-Biała, Zabrze, Nowy Sącz, Tarnów.
  - Metropolia GZM.
  - Geoportale wojewódzkie: brak potwierdzonej warstwy AED w żadnym.
  - Portale powiatów i gmin (e-mapa.net, Geo-System, geoportal2): nie znaleźliśmy żadnej warstwy AED.

## 3. Sieci instytucji

- **InPost Helpbox 365:** ✅ 137 aktywnych stacji, wszystkie dostępne 24/7. Plik GeoJSON opisany w tabeli wyżej.
  - Pola: kod paczkomatu, adres w dwóch polach, opis miejsca, miejscowość, status, wariant. Wariant „blue” (39 stacji) to Wrocław, „yellow” (98) to pozostałe miejscowości.
  - Serwisem urządzeń zajmuje się Centrum Ratownictwa.
  - ✅ 121 ze 137 stacji ma już odpowiednik w OSM w promieniu 40 m.
  - Publiczne API punktów InPost (`api-shipx-pl.easypack24.net/v1/points`, 33 222 punkty) nie ma pola o AED.
- **Operatorzy w danych OSM:** ✅ to pokazuje, kto zgłaszał swoje AED do OSM (liczby punktów wg tagu `operator`):
  - instytucje publiczne: ZUS 177 (+16), Tauron 69, WBiZK 40, Tramwaje Warszawskie 38, UAM 32, UM Koszalin 32, UDT 30, Uniwersytet Gdański 27, NIK 20, UMCS 18, Archiwa Państwowe 14, Urzędy Skarbowe 12, GITD 11;
  - firmy: InPost 96, Biedronka 36, Polskie Koleje Linowe 18, Castorama 13, Decathlon 12.
- **Jak trafiały do OSM:** ✅ wiele punktów ma tag `source` w rodzaju „email od ZUS” (174), „email od UAM” (31), „email od gminy” (31), „email od KP PSP Mielec” (27), „email od UM Wieliczka” (24), „email od NIK” (20), „email od IAS Olsztyn” (20), „email od wojewody maz.” (11). Wolontariusze OSM prosili instytucje mailowo o wykazy i dostawali je. Inne źródła to otwarte dane Warszawy (116), geoportal Gliwic (24), WOPR zachodniopomorskie (26), Tauron (22) i artykuły prasowe.
- **PKP Intercity:** AED w pociągach (Pendolino od 2016, 20 FLIRT-ów od 12.2020, EIP). Wiadomo z komunikatów prasowych, listy brak ❔.
- **Łódzka Kolej Aglomeracyjna:** AED w pociągach (finansuje samorząd województwa). Listy brak ❔.
- **Polregio:** konto „POLREGIO” samo dodaje AED do OSM ❔.
- **Poczta Polska:** ok. 40 lokalizacji (placówki i centra logistyczne), wg komunikatu prasowego. Listy adresów brak ❔.
- **Fundusz Sprawiedliwości (2018):** ponad 100 mln zł na zestawy medyczne i AED dla OSP. Wnioski składały gminy. Załączniki PDF są na arch-bip.ms.gov.pl (sekcja Fundusz Sprawiedliwości / wsparcie dla OSP). Nie potwierdziliśmy, czy jest lista jednostek z liczbą AED ❔.
- **Fundacja LOTTO** („WspieramTo! Dla Ratowania Życia”, „70 AED na 70-lecie”): AED dla OSP, beneficjenci opisani w komunikatach ❔.
- **Parafie, PTTK, GOPR, TOPR, WOPR (poza zachodniopomorskim), Lasy Państwowe, Orlen, BP, Shell, Żabka, Lidl, banki, PZPN, Policja, Straż Miejska:** nie znaleźliśmy publicznych wykazów ❔. Część z nich występuje jako operator w OSM.
- **WOŚP „Ratujemy i uczymy ratować”:** to program szkoleniowy, a nie dystrybucja AED. Listy szkół z AED brak.

## 4. Zamknięte bazy i aplikacje (bez pobierania)

- Pierwszy Ratownik (ZOSP RP), ponad 8 500 AED: szczegóły w ZRODLA-DANYCH.md.
- Fundacja Ratuj Życie, ratujzsercem.pl / Staying Alive: osobna baza. Moderatorzy OSM zaznaczają, że danych nie wolno kopiować między nią a OSM w żadną stronę ❔. Badanie MDPI podaje 1 165 lokalizacji w 2019 ❔.
- Yanosik: zgłoszenia AED trafiają do OSM (szczegóły w ZRODLA-DANYCH.md).
- Aplikacja Ratownik, Pierwsza Pomoc LUX MED, aedmapa.pl (oparta na OSM, ok. 7 028 AED wg artykułu z 2024 ❔), kaszuby24.pl/aed (OSM), Targeo (komercyjne, bez licencji), 24sosnowiec.pl i 24katowice.pl (fragmentaryczne).

## 5. Producenci, dystrybutorzy, mapy komercyjne

- **Producenci** (Philips, ZOLL, Stryker/Physio-Control, Schiller, Mindray, Defibtech, HeartSine i inni) mają systemy rejestracji i monitoringu floty dla klientów, np. Philips HeartStart OnSite, Stryker LIFELINKcentral, ZOLL PlusTrac. Publicznych map ani udostępniania lokalizacji w Polsce nie znaleźliśmy ❔.
- **ZOLL** przekazał w 2024 swój rejestr NEAR do PulsePoint, ale obejmuje on USA.
- **Polscy dystrybutorzy** (AEDMAX, aed.pl, Defibrylatory24 i inni): nie znaleźliśmy publicznych map instalacji ❔.
- **Google Maps, Apple Maps, HERE, TomTom, Foursquare, Wikidata:** brak danych o AED dla Polski, które dałoby się pobrać ❔.
- **Mapillary:** w dokumentacji nie znaleźliśmy klasy obiektu „defibrylator” ❔.

## 6. Źródła pośrednie: zakupy i programy

- **TED (zamówienia UE):** ✅ API v3 działa bez klucza.
  - Ogłoszenia z CPV 33182100 („Defibrylator”) i kupującym z PL: 2023 = 10, 2024 = 275, 2025 = 450.
  - To nie są tylko AED, bo CPV dołącza się też do dużych dostaw sprzętu szpitalnego.
  - TED obejmuje tylko zamówienia powyżej progów UE.
  - `POST https://api.ted.europa.eu/v3/notices/search`
- **e-Zamówienia / BZP:** darmowe API `https://ezamowienia.gov.pl/mo-client-board/api/notices/`. Archiwum sprzed 2021 jest w bzp.uzp.gov.pl. Ogłoszenia podają adres zamawiającego, a miejsca montażu bywają dopiero w SWZ lub opisie przedmiotu zamówienia (załączniki PDF/DOCX).
- **Budżety obywatelskie:** projekty AED były w Łodzi (80 AED, 680 tys. zł), Wrocławiu (WBO 2023, 200 AED), Szczecinie (AED w komunikacji), Gdańsku (2018, 32 AED), Poznaniu (8), Białymstoku (14), Łomiankach i Knurowie. Strony projektów podają zwykle liczbę sztuk, rzadziej adresy. Format: HTML i PDF.
- **Programy regionalne:** Małopolska (konkurs wojewódzki na zakup AED, Małopolski OW NFZ) i łódzkie (UMWŁ). Listy beneficjentów są zwykle w PDF przy wynikach konkursu ❔.
- **BIP gmin:** Kraków ma wykazy i zarządzenia o darowiznach AED, Koszalin i Łomianki mają komunikaty. Nie ma jednolitej kategorii w BIP, a wykazy są częściej w aktualnościach.

## 7. Wnioski faktograficzne (runda 2)

- **Ogólnopolsko:** jedynym otwartym zbiorem do pobrania pozostaje OSM, z 18 297 punktami. ✅ Plik jest aktualizowany: 2 981 punktów ma `check_date` z 2026, a 1 672 z 2025.
- **Państwo** (Geoportal, dyspozytorzy medyczni i CPR 112) korzysta z OSM: z WMS GUGiK albo z importu z OpenAEDMap. Szczegóły w STAN-PRAWNY.md.
- **Lokalne zbiory maszynowe:**
  - Warszawa (708) i InPost (137) to jedyne duże.
  - Pozostałe miasta mają co najwyżej HTML, PDF albo mapę Google: Łódź, Lublin, Gliwice, Gdańsk, Koszalin, WOPR zachodniopomorskie.
  - Większość miast nie publikuje niczego.
- **Licencje:** poza OSM (ODbL) i Warszawą (CC BY w API) żadne z tych źródeł nie podaje licencji.
- **OSM jako zbiór list od instytucji:** znaczna część danych OSM to listy przekazane przez instytucje publiczne na prośbę wolontariuszy (tag `source` = „email od …”).

## 8. Do sprawdzenia

- Backend geoportalu MSIP Gliwice: czy warstwa AED ma WMS albo WFS.
- Mapa Łodzi: technologia, pola i liczba (strona blokuje curl).
- Załączniki Funduszu Sprawiedliwości: czy jest lista OSP z AED.
- CloudFerro WMS `geo.cloudferro.com/ogc/wms?map=/OSM/AED/Poland` ❔.
- ratujzsercem.pl: warunki i licencja, aktualna liczba.
- Słupsk, Zielona Góra (PDF „Bezpieczne Serce” z 2016) i Leszno (SIP zwrócił błąd 500).
