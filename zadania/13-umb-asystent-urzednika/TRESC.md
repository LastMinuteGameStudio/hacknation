<!-- Oryginalny PDF to skan bez warstwy tekstowej. Poniżej ręczna transkrypcja stron 1–3;
     strony 4–8 (wymagania formalne, kryteria oceny, kontakt) — patrz PDF. -->

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
