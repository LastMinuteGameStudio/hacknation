# Źródła danych o lokalizacji AED poza dane.gov.pl

Stan: 21.11.2026. Research robili subagenci, a liczbę z OSM sprawdziłem ręcznie. Lista zawiera tylko fakty, bez rozwiązań.
Oznaczenia: ✅ zweryfikowane, ❔ niezweryfikowane (tylko wyniki wyszukiwania lub prasa).

## Otwarte i odczytywalne maszynowo

### OpenStreetMap / OpenAEDMap ✅
- **Operator:** społeczność OSM i stowarzyszenie OpenStreetMap Polska. Kampania mapowania AED w Polsce trwa od końca 2021.
- **Mapa:** https://openaedmap.org/pl/ (następca aed.openstreetmap.org.pl, stare repo `aed-mapa` jest zarchiwizowane).
- **Plik:** https://aed.openstreetmap.org.pl/aed_poland.geojson (są też `.csv` i `.ods`). ✅ Plik pobrany 21.11.2026 zawierał **18 297 punktów** (7,1 MB).
- **Inne formy dostępu:** Overpass API (`emergency=defibrillator`) i wyciągi Geofabrik.
- **Licencja:** ODbL. Wolno używać ponownie, jeśli podamy źródło i udostępnimy dalej na tych samych warunkach (share-alike). Licencja OSM nie pozwala kopiować do OSM danych z innych, zamkniętych serwisów.
- **Wypełnienie pól w pliku (na 18 297 punktów):**
  - `access`: 16 917
  - `indoor`: 15 969
  - `defibrillator:location` (opis miejsca): 12 317, w tym `:pl` 5 173 i `:en` 2 407
  - `opening_hours`: 6 781
  - `operator`: 6 007
  - `check_date` (data weryfikacji): 5 982
  - `phone`: 4 481
  - `level`: 3 701
  - `image`: 2 168
  - `wheelchair`: 463
  - `manufacturer`: 347
  - `emergency:phone`: 200
- **Opis tagów:** https://wiki.openstreetmap.org/wiki/Tag:emergency=defibrillator
- **Kopia danych:** github.com/openstreetmap-polska/aed_backup

## Państwowe (oparte na OSM)

- **Geoportal.gov.pl, warstwa „Defibrylatory”:** prowadzi Główny Geodeta Kraju na podstawie porozumienia z OSM Polska. Dostęp przez WMS, tylko podgląd. ❔
- **mojeIKP, funkcja „Na ratunek” (Ministerstwo Zdrowia):** pokazuje AED na podstawie danych z OSM Polska. Źródło: odpowiedź rządu na petycję, gov.pl/attachment/6b98e1da-f278-48b6-9f61-f7d289d6ca2f. ❔
- **Rejestr krajowy:** nie znaleźliśmy urzędowego rejestru AED. W Polsce nie ma przepisów nakazujących rozmieszczanie AED. Jest interpelacja nr 16205 (Sejm, X kadencja). ❔

## Zamknięte aplikacje i mapy (bez pliku ani API, licencja nieznana)

- **Pierwszy Ratownik** (ZOSP RP + PZU, Google Cloud): ponad 8 500 AED, dane także z crowdsourcingu. ❔ https://spidersweb.pl/2026/03/darmowa-aplikacja-pierwszy-ratownik-polska-osp.html
- **Fundacja Ratuj Życie, Ogólnopolska Mapa AED** (ratujzsercem.pl/Map.aspx): działa od 2011 i trafia do aplikacji Staying Alive. Podawane liczby to 1 605 i 2 192 (2022). ❔
- **Staying Alive:** aplikacja europejska, polska wersja korzysta z mapy fundacji. ❔
- **Mapa AED / aedmapa.pl, „AED map – defibrillators”:** aplikacje oparte na OSM.
- **Yanosik** (Yanosik S.A., dawniej Neptis): od 03.2022, razem z ZOSP RP i OSM Polska. Użytkownik przytrzymuje miejsce na mapie, wybiera „defibrylator AED” i zaznacza, czy jest wewnątrz, czy na zewnątrz budynku. Dział mapowy weryfikuje zgłoszenie i **dodaje je do OSM**, więc te dane są w pliku OSM na licencji ODbL. https://yanosik.pl/blog/yanosik-bedzie-ratowal-zycie-kierowcom-wprowadzamy-nowe-funkcje-lld3l47cjuawzoxrn5w0dyue
  - **Publicznego API ani portalu dla programistów nie znaleźliśmy.** Firma sprzedaje dane partnerom komercyjnym i instytucjom na podstawie umowy (PAP Biznes). Klauzul regulaminu o własności zgłoszeń nie udało się odczytać ❔.
