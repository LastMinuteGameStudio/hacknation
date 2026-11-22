# Audyt dostępności i responsywności frontu TuAED (E2)

Data: 22.11.2026. Wersja: kreator na main po c72a1af, mapa po 70d6c41. Ścieżka C (front).

## Wynik w skrócie

| | Przed poprawkami | Po poprawkach |
|---|---|---|
| axe-core 4.14, WCAG 2.0/2.1/2.2 A i AA (33 ekrany: 11 stanów × 320/768/1440 px) | 0 naruszeń | 0 naruszeń |
| axe-core, „best practice” | 0 | 0 |
| Lighthouse 12.8, dostępność (22 migawki: 11 stanów × 320 i 1440 px) | 100 na każdym ekranie | 100 na każdym ekranie |
| Poziome przewijanie strony (320/768/1440 px) | brak | brak |
| Cele dotyku < 24 px (WCAG 2.5.8) | 0 | 0 |
| Lista wyboru pola przy długich wartościach w pliku (przemysl_2024.csv, 1440 px) | ok. 80 px, nieczytelna („Ident”, „Nazw”) | min. 259 px przy każdej szerokości |

Automaty nie wykryły błędów, bo front od początku pisaliśmy pod WCAG 2.2 AA. Jedyny poważny problem był w układzie: tabela mapowania przy realnym pliku z długimi opisami. Znalazła go ścieżka D na zrzutach z demo.

## Sprawdzone ekrany

1. Strona startowa.
2. Krok 1 Dysponent: pusty i z błędami po wysłaniu pustego formularza.
3. Krok 2 Dane: przed wgraniem, po wgraniu `krosno.csv` (tabela mapowania), po walidacji z błędami, po walidacji bez błędów (z rozwiniętym podglądem wyniku).
4. Krok 3 Publikacja: przed zgodą CC0 i po publikacji (adres, prywatny link, instrukcja dane.gov.pl).
5. `/edycja/{slug}?token=…`: sekcja „Źródło automatyczne”, pusta i po wstrzymaniu (ZMIANA_STRUKTURY).

Dodatkowo tabela mapowania dla `przemysl_2024.csv` (długie opisy) przy 320, 768 i 1440 px.

## Narzędzia i metoda

- **axe-core 4.14.1** wstrzyknięty do strony, reguły `wcag2a`, `wcag2aa`, `wcag21a`, `wcag21aa`, `wcag22aa` oraz `best-practice`.
- **Lighthouse 12.8.2**, kategoria Accessibility. Tryb user flow (migawki stanów aplikacji), Chrome headless shell 159, bez emulacji ekranu (rzeczywista szerokość okna).
- **Puppeteer / Playwright**: skrypt przechodzi cały kreator jak użytkownik. Na każdym stanie mierzy `scrollWidth` strony i rozmiar wszystkich elementów interaktywnych. Linki w zdaniu są pominięte, bo to wyjątek „inline” z 2.5.8.
- **Klawiatura** (Playwright, tylko Tab/Enter/Spacja): kolejność fokusu, widoczność obrysu, fokus po zmianie kroku, link „Przejdź do treści”, błędy formularza.
- **Odstępy tekstu (1.4.12)**: wstrzyknięty CSS z kryterium (interlinia 1,5, litery 0,12 em, słowa 0,16 em, akapity 2 em), szukanie uciętej treści i przewijania.
- **Kontrast**: wzór WCAG dla wszystkich par kolorów z `tokens.css` (tabela niżej). axe sprawdza też kontrast wyrenderowanego tekstu.
- Środowisko lokalne: `vite build` + `vite preview` (proxy do backendu FastAPI na 127.0.0.1:8000), nie tunel ani demo.

Skrypty: `prezentacja/audyt/skrypty/` (`audyt.mjs`, `klawiatura.mjs`, `odstepy.mjs`, `mapa.mjs`). Raporty: `prezentacja/audyt/lighthouse-po-{320,1440}.{html,json}`, `axe-przed.json`, `axe-po.json`. Zrzuty: `prezentacja/audyt/zrzuty/`.

