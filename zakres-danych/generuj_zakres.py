#!/usr/bin/env python3
"""Generuje wzorcowy zakres danych o defibrylatorach AED (xlsx + CSV).

Uruchomienie:  python3 generuj_zakres.py   (wymaga: pip install openpyxl)
Wynik (w katalogu skryptu):
  - wzorcowy-zakres-danych-AED.xlsx  (deliverable dla jury)
  - zakres-pol.csv                    (opis pól, wersja maszynowa)
  - szablon-aed.csv                   (pusty szablon z nagłówkami do wypełnienia)
  - slowniki.csv                      (wartości słownikowe)
"""
import csv
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

OUT = Path(__file__).resolve().parent
WERSJA = "0.1 (szkic, 2026-11-21)"

# Wymagalność: O = obowiązkowe, Z = zalecane, F = fakultatywne
# (grupa, pole, nazwa wyświetlana, typ, format/słownik, wymagalność, opis, przykład, OSM, Warszawa 19115, Legionowo / Krosno)
POLA = [
    # --- Identyfikacja ---
    ("Identyfikacja", "id_aed", "Identyfikator AED", "tekst", "unikalny i stały w zbiorze dostawcy; zalecany wzór <kod_terc>-<numer>", "O",
     "Stały identyfikator urządzenia nadany przez dostawcę danych. Nie zmienia się przy aktualizacji rekordu.", "1408011-0001", "@osm_id (inny system)", "id", "– / id"),
    ("Identyfikacja", "id_zrodlowe", "Identyfikator w systemie źródłowym", "tekst", "dowolny", "F",
     "Identyfikator rekordu w systemie, z którego pochodzi (np. ewidencja miasta).", "AED-WAW-0512", "ref", "id", "– / id"),
    ("Identyfikacja", "osm_id", "Identyfikator OpenStreetMap", "tekst", "node/<liczba> lub way/<liczba>", "F",
     "Powiązanie z obiektem w OSM, ułatwia deduplikację z mapą OSM, Geoportalem i mojeIKP. UWAGA: wg wytycznych OSMF powiązanie kluczem może sprawić, że zbiór uzna się za pochodny od OSM (ODbL). Pole do potwierdzenia z MC.", "node/123456789", "@osm_type/@osm_id", "–", "–"),

    # --- Lokalizacja ---
    ("Lokalizacja", "szerokosc_geograficzna", "Szerokość geograficzna", "liczba dziesiętna", "WGS84 (EPSG:4326), min. 6 miejsc po przecinku, kropka dziesiętna", "O",
     "Szerokość geograficzna miejsca, w którym fizycznie znajduje się urządzenie (nie środek budynku).", "52.395198", "geometria (lat)", "geometria [[lon,lat]]", "szerokosc_geograficzna / lat"),
    ("Lokalizacja", "dlugosc_geograficzna", "Długość geograficzna", "liczba dziesiętna", "WGS84 (EPSG:4326), min. 6 miejsc po przecinku, kropka dziesiętna", "O",
     "Długość geograficzna miejsca urządzenia.", "20.931382", "geometria (lon)", "geometria [[lon,lat]]", "dlugosc_geograficzna / lon"),
    ("Lokalizacja", "nazwa_obiektu", "Nazwa obiektu", "tekst", "dowolny", "O",
     "Nazwa budynku lub miejsca, w którym jest AED, zrozumiała dla osoby z zewnątrz.", "Urząd Miasta Legionowo", "name (rzadko)", "nazwa obiektu", "nazwa / nazwa"),
    ("Lokalizacja", "cecha_ulicy", "Cecha ulicy", "słownik", "słownik: cecha_ulicy (wg TERYT ULIC)", "Z",
     "Rodzaj ulicy zgodnie z rejestrem TERYT.", "ulica", "–", "w adresie", "cecha_ulicy / –"),
    ("Lokalizacja", "nazwa_ulicy", "Nazwa ulicy", "tekst", "pełna nazwa bez cechy, zgodna z TERYT ULIC", "O",
     "Słowna nazwa ulicy (lub placu, alei). Gdy obiekt nie ma ulicy, wpisuje się nazwę miejscowości.", "Piłsudskiego", "addr:street (rzadko)", "ulica", "nazwa_ulicy / w polu adres"),
    ("Lokalizacja", "nr_budynku", "Numer budynku", "tekst", "np. 41, 12A", "Z",
     "Numer porządkowy budynku.", "41", "addr:housenumber (rzadko)", "nr domu", "nr_budynku / w polu adres"),
    ("Lokalizacja", "nr_lokalu", "Numer lokalu", "tekst", "dowolny", "F",
     "Numer lokalu, jeśli dotyczy.", "", "–", "–", "nr_lokalu / –"),
    ("Lokalizacja", "kod_pocztowy", "Kod pocztowy", "tekst", "NN-NNN", "Z",
     "Kod pocztowy adresu.", "05-120", "addr:postcode", "kod pocztowy", "kod_pocztowy / –"),
    ("Lokalizacja", "miejscowosc", "Miejscowość", "tekst", "nazwa zgodna z TERYT SIMC", "O",
     "Nazwa miejscowości.", "Legionowo", "addr:city (rzadko)", "miasto", "miejscowosc / w polu adres"),
    ("Lokalizacja", "kod_terc", "Kod TERC gminy", "tekst", "7 cyfr (TERYT TERC, z rodzajem gminy)", "Z",
     "Kod gminy z rejestru TERYT. Pozwala agregować dane według gmin, powiatów i województw.", "1408011", "–", "– (dzielnica tekstem)", "kod_terc (6 cyfr) / –"),
    ("Lokalizacja", "kod_simc", "Kod SIMC miejscowości", "tekst", "7 cyfr (TERYT SIMC), z zerami wiodącymi", "Z",
     "Identyfikator miejscowości z rejestru TERYT.", "0920806", "–", "–", "kod_simc / –"),
    ("Lokalizacja", "kod_ulic", "Kod ULIC ulicy", "tekst", "5 cyfr (TERYT ULIC)", "F",
     "Identyfikator ulicy z rejestru TERYT.", "12345 (przykład)", "–", "–", "– / –"),
    ("Lokalizacja", "wewnatrz_budynku", "Wewnątrz budynku", "słownik", "słownik: tak_nie", "O",
     "Czy urządzenie jest wewnątrz budynku (tak) czy na zewnątrz (nie).", "tak", "indoor", "wewnątrz/na zewnątrz", "– / –"),
    ("Lokalizacja", "kondygnacja", "Kondygnacja", "liczba całkowita", "0 = parter, -1 = piwnica", "F",
     "Kondygnacja, na której jest urządzenie.", "0", "level", "piętro", "– / –"),
    ("Lokalizacja", "opis_lokalizacji", "Opis miejsca", "tekst", "krótki opis, max ok. 200 znaków", "Z",
     "Jak znaleźć urządzenie na miejscu.", "Hol główny, na ścianie przy recepcji", "defibrillator:location(:pl)", "opis lokalizacji", "– / lokalizacja"),
    ("Lokalizacja", "zdjecie_url", "Zdjęcie (adres URL)", "URL", "https://…, plik JPG/PNG; nie osadzać base64", "F",
     "Adres zdjęcia pokazującego urządzenie i jego otoczenie.", "https://example.gov.pl/aed/1408011-0001.jpg", "image", "zdjęcie (base64)", "– / –"),
    ("Lokalizacja", "zdjecie_licencja", "Licencja zdjęcia", "tekst", "np. CC BY 4.0, CC0", "F",
     "Licencja, na której udostępniono zdjęcie (wymagana, gdy podano zdjecie_url).", "CC0 1.0", "image:license", "–", "– / –"),

    # --- Dostępność ---
    ("Dostępność", "dostepnosc", "Kto ma dostęp", "słownik", "słownik: dostepnosc", "O",
     "Kto może skorzystać z urządzenia.", "publiczny", "access", "publiczny/prywatny", "– / –"),
    ("Dostępność", "dostepny_24_7", "Dostępny całą dobę", "słownik", "słownik: tak_nie_ograniczony", "O",
     "Czy urządzenie jest dostępne przez całą dobę, 7 dni w tygodniu.", "nie", "opening_hours=24/7", "dostępność 24/7 (Tak/Nie/Ograniczona)", "– / –"),
    ("Dostępność", "godziny_dostepnosci", "Godziny dostępności", "tekst", "składnia OSM opening_hours", "Z",
     "Godziny, w których urządzenie jest dostępne. Wymagane, gdy dostepny_24_7 = nie lub ograniczony.", "Mo-Fr 07:30-15:30; Sa-Su,PH off", "opening_hours", "godziny (wolny tekst)", "– / –"),
    ("Dostępność", "zabezpieczenie", "Zabezpieczenie urządzenia", "słownik", "słownik: zabezpieczenie", "Z",
     "Czy i jak urządzenie jest zamknięte. Kodów ani haseł do szafki nie publikuje się.", "szafka_otwarta", "–", "–", "– / –"),
    ("Dostępność", "instrukcja_dostepu", "Jak uzyskać dostęp", "tekst", "krótki opis, bez kodów i haseł", "F",
     "Informacja, co zrobić, gdy urządzenie jest zamknięte lub w strefie z ograniczonym wejściem.", "Klucz w portierni, czynnej całą dobę", "description", "–", "– / –"),
    ("Dostępność", "dostepnosc_wozek", "Dostęp dla osób na wózku", "słownik", "słownik: tak_nie_ograniczony", "F",
     "Czy osoba na wózku dotrze do urządzenia bez barier.", "tak", "wheelchair", "–", "– / –"),

    # --- Urządzenie ---
    ("Urządzenie", "producent", "Producent", "tekst", "dowolny", "F",
     "Producent urządzenia.", "Philips", "manufacturer", "producent (wolny tekst)", "– / –"),
    ("Urządzenie", "model", "Model", "tekst", "dowolny", "F",
     "Model urządzenia.", "HeartStart FRx", "model", "–", "– / –"),
    ("Urządzenie", "tryb_pediatryczny", "Elektrody lub tryb dziecięcy", "słownik", "słownik: tak_nie", "F",
     "Czy urządzenie ma elektrody pediatryczne lub tryb dla dzieci.", "tak", "–", "–", "– / –"),

    # --- Stan i aktualność ---
    ("Stan i aktualność", "status", "Status urządzenia", "słownik", "słownik: status", "O",
     "Aktualny stan urządzenia według ostatniej wiedzy dysponenta.", "sprawny", "–", "status zgłoszenia (inne znaczenie)", "– / –"),
    ("Stan i aktualność", "data_weryfikacji", "Data ostatniej weryfikacji", "data", "ISO 8601: RRRR-MM-DD", "O",
     "Data, w której ktoś na miejscu potwierdził obecność, dostępność i sprawność urządzenia.", "2026-11-15", "check_date", "data ostatniej weryfikacji", "– / –"),
    ("Stan i aktualność", "data_przegladu", "Data ostatniego przeglądu", "data", "ISO 8601: RRRR-MM-DD", "F",
     "Data ostatniego przeglądu technicznego.", "2026-03-01", "–", "–", "– / –"),
    ("Stan i aktualność", "data_waznosci_elektrod", "Ważność elektrod", "data", "ISO 8601: RRRR-MM-DD", "F",
     "Data ważności elektrod.", "2028-05-31", "–", "–", "– / –"),
    ("Stan i aktualność", "data_waznosci_baterii", "Ważność baterii", "data", "ISO 8601: RRRR-MM-DD", "F",
     "Data ważności baterii.", "2029-01-31", "–", "–", "– / –"),

    # --- Dysponent ---
    ("Dysponent", "dysponent_nazwa", "Dysponent urządzenia", "tekst", "pełna nazwa instytucji lub firmy", "O",
     "Instytucja odpowiedzialna za urządzenie (właściciel lub zarządca).", "Urząd Miasta Legionowo", "operator", "–", "– / –"),
    ("Dysponent", "dysponent_typ", "Typ dysponenta", "słownik", "słownik: dysponent_typ", "Z",
     "Kategoria dysponenta.", "jst", "operator:type (rzadko)", "–", "– / –"),
    ("Dysponent", "dysponent_regon", "REGON dysponenta", "tekst", "9 lub 14 cyfr", "F",
     "REGON instytucji. Ułatwia jednoznaczne powiązanie urządzeń z dysponentem.", "000000000 (przykład)", "–", "–", "– / –"),
    ("Dysponent", "telefon_kontaktowy", "Telefon kontaktowy", "tekst", "+48 NNN NNN NNN; wyłącznie numer służbowy", "Z",
     "Służbowy numer w sprawie urządzenia (np. portiernia, ochrona). Nie podaje się danych osobowych.", "+48 22 000 00 00 (przykład)", "phone / emergency:phone", "–", "– / –"),
    ("Dysponent", "email_kontaktowy", "E-mail kontaktowy", "tekst", "adres funkcyjny, np. aed@…", "F",
     "Służbowy adres funkcyjny, pod który można zgłosić problem z urządzeniem. Nie imienny.", "aed@example.gov.pl", "email", "–", "– / –"),

    # --- Metadane rekordu ---
    ("Metadane rekordu", "zrodlo_danych", "Źródło danych", "słownik", "słownik: zrodlo_danych", "O",
     "Skąd pochodzi rekord.", "dysponent", "source", "–", "– / –"),
    ("Metadane rekordu", "data_aktualizacji", "Data aktualizacji rekordu", "data i czas", "ISO 8601: RRRR-MM-DDTGG:MM:SS+01:00", "O",
     "Moment ostatniej zmiany rekordu (dowolnego pola).", "2026-11-21T12:00:00+01:00", "@osm_version (pośrednio)", "–", "– / –"),
    ("Metadane rekordu", "uwagi", "Uwagi", "tekst", "dowolny", "F",
     "Dodatkowe informacje.", "", "note / description", "–", "– / –"),
]

