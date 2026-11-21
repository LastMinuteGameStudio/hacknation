# HackNation 2026: szczegóły zadań (wymagania, dane, jak oceniają)

Skrót z pełnych treści zadań. Szczegóły są w `NN-*/TRESC.md` i w oryginalnych PDF-ach.
Legenda: 🔒 = ograniczenia technologiczne, 📦 = dane/materiały, ⚖️ = kryteria oceny, 🧪 = jak testują.

---

## 01 · AGH: Attack Surface Intelligence (25 000 zł)
**Co:** prototyp systemu do discovery scanów dużej infrastruktury (>10 tys. IP).
- Wejście: lista IP, CIDR lub domen, wpisywana ręcznie albo z pliku CSV/JSON.
- Wielowątkowy skan (nmap): aktywne hosty, usługi, a dla HTTP(S) tytuł, kod odpowiedzi, nagłówki, ciasteczka, certyfikat TLS i przekierowania.
- Fingerprinting: CMS, framework, serwer, IoT, środowiska staging i panele admina.
- Diff między skanami: nowe, znikające i zmienione usługi oraz obsługa hostów, które odpowiadają tylko czasem.
- Własne sygnatury detekcji, wyłącznie bezpieczne (nagłówek, cookie, hash favicony, ścieżka bez logowania).
- Harmonogram i okna czasowe skanów: skan, który przekroczy okno, ma się zatrzymać i ruszyć w kolejnym oknie.
- **RBAC z 4 rolami**, edycja wyników, która przetrwa kolejne skany, dashboard, szyfrowanie danych w spoczynku, integracja z DefectDojo.

🔒 Wyłącznie darmowe narzędzia open source; sugerowane Go, Rust lub C++.
📦 Środowisko testowe w kontenerach, lista portów, wyniki referencyjne, przykładowe sygnatury i formaty JSON/CSV, opcjonalnie testowy DefectDojo. Dostęp przez Discord albo na stoisku AGH.
🧪 Laboratorium z hostami, co najmniej 2 przebiegi skanu, sprawdzane też role i import.
⚖️ Discovery i identyfikacja usług 30% · zmiany w czasie i niestabilne hosty 15% · jakość techniczna, dokumentacja, DefectDojo 20% · bezpieczeństwo skanowania i dashboard 15% · fingerprinting 10% · role i ochrona danych 10%.


---

## 02 · COI: Cyfryzacja formularzy (25 000 zł)
**Co:** REST API przyjmujące formularz urzędowy (PDF, DOC/DOCX, ODS, XLSX, JPG, PNG) i zwracające **JSON z konfiguracją e-formularza** w formacie z przykładów.
- Wymagany podział na strony tematyczne zgodnie z wytycznymi projektowania formularzy.
- Dodatkowo punktowane: podpięcie słowników i danych inicjalnych, zaproponowanie nowych słowników, zależności i dynamiczne przejścia między polami, sekcjami i stronami.

🔒 **Nie wolno używać LLM-ów dostępnych tylko przez API** (rozwiązanie musi działać na lokalnym modelu open source). Bez zewnętrznych API, MCP i SaaS. Bez licencji copyleft (GPL/AGPL). Preferowana Java 21+ albo Python 3.14+. Docker (oficjalne, lekkie obrazy, bez tagu `latest`, użytkownik bez uprawnień roota), JWT, walidacja MIME, nazwy i rozmiaru pliku, pliki tylko tymczasowo, README z opisem API.
📦 Na Discordzie: przykładowe formularze z oczekiwanymi JSON-ami i screenami e-usługi, formularze do oceny, wymagania projektowe, słowniki.
🧪 Finaliści uruchamiają rozwiązanie na **nowych plikach podanych podczas obrony**.


---

## 03 · KPRM: Cyfrowy asystent ocen okresowych (30 000 zł)
**Co:** cyfrowy proces oceny okresowej w służbie cywilnej (około 1743 urzędy, 123 tys. osób) plus moduł **„wirtualny HR partner”**.
- Odwzorowanie arkuszy A, B i C ze wszystkimi polami, edycja, uprawnienia i wydruk.
- Wybór arkusza i do 3 kryteriów dodatkowych, przygotowanie przełożonego do rozmowy rozpoczynającej i oceniającej, rekomendacje rozwojowe, sygnały wypalenia.
- Użytkownicy: oceniający, oceniani, kadry, dyrektor generalny (statystyki).

🔒 Rozwiązanie neutralne technologicznie, bez płatnych licencji, łatwe do wdrożenia w małym i dużym urzędzie, z regułami prawnymi łatwymi do zmiany. Kontrola dostępu i anonimizacja, jeśli dane wychodzą poza urząd.
📦 **Najwięcej materiałów ze wszystkich zadań:** akty prawne, przypadki użycia, schemat procesu, formularze ocen z opisem pól, wypełnione przykłady i materiały dodatkowe (archiwa w folderze).
🧪 Demo całego procesu oceny i modułu HR partnera.
⚖️ Związek z wyzwaniem i zgodność z prawem 30% · oryginalność 20% · kompletność 20% · **potencjał wdrożeniowy 30%**.