- **Ratownik:** aplikacja, w której można dodawać AED. ❔
- **Pierwsza Pomoc LUX MED:** mapa AED. ❔

### Pierwszy Ratownik: szczegóły (research 21.11)

**Skąd dane**
- Baza powstała z crowdsourcingu. Zalogowani użytkownicy mogą dodawać i aktualizować AED oraz zgłaszać ich brak; robią to „społeczność ratownicza i ZOSP RP” (App Store, aplikacja Reanimator 1R).
- FAQ: „dodawanie nowych urządzeń do bazy (aktualnie niedostępne)”. https://pierwszyratownik.pl/aplikacja/faq/
- Liczba: ponad 8 500 AED (spidersweb, 03.2026). Strona główna podaje „10 000+” AED zarejestrowanych w programie. W styczniu 2024 było ponad 7 700 ❔.
- Proces weryfikacji nie jest opisany. W źródłach nie ma wzmianki o OSM, fundacjach, samorządach ani dane.gov.pl ❔.

**Jak działa aplikacja**
- Jednym dotknięciem łączy z numerem 112 i jednocześnie alarmuje ratowników-wolontariuszy w promieniu kilku km.
- Ratownik, który przyjmie zgłoszenie, dostaje trasę i informacje o zdarzeniu. Aplikacja wskazuje najbliższy AED, także po drodze, z szacowanym czasem dojścia.
- Ma połączenie wideo (Google Meet), przez które można prowadzić osobę zgłaszającą.
- Pilotaż: ok. 600 strażaków OSP, średni czas dotarcia pierwszej pomocy 87 s.
- Ratownikiem może zostać osoba, która ma ukończone 18 lat i „odpowiednie kwalifikacje medyczne” (regulamin §3.2). Sposób weryfikacji kwalifikacji nie jest opisany. To wolontariat. Lokalizacja jest śledzona tylko podczas dyżuru.
- Regulamin §5.1 mówi o przyjmowaniu zdarzeń z zewnętrznych systemów przez API. Integracji z CPR i dyspozytornią PRM nie potwierdzono ❔. Regulamin §8.2: aplikacja „nie zastępuje wezwania służb”.
- Platformy: iOS i Android. Aplikacja jest bezpłatna. Osobna aplikacja Reanimator służy do wyszukiwania AED i podpowiada pierwszą pomoc.

**Własność i udostępnianie**
- Właścicielem jest ZOSP RP (regulamin §1.2). Aplikację stworzyła i utrzymuje HomerSafe Sp. z o.o. (§1.3). Administratorem danych osobowych jest ZOSP RP. Partnerzy to PZU i Google Cloud.
- Strona mówi o „otwartej bazie”, ale **nie ma publicznego API, licencji ani eksportu**. Baza zasila też aplikację Reanimator „i inne usługi”.
- **Pogłębione szukanie (21.11): danych nie ma nigdzie publicznie.** „Otwarta” oznacza, że każdy może dodać AED, a nie że dane można pobrać.
  - Sprawdzone strony bez wyników: /dolacz/jst/, /dolacz/firma/ (ogólniki, brak panelu i importu dla dysponentów), /aplikacja/rejestr-zmian/ (wspomina „panel administracyjny”, bez szczegółów), wp-json (standardowy WordPress), sitemap.xml.
  - Inne miejsca bez wyników: dane.gov.pl (0 zbiorów od ZOSP lub HomerSafe), GitHub (0 repozytoriów), homersafe.com (brak wzmianki).
  - Nie znaleźliśmy umowy o przekazywaniu danych do OSM, Geoportalu ani PRM.
  - API z regulaminu §5.1 służy do przyjmowania zdarzeń (np. z dyspozytorni), a nie do udostępniania lokalizacji AED.
  - Blog z 29.03.2026: integracja z PRM i 112 jest „w trakcie prac”.
  - Blog z 18.10.2026 („Wspólny front dla życia”): list intencyjny „Systemy Ratujące Życie” zapowiada rozwój rejestrów AED i powiązanie dyspozytorni z rejestrem AED. To deklaracja, nie otwarcie danych.
  - ⚠️ Sprzeczność: blog podaje, że aplikację zbudowali Endava i Google Cloud Polska, a regulamin §1.3 wskazuje HomerSafe. Partnerzy wspierający to m.in. AEDMAX, Philips Polska i InPost.
  - Dostęp do danych zostaje tylko przez kontakt z ZOSP RP (iod@zosprp.org.pl jest adresem inspektora ochrony danych, a nie kontaktem w sprawie danych AED).