SLOWNIKI = {
    "tak_nie": [("tak", "Tak"), ("nie", "Nie")],
    "tak_nie_ograniczony": [("tak", "Tak"), ("nie", "Nie"), ("ograniczony", "Częściowo / z ograniczeniami")],
    "cecha_ulicy": [("ulica", "ul."), ("aleja", "al."), ("plac", "pl."), ("skwer", "skwer"), ("rondo", "rondo"),
                    ("osiedle", "os."), ("bulwar", "bulw."), ("inne", "inna cecha wg TERYT")],
    "dostepnosc": [("publiczny", "Dostępny dla każdego (OSM: access=yes)"),
                   ("klienci", "Dla klientów lub odwiedzających obiekt w godzinach otwarcia (OSM: access=customers)"),
                   ("na_prosbe", "Po zgłoszeniu się do obsługi lub ochrony (OSM: access=permit)"),
                   ("prywatny", "Tylko dla pracowników lub mieszkańców (OSM: access=private)")],
    "zabezpieczenie": [("brak", "Urządzenie bez szafki"),
                       ("szafka_otwarta", "Szafka otwierana bez klucza (może mieć alarm)"),
                       ("szafka_kod", "Szafka zamknięta na kod (kod podaje dyspozytor 112 lub obsługa)"),
                       ("szafka_klucz", "Szafka lub pomieszczenie zamknięte na klucz")],
    "status": [("sprawny", "Urządzenie dostępne i sprawne"),
               ("tymczasowo_niedostepny", "Czasowo niedostępne (serwis, remont, użycie)"),
               ("niesprawny", "Zgłoszona usterka"),
               ("wycofany", "Urządzenie usunięte; rekord zostaje dla historii")],
    "dysponent_typ": [("administracja_rzadowa", "Administracja rządowa"), ("jst", "Jednostka samorządu terytorialnego"),
                      ("ochrona_zdrowia", "Podmiot leczniczy"), ("edukacja", "Szkoła lub uczelnia"),
                      ("sluzby", "Służby (PSP, OSP, Policja)"), ("transport", "Transport (dworzec, pojazd, lotnisko)"),
                      ("firma", "Przedsiębiorstwo"), ("ngo", "Organizacja pozarządowa"),
                      ("wyznaniowy", "Związek wyznaniowy"), ("inne", "Inne")],
    "zrodlo_danych": [("dysponent", "Dane podane przez dysponenta urządzenia"),
                      ("jst", "Ewidencja jednostki samorządu"),
                      ("osm", "OpenStreetMap (licencja ODbL)"),
                      ("zgloszenie_zweryfikowane", "Zgłoszenie obywatela potwierdzone przez dysponenta"),
                      ("inne", "Inne źródło")],
}

