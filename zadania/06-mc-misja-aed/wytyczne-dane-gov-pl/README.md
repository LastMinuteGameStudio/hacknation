# Wytyczne dane.gov.pl: pliki, linki i streszczenia reguł

Kryterium oceny w zadaniu 06 (30%) brzmi „zgodność z zasadami działania portalu dane.gov.pl”. Treść zadania wskazuje dwa źródła: bazę wiedzy (https://dane.gov.pl/pl/knowledgebase/useful-materials) i otwarty kod portalu (https://dane.gov.pl/source-code/). Ten katalog zbiera dokumenty z bazy wiedzy, które opisują te zasady.

Stan na 2026-11-21. Pliki pobrano z `cms.dane.gov.pl/documents/...` i `dane.gov.pl/media/...`. Strony portalu to SPA, więc ich treść zapisano jako JSON z publicznego CMS API (`https://cms.dane.gov.pl/api/pages/...`).

Ten plik zawiera wyłącznie streszczenia dokumentów, bez propozycji rozwiązań.

---

## Hierarchia: co jest wiążące

1. **Ustawa o otwartych danych** (Dz.U. 2021 poz. 1641) → `02-prawo/`
2. **Rozporządzenie RM w sprawie portalu danych** (Dz.U. 2022 poz. 2415). Określa metadane, sposoby udostępniania i automatyczną weryfikację → `02-prawo/`
3. **Standard techniczny i Standard API, czyli załączniki nr 2 i 3 do Programu otwierania danych 2021–2027** (uchwała RM nr 28, M.P. 2021 poz. 290). **Na tę wersję MC powołuje się dziś w FAQ i w przewodniku.** Pliki „standard-*-2020.pdf” to wcześniejsze wersje z 2020 r. → `02-prawo/program-otwierania-danych-MP-290.pdf`, s. 118–155
4. **Przewodnik dla dostawców danych v1.23** (16.07.2026). Opisuje panel, walidację, mapy i dane osobowe → `03-przewodniki/`
5. **Regulamin portalu** i strony o licencjach → `07-strony-portalu/`
6. **Precedensy „wzorcowego zakresu danych”.** MC przygotowało jednolity zakres dla wielu rozproszonych dostawców w dwóch sprawach: rzeczy znalezione (starostowie, 2026) i ceny mieszkań (deweloperzy, 2025–2026) → `05-…`, `06-…`

---

## 01-standardy/ (Standardy otwartości danych, wersje z 2020)

Strona: https://dane.gov.pl/pl/knowledgebase/useful-materials/standardy-otwartosci-danych (ostatnia zmiana 2020-11-12). Wersje z 2018 r. (PDF/ODT) są na tej samej stronie i ich nie pobierano.

| Plik | Źródło | Reguły (streszczenie) |
|---|---|---|
| `standard-techniczny-2020.pdf` | https://dane.gov.pl/media/ckeditor/2020/06/16/standard-techniczny.pdf | Poprzednik załącznika nr 2 do POD (treść prawie taka sama, streszczenie niżej przy POD). Pięć poziomów otwartości (★–★★★★★), wymagania dla formatów, formatowanie dat, liczb i wartości logicznych, adresy w osobnych polach, „adres uniwersalny”, CSV wg RFC 4180, CSVW dla 4★. |
| `standard-api-2020.pdf` | https://dane.gov.pl/media/ckeditor/2020/05/29/standard-api.pdf | Poprzednik załącznika nr 3 do POD: API REST, odpowiedzi wg JSON:API 1.0, kontekst JSON-LD (zalecany), tylko HTTPS, wersjonowanie semantyczne z wersją w URL (`/api/vXX/`), zasób `/version`, dokumentacja w OpenAPI 3.0 (zalecana), stronicowanie, filtrowanie, sortowanie, kody błędów. |
| `standard-prawny-2020.pdf` | https://dane.gov.pl/media/ckeditor/2020/05/29/standard-prawny.pdf | Rekomendacje prawne: udostępniać dane bezpłatnie, bez warunków albo na otwartych licencjach standardowych, unikać licencji wyłącznych, wyraźnie oznaczać dane, których nie wolno ponownie wykorzystywać. Zawiera też zalecenia dla twórców przepisów (słowniczek pojęć, obowiązek bieżącej aktualizacji, otwarte formaty). |
| `standard-bezpieczenstwa-2020.pdf` | https://dane.gov.pl/media/ckeditor/2020/06/01/standard-bezpieczenstwa.pdf | Udostępnianie danych a ochrona danych osobowych i tajemnic: anonimizacja, ryzyko ponownej identyfikacji, zmiana celu przetwarzania (test zgodności celów), wzory narzędzi oceny. |

## 02-prawo/

Strona: https://dane.gov.pl/pl/knowledgebase/useful-materials/prawo

| Plik | Źródło | Reguły (streszczenie) |
|---|---|---|
| `rozporzadzenie-RM-portal-danych-DzU-2022-2415.pdf` | https://cms.dane.gov.pl/documents/116/ | **Najważniejszy akt wykonawczy.** §4: dostawca udostępnia dane jako (1) plik przechowywany w portalu, (2) URL albo (3) z automatyzacją (import). §5: konto użytkownika (e-mail + hasło). Profil dostawcy zakłada administrator (MC) na wniosek elektroniczny, a konto edytora zawiera nazwę dostawcy, imię i nazwisko, służbowy telefon i e-mail. Do jednego profilu można podpiąć wiele kont. §6: metadane zbioru: tytuł, słowo kluczowe (≥1), opis, częstotliwość aktualizacji, kategoria, a „o ile dotyczą”: warunki, źródło URL, logotyp, oznaczenia danych badawczych, dynamicznych i o wysokiej wartości. Portal sam dodaje identyfikator, dostawcę, datę udostępnienia i datę aktualizacji. §7: metadane zasobu: tytuł, opis, dane na dzień, język, a „o ile dotyczą”: znaki umowne i lokalizacja (wg podziału terytorialnego). Portal sam dodaje identyfikator, format, datę, typ, źródło i **poziom otwartości**. §9: portal zapewnia wyszukiwanie, pobieranie, API, automatyzację i zgłaszanie uwag oraz propozycji danych przez użytkowników. §10: **automatyczna weryfikacja** kompletności metadanych (§6 pkt 1–5 i 9–11, §7 pkt 1–3 i 6), formatu danych i dostępności URL. |
| `ustawa-otwarte-dane-DzU-2021-1641.pdf` | https://cms.dane.gov.pl/documents/65/ | Ustawa z 11.08.2021 o otwartych danych i ponownym wykorzystywaniu ISP. Zasada bezwarunkowego udostępniania, wyjątki (art. 14–15: warunki, licencje). Art. 32–34: portal danych i obowiązki podmiotów zobowiązanych (art. 3). Art. 35–36: **dane prywatne** w portalu (podmioty spoza sektora publicznego). Art. 2: definicje danych dynamicznych, badawczych i o wysokiej wartości. Art. 37–38: pełnomocnicy ds. otwartości danych. Tekst jednolity: Dz.U. 2023 poz. 1524. |
| `nowa-ustawa-o-otwartych-danych-informacje.pdf` | https://cms.dane.gov.pl/documents/66/ | 7-stronicowe omówienie ustawy przygotowane przez MC (co się zmieniło, nowe pojęcia). |
| `program-otwierania-danych-MP-290.pdf` | https://cms.dane.gov.pl/documents/29/ | **Program otwierania danych 2021–2027 (POD).** Strona: https://dane.gov.pl/pl/knowledgebase/useful-materials/program-otwierania-danych-na-lata-2021-2027. **Zał. nr 2 „Standard techniczny” (s. 118–133)** jest dziś obowiązującym standardem: wymaga się / zaleca się / dopuszcza się (zob. sekcja „Standard techniczny: kluczowe reguły” niżej). **Zał. nr 3 „Standard API” (s. 134–155)**: REST + JSON:API ≥1.0, HTTPS, wersja w URL, OpenAPI ≥3.0, JSON-LD zalecany. |
| `raport-obowiazki-informacyjne-dane-osobowe.pdf` | https://cms.dane.gov.pl/documents/91/ | Raport Laboratorium Otwartych Danych o obowiązkach informacyjnych z art. 13 i 14 RODO przy publikacji danych osobowych na portalu. Strona: https://dane.gov.pl/pl/knowledgebase/useful-materials/udostepnianie-w-portalu-danegovpl-zasobow-zawierajacych-dane-osobowe |

Na stronie „Prawo” są też niepobrane: dyrektywa (UE) 2019/1024 (CELEX), stare akty (Dz.U. 2014/361, 2017/492, 2020/646) oraz raporty z ewaluacji ustawy (PL i EN).

## 03-przewodniki/

| Plik | Źródło | Reguły (streszczenie) |
|---|---|---|
| `przewodnik-dla-dostawcow-danych-1.23.pdf` | https://cms.dane.gov.pl/documents/283/ (strona: https://dane.gov.pl/pl/knowledgebase/useful-materials/nowy-przewodnik-dla-dostawcow-danych) | **Instrukcja publikacji, wersja 1.23 z 16.07.2026.** Konto: służbowy e-mail, potem e-mail do kontakt@dane.gov.pl o uprawnienia edytora. **Zbiór:** tytuł zrozumiały dla użytkownika, **bez daty w tytule**, dane z kolejnych lat w jednym zbiorze. Opis ≥20 znaków z odwołaniem do przepisów. Co najmniej 1 słowo kluczowe (najlepiej już istniejące w systemie). Kategoria (można kilka). Logotyp jpg/gif/png **z tekstem alternatywnym**. **Zalecana licencja CC0 1.0 (bez warunków).** Tłumaczenie EN tytułu i opisu (opcjonalne). **Zasób:** „dane na dzień” z opcją automatycznej aktualizacji dla URL i API, znaki umowne, lokalizacja (jednostki TERYT). **Walidacja trzystopniowa:** link, format pliku, dane (czy da się zbudować widok tabelaryczny). Widok tabelaryczny daje automatyczną konwersję xls/xlsx→csv i json-ld oraz csv→json-ld, ale tylko dla plików przechowywanych w portalu, nie zdalnych. **Weryfikacja jakości** kolumn regułami: liczba, REGON, NIP, KRS, adres uniwersalny, kod PNA, cecha adresu, telefon, wartość logiczna. **Mapa (rozdz. 10):** punkty z adresu uniwersalnego albo z **kolumn długość i szerokość geograficzna (WGS84, typ numeryczny)** + etykieta, albo z adresu (miejscowość, kod, opcjonalnie ulica i numer). Rozdz. 14: WCAG (deklaracja języka EN w opisach, tekst alternatywny logotypów). Rozdz. 15: dane osobowe (dostawca jest administratorem w rozumieniu RODO; DPIA, warunki ponownego wykorzystywania, obowiązek informacyjny, IOD; **nie publikować danych wrażliwych**). Rozdz. 16: wykazy danych chronionych. Lista ok. 70 rozpoznawanych formatów (m.in. csv, json, jsonld, xml, xlsx, ods, shp, geotiff, rdf, ttl). |
| `przewodnik-automatycznego-zasilania-danych-xml.pdf` | https://cms.dane.gov.pl/documents/225/ | **Import XML, wersja 1.02 (część ogólna).** Dostawca hostuje jeden plik XML opisujący **wszystkie** swoje zbiory i zasoby (zgodny z XSD `otwarte_dane_latest.xsd`) oraz plik `.md5` pod tym samym URL (hash małymi literami). Port 80 lub 443. Odpowiedź na żądanie HEAD musi mieć Content-Type `text/xml` albo `application/xml`. Wniosek do kontakt@dane.gov.pl: imię i nazwisko, dostawca, URL XML i MD5, częstotliwość (dzień, tydzień, miesiąc, kwartał). Zbiory i zasoby identyfikuje `extIdent`. Jego zmiana oznacza usunięcie i utworzenie obiektu od nowa. Obiekt, którego brakuje w XML, zostaje usunięty z portalu. `intIdent` pozwala przejąć obiekty dodane ręcznie. Nowe zasoby przechodzą standardową walidację. |
| `praktyczny-poradnik-otwieranie-danych.pdf` | https://cms.dane.gov.pl/documents/127/ | Zaktualizowany poradnik MC: nowe kategorie danych (dynamiczne, HVD, badawcze), polityki otwartości wg ustawy z 2021 i POD, gotowe narzędzia publikacji (dane.gov.pl, kronika.gov.pl). Adresowany do urzędów i podmiotów prywatnych. Strona: https://dane.gov.pl/pl/knowledgebase/useful-materials/podreczniki-dot-otwartosci-danych |
| `otwieranie-danych-podrecznik-dobrych-praktyk.pdf` | https://dane.gov.pl/media/ckeditor/2018/11/22/otwieranie-danych-podrecznik-dobrych-praktyk.pdf | Podręcznik z 2018 r.: czym są otwarte dane, otoczenie prawne (dostęp do informacji publicznej, ponowne wykorzystywanie, dane osobowe), portale i wizualizacje, organizacja pracy w urzędzie (zespół, polityka otwartości, schemat otwierania zbiorów). |

Linki bez pobierania (z tej samej strony): „Dane miejskie w praktyce. Podręcznik dla samorządów” https://danemiejskie.pl/publikacja/dane-miejskie-w-praktyce-podrecznik-dla-samorzadow/ oraz IRMiR „Zarządzanie danymi” http://obserwatorium.miasta.pl/wp-content/uploads/2021/10/IRMiR_Zarzadzaniedanymi_20210922-4.pdf

## 04-metadane-dcat/

| Plik / link | Źródło | Reguły (streszczenie) |
|---|---|---|
| `otwarte_dane_latest.xsd` | https://www.dane.gov.pl/static/xml/otwarte_dane_latest.xsd | **Schemat importu XML** (namespace `urn:otwarte-dane:harvester:1.13`). Elementy: dataset/resource, extIdent, intIdent, title i description (polish i english), updateFrequency, categories, tags, conditions, availability (local/remote), dataDate, isAutoDataDate, specialSigns, regions/terytIdent, hasDynamicData, hasHighValueData, hasResearchData, containsProtectedData, personalData, supplements. **Słowniki:** kategorie AGRI, ECON, EDUC, ENER, ENVI, GOVE, **HEAL** (zdrowie), INTR, JUST, REGI, SOCI, TECH, TRAN. Licencje: CC0 1.0, CC BY 4.0, CC BY-SA, BY-NC, BY-NC-SA, BY-ND, BY-NC-ND (**brak ODbL**). Częstotliwości: daily, weekly, monthly, quarterly, everyHalfYear, yearly, irregular, notPlanned. Znaki umowne: `- : . # X`. |
| `ekspertyza-dcat-ap.docx` | https://dane.gov.pl/media/ckeditor/2019/07/05/ekspertyza-dcat-ap.docx | Ekspertyza z 2019 r.: zasady opisu zbiorów zgodnie z DCAT-AP. Podstawa modelu metadanych portalu. Strona: https://dane.gov.pl/pl/knowledgebase/useful-materials/ekspertyza-dotyczaca-okreslenia-zasad-opisujacych-zbiory-danych-publicznych-zgodnych-z-dcat-ap |
| `model_metadanych.xlsx` | https://dane.gov.pl/media/ckeditor/2019/07/05/model_metadanych.xlsx | Model metadanych portalu w JSON-LD (dcat:Catalog, dataset, distribution) z opisem pól. |
| DCAT-AP-PL 2.1.0 (strona) | https://dane.gov.pl/dcat-ap-pl/ | Polski profil aplikacyjny DCAT-AP (klasy, słowniki, przestrzenie nazw), według którego portal eksportuje metadane. |

## 05-wzor-rzeczy-znalezione/ (precedens: wielu lokalnych dostawców, jeden wzór)

Strona: https://dane.gov.pl/pl/knowledgebase/useful-materials/udostepnianie-danych-dotyczacych-rzeczy-znalezionych-informacje-dla-starostow (stan na 15.05.2026, obowiązek z art. 15 ust. 5 ustawy o rzeczach znalezionych). Pakiet zawiera instrukcję profilu, wskazówki, instrukcję panelu, wzorcowy zakres danych (xlsx i csv) oraz szablon XML.

| Plik | Źródło | Reguły (streszczenie) |
|---|---|---|
| `instrukcja-profil-dostawcy-rzeczy-znalezione.pdf` | https://cms.dane.gov.pl/documents/277/ | Rejestracja na **imienny e-mail w domenie służbowej** (brak takiego adresu wymaga oświadczenia). Hasło: ≥8 znaków, mała i wielka litera, znak specjalny. Do profilu można podpiąć wielu edytorów, a odebranie uprawnień zgłasza się e-mailem. Wniosek o profil: nazwa, adres, WWW, ogólny e-mail i telefon, REGON, adres do e-Doręczeń, imię, nazwisko i e-mail edytora. |
| `wskazowki-przygotowania-danych-v1.0.pdf` | https://cms.dane.gov.pl/documents/278/ | **13 reguł arkusza** (skrót zał. 2 POD): jeden wiersz nagłówka bez pustych i powtórzonych nazw, bez scalonych komórek, jeden rekord w jednym wierszu, bez formuł agregujących i filtrów, bez tytułów i przypisów poza tabelą, bez formuł z odwołaniami zewnętrznymi, jednorodny typ w kolumnie, jedna wartość elementarna w kolumnie, spójny format, najlepiej jeden arkusz, **puste komórki wypełniać znakiem umownym „X”**, w CSV cudzysłowy wokół znaków specjalnych, daty `yyyy-mm-dd`. Nie publikować PDF ani obrazów. |
| `instrukcja-panel-rzeczy-znalezione.pdf` | https://cms.dane.gov.pl/documents/276/ | Krok po kroku w panelu: zbiór, metadane, dodanie pliku, publikacja. |
| `WYKAZ_RZECZY_ZNALEZIONYCH-dostawca_XYZ.xlsx` / `.csv` | https://cms.dane.gov.pl/documents/279/ , /280/ | **Wzorcowy zakres danych**: 6 kolumn (Lp., Opis ogólny, Data znalezienia, Miejsce znalezienia, Data przyjęcia, Uwagi). CSV z przecinkiem, daty ISO, „X” jako znak braku. Nazwa pliku zawiera nazwę dostawcy. |
| `RZECZ_szablon-xml-v1.14-2026-04-24.xml` | https://cms.dane.gov.pl/documents/275/ | Gotowy szablon XML: tytuł i opis PL/EN z placeholderem `{nazwa dostawcy}`, kategoria `REGI`, `updateFrequency=irregular`, `availability=local`, specialSign `X`, tag „Rzeczy znalezione”, extIdent. |

## 06-wzor-deweloperzy/ (precedens: dostawcy prywatni, codzienny import XML)

Strona: https://dane.gov.pl/pl/knowledgebase/useful-materials/udostepnianie-danych-dotyczacych-cen-mieszkan-informacje-dla-deweloperow (aktualizacja 10.11.2026) i https://dane.gov.pl/pl/knowledgebase/useful-materials/wzorcowe-dokumenty-elektroniczne-suzace-do-realizacji-obowiazkow-deweloperow-mieszkaniowych-11112026 (wzory z rozporządzenia MC, Dz.U. 2026 poz. 1489).

| Plik | Źródło | Reguły (streszczenie) |
|---|---|---|
| `instrukcja-profil-dostawcy-i-uprawnienia-edytora.pdf` | https://cms.dane.gov.pl/documents/223/ | Ten sam proces co dla starostów, w wersji dla firm. |
| `wskazowki-przygotowania-danych-v1.0.1.pdf` | https://cms.dane.gov.pl/documents/234/ | Te same reguły arkusza co w 05 (wersja dla deweloperów). |
| `instrukcja-panel-administracyjny-1.0.2.pdf` | https://cms.dane.gov.pl/documents/253/ | Skrócona instrukcja panelu (stan na 30.09.2025). |
| `instrukcja-zasilania-XML-dla-deweloperow-1.0.6.pdf` | https://cms.dane.gov.pl/documents/256/ | Import XML w wersji szczegółowej: tabela elementów z wymagalnością, `extIdent` dokładnie 36 znaków (nadaje go dostawca, unikalny w pliku, po nadaniu **nie zmieniać**), kategoria ECON, `availability` local albo remote, szablon nazewnictwa zasobów z datą. |
| `szablon-xml-v1.14-2025-11-12.xml`, `przyklad-3-kolejne-publikacje-v1.14.xml` | https://cms.dane.gov.pl/documents/254/ , /255/ | Szablon i przykład dopisywania kolejnych dziennych zasobów do jednego zbioru. |
| `dane-niezbedne-do-automatyzacji.docx` | https://cms.dane.gov.pl/documents/250/ | Formularz wniosku o uruchomienie importu XML: zgłaszający, nazwa dostawcy (zgodna z profilem), URL XML i MD5, e-maile edytorów, częstotliwość. |
| `rekomendacje-max-liczba-zasobow.pdf` | https://cms.dane.gov.pl/documents/268/ | **Maks. 1000 zasobów (`<resource>`) w jednym pliku XML.** Po przekroczeniu tej liczby uruchamia się nowe źródło, a stare zostaje dezaktywowane. Nowe źródło nie powinno dublować danych ze starego. |
| `wzorcowy-zakres-danych-ceny-mieszkan.xlsx` / `.csv` | https://cms.dane.gov.pl/documents/238/ , /239/ | Wzorcowy zakres z 2025 r.: jeden arkusz, nagłówki opisowe po polsku, przykładowe wiersze, **adres rozbity na województwo, powiat, gminę, miejscowość, ulicę, numer i kod**, NIP, REGON i KRS jako ciągi cyfr. |
| `wzor-2026-ceny-ofertowe.csv` / `.json` / `.xml` | https://cms.dane.gov.pl/documents/289/ , /290/ , /292/ (xlsx: /291/) | Wzory z rozporządzenia MC z 10.11.2026. **Uwaga: CSV ma separator „;” i BOM**, więc odbiega od RFC 4180 z zał. 2 POD. Nazwa pliku według wzoru `ceny-ofertowe-mieszkan-dewelopera-{nazwafirmy}-{YYYY-MM-DD}`. |

Wybrane fakty z FAQ na stronie deweloperów:
- Brak kont testowych dla dostawców.
- Pierwszy import po włączeniu źródła przez administratora, kolejne raz dziennie.
- Formaty maszynowe to xlsx, csv, xml, json. PDF i DOC są niedopuszczalne.
- Jeden zbiór, a w nim osobny plik na każdy dzień.
- MC **nie** ustala zakresu danych (wynika on z ustawy dziedzinowej), ale publikuje „wzorcowy zakres danych”, żeby zapewnić zgodność ze standardem i spójność danych.
- Od 25.09.2025 dla plików deweloperów nie jest generowany widok tabelaryczny ani konwersja do csv i json-ld (ograniczenie dotyczy tylko tej kategorii, z powodu wolumenu).
- Publikacja może się opóźniać przy dużym napływie danych.

## 07-strony-portalu/ (zrzuty JSON z CMS API)

| Plik | Strona | Reguły (streszczenie) |
|---|---|---|
| `regulations.json` | https://dane.gov.pl/pl/regulations | **Regulamin portalu** (2025). Dostawca jest administratorem swoich danych i odpowiada za ich jakość, aktualność i kompletność (§11). Edytora wyznacza dostawca, a uprawnienia nadaje MC (§7). Profil dostawcy wymaga pełnej nazwy, adresu, REGON, telefonu, e-maila, ESP i adresu do e-Doręczeń (§8). Użytkownicy mogą zgłaszać uwagi do danych i propozycje nowych danych (§9). Administrator może zablokować konto edytora po 2 latach nieaktywności. „Inny podmiot” (spoza art. 3 ustawy) również może być dostawcą. |
| `opis-warunkow-i-licencji-dla-dostawcow-sektora-publicznego.json` | https://dane.gov.pl/pl/page/opis-warunkow-i-licencji-dla-dostawcow-sektora-publicznego | Zasada bezwarunkowości. **Rekomendowana licencja CC0 1.0** (zakładki „Warunki” nie wypełnia się). CC BY 4.0 odpowiada warunkom z art. 15 ust. 1 pkt 1–3. Pozostałe licencje CC tylko wtedy, gdy dostawcy przysługują prawa własności intelektualnej (np. do bazy danych). |
| `opis-warunkow-i-licencji-dla-dostawcow-sektora-prywatnego.json` | https://dane.gov.pl/pl/page/opis-warunkow-i-licencji-dla-dostawcow-sektora-prywatnego | To samo dla danych prywatnych (art. 36 ustawy). Rekomendacja: bez warunków (CC0). |
| `udostepnianie-w-portalu-danegovpl-zasobow-zawierajacych-dane-osobowe.json` | https://dane.gov.pl/pl/knowledgebase/useful-materials/udostepnianie-w-portalu-danegovpl-zasobow-zawierajacych-dane-osobowe | Dane osobowe: dostawca jest administratorem w rozumieniu RODO, zalecana DPIA, warunki ponownego wykorzystywania, obowiązek informacyjny, konsultacja z IOD. |
| `standardy-otwartosci-danych.json`, `faq.json`, `udostepnianie-danych-*.json` | strony bazy wiedzy | Kopie treści stron, z których pochodzą powyższe pliki. |
| `deklaracja-dostepnosci.json`, `o-serwisie.json` | https://dane.gov.pl/pl/page/deklaracja-dostepnosci , /o-serwisie | Deklaracja dostępności portalu (WCAG) i opis portalu. |

---

## Standard techniczny (zał. nr 2 do POD 2021–2027): kluczowe reguły

Źródło: `02-prawo/program-otwierania-danych-MP-290.pdf`, s. 118–133. Słowa „wymaga się / nie dopuszcza się” oznaczają reguły bezwarunkowe. Odstępstwo od „zaleca się / nie zaleca się” wymaga uzasadnienia w dokumentacji.

**Poziomy otwartości (portal wylicza je sam):**
- ★: PDF, JPG, PNG, TXT, nieustrukturyzowany HTML
- ★★: XLS, DOC, XLSX, DOCX (XLSX „nie zalecany” powyżej ★★)
- ★★★: CSV (zalecany), JSON (zalecany), XML (dopuszczalny), ODS, DBF, HTML. Dane przestrzenne wektorowe (**GeoJSON, KML, GML, SHP, GPX**) też są na ★★★.
- ★★★★ / ★★★★★: RDF, JSON-LD, Turtle, CSV + CSVW. ★★★★★ oznacza dodatkowo powiązania z innymi danymi.
- Nie zaleca się publikowania na ★. Dane na ★★★ i wyżej zaleca się udostępniać przez API.

**Formatowanie (wszystkie poziomy):**
- wartości logiczne `true`/`false`
- kropka dziesiętna, bez separatorów tysięcy
- daty `yyyy-mm-dd`, data z czasem `yyyy-mm-ddThh:mm` albo `yyyy-mm-dd hh:mm:ss` (ISO 8601)
- maksymalna granulacja: nie łączyć kilku danych w jednym polu

**Arkusz xls/xlsx:**
- jeden wiersz nagłówka
- zakaz: scalonych komórek, rekordu w kilku wierszach, opisów poza tabelą, formuł agregujących i filtrów, odwołań zewnętrznych
- jeden typ danych w kolumnie, jedna wielkość elementarna w kolumnie, zgodność z maską
- unikać dywizów, które mogą zostać odczytane jako operator
- zalecany jeden arkusz

**Identyfikatory:**
- REGON: 9 albo 14 cyfr
- NIP: 10 cyfr
- KRS: 10 cyfr
- bez spacji i łączników
- telefon (zalecenie): 9 cyfr, dopuszczalny prefiks `+`

**Adres:**
- **wymaga się** osobnych pól: ulica, numer budynku, kod pocztowy, miejscowość (opcjonalnie cecha i nr lokalu)
- nazwy literalnie zgodne z TERYT (ULIC, SIMC, TERC)
- **zaleca się „adres uniwersalny”**: `PNA|TERC(6)|SIMC podst.(7)|SIMC(7)|ULIC(5)|x|y|nr budynku`
- systemy do wprowadzania adresów powinny blokować adresy nieistniejące (wybór ze słowników TERYT i PRG). Portal udostępnia aplikację do sprawdzania adresu uniwersalnego.

**CSV:**
- ★★★: RFC 4180 zalecane, ★★★★: wymagane ściśle (CRLF, przecinek, cudzysłowy, UTF-8)
- dokładnie jeden wiersz nagłówka
- zakaz kolumn bez nagłówka i powtórzonych nagłówków
- równa liczba komórek w każdym wierszu
- **zakaz całkowicie pustych kolumn i wierszy**
- wiersze niezależne: nie zostawiać pustych miejsc zamiast powtórzonej wartości
- ★★★★: wymagany CSVW (W3C Model for Tabular Data and Metadata)

**JSON:**
- ★★★: RFC 8259, a dla API JSON:API
- ★★★★: JSON-LD z pełnym kontekstem (kontekst w nagłówku HTTP)

**XML:**
- ★★★: dowolna poprawna struktura
- ★★★★: przestrzenie nazw i schematy

**Dane przestrzenne:** dobre praktyki „Spatial Data on the Web Best Practices” (W3C), usługi WMS, WMTS, WFS i ATOM oraz INSPIRE dla zbiorów przestrzennych.

---

## Rozbieżności między dokumentami

1. **Puste wartości.** Zał. 2 POD zakazuje całkowicie pustych kolumn i wierszy, ale o pojedynczych pustych komórkach nie mówi wprost. Wskazówki dla starostów (2026) każą wpisywać w puste komórki znak umowny „X” i deklarować go w metadanych (specialSign `X` w XSD).
2. **Separator CSV.** Zał. 2 POD: przecinek (RFC 4180). Wzory dla deweloperów z rozporządzenia MC z 2026 r.: średnik i BOM.
3. **Standard techniczny 2020 a zał. 2 POD 2021.** MC w FAQ i w przewodniku 1.23 odsyła do załącznika nr 2 POD, a pliki z 2020 r. nadal leżą na stronie „Standardy otwartości danych”.
