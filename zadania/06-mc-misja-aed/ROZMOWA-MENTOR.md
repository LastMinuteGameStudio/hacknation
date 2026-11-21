# Notatki: rozmowa z mentorem, 06 Misja AED (21.11.2026)

Źródło: nagranie `rozmowa.m4a` (14 min, Drive) i [transkrypcja automatyczna](ROZMOWA-MENTOR-TRANSKRYPCJA.md). W nawiasach znaczniki czasu.

**Kim jest mentor (z jego słów):** medyk, który zajmuje się też sprawami technicznymi. Reprezentuje dostawcę, który jest jednocześnie producentem i sprzedawcą AED oraz prowadzi aplikację dla społecznych ratowników. Dodał: „Mnie nie łączcie z Ministerstwem Cyfryzacji” [09:44]. Sprawy techniczne i punktację trzeba ustalać z MC [09:40, 13:30]. Jutro go nie będzie [13:38].

To są opinie i wskazówki mentora, a nie oficjalne stanowisko organizatora.

## Najważniejsze tezy

1. **Budujemy bazę danych, a nie aplikację** [02:58, 13:27]. Baza ma być jednorodna, ma wymieniać dane z dostawcami i dbać o wysoką jakość danych [03:00, 05:35]. Frontend i aplikacje to sprawa portfela i biznesu, „zostawcie sobie na inny” etap [12:25–13:12].
2. **Rola dane.gov.pl:** portal tylko zbiera dane od dostawców i buduje z nich ujednoliconą, ogólnodostępną bazę. **Odpowiedzialność za dane ponoszą dostawcy**, a ministerstwo jest „patronem wiarygodności i jakości” [02:10–03:14]. Przykład: fundacja prowadząca OSM może się zgłosić jako dostawca i wziąć odpowiedzialność za swoje ok. 18 tys. rekordów [02:26–02:44].
3. **Nie zbieramy zgłoszeń bezpośrednio od obywateli.** „Nie chcemy, żeby milion obywateli dziennie się logowało, robiło zdjęcie” [05:56–06:07]. Na dane.gov.pl mają trafiać kompletne dane od dostawców, którzy za nie odpowiadają.
4. **Jedna, „czysta formatka”:** dane mają mieć taki sam format dla każdego dostawcy, czyli dla firmy, OSP, Policji, Straży, m.st. Warszawy i Kancelarii Prezydenta [04:42–04:57]. Każdy podmiot (osoba prawna) zgłasza się do dane.gov.pl i wskazuje osobę odpowiedzialną [04:58–05:19].
5. **Bez przeregulowania.** Według mentora Francja przed igrzyskami zrobiła inwentaryzację, z której wyszło, że ok. 40% urządzeń było niesprawnych, rozkradzionych lub porzuconych. Potem wprowadziła przepisy, ale je „przeregulowała”, przez co rynek zahamował, a ludzie się przestraszyli [03:28–03:54]. Pierwsza pomoc to sprawa osobista i empatyczna: zbyt wiele ograniczeń zniechęci ludzi do społecznego udziału [03:56–04:12]. Obowiązki można nakładać na dostawców, a nie na ludzi [04:12–04:40].
   - ❔ Liczba 40% i „przeregulowanie” to opinia mentora, której nie weryfikowaliśmy. Dla porównania nasz research: 41% rekordów w Géo'DAE ma ostatni przegląd przed 2025 (patrz RESEARCH.md). To inna miara.
