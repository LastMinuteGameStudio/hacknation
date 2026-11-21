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
- **Yanosik:** użytkownicy mogą zgłaszać AED. ❔
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
- Do dopytania w ZOSP i HomerSafe: skąd pochodzi początkowa baza, jak wygląda weryfikacja, licencja i API, integracja z CPR.

## Miejskie, wojewódzkie i instytucjonalne

- **Warszawa, MCK 19115:** https://warszawa19115.pl/urzadzenia-aed. Mapa ładuje się dynamicznie i ma formularz „Zgłoś urządzenie AED”. Ok. 517 urządzeń (placówki, metro, autobusy, SKM, Straż Miejska). ❔ Na api.um.warszawa.pl nie znaleźliśmy zbioru AED.
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