- Do dopytania w ZOSP i HomerSafe: skąd pochodzi początkowa baza, jak wygląda weryfikacja, licencja i API, integracja z CPR.

## Miejskie, wojewódzkie i instytucjonalne

- **Warszawa, MCK 19115 / Stołeczne Centrum Bezpieczeństwa (sprawdzone 21.11.2026):** https://warszawa19115.pl/urzadzenia-aed. Mapa ma formularz „Zgłoś urządzenie AED”.
  - **Publiczny feed mapy (bez tokena):** `https://warszawa19115.pl/urzadzenia-aed?p_p_id=portalCKMaedportlet_WAR_portalCKMaedportlet&p_p_lifecycle=2&p_p_resource_id=get_bw_data&_portalCKMaedportlet_WAR_portalCKMaedportlet_type=published` zwraca GeoJSON FeatureCollection z **708 AED**, wszystkie w Warszawie. Jest to endpoint wewnętrzny portletu Liferay, nieudokumentowany, bez deklarowanej licencji.
  - Pola: defibrillator_id, location_object_name, location_description, location_street, location_building, location_postcode, location_floor, location_city, location_country, location_borough, location_district, device_availability (Tak 100 / Nie 511 / Ograniczona 95, wartości częściowo wolnym tekstem), device_location (wewnątrz 686 / na zewnątrz 20), device_public_access (Publiczny 608 / Prywatny 100), device_access_description (godziny wolnym tekstem), device_specifications, device_manufacturer (wolny tekst, np. „Philips”, „PHILIPS”, „Philips HS1”), application_status (wszystkie „5”, najpewniej opublikowane), application_date_last_verification (683/708; lata 2022–2026, 227 z 2022).
  - Uwaga techniczna: geometria `Point` ma współrzędne zagnieżdżone `[[lon, lat]]`, co jest niezgodne z RFC 7946.
  - **Oficjalny zbiór w katalogu Otwarte dane Warszawy:** https://dane.um.warszawa.pl/pl/catalogue/7bc32ffc-c2ac-4d32-83c9-b6f7a0b38de8 („Lokalizacja defibrylatorów (AED)”, dostawca: Stołeczne Centrum Bezpieczeństwa, CC BY, JSON, aktualizacja codziennie). Ten sam schemat. API: `POST https://dane.um.warszawa.pl/api/action/get_scb_lokalizacja_defibrylatorow`, nagłówek `Authorization: <token>`. Bez tokena zwraca 403. Token wymaga konta na portalu miasta. Opcjonalny parametr `defibrillator_id` zwraca też zdjęcie (base64). Opis pól: https://dane.um.warszawa.pl/files/scb_lokalizacja_defibrylatorow_pa.json , przykłady: …_pw.json
  - Na dane.gov.pl ten zbiór to ds 39512. Jest tam tylko link (harvest CKAN, ostatni import 21.11.2026).
  - Porównanie z OSM (bbox Warszawy): w OSM jest 1241 punktów. 353 z 708 punktów 19115 ma odpowiednik OSM w promieniu 50 m.
