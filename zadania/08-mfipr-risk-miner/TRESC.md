<!-- tekst wyciągnięty automatycznie z: MFiPR - Pełna treść zadania konkursowego.pdf -->

1 
RISK MINER  
inteligentna baza doświadczeń inwestycji publicznych 
Błędnie oszacowane ryzyka budżetów i opóźnień przy inwestycjach publicznych, generują potężne 
straty i koszty społeczne. Wyzwanie „Risk Miner” pozwoli nam wyciągnąć lekcje z bogatej, ale 
rozproszonej dokumentacji zrealizowanych kontraktów. Dzięki ogólnodostępnemu narzędziu 
sprzężonemu z rosnącą bazą danych, sektor publiczny będzie mógł szybciej zrozumieć, co 
wpłynęło na przebieg inwestycji, oraz skuteczniej wykorzystywać tę wiedzę przy planowaniu 
kolejnych projektów. Dodatkowo moduł monitorowania ich przebiegu wychwyci zdarzenia ryzyk 
zanim zmaterializują się one z pełną mocą. Uniknięte błędy przy inwestycjach to olbrzymie 
oszczędności w skali całego budżetu. 
1. Wprowadzenie 
Jako Ministerstwo Funduszy i Polityki Regionalnej wspieramy przygotowanie i realizację inwestycji 
publicznych oraz odpowiadamy za system wdrażania Funduszy Europejskich. Zgłaszający 
wyzwanie Departament Partnerstwa Publiczno-Prywatnego rozwija narzędzia i standardy 
wspierające przygotowanie złożonych przedsięwzięć infrastrukturalnych. W praktyce, 
podejmowane przez podmioty publiczne decyzje dotyczące zakresu, harmonogramu, budżetu 
i podziału ryzyk w treści umów, wpływają później na koszty inwestycji oraz jakość usług 
publicznych przez wiele lat. 
Wraz z setkami tysięcy zrealizowanych inwestycji, jednostki publiczne nabierają doświadczeń, 
wyciągają wnioski, wypracowują schematy i starają się optymalizować efekty zamówień. Niestety 
pamięć instytucjonalna oparta na doświadczeniu poszczególnych jednostek jest mocno 
rozproszona, oparta na wiedzy poszczególnych uczestników, a ograniczona wymiana informacji 
pomiędzy jednostkami w praktyce mocno ogranicza dostęp do wiedzy. 
Postępująca cyfryzacja pozwoliła Administracji na zgromadzenie milionów dokumentów 
zawierających opisy projektów, zamówień i kontraktów, lecz wiedza o ich rzeczywistym przebiegu 
wciąż pozostaje rozproszona. Podstawowe dane o projektach znajdują się w bazach 
poszczególnych instytucji, informacje o postępowaniach i wykonaniu umów w BZP, TED lub Bazie 
Konkurencyjności, dane techniczne w bazach sektorowych, a ustalenia dotyczące zmian, zdarzeń 
i problemów oraz ich przyczynach znajdziemy w aneksach, raportach i wynikach kontroli. 
Poszczególne źródła opisują różne poziomy tej samej inwestycji: jeden projekt może obejmować 
wiele zamówień, kontraktów, zmian oraz zdarzeń wpływających na koszt i czas. 
Zakładamy, że dane te można skutecznie połączyć, a uzyskany obraz wykorzystać do systemowego 
wyciągania wniosków i wymuszenia stosowania efektywnych i skutecznych rozwiązań. Potrzebne 
jest rozwiązanie, które wykonywałoby tę pracę automatycznie i tworzyło z wyników spójną, stale 
zasilaną bazę przypadków. 
Utworzona w ten sposób baza danych to tylko środek do właściwego narzędzia skierowanego do 
końcowego użytkownika. Osoba przygotowująca nową inwestycję powinna móc opisać 
przedsięwzięcie przekazując jego wstępne dokumenty lub nawet opisując je językiem naturalnym, 
a w rezultacie otrzymać zestawienie i porównanie sektorowe wraz z dobranymi przykładami 
zrealizowanych już inwestycji. Informacje o szacowanych kosztach i czasie, co wydarzyło się 
w podobnych inwestycjach, jakie odchylenia kosztu i czasu w nich wystąpiły, co je spowodowało, 
jakie zapisy umowne lub działania ograniczały problemy i które kwestie należy sprawdzić przed 
uruchomieniem nowego projektu. 
2 
2. Wyzwanie 
Zadaniem zespołu jest stworzenie rozwiązania, które zbuduje cyfrową pamięć instytucjonalną 
Administracji Publicznej, a następnie udostępni narzędzia, które pozwolą z niej efektywnie 
korzystać. 
Risk Miner ma połączyć trzy zadania: 
• automatycznie budować z rozproszonych źródeł empiryczną bazę doświadczeń, 
• identyfikować udokumentowane zdarzenia wpływające na realizację projektów oraz fragmenty 
dokumentów mogące świadczyć o ryzyku, zgodnie z katalogami eksperckimi, i przedstawiać 
wyniki do eksperckiej weryfikacji, 
• udostępniać wiedzę i precyzyjnie wspierać przygotowanie kolejnych inwestycji. 
Uczestnicy otrzymają od nas pełen pakiet wiedzy eksperckiej z zakresu pilotażowego sektora, 
obejmujący katalog zdarzeń, opisy typów inwestycji, wskazówki dotyczące interpretacji danych 
i metodyki (czego szukać, gdzie szukać, co z czego wynika itd.) oraz FAQ, a także dane około 20 
wybranych projektów m.in. z naszej CST2021 (baza projektów finansowanych z funduszy UE), 
zawierające publiczne informacje i identyfikatory potrzebne do łączenia źródeł. 
3. Oczekiwany rezultat 
Rezultatem ma być funkcjonalny prototyp Risk Minera, który z dostarczonych rekordów (w postaci 
pliku .xls) i danych odnalezionych w źródłach publicznych zbuduje ustrukturyzowaną bazę 
projektów, a każdy dodany projekt przeanalizuje pod kątem występujących zdarzeń ryzyka. 
Interfejs do powstałej w ten sposób bazy danych musi umożliwić analizę nowej inwestycji. 
Pilotaż obejmie sektor wodociągowo-kanalizacyjny, w którym projekty mają powtarzalne elementy 
techniczne, mierzalne rezultaty i liczne publiczne źródła danych. Rozwiązanie powinno być od 
początku projektowane tak, aby można je było rozszerzać o następne projekty, dokumenty, źródła 
i sektory 
Automatyczne zasilanie bazy. Rozwiązanie ma umożliwić wgrywanie dodatkowych danych 
z plików oraz ma samodzielnie wyszukać powiązane dane z innych publicznie dostępnych źródeł, 
co najmniej z BZP/e-Zamówienia oraz w dodatkowych źródłach, np.TED, BK2021, KPOŚK/AKPOŚK, 
BIPy konkretnych samorządów lub publikacje NIK. 
Zespół buduje własne mechanizmy pobierania, normalizacji i aktualizacji danych. Do łączenia 
rekordów można używać wspólnych identyfikatorów, takich jak numer ogłoszenia BZP/TED, numer 
projektu CST, NIP lub OCID. Gdy jednoznacznego klucza nie ma, rozwiązanie może dopasować 
rekordy na podstawie nazwy, zamawiającego, miejsca, CPV, wartości i dat oraz pokazać podstawę 
i poziom pewności dopasowania. 
W przypadku pojawienia się lub wgrania nowych dokumentów, system powinien mieć możliwość 
ponownej analizy wpływu na stan inwestycji i wniosków. 
Ustrukturyzowana baza przypadków. Prototyp powinien budować bazę danych, która będzie 
zachowywać relacje między projektem, zamówieniami, kontraktami, ogłoszeniami, zmianami, 
dokumentami, kosztami, terminami oraz zdarzeniami wpływającymi na realizację. Każdy ważny 
rekord i wniosek musi prowadzić do źródła. 
Ekstrakcja informacji o ryzykach. Rozwiązanie ma identyfikować udokumentowane zdarzenia 
wpływające na realizację projektów oraz fragmenty dokumentów mogące świadczyć o ryzyku, 
zgodnie z katalogami eksperckimi, i przedstawiać wyniki do eksperckiej weryfikacji. Katalog 
zdarzeń ma charakter otwarty: rozwiązanie powinno umożliwiać proponowanie dodatkowych 
3 
kategorii do zatwierdzenia przez eksperta. Określić skutki mierzone w czasie opóźnień i wzroście 
kosztów. Określić możliwe przyczyny zajścia tych zdarzeń. Podać podjęte działania zaradcze 
i określić ich skuteczność (jeśli możliwe). 
Człowiek w procesie. Dbamy o wiarygodność informacji, aby uniknąć utrwalenia błędnych 
danych, przy budowaniu bazy, każde zdarzenie i każdy wyciągnięty wniosek wymaga zatwierdzenia 
przez eksperta. 
Panel eksperta musi dawać możliwość przeglądu, wpisu, edycji i modyfikacji wszystkich danych 
wejściowych. Od eksperckich opisów sektorów, tabel wyboru, podejmowania decyzji, modyfikacji 
połączeń, oceny wiarygodności, po mozliwość oznaczania materiałów jako wzorcowych. 
System powinien zapisywać decyzje ekspertów i wykorzystywać zatwierdzone przykłady oraz reguły 
w kolejnych analizach. 
Analiza nowej inwestycji. Użytkownik opisuje planowany projekt albo przekazuje jego wstępne 
dokumenty. System wyszukuje i przedstawia najbardziej zbliżone zakończone inwestycje i wyjaśnia 
podobieństwo. Wynik może obejmować prognozy kosztów i czasu trwania inwestycji wraz 
z możliwymi odchyleniami wynikającymi z potencjalnych zdarzeń ryzyka. System przekazuję listę 
zagadnień do analizy, rekomendowane działania oraz propozycje zapisów oparte na wiedzy i 
odnalezionych przypadkach. System powinien wyraźnie odróżniać dane źródłowe, obliczenia 
i wnioski modelu aby ułatwiać pracę ekspertowi. 
Rozwój. Możliwości i potrzeby dodatkowych funkcji są ograniczone jedynie nasza inwencją. 
Zachęcamy do twórczego podejścia. Dla przykładu, dodatkowym atutem będzie pokazanie 
automatycznej aktualizacji bazy w oparciu o moduł monitorowania dla projektów o statusie 
nieukończonym, który po pojawieniu się nowego dokumentu albo ogłoszenia rozpoznaje zmianę 
istotną dla trwającej inwestycji. 
Przystępność. Użytkownikami końcowymi są osoby przygotowujące i oceniające inwestycje 
w administracji rządowej, samorządowej i podmiotach publicznych. Rozwiązanie powinno być 
zrozumiałe dla specjalisty merytorycznego bez kompetencji programistycznych. 
4. Wymagania formalne 
Projekt przesyłany do oceny powinien zawierać: 
• Dostęp do działającego prototypu. Uczestnicy powinni udostępnić link do uruchomionej 
aplikacji, umożliwiający samodzielne przetestowanie jej funkcjonalności przez jury (w 
przypadku uzasadnionego braku technicznej możliwości udostępnienia aplikacji online 
dopuszcza się udostępnienie wersji uruchomionej lokalnie), 
• szczegółowy opis i tytuł projektu, 
• prezentację w formacie PDF (maksymalnie 10 slajdów), 
• repozytorium kodu, 
• film umieszczony w dostępnym, otwartym repozytorium (link), trwający maksymalnie 3 minuty 
i prezentujący projekt. 
Dodatkowo może zawierać: 
• zrzuty ekranu, 
• opis/makiety funkcji, których nie udało się w pełni zaimplementować podczas hackathonu. 
4 
5. Wymagania techniczne 
Nie narzucamy języka programowania, konkretnego modelu ani dostawcy usług (no prawie). 
Oceniany będzie efekt, sprawdzalność wyników i możliwość dalszego rozwoju. 
Model. Ustawiamy w konfiguracji, tak żeby zmiana modelu  nie wymagała zmian w kodzie. 
Poprosimy o plik z przykładową konfiguracją, z którego wynika, co trzeba ustawić, żeby uruchomić 
rozwiązanie z własnym kluczem. Informację, gdzie przetwarzane są dane (lokalnie, UE, poza UE), 
licencja. 
Integracje. Prototyp powinien wykorzystywać plik wyeksportowanych danych dostarczonych przez 
Organizatora, inne pliki wsadowe z danymi w popularnych formatach (.doc .xls .pdf .csv), publiczny 
odczyt danych BZP/e-Zamówień oraz dodatkowych źródeł spośród TED, BK2021, KPOŚK/AKPOŚK, 
NIK, KIO i innych uzasadnionych baz publicznych. 
Łączenie po identyfikatorach. Podstawową metodą powinno być dopasowanie po numerze 
ogłoszenia BZP/TED, numerze projektu CST, NIP/REGON lub OCID. Format numerów należy 
normalizować i weryfikować z danymi podmiotu oraz zamówienia. 
Model danych. Baza powinna odwzorowywać strukturę projektu i jego realizacji. Jeden projekt 
może obejmować wiele postępowań o udzielenie zamówienia, a każde postępowanie może być 
powiązane z wieloma ogłoszeniami oraz jednym lub większą liczbą kontraktów. 
Model powinien rozdzielać co najmniej: projekty, postępowania, ogłoszenia, kontrakty, zmiany 
kontraktów, zdarzenia wpływające na realizację, dane o kosztach i terminach oraz dokumenty 
i źródła. Powiązania między rekordami muszą umożliwiać odtworzenie przebiegu projektu 
i wskazanie źródła każdej istotnej informacji. 
Obsługiwane dane. Prototyp powinien przetwarzać dane tabelaryczne oraz co najmniej 
dokumenty w formacie DOCX i PDF z warstwą tekstową. Dodatkowym atutem będzie OCR skanów 
i obsługa innych formatów. 
Analiza podobieństwa. Wynik wyszukiwania podobnych inwestycji powinien łączyć dane 
strukturalne z treścią opisów i dokumentów oraz wyjaśniać, które cechy przesądziły 
o podobieństwie. 
Wnioski i prognozy. Przedziały odchyleń kosztu i czasu, flagi oraz rekomendacje muszą wynikać 
z danych i wskazanych przypadków. Należy podawać liczebność próby i informować 
o niepewności. 
Identyfikowalność. Każdy rekord, powiązanie i kluczowy wniosek powinny zawierać identyfikator 
źródła, link, datę pobrania oraz w przypadku dokumentu, stronę lub fragment uzasadniający wynik, 
informacje o zatwierdzeniu przez eksperta i historię edycji tych zatwierdzeń (jeśli zasadne). 
Struktura wyniku. Wyniki muszą być zapisywane jako rekordy możliwe do filtrowania, aktualizacji 
i eksportu, np. do JSON lub CSV; odpowiedź wyświetlana wyłącznie w oknie rozmowy nie spełnia 
wymagania. 
Bezpieczeństwo i wdrażalność. Należy rejestrować źródła i operacje, ograniczać przetwarzanie 
danych, opisać użyte usługi i licencje oraz unikać trwałego uzależnienia od jednego dostawcy. 
Architektura musi umożliwiać dalsze skalowanie liczby projektów i sektorów. Każda rekomendacja 
powinna prowadzić do danych lub dokumentu źródłowego, a prognoza powinna pokazywać 
poziom pewności. 
Skalowalność. Zaprezentowane rozwiązanie nie może działać na zasadzie manualnego importu 
i powiązania dostarczonych danych testowych. Proponowane przez system wpisy do bazy danych, 
muszą powstawać automatycznie na podstawie przetworzenia materiałów. 
5 
6. Sposób testowania i/lub walidacji 
W pierwszej kolejności będziemy oceniać faktyczne działanie rozwiązania. Możliwość 
uruchomienia i zaprezentowania na żywo na dostarczonym zbiorze testowym. 
Demonstracja dwóch ścieżek. Pokaz importu i automatycznego wzbogacenia co najmniej 
jednego projektu oraz analiza przykładowej nowej inwestycji w interfejsie wraz z eksportem 
uzyskanych rekordów/wyników. 
Rozwiązania zostaną sprawdzone na dostarczonych projektach wodociągowo-kanalizacyjnych 
oraz na opisie lub dokumentach przykładowej nowej inwestycji. Dostarczone dane mogą zawierać 
błędy/braki, których Organizator będzie świadomy, ale nie będą one bezpośrednio wskazane. 
Test integracji. Zespół uruchamia pobieranie danych z publicznych źródeł. Oceniane będą 
poprawność zapytań, liczba prawidłowo odnalezionych rekordów oraz możliwość ponownego 
uruchomienia procesu bez ręcznego wpisywania wyników. 
Test łączenia. Wybrane powiązania zostaną porównane z zestawem referencyjnym. 
Test kompletności przypadku. Juror sprawdzi, czy system prawidłowo łączy projekt z jego 
zamówieniami, ogłoszeniami, wynikiem, zmianami i wykonaniem umowy, tworzy/proponuje 
zdarzenia ryzyka oraz czy zachowuje relacje między tymi rekordami. 
Test nowej inwestycji. Na podstawie przekazanego opisu lub dokumentów system wskazuje 
podobne projekty, wyjaśnia wybór, przedstawia dane porównawcze, flagi, rekomendacje i przedział 
możliwych odchyleń. 
Test źródłowy. Juror wybiera powiązania i wnioski oraz sprawdza, czy wskazane dane lub fragment 
dokumentu rzeczywiście je potwierdzają. Wynik bez możliwego do sprawdzenia źródła jest 
traktowany jako nieudokumentowany. 
Test pracy eksperta. Juror akceptuje, poprawia lub odrzuca niepewne dopasowanie i ocenia, czy 
interfejs pozwala szybko zrozumieć podstawę analizy, ograniczenia danych i poziom niepewności. 
Test założeń. Juror sprawdza zastosowane rozwiązania pod kątem ich uniwersalności 
i skalowalności. 
Będziemy się też opierać na dostarczonych przez zespoły materiałach: 
Krótki opis rozwiązania. Problem, przyjęty zakres, główny scenariusz użytkownika oraz 
jednoznaczne wskazanie elementów działających i zaprojektowanych (limit 10 stron). Uczestnicy 
mogą też nagrać swoją prezentację (limit 3 minut). 
Dokumentacja techniczna. Schemat architektury i modelu danych, opis źródeł i metod 
dopasowania, instrukcja uruchomienia oraz lista wykorzystanych modeli, usług, bibliotek i licencji. 
Raport z testu. Zestawienie poprawnych, niepewnych i błędnych połączeń między bazami oraz 
wyniki analizy nowego projektu. 
Materiały do dalszej pracy. Repozytorium kodu lub paczka źródłowa, konfiguracja niezbędna do 
uruchomienia oraz przykładowy eksport ustrukturyzowanych danych. 
Dodatkowo punktowana będzie demonstracja fakultatywnych funkcji Risk Minera (po ocenie ich 
przydatności i sposobu wykonania). 
7. Dostępne zasoby 
Na potrzeby wydarzenia MFiPR planuje przygotować pakiet podstawowych danych obejmujący 
około 20 wybranych publicznych projektów wodociągowo-kanalizacyjnych. Dane będą zawierać 
publiczne informacje i identyfikatory potrzebne do automatycznego łączenia źródeł. 
6 
Rekordy inwestycji. Dane projektów, zamówień publicznych i kontraktów, w tym w miarę 
dostępności: numer projektu, tytuł i opis, beneficjent, NIP, lokalizacja, daty, wartości, zakres, 
numer ogłoszenia BZP/TED, dane zamawiającego i wykonawcy i wartość kontraktu. Dane będą 
dostępne w publicznym repozytorium (zapewnionym przez Organizatora) lub na stronie. 
Dane eksperckie. Pełen pakiet wiedzy eksperckiej z zakresu pilotażowego sektora, obejmujący 
katalog zdarzeń, opisy typów inwestycji, wskazówki dotyczące interpretacji danych i metodyki 
(czego szukać, gdzie szukać, co z czego wynika itd.) oraz FAQ 
Publiczne źródła. BZP/e-Zamówienia, TED, Baza Konkurencyjności 2021, Biuletyny Informacyjne 
poszczególnych jednostek publikacje NIK, KIO, KPOŚK, wyszukiwarki i cokolwiek jeszcze przyjdzie 
uczestnikom do głowy. Uczestnicy korzystają z publicznej dokumentacji i samodzielnie 
przygotowują integracje. 
Nie gwarantujemy, że każdy projekt będzie miał kompletny zestaw danych w każdym źródle (np. 
ciężko spotkać sygnowane umowy) – często trzeba szukać alternatywnych źródeł i oznaczać ich 
pewność. Rozpoznanie braku danych, wielu zamówień w jednym projekcie lub niejednoznacznego 
dopasowania jest częścią wyzwania. 
Konsultacje. Mentorzy MFiPR będą wyjaśniać cele projektu, strukturę i znaczenie danych, proces 
inwestycyjny, znaczenie poszczególnych pól i zasady walidacji. 
Wsparcie organizacyjne i techniczne będzie zapewniane zgodnie z zasadami HackNation. 
8. Kryteria oceny 
Automatyczne pozyskiwanie, łączenie i organizacja danych – 20%.  
Poprawność wyszukiwania i łączenia informacji z różnych źródeł, jakość identyfikacji projektów 
i kontraktów, uporządkowanie danych oraz powtarzalność i możliwość aktualizacji procesu. 
Jakość analizy dokumentów, identyfikacji zdarzeń i wiarygodność wyników – 20%.  
Trafność rozpoznanych zdarzeń, przyczyn i skutków, prawidłowość wykorzystania danych, 
odwołania do dokumentów źródłowych oraz komunikowanie ograniczeń i niepewności. 
Użyteczność analizy planowanej inwestycji i rekomendacji – 25%.  
Trafność doboru i uzasadnienia grupy porównawczej, użyteczność oceny kosztorysu 
i harmonogramu, wskazanych ryzyk, czerwonych flag, działań zaradczych i propozycji zapisów 
umownych. 
Kontrola ekspercka, edytowalność założeń i modułowość – 20%.  
Możliwość zatwierdzania, poprawiania i odrzucania wszystkich wniosków AI, wygoda zarządzania 
wiedzą ekspercką bez zmian w kodzie oraz możliwość wykorzystania systemu w kolejnych 
sektorach. 
UX/UI, jakość techniczna i potencjał dalszego rozwoju – 15%.  
Czytelność i wygoda obsługi, jakość modelu danych i architektury, stabilność działania, możliwość 
rozwoju, skalowalność oraz przydatność raportów i eksportu. 
9. Dodatkowe uwagi / kontekst wdrożeniowy 
Wyzwanie jest częścią zaawansowanej fazy przygotowań Ministerstwa do realizacji programu 
badawczo-rozwojowego. Działający prototyp pozwoli zweryfikować nasze założenia 
i harmonogramy działań. Najlepsze rozwiązania mogą stać się punktem wyjścia do pilotażu 
i dalszych prac MFiPR nad empiryczną bazą doświadczeń z inwestycji publicznych. Docelową 
formą jest rozwiązanie wielosektorowe, automatycznie rozszerzane o kolejne projekty 
i wykorzystywane do lepszego przygotowania, porównywania i monitorowania inwestycji. 
7 
10. Kontakt 
Kontakt merytoryczny: stoisko MFiPR/PPP, kanał Discord. 
Podczas HackNation: mentorzy merytoryczni MFiPR dostępni przy stanowisku wyzwania oraz na 
odpowiednich kanałach serwera Discord. 