ZASADY = [
    ("Format pliku", "CSV w kodowaniu UTF-8 (bez BOM), separator: przecinek, zgodnie z RFC 4180. Pierwszy wiersz to nagłówki = nazwy techniczne pól."),
    ("Jeden wiersz", "Jeden wiersz = jedno urządzenie AED."),
    ("Współrzędne", "WGS84 (EPSG:4326), dwie osobne kolumny, kropka dziesiętna, kolejność: szerokość, długość."),
    ("Daty", "ISO 8601 (RRRR-MM-DD, a dla daty i czasu RRRR-MM-DDTGG:MM:SS ze strefą czasową)."),
    ("Adres", "Każdy element adresu w osobnym polu. Kody TERYT (TERC, SIMC, ULIC) zalecane."),
    ("Słowniki", "Pola słownikowe przyjmują tylko kody z arkusza „Słowniki”."),
    ("Puste wartości", "Brak wartości = puste pole. Nie wpisywać „brak”, „-”, „0”."),
    ("Dane osobowe", "Bez imion, nazwisk i prywatnych numerów. Kontakt tylko służbowy lub funkcyjny. Kodów do szafek nie publikuje się."),
    ("Wymagalność", "O = obowiązkowe, Z = zalecane, F = fakultatywne."),
    ("Zgodność z OSM", "Kolumna „Odpowiednik OSM” wskazuje tag emergency=defibrillator, co pozwala łączyć zbiór z OpenStreetMap."),
]