---

## 04 · KOWR: Zatrzymaj wodę, chroń plony (27 778 zł)
**Co:** aplikacja webowa dla rolnika. Po podaniu numeru działki ewidencyjnej albo wskazaniu jej na mapie:
1. ocena stanu wilgotności na podstawie wskaźników satelitarnych, gleby i meteo **za ostatnie 10 lat**, z uwzględnieniem rodzaju uprawy,
2. rekomendacje dotyczące retencji i ograniczania strat wody,
3. agrotechnika,
4. plan nawadniania.

Wszystko oparte na wiedzy naukowej (załącznik „Podstawy naukowe”).

🔒 Technologia dowolna, AI dozwolone, ale trzeba je opisać. Aplikacja ma działać w przeglądarce na Windowsie; wersja mobilna to plus.
📦 **KOWR nie daje danych**, trzeba je zebrać samemu: Copernicus/Sentinel-2, IMGW, Open-Meteo, IUNG (monitoring suszy), SoilGrids, ULDK/EGiB (działki), Hydroportal, EDO.
⚖️ Wartość praktyczna 25% · dane i wiarygodność rekomendacji 25% · innowacyjność 20% · prostota obsługi 15% · prototyp 15%.


---

## 05 · MC (BDG): Kompas kompetencji (22 223 zł)
**Co:** prowadzi przełożonego przez ocenę pracownika. Dwie ścieżki: **pierwsza ocena w służbie cywilnej** i **ocena okresowa**.
- Model kompetencji ze wskaźnikami behawioralnymi: przełożony wybiera zachowania, system liczy **sugerowany poziom**, a ostateczną decyzję podejmuje przełożony.
- Wybór kryteriów, terminy, dokumentacja w PDF.
- **Asystent AI (RAG)** na ustawie, rozporządzeniach, modelu kompetencji, poradnikach KPRM i zestawie pytań i odpowiedzi. Ma podawać źródło, a gdy nie wie, uczciwie to mówić.

🔒 Tylko darmowe narzędzia AI, ale gotowe modele, chmura i zewnętrzne API są dozwolone. Logowanie, role, RODO, PDF, interfejs w przeglądarce; **wersja na smartfony niepotrzebna**.
📦 `HackNation.zip` (11 MB) z materiałami.
🧪 Pełna ścieżka użytkownika na żywo; jurorzy zadają asystentowi pytania i oceniają poprawność odpowiedzi.
⚖️ Zgodność merytoryczna 25% · UX 25% · jakość AI 20% · innowacyjność 20% · wdrożenie 10%.


---

## 06 · MC (DZD): Misja AED (27 778 zł)
**Co:** narzędzie zbierające dane o defibrylatorach z rozproszonych źródeł w jeden zbiór pod dane.gov.pl oraz **wzorcowy schemat danych (xlsx)**. Do tego **nazwa akcji, logo i księga znaku** (kolory, pole ochronne, minimalny rozmiar, niedozwolone użycia).

🔒 Dane w formacie maszynowym, zgodność z dane.gov.pl, WCAG, responsywność.
⚖️ Zgodność z dane.gov.pl 30% · **logo i hasło 25%** · kreatywność 15% · temat 15% · schemat danych 10% · prezentacja 5%.


---

## 07 · MF/KAS: OSINTowy Łapacz Cyfrowych Śladów (30 000 zł)
**Co:** wpisujesz identyfikator (imię i nazwisko, nick, e-mail, login, adres portfela), a narzędzie przeszukuje **jawne** źródła Web2 (fora, social media, GitHub, ogłoszenia P2P) w poszukiwaniu adresów krypto. Potem analizuje je on-chain (BTC, ETH): wolumen, swapy, wyjścia do walut tradycyjnych, giełdy i P2P. Wylicza **Wskaźnik Pewności** powiązania. Cykliczne analizy, historia i porównywanie wyników.

🔒 Backend najlepiej w .NET, Javie albo Node (Python, Go i Rust trzeba uzasadnić). Front w Angularze, Reacie albo Vue. Baza open source. Model AI wymienny. Monorepo. **Wyłącznie OSINT**: bez nmapa, bez obchodzenia zabezpieczeń, bez łamania regulaminów serwisów.
🧪 Obowiązkowy scenariusz: wejście → ślady OSINT → wykrycie i weryfikacja adresu → Wskaźnik Pewności → **odrzucenie błędnych przypisań (adresy giełd, kontrakty)** → wskaźniki on-chain → źródła i wynik.
⚖️ Zgodność i scenariusz 25% · **jakość Wskaźnika Pewności 25%** · przejrzystość raportu i źródeł 20% · oryginalność 15% · architektura 15%.