## Klawiatura (WCAG 2.1.1, 2.4.3, 2.4.7, 2.4.11)

| Sprawdzenie | Wynik |
|---|---|
| Pierwszy Tab | „Przejdź do treści”, widoczny; Enter przenosi do `#tresc` |
| Fokus po zmianie kroku | zawsze na `h1` kroku (krok 1, 2, 3, „Dane opublikowane”); tytuł karty zmienia się na „Krok N z 3: …” |
| Fokus po wgraniu pliku i po sprawdzeniu | na nagłówku „Dopasuj kolumny” i „Wynik sprawdzenia” |
| Widoczny fokus | na każdym elemencie (obrys 3 px `#1a4e8a`, 8,4:1) |
| Kolejność | zgodna z kolejnością wizualną, bez skoków w górę |
| Błędy formularza | fokus na pierwsze błędne pole, `aria-invalid`, komunikat podpięty przez `aria-describedby` |
| Błędy walidacji pliku | listy wyboru kolumn i „Ustaw dla wszystkich AED” wskazują `aria-describedby` na grupę komunikatów swojego pola |
| Zgoda CC0, Opublikuj, Kopiuj | obsługa Spacją i Enterem; wynik „Kopiuj” ogłaszany przez `role="status"` |
| Fokus zasłonięty (2.4.11) | brak przyklejonych nagłówków, nic nie zasłania fokusu |

## Kontrast (WCAG 1.4.3, 1.4.11)

| Zastosowanie | Kolory | Kontrast |
|---|---|---|
| zieleń kampanii na białym: **nieużywana w interfejsie** | `#008c15` na `#ffffff` | 4,41:1 (za mało dla tekstu) |
| przyciski i zielony tekst | `#006b10` na `#ffffff` | 6,75:1 |
| biały tekst na przycisku / hover | `#ffffff` na `#006b10` / `#00520c` | 6,75:1 / 9,49:1 |
| tekst główny | `#101820` na `#ffffff` | 17,89:1 |
| tekst drugorzędny | `#3f4a45` na `#ffffff` / `#f3f7f4` | 9,22:1 / 8,53:1 |
| linki | `#1a4e8a` na `#ffffff` | 8,40:1 |
| błąd (tekst / na tle ramki) | `#b3261e` na `#ffffff` / `#fdecea` | 6,54:1 / 5,72:1 |
| ostrzeżenie (tekst / na tle ramki) | `#8a5a00` na `#ffffff` / `#fff4dc` | 5,93:1 / 5,43:1 |
| znacznik „pewne” | `#006b10` na `#e6f4e8` | 5,94:1 |
| stopka (tekst / link) | `#101820` / `#1a4e8a` na `#d1e0d7` | 13,08:1 / 6,14:1 |
| obramowanie pól formularza | `#5f6b66` na `#ffffff` | 5,55:1 (wymagane 3:1) |
| obrys fokusu | `#1a4e8a` na `#ffffff` | 8,40:1 (wymagane 3:1) |
| akcent `#5bc500` (pasek pod nagłówkiem, serce w logo) | `#5bc500` na `#ffffff` | 2,23:1, tylko dekoracja i logo (wyjątek 1.4.3) |

`#008c15` jest tylko w `tokens.css`. Cały zielony tekst i przyciski używają `#006b10`.

## Poprawki

| Problem | Kryterium | Waga | Poprawka |
|---|---|---|---|
| Tabela mapowania przy 768–1440 px i pliku z długimi wartościami (`przemysl_2024.csv`): kolumna „Co zawiera” ma ok. 80 px, listy wyboru są nieczytelne | 1.4.10 Reflow / użyteczność | poważna | od 700 px: lista wyboru min. 15 rem, kolumna z nazwą maks. 40%, kolumna podpowiedzi min. 9 rem; przykłady wartości przycięte wizualnie do 2 linii (`line-clamp`), czytnik ekranu dostaje pełną treść |
| Komunikat zapasowy „Kopiuj” podawał tylko Ctrl+C | 3.3.2 Etykiety i instrukcje | drobna | „Ctrl+C (na Macu Cmd+C)” |