# Metadane zbioru na dane.gov.pl (propozycja, do potwierdzenia z rozp. Dz.U. 2022 poz. 2415 §6–7 i DCAT-AP-PL).
METADANE = [
    ("Tytuł", "dct:title", "Defibrylatory AED – <nazwa dysponenta>"),
    ("Opis", "dct:description", "Wykaz automatycznych defibrylatorów zewnętrznych (AED) wraz z lokalizacją, dostępnością i stanem, zgodny z wzorcowym zakresem danych AED."),
    ("Słowa kluczowe", "dcat:keyword", "AED, defibrylator, pierwsza pomoc, ratownictwo, zdrowie"),
    ("Kategoria", "dcat:theme", "Zdrowie (HEAL); Rząd i sektor publiczny (GOVE)"),
    ("Licencja", "dct:license", "CC0 1.0 lub CC BY 4.0 (do ustalenia z MC). Portal dane.gov.pl nie oferuje ODbL, więc danych z OSM nie można wprost włączyć do zbioru."),
    ("Częstotliwość aktualizacji", "dct:accrualPeriodicity", "co najmniej raz w miesiącu oraz po każdej zmianie"),
    ("Zasięg przestrzenny", "dct:spatial", "obszar dysponenta (kod TERC)"),
    ("Dostawca", "dct:publisher", "nazwa dostawcy na dane.gov.pl"),
    ("Format zasobu", "dct:format", "CSV (UTF-8, RFC 4180); opcjonalnie GeoJSON"),
    ("Kontakt", "dcat:contactPoint", "adres funkcyjny dostawcy"),
]

