# HackNation 2026: przegląd zadań

Źródło: folder organizatorów na Google Drive („HackNation 2026 - Zadania dla Uczestników”), pobrany 21.11.2026.
W każdym folderze są oryginalne pliki (pełna treść zadania, regulamin, materiały) oraz `TRESC.md` z tekstem wyciągniętym z PDF-a, wygodnym do grepowania i wklejania do LLM-a.

Hackathon trwa od 21.11, 11:00 do 22.11, 11:00. Do finału z każdego zadania przechodzi 5 zespołów.

## Ściąga

| # | Zadanie | Zgłaszający | Nagroda | Co zbudować | Typ |
|---|---|---|---|---|---|
| 01 | [Attack Surface Intelligence](01-agh-attack-surface-intelligence) | AGH (CBI) | 25 000 zł | Cykliczny skaner dużych sieci (>10k IP): nmap, fingerprinting HTTP/CMS, diff między skanami, własne sygnatury, RBAC, dashboard, integracja z DefectDojo | security / backend |
| 02 | [Cyfryzacja formularzy](02-coi-cyfryzacja-formularzy) | COI | 25 000 zł | REST API: formularz urzędowy (PDF/DOCX/XLSX/skan) → JSON w zadanym schemacie e-formularza. Plusy za słowniki i zależności między polami | AI / ekstrakcja dokumentów |
| 03 | [Cyfrowy asystent ocen okresowych](03-kprm-asystent-ocen-okresowych) | KPRM | 30 000 zł | Cyfrowy proces oceny okresowej w służbie cywilnej (arkusze A/B/C, kryteria, rozmowy, wydruk) + „wirtualny HR partner” z AI. Dużo materiałów (akty prawne, formularze, przykłady) | web app + LLM |
| 04 | [Zatrzymaj wodę, chroń plony](04-kowr-zatrzymaj-wode) | KOWR | 27 778 zł | Web app dla rolnika: po numerze działki ocenia ryzyko suszy z danych satelitarnych, meteo i glebowych za 10 lat i daje rekomendacje dotyczące retencji i nawadniania | GIS / dane otwarte |
| 05 | [Kompas kompetencji](05-mc-kompas-kompetencji) | MC (BDG) | 22 223 zł | Prowadzi przełożonego przez ocenę pracownika: model kompetencji i wskaźniki behawioralne → sugerowany poziom, dokumenty + asystent AI. Tylko desktop. **Bardzo podobne do 03** | web app + LLM |
| 06 | [Misja AED](06-mc-misja-aed) | MC (DZD) | 27 778 zł | Zebrać dane o defibrylatorach z rozproszonych źródeł w jeden zbiór pod dane.gov.pl, zaprojektować wzorcowy schemat (xlsx) **oraz** nazwę akcji, logo i księgę znaku | dane + branding |
| 07 | [OSINTowy Łapacz Cyfrowych Śladów](07-mf-osint-lapacz) | MF / KAS | 30 000 zł | Z identyfikatora (nick, e-mail, imię) znajduje w jawnych źródłach powiązane adresy krypto, analizuje je on-chain (wolumen, wyjścia do fiat, giełdy/P2P) i podaje prawdopodobieństwo powiązania | OSINT / scraping / blockchain |
| 08 | [Risk Miner](08-mfipr-risk-miner) | MFiPR | 25 000 zł | Baza doświadczeń z dokumentów inwestycji publicznych (BZP, TED, aneksy, kontrole): ekstrakcja zdarzeń i ryzyk wg katalogu ekspertów + wyszukiwanie podobnych inwestycji dla nowego projektu. Jest paczka startowa | AI / RAG / ekstrakcja |
| 09 | [Prawdowid](09-msz-prawdowid) | MSZ | 30 000 zł | Fact-checker dla obywatela przez dowolny kanał (np. komunikator): twierdzenia → wyszukanie w wiarygodnych źródłach → werdykt (potwierdzone / fałsz / mylące / brak dowodów) z cytatami, odporny na prompt injection | LLM / RAG |
| 10 | [Kolekcjoner fejków](10-nask-kolekcjoner-fejkow) | NASK | 33 333 zł | Grupowanie fałszywych reklam „z celebrytami” w kampanie na podstawie tekstu, obrazu, domen, przekierowań i WHOIS. Deduplikacja, przypisanie nowej reklamy do kampanii, wizualizacja powiązań | ML / clustering / OSINT |
| 11 | [Radar innowacji](11-pci-radar-innowacji) | PCI | 11 111 zł | Mechanizm wyszukiwania i oceny „ukrytych” innowacji w szkołach, uczelniach i JST oraz łączenia ich z partnerami i inwestorami. Forma otwarta | produkt / platforma |
| 12 | [#InvestWatch](12-uknf-investwatch) | UKNF | 30 000 zł | Scraper (web + social media) i 3 moduły: reklamy firm inwestycyjnych u finfluencerów, ocena, czy informacja o ryzyku jest wystarczająca, wykrywanie nieautoryzowanego doradztwa. Otwarte modele (Gemma/BERT) | scraping / NLP |
| 13 | [Inteligentny asystent urzędnika](13-umb-asystent-urzednika) | UM Bydgoszcz | 15 000 zł | Obsługa wniosków o dostęp do informacji publicznej: kalendarz terminów, wyszukiwanie podobnych wniosków, podpowiedź wydziałów, generowanie projektu odpowiedzi, anonimizacja. Docelowo lokalny LLM | web app + LLM |
| 14 | [Odwołania2JSON](14-uzp-odwolania2json) | UZP | 20 000 zł | PDF z odwołaniem do KIO (odwołanie, pełnomocnictwo, przelew) → klasyfikacja dokumentu → JSON wg schematu. Tylko open source, bez GPU. Dane treningowe na [GitHubie UZP](https://github.com/Urzad-Zamowien-Publicznych/hacknation-2026) | ekstrakcja dokumentów |
| 15 | [Przewodnik przyszłego rodzica](15-zus-przewodnik-rodzica) | ZUS | 30 000 zł | Aplikacja prowadząca (przyszłych) rodziców przez świadczenia ZUS (zasiłek macierzyński, chorobowy w ciąży, adopcja, sytuacje trudne). Są materiały od ZUS | web/mobile + treści |

## Grupy tematyczne

- **Ekstrakcja z dokumentów → JSON** (najłatwiej zmierzyć jakość): 02 COI, 14 UZP, częściowo 08 MFiPR
- **Asystenci LLM dla urzędników / HR**: 03 KPRM, 05 MC, 13 UMB (03 i 05 to prawie ten sam problem)
- **Dezinformacja i oszustwa**: 09 MSZ, 10 NASK, 12 UKNF
- **OSINT / security**: 01 AGH, 07 MF
- **Aplikacje dla obywateli**: 04 KOWR, 15 ZUS, 06 MC (AED)
- **Otwarte / koncepcyjne**: 11 PCI

## Wstępne obserwacje (do dyskusji)

- **Najlepiej zdefiniowane** (jasne wejście, wyjście i dane): 14 UZP (gotowe schematy JSON i zbiór treningowy na GitHubie), 02 COI (przykładowe pary formularz → JSON), 13 UMB (bardzo konkretny opis przepływu).
- **Najwięcej pieniędzy**: 10 NASK (33 tys. zł), potem 03, 07, 09, 12 i 15 (po 30 tys. zł).
- **Duży zakres jak na 24 godziny**: 01 AGH (RBAC, szyfrowanie, scheduler, DefectDojo), 12 UKNF (scraping social mediów i 3 moduły), 04 KOWR (dane satelitarne za 10 lat).
- **Mniej programowania, więcej designu**: 06 AED (logo i księga znaku są wymagane), 11 PCI.

Następny krok: wybieramy 2–3 kandydatów i robimy pogłębioną analizę (regulamin, kryteria oceny, dane wejściowe, plan MVP).