6. **Deduplikacja:** baza ma krzyżować dane i sprawdzać **numery seryjne**, żeby potwierdzić albo wykluczyć duplikaty [06:12–06:23]. Przykład: OSP zgłasza AED jako swój, gmina, która go kupiła, też, a lokalny biznes, który się dołożył, również. Wychodzą trzy rekordy dla jednego urządzenia [06:40–06:55]. Na początek wystarczy oznaczyć takie przypadki jako wyjątek. Mentor nie spodziewa się, że będzie ich dużo, i radzi nie robić z tego głównego problemu [07:08–07:30].
7. **Jak sprawdzać, kto jest odpowiedzialny za AED:** mentor „na tym etapie” nie odpowiedział [07:05].
8. **Źródła danych dziś i docelowo:** docelowo dostawcy sami się zgłaszają, ale „na dziś działacie na tym, co jest”. Organizatorzy chcą realnego działania [07:50–07:58]. Z tego, co zagregujemy, wyjdą braki i wtedy można wrócić do administratorów danych, żeby je uzupełnili według gotowej formatki. Na początku to ręczna robota [07:59–08:14].
9. **Skala:** docelowo „hipotetycznie tysiące rekordów” w skali kraju. Według mentora to ok. pół roku dobrej pracy w terenie [08:18–08:38]. W innym miejscu podał przykład z 20 dostawcami i 44 tys. unikalnych rekordów [06:10–06:14].
10. **AED w pojazdach pomijamy:** „nie pokazujemy urządzeń w ruchu”, bo człowiek nie będzie gonił autobusu [08:49–09:02]. Ewentualnie w przyszłości mogliby z nich korzystać dyspozytorzy 112 i PRM, ale „to już nie ten poziom” [09:03–09:31]. To zgadza się z decyzją zespołu z 21.11.
11. **Ciągła synchronizacja:** dane takie jak data ważności baterii muszą być aktualizowane na bieżąco, nie jednorazowo. Baza ma umożliwiać ciągłą synchronizację z dostawcami [10:20–10:39]. Mentor zaznaczył, że synchronizacja jest „dobra, żeby była”, ale główne założenie to baza danych [13:15–13:28].
12. **Informacja zwrotna między dostawcami przez dane.gov.pl:** przykład mentora: jego aplikacja codziennie o północy wymienia dane z dane.gov.pl. Jeśli użytkownik jego aplikacji zgłosi, że AED innego dostawcy jest niesprawny, dane.gov.pl automatycznie przekazuje tę informację temu dostawcy [10:58–12:04]. Opisał to jako „hipotetycznie, przyszłościowo”.

## Pola danych wymienione przez mentora [00:02–01:56]

- nazwa producenta i nazwa urządzenia
- **numer seryjny** (potrzebny też do deduplikacji)
- rok lub data produkcji
- lokalizacja: adres i współrzędne. Uwaga: różne bazy mają różną liczbę miejsc po przecinku, przez co punkty mogą się potem rozjeżdżać [00:34–00:38].
- data ważności elektrod (wymienne) i data ważności baterii (wymienna)
- **dostępność w formie ustrukturyzowanej**, nie wolnym tekstem: zaznaczenie „24h” i nic więcej albo dni tygodnia z godzinami od–do [00:42–01:00]. Dziś w bazach jest „papka”, np. „defibrylator w Żabce, za prawym rogiem, od 6 do 15”, a w innym systemie te same godziny są zapisane inaczej. Takich danych nie da się połączyć [01:02–01:30].
- **kto odpowiada** za urządzenie, czyli opiekun lub podmiot, który go zgłosił [01:44–01:56, 10:52]
- dodatkowe dane (np. pogoda, temperatura, czujniki w przyszłości) zespół może dodać, jeśli uzna je za ważne, ale dane.gov.pl ich nie wyświetla [01:57–02:12].

## Związek z naszymi ustaleniami

- Lista pól pokrywa się z francuskim schematem `schema-dae`: numer seryjny, producent, daty ważności elektrod i baterii, godziny w strukturze `opening_hours`, dysponent. Patrz RESEARCH.md.
- Odpowiada na nasze pytanie „narzędzie czy zbiór?”: według mentora **baza danych**, czyli agregacja i jednolity format, z wymianą danych z dostawcami. Aplikacja nie jest celem.
- Kłóci się z pomysłem zgłoszeń od obywateli. Według mentora dane mają pochodzić od dostawców, którzy biorą za nie odpowiedzialność.
- Potwierdza decyzję o pominięciu AED w pojazdach.

## Otwarte po rozmowie

- Jak weryfikować, kto jest dysponentem lub opiekunem AED (mentor nie odpowiedział).
- Szczegóły techniczne i punktacja: pytać MC, nie mentora.