# Przykładowe rekordy. Rekord 1 to dane rzeczywiste z dane.gov.pl (Legionowo, CC0); pola, których źródło nie ma, pozostają puste.
# Rekordy 2 i 3 są FIKCYJNE i pokazują pełne wypełnienie.
PRZYKLADY = [
    {"id_aed": "1408011-0001", "szerokosc_geograficzna": "52.395198", "dlugosc_geograficzna": "20.931382",
     "nazwa_obiektu": "Urząd Miasta Legionowo", "cecha_ulicy": "ulica", "nazwa_ulicy": "Piłsudskiego", "nr_budynku": "41",
     "kod_pocztowy": "05-120", "miejscowosc": "Legionowo", "kod_terc": "1408011", "kod_simc": "0920806",
     "dysponent_nazwa": "Urząd Miasta Legionowo", "dysponent_typ": "jst", "zrodlo_danych": "jst",
     "uwagi": "Dane rzeczywiste: dane.gov.pl, zasób 2625221 (CC0). Kod TERC uzupełniony do 7 cyfr (źródło podaje 6 cyfr: 140801). Pozostałe pola puste, bo nie ma ich w źródle."},
    {"id_aed": "PRZYKLAD-0002", "szerokosc_geograficzna": "52.229676", "dlugosc_geograficzna": "21.012229",
     "nazwa_obiektu": "Szkoła Podstawowa nr 999 (przykład)", "cecha_ulicy": "ulica", "nazwa_ulicy": "Przykładowa",
     "nr_budynku": "1", "kod_pocztowy": "00-001", "miejscowosc": "Warszawa", "wewnatrz_budynku": "tak", "kondygnacja": "0",
     "opis_lokalizacji": "Hol główny, przy portierni", "dostepnosc": "na_prosbe", "dostepny_24_7": "nie",
     "godziny_dostepnosci": "Mo-Fr 07:00-17:00; Sa-Su,PH off", "zabezpieczenie": "szafka_otwarta",
     "instrukcja_dostepu": "Wejście główne, poprosić portiera", "dostepnosc_wozek": "tak", "producent": "Philips",
     "model": "HeartStart FRx", "tryb_pediatryczny": "tak", "status": "sprawny", "data_weryfikacji": "2026-11-15",
     "data_przegladu": "2026-03-01", "data_waznosci_elektrod": "2028-05-31", "data_waznosci_baterii": "2029-01-31",
     "dysponent_nazwa": "Szkoła Podstawowa nr 999 (przykład)", "dysponent_typ": "edukacja",
     "telefon_kontaktowy": "+48 22 000 00 00", "email_kontaktowy": "aed@example.edu.pl", "zrodlo_danych": "dysponent",
     "data_aktualizacji": "2026-11-21T12:00:00+01:00", "uwagi": "REKORD FIKCYJNY – przykład wypełnienia"},
    {"id_aed": "PRZYKLAD-0003", "osm_id": "node/1", "szerokosc_geograficzna": "50.061947", "dlugosc_geograficzna": "19.936856",
     "nazwa_obiektu": "Przystanek przykładowy", "nazwa_ulicy": "Przykładowa", "miejscowosc": "Kraków",
     "wewnatrz_budynku": "nie", "opis_lokalizacji": "Szafka na ścianie wiaty, od strony jezdni", "dostepnosc": "publiczny",
     "dostepny_24_7": "tak", "godziny_dostepnosci": "24/7", "zabezpieczenie": "szafka_kod",
     "instrukcja_dostepu": "Kod do szafki podaje dyspozytor pod numerem 112", "status": "tymczasowo_niedostepny",
     "data_weryfikacji": "2026-10-02", "dysponent_nazwa": "Przykładowy Zarząd Transportu", "dysponent_typ": "transport",
     "zrodlo_danych": "zgloszenie_zweryfikowane", "data_aktualizacji": "2026-11-20T08:30:00+01:00",
     "uwagi": "REKORD FIKCYJNY – urządzenie zabrane do serwisu po użyciu"},
]