Rozwiązania, które były w froncie przed audytem: fokus na nagłówek po zmianie kroku, tytuł strony per krok, błędy przy polach (`aria-invalid`, `aria-describedby`), stan kroku w postępie tekstem („zrobione”, `aria-current="step"`), pewność podpowiedzi tekstem i kolorem, przyciski min. 44 px, karty zamiast tabeli poniżej 700 px, ciemniejsza zieleń `#006b10`, `lang="pl"`, region `aria-live` przy wgrywaniu i sprawdzaniu.

## Mapa AED (/mapa, dodana po audycie kreatora)

Sprawdzona tymi samymi narzędziami (axe-core, Playwright) przy 320, 768 i 1440 px, z OSM i bez OSM oraz z otwartym popupem: 0 naruszeń WCAG, bez poziomego przewijania strony.

| Sprawdzenie | Wynik |
|---|---|
| Klawiatura | Tab przechodzi po kontrolkach przybliżenia, grupach (klastrach) i punktach; Enter na grupie przybliża, na punkcie otwiera popup; fokus wchodzi do popupu, Escape zamyka i wraca na punkt; mapę przesuwają strzałki, gdy kontener ma fokus |
| Nazwy dostępne | grupa: „1515 AED w tym obszarze. Enter przybliża.”; punkt: „AED: {nazwa obiektu}” (`role="button"`) |
| Cel dotyku punktu | 24×24 px (widoczna kropka 14 px) |
| Alternatywa tekstowa | liczba AED na mapie (`role="status"`), tabela liczby AED według pochodzenia, linki do CSV i GeoJSON tych samych danych |
| Kolor | pochodzenie punktu opisane w legendzie tekstem i w popupie, nie tylko kolorem |
| Bezpieczeństwo treści | popup budowany przez DOM (`textContent`), dane z zewnętrznych źródeł nie są wstawiane jako HTML |

Poprawka w trakcie: Escape nie zamykał popupu, bo Leaflet obsługuje klawisze tylko przy fokusie na kontenerze mapy. Dodaliśmy własną obsługę Escape z powrotem fokusu na punkt (WCAG 2.1.2, 2.4.3).

Ograniczenia mapy: kafelki OSM to obraz bez tekstu dla czytnika ekranu (stąd alternatywa pod mapą); przejście Tabem po wszystkich punktach przy dużym przybliżeniu jest długie, dlatego pełna lista jest w CSV.

## Znane ograniczenia

- Nie testowaliśmy na prawdziwych czytnikach ekranu (NVDA, VoiceOver, TalkBack) ani z udziałem użytkowników. Automaty wykrywają ok. 30–50% problemów WCAG. Resztę sprawdziliśmy ręcznie skryptami (klawiatura, odstępy), ale bez odsłuchu.
- Natywne `<select>` i `<input type="file">` wyglądają i działają zależnie od systemu. Na macOS strzałka otwiera listę zamiast zmieniać wartość. Napis przycisku pliku pochodzi z przeglądarki (w polskiej wersji „Wybierz plik”).
- Przyciski „Dalej” i „Opublikuj” są wyłączone (`disabled`), dopóki nie ma warunków, więc nie dostają fokusu. Powód jest napisany tekstem tuż pod nimi i podpięty przez `aria-describedby`.
- Długie przykłady wartości w tabeli mapowania są przycięte do 2 linii tylko wizualnie. Osoba widząca nie zobaczy całego opisu, ale to wyłącznie podgląd pliku.
- Nie sprawdzaliśmy trybu wysokiego kontrastu systemu (`forced-colors`) ani powiększenia 400% poza odpowiednikiem 320 px.
- Kod źródłowy pliku publikowanego (CSV/JSON) nie jest częścią audytu. To dane, nie interfejs.
