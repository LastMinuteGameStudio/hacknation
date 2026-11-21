<!-- Oryginalny PDF to skan bez warstwy tekstowej. Poniżej ręczna transkrypcja (skrócona). -->

# Inteligentny asystent urzędnika
## Generator odpowiedzi na UDIP z kalendarzem (organizerem) wniosków

Każdego dnia do urzędów trafiają dziesiątki wniosków o Dostęp do Informacji Publicznej od mieszkańców, aktywistów i dziennikarzy. Dla urzędników oznacza to setki godzin ręcznego przeszukiwania archiwów, weryfikacji stron BIP i pisania od nowa powtarzalnych pism.

Zadaniem jest stworzenie prostej i bezpiecznej aplikacji, która skróci czas przygotowania odpowiedzi z kilku dni do paru minut.

## 2. Wyzwanie

Narzędzie wspierające urzędników przy obsłudze wniosków o dostęp do informacji publicznej w Urzędzie Miasta Bydgoszczy. W skrócie: **kalendarz wniosków z terminami, moduł generowania odpowiedzi i moduł anonimizacji danych.**

Kluczowe założenia prototypu:

1. **Model AI i środowisko:** w czasie hackathonu można używać otwartego AI, ale docelowo program musi działać na zamkniętym modelu bez dostępu do Internetu i uczyć się na wprowadzanych danych (ustawy, aktualizacje ustaw, wnioski, odpowiedzi itd.).
2. **Wgrywanie plików:** urzędnik wprowadza dane ręcznie, wgrywając plik PDF lub Word.
3. **Kalendarz wniosków:** tabela zintegrowana z kalendarzem, z wnioskami ułożonymi od najstarszego i liczbą dni pozostałych na odpowiedź. Wnioski z terminem na dziś i jutro są podświetlone. Statusy: w przygotowaniu, kwerenda (dodatkowy czas na odpowiedź), wysłana. Pola: inicjały osoby obsługującej, lp., nr wniosku, skrócony opis tematu, data wpływu, termin, data odpowiedzi. Możliwość wyboru roku.
4. **Anonimizacja:** narzędzie podpowiada dane do anonimizacji (podświetla na szaro, a po akceptacji urzędnika zaczernia) i automatycznie anonimizuje nadmiarowe dane, np. osobowe.
5. **Automatyzacja** rutynowych czynności.
6. **Przeszukiwanie archiwum** odpowiedzi w poszukiwaniu podobnych wniosków.
7. **Wskazywanie ścieżki:** podpowiada, z których wydziałów urzędu pozyskać odpowiedź.
8. **Projekt odpowiedzi:** po wgraniu odpowiedzi z wydziałów przygotowuje projekt pisma do weryfikacji przez urzędnika.
9. **Brak automatycznej wysyłki:** narzędzie niczego samo nie wysyła.
10. **Kompleksowe wsparcie:** projekty odpowiedzi, anonimizacja i kalendarz.
11. **Brak integracji** z innymi systemami urzędowymi (w tym SIDAS).
12. **Narzędzie pomocnicze:** ostateczną decyzję zawsze podejmuje urzędnik.

### Uproszczony przepływ
1. Narzędzie „uczy się” z wgranych ustaw, archiwalnych odpowiedzi, zarządzeń.
2. Urzędnik wgrywa wniosek (PDF/Word).
3. Narzędzie pokazuje podobne wnioski z ostatniego roku.
4. Proponuje wydziały, do których należy się zwrócić ([wydziały UMB](https://bip.um.bydgoszcz.pl/artykuly/198/wydzialy), [biura](https://bip.um.bydgoszcz.pl/artykuly/1158/biura)).
5. Wniosek trafia na listę, a urzędnik akceptuje dane (termin, inicjały, numer).
6. Odpowiedzi z wydziałów przychodzą poza narzędziem i urzędnik je wgrywa.
7. Narzędzie tworzy szablon odpowiedzi z zaznaczonymi polami do anonimizacji.
8. Urzędnik akceptuje anonimizację.
9. Narzędzie generuje odpowiedź w formacie doc/txt.
10. Urzędnik weryfikuje treść odpowiedzi.
11. Status sprawy aktualizuje się na każdym kroku: brak działań → zapytania do wydziałów → kwerenda → przygotowana odpowiedź → wysłana.

## 3. Oczekiwany rezultat
W pełni funkcjonalny prototyp, który zamienia obsługę wniosków o dostęp do informacji publicznej w szybki, półautomatyczny i bezpieczny proces wspierany przez AI lub inną technologię. Organizator nie narzuca technologii; liczą się kreatywność i „efekt zaskoczenia”.

## 4. Wymagania formalne
- Film z prezentacją prototypu, **maks. 3 minuty**.
- Prezentacja, **maks. 10 slajdów**: nazwa i zespół, problem (przyspieszenie pracy urzędnika i ochrona danych osobowych), jak działa rozwiązanie (wyszukiwanie w archiwum, anonimizacja, kalendarz) i w jakiej technologii, demo (wgranie PDF/Word, przetwarzanie, projekt odpowiedzi), dla kogo (urzędnicy JST), plan na stałe użycie w UMB, lista narzędzi, **czy prototyp zadziała w zamkniętym systemie bez Internetu, z propozycją konkretnego modelu do takiego środowiska**.

## 5. Wymagania techniczne
- Prototyp ma wczytać plik (PDF/Word), przeszukać lokalną bazę, podpowiedzieć wydział, wygenerować projekt odpowiedzi i zanonimizować dane.
- **Kalendarz ma pokazać 10 wniosków testowych** od najstarszego i podświetlić kolorem te, na które trzeba odpowiedzieć w pierwszej kolejności.
- Ma być stabilny i działający (to demo, nie plan) oraz tani i dostępny technologicznie.
- Na hackathonie wolno użyć otwartego AI, ale koncepcja musi zakładać pracę w pełni lokalną, bez Internetu.
- Bezpieczeństwo (brak wycieków), łatwa instalacja i skalowalność do setek archiwalnych dokumentów.

## 6. Jak jury testuje
1. Wgrywa przykładowy wniosek i sprawdza, czy program znajduje podobne sprawy w archiwum.
2. Sprawdza, czy po podaniu odpowiedzi z wydziału powstaje poprawny projekt pisma.
3. Test anonimizacji na pliku z danymi osobowymi.
4. Łatwość obsługi, stabilność i realność wdrożenia.
5. Układ kalendarza: oznaczanie wniosków z terminem i etapu obsługi.
6. Łatwość wgrywania danych, aktualizacji ustaw i archiwalnych odpowiedzi.

**Materiały:** przykładowe wnioski o dostęp do informacji publicznej z odpowiedziami oraz robocza wizualizacja kalendarza, dostępne pod kodem QR od mentorów w dniu startu. Dodatkowo: BIP UMB, [KPA](https://isap.sejm.gov.pl/isap.nsf/DocDetails.xsp?id=wdu19600300168), [ustawa o dostępie do informacji publicznej](https://isap.sejm.gov.pl/isap.nsf/DocDetails.xsp?id=wdu20011121198).

## 8. Kryteria oceny
- Związek z wyzwaniem (zgodność z założeniami): **30%**
- Bezpieczeństwo i skuteczna anonimizacja danych: **20%**
- Łatwość obsługi i użyteczność dla urzędnika: **20%**
- Kompletność i jakość działającego prototypu: **30%**

Kontakt: Biuro Komunikacji Społecznej i Biuro Rady Miasta, stoisko Bydgoszczy oraz kanał na Discordzie.
