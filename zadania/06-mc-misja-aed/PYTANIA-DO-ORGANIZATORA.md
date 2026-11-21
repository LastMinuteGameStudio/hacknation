# Pytania do organizatora: 06 Misja AED (MC DZD)

Gdzie pytać: stoisko danych lub Discord MC.
Plik zbiera pytania wszystkich sesji. Format: każda sekcja ma w nagłówku autora. Pierwsze sekcje, aż do „Formalne”, to lista Grzana (wcześniej w `zadania/WNIOSKI.md`). Nowe pytania dopisuj w sekcji ze swoim podpisem.
⭐ = najważniejsze, zadać na pewno.

Odpowiedzi organizatora wpisywać pod pytaniem jako `> **Odp. (data, kto):** ...`.

### Zgodność z dane.gov.pl (30%) (lista Grzana)
- ⭐ Co dokładnie jury rozumie przez „zgodność z zasadami działania portalu dane.gov.pl”? Czy chodzi o rozporządzenie Dz.U. 2022/2415, standard techniczny (5★, CSV RFC 4180, ISO 8601), standard API, DCAT-AP-PL, czy o coś innego? Czy jest lista, według której sprawdzacie?
- ⭐ Jaki poziom otwartości (liczba gwiazdek) jest oczekiwany od udostępnianego zbioru?
- Czy rozwiązanie ma faktycznie publikować dane na dane.gov.pl (konto dostawcy, API), czy wystarczy, że dane są przygotowane zgodnie z wymaganiami portalu? Czy na hackathon jest dostępne środowisko testowe lub konto dostawcy?
- Kto w zamyśle MC ma być dostawcą ogólnopolskiego zbioru: jedna instytucja (agregator) czy każdy dysponent osobno?
- Czy metadane zbioru (DCAT-AP-PL) są częścią oceny?

### Wzorcowy zakres danych (10%) (lista Grzana)
- ⭐ Czy MC ma listę pól, których oczekuje (np. godziny dostępności, stan techniczny, data przeglądu, kontakt)? Czy są pola obowiązkowe lub zakazane, np. ze względu na RODO (dane osoby odpowiedzialnej, telefon prywatny)?
- Czy zakres danych ma się opierać na istniejącym standardzie (np. tagi OSM `emergency=defibrillator`, schematy z innych krajów) czy ma być od zera?
- Czy w xlsx oczekujecie samego opisu pól (nazwa, typ, opis, wymagalność, przykład), czy także przykładowych rekordów?
- Czy kody TERC/SIMC i standard adresowy są wymagane?

### Źródła danych (lista Grzana)
- ⭐ Czy MC zna lub poleca konkretne źródła danych o AED poza dane.gov.pl (rejestry ratownicze, PRM/KSRG, wojewodowie, NFZ, aplikacje typu Ratunek)? Czy któreś są dla nas udostępnione na czas hackathonu?
- Czy wolno korzystać z danych na licencjach z warunkiem udostępniania na tej samej licencji (np. OpenStreetMap, ODbL) i łączyć je w jednym zbiorze z danymi CC0 / CC BY? Jaka licencja docelowego zbioru jest oczekiwana?
- Czy dopuszczalne jest pobieranie danych ze stron www dysponentów (scraping), jeśli nie mają one licencji otwartej?
- Ilu rekordów lub jakiego pokrycia (gminy, miasta, cała Polska) oczekujecie w prototypie?

### Prototyp i walidacja (lista Grzana)
- ⭐ Jak jury będzie uruchamiać prototyp: link do działającej wersji, repozytorium + instrukcja, Docker? Na jakich urządzeniach będzie sprawdzane?
- Kto jest głównym użytkownikiem prototypu: dysponent danych (który je przesyła), służby ratownicze czy obywatel szukający AED? Czy wszyscy trzej muszą być obsłużeni?
- ⭐ Jaką wersję i jaki poziom WCAG sprawdzacie (2.1 AA wg ustawy czy 2.2 AA)? Czy wymagana jest deklaracja dostępności?
- Co rozumiecie przez „zgodność z zasadami UX”? Czy jest konkretny standard, np. Gov.pl Design System?
- Czy można korzystać z zewnętrznych usług (mapy, geokodowanie, hosting), czy tylko z rozwiązań otwartych lub darmowych?