NAGLOWKI_POL = ["Lp.", "Grupa", "Nazwa techniczna pola", "Nazwa wyświetlana", "Typ danych", "Format / słownik",
                "Wymagalność", "Opis", "Przykład", "Odpowiednik OSM (emergency=defibrillator)",
                "Odpowiednik: Warszawa 19115", "Odpowiednik: Legionowo / Krosno (dane.gov.pl)"]

HEAD_FONT = Font(bold=True, color="FFFFFF")
HEAD_FILL = PatternFill("solid", fgColor="1F4E79")
REQ_FILL = {"O": PatternFill("solid", fgColor="F8D7DA"), "Z": PatternFill("solid", fgColor="FFF3CD"),
            "F": PatternFill("solid", fgColor="E2EFDA")}
WRAP = Alignment(wrap_text=True, vertical="top")


def naglowek(ws, wiersz, szer):
    ws.append(wiersz)
    for i, c in enumerate(ws[ws.max_row], 1):
        c.font, c.fill, c.alignment = HEAD_FONT, HEAD_FILL, WRAP
    for i, w in enumerate(szer, 1):
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.freeze_panes = f"A{ws.max_row + 1}"


def main():
    wb = Workbook()

    ws = wb.active
    ws.title = "Informacje"
    ws.column_dimensions["A"].width = 24
    ws.column_dimensions["B"].width = 110
    ws.append(["Wzorcowy zakres danych o defibrylatorach AED"])
    ws["A1"].font = Font(bold=True, size=14)
    ws.append(["Wersja", WERSJA])
    ws.append(["Cel", "Jednolity zakres danych, w którym każdy dysponent AED udostępnia dane na portalu dane.gov.pl, tak by dało się je połączyć w jeden ogólnopolski zbiór."])
    ws.append(["Arkusze", "Zakres danych – opis pól; Słowniki – dozwolone wartości; Szablon – nagłówki do wypełnienia; Przykłady – przykładowe rekordy; Metadane zbioru – propozycja opisu zbioru na dane.gov.pl."])
    ws.append([])
    ws.append(["Zasady"])
    ws.cell(row=ws.max_row, column=1).font = Font(bold=True)
    for k, v in ZASADY:
        ws.append([k, v])
    ws.append([])
    ws.append(["Podstawy", "Standard techniczny dane.gov.pl; Rozporządzenie RM Dz.U. 2022 poz. 2415; DCAT-AP-PL; tagowanie OSM emergency=defibrillator; schematy zbiorów Legionowo, Krosno i Warszawa (19115); wzorce The Circuit (UK) i Hjertestarter (DK)."])
    ws.append(["Licencja zakresu", "Do ustalenia (proponowane CC0 1.0)."])
    for row in ws.iter_rows(min_row=2):
        for c in row:
            c.alignment = WRAP

    ws = wb.create_sheet("Zakres danych")
    naglowek(ws, NAGLOWKI_POL, [5, 16, 26, 26, 14, 34, 12, 50, 26, 26, 24, 26])
    for i, p in enumerate(POLA, 1):
        g, pole, nazwa, typ, fmt, wym, opis, przyk, osm, waw, leg = p
        ws.append([i, g, pole, nazwa, typ, fmt, wym, opis, przyk, osm, waw, leg])
        for c in ws[ws.max_row]:
            c.alignment = WRAP
        ws.cell(row=ws.max_row, column=7).fill = REQ_FILL[wym]
        ws.cell(row=ws.max_row, column=3).font = Font(name="Consolas")
    ws.auto_filter.ref = ws.dimensions

    ws = wb.create_sheet("Słowniki")
    naglowek(ws, ["Słownik", "Kod (wartość w pliku)", "Znaczenie"], [24, 28, 80])
    for nazwa, wartosci in SLOWNIKI.items():
        for kod, znaczenie in wartosci:
            ws.append([nazwa, kod, znaczenie])
    ws.auto_filter.ref = ws.dimensions

    nazwy = [p[1] for p in POLA]
    wym = {p[1]: p[5] for p in POLA}
    slownik_pola = {p[1]: p[4].split("słownik: ")[1].split(" ")[0] for p in POLA if p[3] == "słownik"}

    ws = wb.create_sheet("Szablon")
    naglowek(ws, nazwy, [22] * len(nazwy))
    for i, n in enumerate(nazwy, 1):
        ws.cell(row=1, column=i).fill = REQ_FILL[wym[n]]
        ws.cell(row=1, column=i).font = Font(bold=True)
    # listy rozwijane dla pól słownikowych
    for i, n in enumerate(nazwy, 1):
        if n in slownik_pola:
            kody = ",".join(k for k, _ in SLOWNIKI[slownik_pola[n]])
            dv = DataValidation(type="list", formula1=f'"{kody}"', allow_blank=True)
            col = get_column_letter(i)
            dv.add(f"{col}2:{col}1000")
            ws.add_data_validation(dv)

    ws = wb.create_sheet("Przykłady")
    naglowek(ws, nazwy, [22] * len(nazwy))
    for r in PRZYKLADY:
        ws.append([r.get(n, "") for n in nazwy])

    ws = wb.create_sheet("Metadane zbioru")
    naglowek(ws, ["Element", "Właściwość DCAT-AP-PL", "Proponowana wartość"], [26, 26, 90])
    for row in METADANE:
        ws.append(list(row))
        for c in ws[ws.max_row]:
            c.alignment = WRAP

    xlsx = OUT / "wzorcowy-zakres-danych-AED.xlsx"
    wb.save(xlsx)

    with open(OUT / "zakres-pol.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["lp", "grupa", "pole", "nazwa", "typ", "format", "wymagalnosc", "opis", "przyklad", "osm", "warszawa_19115", "legionowo_krosno"])
        for i, p in enumerate(POLA, 1):
            w.writerow([i, *p])
    with open(OUT / "szablon-aed.csv", "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow(nazwy)
    with open(OUT / "slowniki.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["slownik", "kod", "znaczenie"])
        for nazwa, wartosci in SLOWNIKI.items():
            for kod, zn in wartosci:
                w.writerow([nazwa, kod, zn])

    print(f"{xlsx.name}: {len(POLA)} pól ({sum(1 for p in POLA if p[5]=='O')} O, "
          f"{sum(1 for p in POLA if p[5]=='Z')} Z, {sum(1 for p in POLA if p[5]=='F')} F), "
          f"{len(SLOWNIKI)} słowników, {len(PRZYKLADY)} przykłady")


if __name__ == "__main__":
    main()