---

## 08 · MFiPR: Risk Miner (25 000 zł)
**Co:** cyfrowa pamięć instytucjonalna inwestycji publicznych.
1. Automatyczne budowanie bazy z BZP/e-Zamówień, TED, BK2021, NIK i KIO plus pliku od organizatora; łączenie po numerze ogłoszenia, CST, NIP/REGON i OCID.
2. Ekstrakcja zdarzeń i ryzyk z dokumentów (DOCX, PDF) według katalogu ekspertów, z weryfikacją przez eksperta.
3. Dla nowej inwestycji: grupa porównawcza podobnych projektów, odchylenia kosztów i czasu, czerwone flagi, propozycje zapisów umownych.

🔒 Model ustawiany w konfiguracji. Każdy wniosek ze źródłem (link, strona, fragment). Wyniki jako rekordy do eksportu (JSON/CSV); sama odpowiedź w czacie nie wystarcza. **Bez ręcznego importu danych testowych**: wpisy mają powstawać automatycznie.
📦 Paczka startowa `Risk_Miner_materialy_dla_uczestnikow_na_start.zip` z katalogiem zdarzeń, typami inwestycji i metodyką (sektor pilotażowy).
⚖️ Pozyskiwanie i łączenie danych 20% · analiza dokumentów 20% · **użyteczność dla nowej inwestycji 25%** · kontrola ekspercka i modułowość 20% · UX i technika 15%.


---

## 09 · MSZ: Prawdowid (30 000 zł)
**Co:** fact-checker dla obywatela, który przyjmuje tekst albo URL (multimodalność to plus). Wyodrębnia twierdzenia i dla każdego zwraca werdykt: **potwierdzone, fałszywe, wprowadzające w błąd, brak wystarczających dowodów albo nie podlega weryfikacji**. Do każdego podaje źródła (tytuł, wydawca, data, link, cytat). Gdy dowodów brakuje, wstrzymuje się od oceny.

🔒 **Dwa kanały** (WWW plus np. Discord, Messenger, SMS albo adapter demonstracyjny) na tej samej logice. Korpus demo **co najmniej 100 dokumentów z co najmniej 10 domen, minimum 2 typy źródeł**. Ochrona przed prompt injection, maskowanie danych osobowych, logowanie kosztów i czasu odpowiedzi. Dowolne modele, także komercyjne.
📦 Organizator da pakiet JSON/CSV (zasoby EDMO, EUvsDisinfo, materiały NASK) na Discordzie.
⚖️ Jakość weryfikacji i dowodów 30% · bezpieczeństwo i transparentność 20% · wdrożenie 20% · UX 15% · innowacje 15%. **Warunek brzegowy:** działanie end-to-end, zero zmyślonych źródeł, poprawne wstrzymywanie się od oceny i 2 kanały. Bez tego dodatkowe funkcje nie dostają punktów.

---

## 10 · NASK: Kolekcjoner fejków (33 333 zł)
**Co:** dostajesz zbiór podejrzanych reklam „z celebrytami” i stron, na które prowadzą. Trzeba wyciągnąć cechy (tekst, narracja, osoby, logotypy, cechy wizualne, domeny, przekierowania, WHOIS i infrastruktura), znaleźć duplikaty i warianty, **pogrupować je w kampanie** i dla nowego materiału stwierdzić, czy należy do znanej kampanii, czy to nowa. Wynik ma być wyjaśnialny i pokazany np. jako graf.

🔒 Technologia dowolna; Streamlit albo Gradio wystarczą, bo **wygląd UI nie jest oceniany**. Mile widziany kontener z instrukcją.
📦 Przykładowy zbiór danych dostępny w trakcie; ocena na **ukrytym zbiorze testowym** z nowymi wariantami i innymi kampaniami.
⚖️ **Metoda korelacji i grupowania 30% · trafność cech i źródeł 30%** · end-to-end 15% · interpretowalność 15% · wdrożenie 10%.


---

## 11 · PCI: Radar innowacji (11 111 zł)
**Co:** forma dowolna. Rozwiązanie ma wyszukiwać „ukryte” innowacje w szkołach, uczelniach i JST, porządkować je, oceniać potencjał i wskazywać partnerów lub ścieżki rozwoju.
📦 Bazy patentowe (UPRP, EPO), PBN, biblioteki cyfrowe, Interreg, NCBR.
🧪 Demo na co najmniej 2 przypadkach: wejście → zebranie danych → ocena → partnerzy → uzasadnienie.
⚖️ Pięć kryteriów po 20%.


---