### Akcja, logo, księga znaku (25%) (lista Grzana)
- ⭐ Kto jest odbiorcą akcji: dysponenci danych (gminy, firmy, szkoły), obywatele czy oba?
- Czy logo ma współgrać z identyfikacją dane.gov.pl / MC / gov.pl? Czy są ograniczenia (np. zakaz używania godła, barw MC, symbolu serca ERC)?
- Czy wolno używać fontów i ikon na licencjach otwartych (OFL, CC BY) i czy trzeba to udokumentować w księdze znaku?
- Czy ocena logo dotyczy samego znaku, czy także materiałów promocyjnych (plakat, social media)?

### Formalne (lista Grzana)
- Czy lista kryteriów („przykładowe kryteria”) jest ostateczna, czy wagi mogą się zmienić?
- Jak długi będzie pitch lub prezentacja w finale i w jakiej formie składamy materiały (format, limit rozmiaru, gdzie)?
- Przeniesienie praw majątkowych: czy dotyczy także zebranego zbioru danych i kodu z bibliotekami open source?

### Użytkownicy i interakcje (dopisała sesja hacknation-wojtek-28)
- ⭐ Istnieje już przepływ danych OSM Polska → GUGiK (warstwa „Defibrylatory” na Geoportalu) → stanowiska dyspozytorów medycznych i mojeIKP „Na ratunek”. Czy MC chce, żeby nasze rozwiązanie wpinało się w ten przepływ (np. zasilało OSM lub korzystało z niego), czy ma powstać osobny zbiór na dane.gov.pl, który go uzupełnia?
- ⭐ Czy rozwiązanie ma obsługiwać głównie **dysponentów danych** (zgłaszanie i aktualizacja AED, publikacja na dane.gov.pl), czy obywateli szukających AED? Treść zadania wymienia jako użytkowników „służby ratownicze i każdego z nas”, a jednocześnie mówi o „zebraniu danych”.
- Na dane.gov.pl obywatel nie publikuje, może tylko zgłaszać uwagi. Czy wolno w zbiorze uwzględnić informacje od obywateli (np. „AED zamknięte”, „brak urządzenia”, zdjęcie), jeśli zatwierdzi je dysponent? Czy taka ścieżka zgłoszeń przez API portalu jest pożądana?
- Czy MC ma kontakt z dyspozytorami PRM lub LPR i wie, czy SWD PRM ma własną bazę AED? Jeśli tak, to w jakim formacie przyjmuje dane i czy nasz zbiór mógłby ją zasilać?
- Czy MC ma porozumienie lub kontakt z operatorami zamkniętych baz AED (Pierwszy Ratownik / ZOSP, Fundacja Ratuj Życie, Yanosik) albo planuje zachęcić ich do publikacji na dane.gov.pl?
- Czy pola o aktualności i stanie urządzenia (data ostatniego sprawdzenia, status „sprawny”, osoba lub instytucja odpowiedzialna) są pożądane w wzorcowym zakresie? Czy kontakt do opiekuna urządzenia jest dopuszczalny ze względu na RODO (np. tylko kontakt służbowy)?
- Czy informacje o fizycznym dostępie (np. szafka zamknięta, kod do szafki, numer do ochrony) mogą być publikowane w otwartym zbiorze, czy to dane wrażliwe?
- Czy w prototypie możemy pokazać fizyczne elementy kampanii, np. naklejkę z kodem QR na szafce AED prowadzącą do zgłoszenia statusu, czy ocena dotyczy tylko logo, hasła i księgi znaku?
- Czy MC planuje lub zna inicjatywy wprowadzenia obowiązku zgłaszania AED w Polsce? Dziś nie ma krajowego rejestru ani takich przepisów.