- **Kraków, „Krakowski IMPULS ŻYCIA AED”:** https://www.krakow.pl/aed---impuls-zycia/3992,artykul,mapa-aed.html ✅. Stan na 1.10.2026: ok. 80 punktów stałych i 25 w pojazdach (Straż Miejska, MPK, tramwaje). Jest lista HTML i mapa Google, bez pliku i bez podanej licencji.
- **Wrocław, Gdańsk, Poznań, Łódź, Bydgoszcz:** nie potwierdziliśmy miejskich zbiorów. Dla Bydgoszczy pojawia się wzmianka o „własnym rejestrze”. ❔
- **Województwa** (śląskie, łódzkie, małopolskie): są programy szkoleń i zakupów, ale nie znaleźliśmy zbioru ani mapy. ❔
- **Uczelnie:**
  - Politechnika Śląska ma wykaz AED w PDF (VI 2025).
  - Uniwersytet Śląski ma stronę HTML z lokalizacjami. ❔
- **Transport:** wiadomo tylko z prasy, że są AED w metrze w Warszawie (ok. 25), na Lotnisku Chopina oraz w autobusach ZTM w Katowicach. Listy punktów brak. ❔

## Zagraniczne i UE (kontekst)

- **Inne kraje:** Defikarte.ch (Szwajcaria), Defikataster i DEFImap (Niemcy), PulsePoint (Ameryka Północna). Żadne nie obejmuje Polski.
- **Francja, data.gouv.fr „Défibrillateurs publics”:** krajowy zbiór na licencji ODbL.
- **EENA „AED Mapping”** (eena.org/portfolio/aed-mapping/): zaleca europejski rejestr publicznych AED połączony z dyspozytorniami i stwierdza, że w UE nie ma wspólnego standardu.

## Wnioski faktograficzne

- Poza dane.gov.pl jedynym potwierdzonym otwartym i ogólnopolskim źródłem do pobrania jest OSM (ODbL, ok. 18,3 tys. punktów).
- Pozostałe źródła to mapy i aplikacje bez udostępniania danych i bez określonych warunków ponownego użycia.
- Poza tagami OSM nie znaleźliśmy wspólnego standardu pól.

## Do sprawdzenia

- Licencje i warunki: Pierwszy Ratownik, Fundacja Ratuj Życie, Warszawa 19115.
- Mapy producentów i dystrybutorów AED, Google i Apple Maps, Polska Rada Resuscytacji.
- Czy plik GeoJSON z OSM jest nadal odświeżany (repo `aed-mapa` jest zarchiwizowane).

## AED w pojazdach komunikacji miejskiej (stan 21.11.2026)

Pytanie: w których dużych miastach wiadomo, że w pojazdach są AED, i czy da się pobrać bieżącą lokalizację tych pojazdów.