## 12 · UKNF: #InvestWatch (30 000 zł)
**Co:** silnik scrapingu (web plus Facebook, Instagram, TikTok) i 3 moduły:
1. reklamy firm inwestycyjnych publikowane przez finfluencerów i inne podmioty,
2. sprawdzanie, czy materiały marketingowe firm wystarczająco informują o ryzyku (lista wymogów w załączniku),
3. wykrywanie nieautoryzowanego doradztwa inwestycyjnego (shadow advisory).

Do tego aplikacja webowa z panelem kalibracji progów i powiadomieniami w czasie rzeczywistym.

🔒 **Tylko open source i on-premise**: modele przez Ollamę albo vLLM (np. Gemma, BERT), **zero płatnych API**. Docker Compose uruchamiany jedną komendą. Skanowanie zależności (Snyk, npm audit). Krótkie README („bez AI slopu”).
📦 Próbki danych podczas hackathonu, na pendrive przy stoisku.
⚖️ Technologia i demo 30% · proces wytwarzania z asystentami AI 20% · architektura 20% · zgodność ze specyfikacją 20% · „wow” 10%.


---

## 13 · UM Bydgoszcz: Inteligentny asystent urzędnika (15 000 zł)
**Co:** obsługa wniosków o dostęp do informacji publicznej.
- **Kalendarz i tabela wniosków** z terminami, kolorami, statusami (brak działań → zapytania do wydziałów → kwerenda → przygotowana → wysłana) i wyborem roku.
- Wgranie wniosku (PDF/Word) → **podobne wnioski z archiwum** → **podpowiedź wydziałów** (lista z BIP) → wgranie odpowiedzi z wydziałów → **projekt pisma** → **anonimizacja** (szare podświetlenie, po akceptacji zaczernienie) → eksport do DOC lub TXT.
- Narzędzie niczego samo nie wysyła i nie integruje się z innymi systemami (np. SIDAS).

🔒 Na hackathonie wolno użyć otwartego AI, ale w prezentacji trzeba pokazać **plan działania offline z konkretnym lokalnym modelem**. Kalendarz ma pokazać **10 wniosków testowych**. Wymagane: film do 3 minut i maksymalnie 10 slajdów.
📦 Przykładowe wnioski z odpowiedziami i makieta kalendarza, dostępne przez kod QR od mentorów.
🧪 Jury samo wgrywa wniosek, sprawdza wyszukiwanie podobnych, projekt pisma i **anonimizację pliku z danymi osobowymi**, kalendarz oraz wgrywanie ustaw i archiwum.
⚖️ Zgodność z założeniami 30% · **bezpieczeństwo i anonimizacja 20%** · UX 20% · kompletność prototypu 30%.


---

## 14 · UZP: Odwołania2JSON (20 000 zł)
**Co:** PDF ze sprawy odwoławczej (odwołanie, pełnomocnictwo, potwierdzenie przelewu) → **klasyfikacja typu dokumentu** → ekstrakcja pól → JSON zgodny ze schematem z repo UZP. Część dokumentów to skany.

🔒 **Wyłącznie open source, także model językowy.** Musi działać lokalnie **bez GPU** (LLM może być wywoływany przez API, ale sam model ma być otwarty). Premiowane: nowe klasy dokumentów dodawane bez zmian w kodzie i przejrzystość ekstrakcji.
📦 [github.com/Urzad-Zamowien-Publicznych/hacknation-2026](https://github.com/Urzad-Zamowien-Publicznych/hacknation-2026): dokumenty syntetyczne i oczekiwane JSON-y.
🧪 **F1 na ukrytym zbiorze testowym** z prawdziwymi sprawami.
⚖️ Preselekcja: **100% F1**. Finał: F1 50% · rozszerzalność 30% · architektura 20%.


---

## 15 · ZUS: Przewodnik przyszłego rodzica (30 000 zł)
**Co:** responsywna aplikacja webowa, która prowadzi (przyszłych) rodziców, osoby adoptujące i rodziny zastępcze przez świadczenia z ubezpieczenia chorobowego: zasiłek chorobowy w ciąży, macierzyński, opiekuńczy, także w trudnych sytuacjach (np. urodzenie martwego dziecka). Ma też **sprawdzać prawo do zasiłku i wyliczać jego wysokość** na podstawie wniosku.

🔒 Preferowany React/Next.js oraz backend w JS, Pythonie albo C#, połączone przez REST. Wymagany upload lub wybór przykładowego wniosku.
📦 Zanonimizowane przykładowe wnioski i dokumenty (o ubezpieczeniu i wysokości zasiłku), streszczenia przepisów i PDF dla rodziców (archiwum ZIP, 5,8 MB).
🧪 Jury wgrywa przykładowe wnioski i **sprawdza poprawność wyliczeń**, a także przegląda kod w repozytorium.
⚖️ Związek z wyzwaniem 25% · pomysł 20% · oryginalność 15% · kompletność i UX 25% · wdrożenie 15%.