### Istniejące zbiory na dane.gov.pl (dopisała sesja hacknacja-27, inwentaryzacja)
- ⭐ Czy istniejące zbiory AED (Warszawa, Legionowo, Krosno, Przemyśl, Marki) mają być punktem wyjścia, czy rozwiązanie ma od nich nie zależeć? Każdy ma inny schemat, razem jest ich 5.
- Warszawa (ds 39512) publikuje na dane.gov.pl tylko link, a same dane są w API miasta z tokenem. Czy taka forma jest „zgodna z zasadami portalu”? Czy MC może dać nam dostęp do tych danych na czas hackathonu?
- Czy portal ma lub planuje walidację struktury plików względem wzorca, np. schematu kolumn? Dziś przechodzą uszkodzone pliki: w CSV z Marek cały wiersz jest w jednej kolumnie, a lat i lon są zamienione.
- Przemyśl deklaruje częstotliwość „Codziennie”, a na portalu leży kopia z 2024-11. Jak portal traktuje rozjazd między deklarowaną a faktyczną aktualizacją? Czy mechanizm automatycznego importu (jak XML deweloperów z instrukcji COI) jest dostępny także dla zbiorów AED?
- Istniejące zbiory mają licencje CC0 i CC BY 4.0. Czy MC oczekuje jednej licencji dla wzorcowego zbioru?
- Czy AED w pojazdach są w zakresie wyzwania? Przykład: ZTM Gdańsk ma pole `aed` w bazie pojazdów, ustawione w 278 z 503 pojazdów.
- Dysponenci prywatni (sklepy, firmy, parafie) nie są podmiotami zobowiązanymi. Czy MC przewiduje dla nich ścieżkę publikacji na dane.gov.pl? Portal przyjmuje „dane prywatne” (art. 2 pkt 13 ustawy).
- (Pola o stanie urządzenia: sprawność, data przeglądu, ważność elektrod i baterii. Pytanie połączone z pytaniem o aktualność w sekcji „Użytkownicy i interakcje”.)

### WCAG, UX, responsywność (dopisała sesja hacknation-kvba-43)
- ⭐ Jak jury sprawdza WCAG: narzędziami automatycznymi (jakimi? Lighthouse, axe, WAVE), ręcznym audytem czy na podstawie deklaracji lub samooceny zespołu?
- Czy wymagania WCAG obejmują też inne materiały: plik xlsx z zakresem danych, publikowane pliki z danymi i PDF z księgą znaku? Deklaracja dostępności dane.gov.pl wyłącza dane od dostawców zewnętrznych.
- Responsywność: czy wystarczy responsywna aplikacja webowa, czy oczekiwana jest też aplikacja mobilna? Ustawa z 2019 roku i deklaracja traktują aplikację mobilną osobno.
- Która perspektywa liczy się w ocenie: ustawy z 2019 roku (WCAG 2.1 AA) czy EAA, która przez EN 301 549 V4.1.1 idzie w stronę WCAG 2.2? V4.1.1 nie jest jeszcze cytowana w Dzienniku Urzędowym UE, a cytowanie jest spodziewane między 30.11 a 16.12.2026.
- (Pytanie o „zasady UX” i Gov.pl Design System jest już w sekcji „Prototyp i walidacja”.)