| Miasto | AED w pojazdach (fakty) | Lista pojazdów z AED | Pozycje pojazdów na żywo (sprawdzone curl 21.11 ok. 16:53) |
|---|---|---|---|
| **Gdańsk** (GAiT / ZTM) | 278 z 503 pojazdów (pole `aed` w bazie pojazdów) | ✅ **TAK, maszynowo**: dane.gov.pl ds 1803, zasób 31843 „Baza pojazdów” | ✅ https://ckan2.multimediagdansk.pl/gpsPositions?v=2 (JSON, bez klucza, join po vehicleCode działa) |
| **Wrocław** (MPK) | ok. 32 AED w pojazdach (autobusy, tramwaje, radiowozy Nadzoru Ruchu). Od 06.2025 każdy nowy lub modernizowany pojazd ma AED, a pojazdy oznaczone są naklejką. Docelowo cała flota w 2–3 lata | ❌ brak listy | ⚠️ nieoficjalny endpoint `POST https://mpk.wroc.pl/bus_position` (działa bez klucza, zwraca linię i współrzędne, pole `k` = id kursu, **bez numeru taborowego**). Portal open data miasta zwraca 403 z curl |
| **Kraków** (MPK) | AED montowane w 17 tramwajach Krakowiak (WBO, pierwszy od 03.2026). 65 nowych Pesa (2028–29) fabrycznie z AED. Do tego zajezdnie i 8 radiowozów | ❌ brak listy numerów | ✅ GTFS-RT https://gtfs.ztp.krakow.pl/VehiclePositions_T.pb (127 tramwajów) i _A.pb (272 autobusy), bez klucza, `vehicle.label` = numer taborowy |
| **GZM / Katowice** (ZTM) | 2019: przetarg na 15 AED do autobusów linii lotniskowych (AED u przeszkolonych kierowców). Brak potwierdzenia stanu na 2024–26 | ❌ | nie sprawdzono |
| **Lublin** (MPK) | pilotaż: 1 autobus (Solaris 18 m) z AED | ❌ (numer w komunikacie ZTM) | nie sprawdzono |
| **Rzeszów** (MPK) | autobus nr boczny **100** (głównie linie 0A/0B) z AED + AED na przystanku Piłsudskiego 03 | z komunikatu: nr 100 | na Transitland jest feed RT Rzeszowa, niesprawdzony |
| **Szczecin** (ZDiTM) | projekt SBO 2026 „Bezpieczne serce Szczecina – AED w komunikacji miejskiej”, status „wybrany do realizacji”. Brak informacji o wdrożeniu | ❌ | ✅ GTFS-RT https://www.zditm.szczecin.pl/storage/gtfs/gtfs-rt-vehicles.pb (175 pojazdów) oraz JSON https://www.zditm.szczecin.pl/api/v1/vehicles (numer taborowy, model, niska podłoga, operator; **brak pola AED**) |
| **Warszawa** | Dane 19115 nie obejmują pojazdów, tylko perony metra, POP, ekspedycje ZTM i SKM. Według ZTM AED są na peronach metra i w pociągach SKM | ❌ | API api.um.warszawa.pl `busestrams_get` wymaga klucza (bez klucza: „Nieautoryzowany dostęp”) |
| **Poznań** | nie znaleziono informacji o AED w pojazdach | – | ✅ GTFS-RT https://www.ztm.poznan.pl/pl/dla-deweloperow/getGtfsRtFile?file=vehicle_positions.pb (346 pojazdów) |
| **Łódź, Bydgoszcz, Gdynia, Białystok, Toruń** | brak potwierdzenia AED w pojazdach (Bydgoszcz MZK: 4 AED w zajezdniach i budynkach) | – | nie sprawdzono |

Źródła: https://mpk.wroc.pl/komunikacja-miejska-z-sercem-defibrylatory-aed-w-pojazdach-mpk-wroclaw , https://www.wroclaw.pl/dla-mieszkanca/autobusy-tramwaje-mpk-wroclaw-beda-wyposazone-w-defibrylatory-aed , https://www.rmf24.pl/regiony/krakow/news-to-moze-uratowac-komus-zycie-nowosc-w-krakowskich-tramwajach,nId,8072678 , https://krknews.pl/wszystkie-zajezdnie-autobusowe-i-tramwajowe-mpk-z-defibrylatorami-aed/ , https://metropoliagzm.pl/2019/02/07/przetarg-na-defibrylatory/ , https://www.ztm.lublin.eu/pl/aktualnosci/autobus-wyposazony-w-defibrylator-wozi-mieszkancow-lublina.html , https://rzeszow24.pl/nowosc-w-rzeszowie-przystanek-i-autobus-mpk-z-defibrylatorami-aed-3064-00r2kc/ , https://bip.um.szczecin.pl/konsultacje/files/D3B7D7D2B44E4E869F63D07953A012AC/Formularz_projektu_Bezpieczne_serce_Szczecina_AED_w_komunikacji_miejskiej.pdf , https://www.telepolis.pl/artykuly/defibrylatory-w-komunikacji-miejskiej , https://bydgoszcz.eska.pl/bydgoskie-mzk-kupilo-nowe-defibrylatory-sprzet-bedzie-znajdowal-sie-w-zajezdniach-aa-TdSb-fCcA-AtzA.html