### Licencje a przeniesienie praw (dopisała sesja hacknacja-3f)
- ⭐ Czy wolno korzystać z danych OSM (ODbL, share-alike), skoro wynik ma przejść na MC na podstawie przeniesienia autorskich praw majątkowych? Zbiór pochodny z OSM musi zostać na ODbL, a tych praw nie możemy przenieść.
- ⭐ (dopisała sesja hacknation-kvba-43) Czy dane z OSM (ODbL, share-alike) mogą trafić do zbioru publikowanego na dane.gov.pl, skoro portal nie oferuje licencji ODbL? Backend portalu zna tylko CC0 1.0 i warianty CC 4.0.
- (dopisała sesja hacknation-kvba-43) Jakiej licencji MC oczekuje dla wzorcowego zbioru AED: CC0 1.0 czy CC BY 4.0? Istniejące zbiory: Krosno i Przemyśl mają CC0, Marki i Warszawa CC BY 4.0.
- (dopisała sesja hacknation-wojtek-28) Czy wzorcowy zbiór może zawierać pole z identyfikatorem obiektu OSM (osm_id) do deduplikacji? Według wytycznych OSMF powiązanie zbiorów kluczem może sprawić, że zbiór uzna się za pochodny od OSM i obejmie go ODbL.

### Warszawa i AED w pojazdach (dopisała sesja hacknacja, Grzan)
- Mapa 19115 pobiera listę 708 AED z publicznego, nieudokumentowanego endpointu, który nie ma podanej licencji. Oficjalne API Otwartych danych Warszawy (CC BY) wymaga tokena. Czy w prototypie wolno korzystać z tego endpointu, czy tylko z API z tokenem?
- Czy AED w pojazdach komunikacji miejskiej (np. Gdańsk: pole `aed` w bazie pojazdów + pozycje GPS na żywo) mieszczą się w zakresie zbioru, który MC chce mieć na dane.gov.pl, czy zbiór ma obejmować tylko stałe lokalizacje?

### Publikacja przez URL i import (dopisała sesja hacknacja, Grzan)
- ⭐ (Częściowo wyjaśnione w kodzie portalu, patrz RESEARCH.md: przy włączonej „Aktualizacji automatycznej” zasobu portal pobiera plik spod URL ponownie co dzień, tydzień lub miesiąc. Do potwierdzenia, czy produkcja działa tak samo i czy są limity.) Jak często portal odświeża zasoby dodane jako URL (§4 ust. 1 pkt 2 rozporządzenia)? Czy pobiera plik ponownie zgodnie z zadeklarowaną częstotliwością aktualizacji, czy trzyma kopię z momentu dodania? Przykład: Przemyśl (ds 4581) deklaruje „Codziennie”, a na portalu leży kopia z 2024-11, choć źródło się zmieniło.
- ⭐ Jak dostawca rejestruje URL pliku XML do automatycznego importu (jak u deweloperów, schemat COI `<p:datasets>`)? Przez panel, formularz czy zgłoszenie do administratora? Czy ten mechanizm jest dostępny dla zbiorów AED od gmin i innych instytucji?
- (AED w pojazdach: pytanie powyżej jest nieaktualne, bo zespół wyłączył je z zakresu, decyzja z 21.11.)

### Prezentacja: zrzuty z panelu dostawcy (dopisała sesja hacknation-wojtek, Wojtek)
- ⭐ Czy organizator może udostępnić konto testowe dostawcy na dane.gov.pl (albo zrzuty ekranu), żeby pokazać dodanie zasobu jako link z włączoną opcją „Aktualizacja automatyczna: dziennie”? Zrzuty potrzebujemy do instrukcji w aplikacji i do slajdów.

### Plik z wzorcowym zakresem danych (dopisała sesja hacknation-kvba-43)
- Co należy rozumieć przez „plik z wzorcowym zakresem danych do udostępniania danych w portalu” w wymaganiach formalnych? Czy chodzi o dane po stronie użytkownika, czy po stronie aplikacji?

## Pytania NIE do organizatora: do ZOSP i HomerSafe (Pierwszy Ratownik)
(dopisała sesja hacknacja-3f, która sprawdza to teraz)
- Skąd pochodzi początkowa baza AED (ponad 8500)? Jak wygląda weryfikacja zgłoszeń? Jaka jest licencja danych i czy jest API?
