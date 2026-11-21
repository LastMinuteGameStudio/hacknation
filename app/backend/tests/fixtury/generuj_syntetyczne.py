"""D1: syntetyczne „urzędowe” XLSX + ich oczekiwane wyniki (oczekiwane/syntetyczny_*.json).

Uruchomienie (z app/backend):  .venv/bin/python tests/fixtury/generuj_syntetyczne.py

Pliki udają to, co urzędy naprawdę wysyłają: tytuł i data nad tabelą, scalone komórki (tytuł, nagłówek
dwupoziomowy, miejscowość scalona w pionie), przecinek dziesiętny, adres w jednym polu, „24h” i wolny tekst
w godzinach, kolumny w dziwnej kolejności, stopka „Sporządził”, powtórzona nazwa kolumny, daty jako daty
Excela i jako tekst „15.03.2026”. Nazwy podmiotów są zmyślone, współrzędne leżą w Polsce.
Zawartość jest stała (bajty XLSX mogą się różnić przez znaczniki czasu w ZIP).
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font

TU = Path(__file__).parent
OCZEKIWANE = TU / "oczekiwane"
STALA_DATA = datetime(2026, 10, 15, 12, 0, 0)


def _zapisz(wb: Workbook, nazwa: str) -> None:
    wb.properties.created = STALA_DATA
    wb.properties.modified = STALA_DATA
    wb.properties.creator = "Urząd (syntetyczny)"
    wb.save(TU / nazwa)


def _oczekiwane(nazwa: str, dane: dict) -> None:
    (OCZEKIWANE / nazwa).write_text(json.dumps(dane, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------------------------
# 1. Gmina: tytuł nad tabelą (scalony), kolumny w dziwnej kolejności, przecinek dziesiętny w tekście,
#    adres w jednym polu, „24h” w godzinach, miejscowość scalona w pionie, stopka pod tabelą.
# ---------------------------------------------------------------------------------------------
def gmina() -> None:
    wb = Workbook()
    ws = wb.active
    ws.title = "AED"
    naglowek = ["Lp.", "Godziny dostępności", "Adres", "Miejsce / obiekt", "Miejscowość",
                "Szer. geogr.", "Dł. geogr.", "Dostęp", "Gdzie wisi", "Uwagi"]
    ws["A1"] = "WYKAZ DEFIBRYLATORÓW AED NA TERENIE GMINY PRZYKŁADOWO"
    ws["A1"].font = Font(bold=True, size=14)
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=len(naglowek))
    ws["A2"] = "stan na dzień 15.10.2026 r."
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=len(naglowek))
    # wiersz 3 pusty
    for i, h in enumerate(naglowek, 1):
        c = ws.cell(row=4, column=i, value=h)
        c.font = Font(bold=True)
        c.alignment = Alignment(wrap_text=True)
    dane = [
        # lp, godziny, adres, obiekt, miejscowość, szer, dł, dostęp, gdzie, uwagi
        (1, "24h", "ul. Rynek 1, 34-100 Przykładowo", "Urząd Gminy", "Przykładowo",
         "49,883512", "19,493187", "ogólnodostępny", "na zewnątrz, przy wejściu głównym", ""),
        (2, "pn-pt 7:30-15:30", "ul. Szkolna 5, 34-100 Przykładowo", "Szkoła Podstawowa nr 1", None,
         "49,879044", "19,501266", "ogólnodostępny", "wewnątrz, hol na parterze", ""),
        (3, "całodobowo", "ul. Strażacka 2, 34-100 Przykładowo", "OSP Przykładowo", None,
         "49,886301", "19,487954", "ogólnodostępny", "na zewnątrz, szafka na ścianie remizy", "szafka ogrzewana"),
        (4, "w godzinach otwarcia ośrodka", "Wola Przykładowa 12, 34-101 Wola Przykładowa", "Ośrodek Zdrowia",
         "Wola Przykładowa", "49,861577", "19,520034", "w godzinach pracy", "wewnątrz, rejestracja", ""),
        (5, "24/7", "Wola Przykładowa 40, 34-101 Wola Przykładowa", "Świetlica wiejska", None,
         "49,858902", "19,524411", "ogólnodostępny", "na zewnątrz", "nowy, zamontowany 2026"),
    ]
    for r, wiersz in enumerate(dane, start=5):
        for c, v in enumerate(wiersz, 1):
            ws.cell(row=r, column=c, value=v)
    # Miejscowość scalona w pionie: Przykładowo w wierszach 5–7, Wola Przykładowa w 8–9.
    ws.merge_cells("E5:E7")
    ws.merge_cells("E8:E9")
    ws.cell(row=11, column=1, value="Sporządził: Referat Zarządzania Kryzysowego, tel. 33 000 00 00")
    ws.merge_cells("A11:J11")
    _zapisz(wb, "syntetyczny_gmina.xlsx")

    _oczekiwane("syntetyczny_gmina.json", {
        "plik": "syntetyczny_gmina.xlsx",
        "arkusz": None,
        "wymaga_100": False,
        "syntetyczny": True,
        "dostawca": {"nazwa": "Urząd Gminy Przykładowo", "typ": "jst", "slug": "gmina-przykladowo"},
        "wartosci_stale": {},
        "liczba_wierszy": 5,
        "naglowek_w_wierszu": 4,
        "mapowanie": {
            "Lp.": None,
            "Godziny dostępności": "_godziny",
            "Adres": "_adres_pelny",
            "Miejsce / obiekt": "nazwa_obiektu",
            "Miejscowość": ["miejscowosc", None],
            "Szer. geogr.": "szerokosc_geograficzna",
            "Dł. geogr.": "dlugosc_geograficzna",
            "Dostęp": "dostepnosc",
            "Gdzie wisi": ["opis_lokalizacji", "wewnatrz_budynku"],
            "Uwagi": "uwagi",
        },
        "rekordy": [
            {"wiersz": 5, "pola": {
                "nazwa_obiektu": "Urząd Gminy",
                "szerokosc_geograficzna": "49.883512", "dlugosc_geograficzna": "19.493187",
                "cecha_ulicy": "ulica", "nazwa_ulicy": "Rynek", "nr_budynku": "1",
                "kod_pocztowy": "34-100", "miejscowosc": "Przykładowo",
                "dostepny_24_7": "tak", "godziny_pn": "X", "godziny_nd": "X",
                "dostepnosc": "publiczny"}},
            {"wiersz": 6, "pola": {
                "nazwa_obiektu": "Szkoła Podstawowa nr 1", "miejscowosc": "Przykładowo",
                "dostepny_24_7": "nie", "godziny_pn": "07:30-15:30", "godziny_pt": "07:30-15:30",
                "godziny_so": ["zamkniete", ""], "szerokosc_geograficzna": "49.879044"}},
            {"wiersz": 7, "pola": {"dostepny_24_7": "tak", "miejscowosc": "Przykładowo", "uwagi": "szafka ogrzewana"}},
            {"wiersz": 8, "pola": {
                "nazwa_obiektu": "Ośrodek Zdrowia", "nazwa_ulicy": ["Wola Przykładowa"], "nr_budynku": "12",
                "kod_pocztowy": "34-101", "miejscowosc": "Wola Przykładowa", "dostepnosc": ["klienci", "na_prosbe"]}},
            {"wiersz": 9, "pola": {"dostepny_24_7": "tak", "miejscowosc": "Wola Przykładowa"}},
        ],
        "komunikaty": {
            "musza_byc": ["ROZBITO_ADRES"],
            "nie_moze_byc": ["POZA_POLSKA", "PUSTY_PLIK", "ZAMIENIONE_WSPOLRZEDNE"],
        },
        "uwagi": (
            "Nagłówek w wierszu 4 (tytuł scalony w A1:J1, data w A2, pusty wiersz 3), dane od wiersza 5. "
            "Stopka 'Sporządził:' w wierszu 11 nie jest rekordem. Miejscowość scalona w pionie (E5:E7, E8:E9): "
            "wartość jest tylko w pierwszej komórce, scalone wiersze powinny ją dziedziczyć. Współrzędne jako tekst z "
            "przecinkiem dziesiętnym. Godziny: '24h', 'całodobowo', '24/7' → dostepny_24_7=tak + X; "
            "'pn-pt 7:30-15:30' → godziny_pn..pt; 'w godzinach otwarcia ośrodka' → NIEZROZUMIALE_GODZINY. "
            "Wola Przykładowa 12: miejscowość bez ulicy → nazwa_ulicy = miejscowość (ULICA_Z_MIEJSCOWOSCI). "
            "'Gdzie wisi' łączy wewnątrz/na zewnątrz z opisem miejsca."),
    })


# ---------------------------------------------------------------------------------------------
# 2. Powiat: nagłówek dwupoziomowy ze scalonymi komórkami, liczby XLSX (float), daty Excela,
#    TAK/NIE, status „czynny”, arkusz z danymi nie jest pierwszy (pierwszy to „Informacje”).
# ---------------------------------------------------------------------------------------------
def powiat() -> None:
    wb = Workbook()
    info = wb.active
    info.title = "Informacje"
    info["A1"] = "Starostwo Powiatowe w Przykładowie"
    info["A2"] = "Ewidencja defibrylatorów w jednostkach powiatowych. Dane w arkuszu 'Defibrylatory'."
    ws = wb.create_sheet("Defibrylatory")
    ws["A1"] = "Ewidencja AED – jednostki powiatowe"
    ws.merge_cells("A1:N1")
    gora = ["Nr ewid.", "Jednostka", "Adres", None, None, None, "Położenie", None,
            "Wewnątrz budynku", "Stan", "Data przeglądu", "Ważność elektrod", "Nr seryjny", "Producent"]
    dol = [None, None, "Ulica", "Nr", "Kod", "Miejscowość", "Szerokość", "Długość",
           None, None, None, None, None, None]
    for i, (g, d) in enumerate(zip(gora, dol), 1):
        ws.cell(row=2, column=i, value=g).font = Font(bold=True)
        ws.cell(row=3, column=i, value=d).font = Font(bold=True)
    ws.merge_cells("C2:F2")  # Adres
    ws.merge_cells("G2:H2")  # Położenie
    for kol in "ABIJKLMN":  # jednopoziomowe nagłówki scalone w pionie
        ws.merge_cells(f"{kol}2:{kol}3")
    dane = [
        ("SP/AED/01", "Starostwo Powiatowe", "ul. Kościuszki", "3", "34-100", "Przykładowo",
         49.8851234, 19.4967812, "TAK", "czynny", datetime(2026, 3, 15), datetime(2028, 5, 31), "B21K-00412", "Philips"),
        ("SP/AED/02", "Powiatowy Urząd Pracy", "Mickiewicza", "10a", "34-100", "Przykładowo",
         49.8822001, 19.4901120, "TAK", "sprawny", datetime(2026, 1, 9), datetime(2027, 11, 30), "B21K-00977", "Philips"),
        ("SP/AED/03", "Liceum Ogólnokształcące im. M. Kopernika", "al. Wolności", "22", "34-100", "Przykładowo",
         49.8790456, 19.4889903, "NIE", "w serwisie", datetime(2025, 12, 1), datetime(2026, 12, 31), "ZOLL-AP-55120", "ZOLL"),
        ("SP/AED/04", "Dom Pomocy Społecznej", "Leśna", "1", "34-120", "Brzezinka Przykładowa",
         49.9012, 19.4588, "TAK", "czynny", datetime(2026, 6, 20), datetime(2029, 1, 31), "HS-360P-0081", "HeartSine"),
    ]
    for r, wiersz in enumerate(dane, start=4):
        for c, v in enumerate(wiersz, 1):
            cell = ws.cell(row=r, column=c, value=v)
            if isinstance(v, datetime):
                cell.number_format = "DD.MM.YYYY"
            elif isinstance(v, float):
                cell.number_format = "0.0000000"
    legenda = wb.create_sheet("Legenda")
    legenda["A1"] = "Stan: czynny / w serwisie / wycofany"
    _zapisz(wb, "syntetyczny_powiat.xlsx")

    _oczekiwane("syntetyczny_powiat.json", {
        "plik": "syntetyczny_powiat.xlsx",
        "arkusz": "Defibrylatory",
        "wymaga_100": False,
        "syntetyczny": True,
        "dostawca": {"nazwa": "Starostwo Powiatowe w Przykładowie", "typ": "jst", "slug": "powiat-przykladowo"},
        "wartosci_stale": {"dostepnosc": "publiczny", "dostepny_24_7": "nie"},
        "liczba_wierszy": 4,
        "arkusze": ["Informacje", "Defibrylatory", "Legenda"],
        "mapowanie": {
            "Nr ewid.": ["id_zrodlowe", "id_aed"],
            "Jednostka": "nazwa_obiektu",
            "Ulica": "nazwa_ulicy",
            "Nr": "nr_budynku",
            "Kod": "kod_pocztowy",
            "Miejscowość": "miejscowosc",
            "Szerokość": "szerokosc_geograficzna",
            "Długość": "dlugosc_geograficzna",
            "Wewnątrz budynku": "wewnatrz_budynku",
            "Stan": "status",
            "Data przeglądu": "data_przegladu",
            "Ważność elektrod": "data_waznosci_elektrod_doroslych",
            "Nr seryjny": "numer_seryjny",
            "Producent": "producent",
        },
        "rekordy": [
            {"wiersz": 4, "pola": {
                "nazwa_obiektu": "Starostwo Powiatowe", "cecha_ulicy": "ulica", "nazwa_ulicy": "Kościuszki",
                "nr_budynku": "3", "kod_pocztowy": "34-100", "miejscowosc": "Przykładowo",
                "szerokosc_geograficzna": "49.8851234", "dlugosc_geograficzna": "19.4967812",
                "wewnatrz_budynku": "true", "status": "sprawny",
                "data_przegladu": "2026-03-15", "data_waznosci_elektrod_doroslych": "2028-05-31",
                "numer_seryjny": "B21K-00412", "producent": "Philips"}},
            {"wiersz": 5, "pola": {"nazwa_ulicy": "Mickiewicza", "nr_budynku": ["10a", "10A"], "status": "sprawny"}},
            {"wiersz": 6, "pola": {"cecha_ulicy": "aleja", "nazwa_ulicy": "Wolności", "wewnatrz_budynku": "false",
                                   "status": "tymczasowo_niedostepny", "data_waznosci_elektrod_doroslych": "2026-12-31"}},
            {"wiersz": 7, "pola": {"szerokosc_geograficzna": "49.9012", "dlugosc_geograficzna": "19.4588"}},
        ],
        "komunikaty": {
            "musza_byc": ["NISKA_PRECYZJA"],
            "nie_moze_byc": ["POZA_POLSKA", "DUPLIKAT_NR_SERYJNEGO", "DOMYSLNY_STATUS"],
        },
        "uwagi": (
            "Dane w drugim arkuszu 'Defibrylatory' (pierwszy to opis). Nagłówek dwupoziomowy w wierszach 2–3: 'Adres' scalony "
            "nad Ulica/Nr/Kod/Miejscowość, 'Położenie' nad Szerokość/Długość, pozostałe scalone w pionie. Parser może nazwać kolumny "
            "'Ulica' albo 'Adres Ulica' (raport dopasowuje po końcówce nazwy). Dane od wiersza 4. Współrzędne to liczby XLSX: "
            "bez utraty cyfr (49.8851234, nie 49.885123400000001). Daty Excela → ISO. 'w serwisie' → tymczasowo_niedostepny, "
            "'czynny' → sprawny. Wiersz 7 ma 4 miejsca po przecinku → NISKA_PRECYZJA. Ulica bez cechy ('Mickiewicza') → cecha "
            "pusta albo 'ulica'."),
    })


# ---------------------------------------------------------------------------------------------
# 3. Ośrodek sportu: współrzędne w jednej kolumnie, godziny w wolnym tekście, daty jako tekst
#    „15.03.2026”, powtórzona nazwa kolumny „Uwagi”, puste wiersze w środku, kondygnacja słownie.
# ---------------------------------------------------------------------------------------------
def osir() -> None:
    wb = Workbook()
    ws = wb.active
    ws.title = "Arkusz1"
    naglowek = ["Obiekt", "Współrzędne GPS", "Uwagi", "Dostępny", "Godziny", "Piętro",
                "Kontakt", "Uwagi", "Data ostatniej kontroli", "Dla dzieci"]
    for i, h in enumerate(naglowek, 1):
        ws.cell(row=1, column=i, value=h).font = Font(bold=True)
    dane = [
        ("Hala sportowa OSiR, ul. Sportowa 1", "49.874120, 19.479233", "przy wejściu do szatni", "NIE",
         "pon.-pt. 8:00-22:00, sob.-niedz. 9:00-20:00", "parter", "33 000 11 22", "", "15.03.2026", "tak"),
        None,  # pusty wiersz w środku tabeli
        ("Basen miejski, ul. Sportowa 3", "49.873511, 19.481002", "kasa", "nie",
         "Pn-Nd 06:00-22:00", "0", "+48 33 000 11 23", "elektrody pediatryczne w szafce", "2026-02-01", "TAK"),
        ("Stadion miejski, ul. Kolejowa 8", "49.869004, 19.475518", "budynek klubowy, na zewnątrz", "całą dobę",
         "", "", "", "", "01.10.2025", "nie"),
    ]
    r = 2
    for wiersz in dane:
        if wiersz is not None:
            for c, v in enumerate(wiersz, 1):
                ws.cell(row=r, column=c, value=v)
        r += 1
    _zapisz(wb, "syntetyczny_osir.xlsx")

    _oczekiwane("syntetyczny_osir.json", {
        "plik": "syntetyczny_osir.xlsx",
        "arkusz": None,
        "wymaga_100": False,
        "syntetyczny": True,
        "dostawca": {"nazwa": "Ośrodek Sportu i Rekreacji w Przykładowie", "typ": "jst", "slug": "osir-przykladowo"},
        "wartosci_stale": {"wewnatrz_budynku": "true", "dostepnosc": "publiczny"},
        "liczba_wierszy": 3,
        "mapowanie": {
            "Obiekt": ["nazwa_obiektu", "_adres_pelny"],
            "Współrzędne GPS": "_geometria",
            "Uwagi": ["opis_lokalizacji", "uwagi"],
            "Dostępny": "dostepny_24_7",
            "Godziny": "_godziny",
            "Piętro": "kondygnacja",
            "Kontakt": "telefon_kontaktowy",
            "Uwagi (2)": ["uwagi", None],
            "Data ostatniej kontroli": "data_weryfikacji",
            "Dla dzieci": "tryb_pediatryczny",
        },
        "rekordy": [
            {"wiersz": 2, "pola": {
                "szerokosc_geograficzna": "49.874120", "dlugosc_geograficzna": "19.479233",
                "opis_lokalizacji": ["przy wejściu do szatni", ""], "kondygnacja": "0", "dostepny_24_7": "nie",
                "telefon_kontaktowy": ["330001122", "+48330001122"], "data_weryfikacji": "2026-03-15",
                "tryb_pediatryczny": "true",
                "godziny_pn": "08:00-22:00", "godziny_pt": "08:00-22:00", "godziny_so": "09:00-20:00",
                "godziny_nd": "09:00-20:00"}},
            {"wiersz": 4, "pola": {
                "telefon_kontaktowy": ["330001123", "+48330001123"], "data_weryfikacji": "2026-02-01",
                "godziny_pn": "06:00-22:00", "godziny_nd": "06:00-22:00",
                # dwie kolumny „Uwagi”: pierwsza → opis_lokalizacji, druga → uwagi, albo (heurystyka A3) pierwsza → uwagi,
                # druga pominięta. Bez reguły dopasowanej pod ten plik nie da się ich rozróżnić; poprawka w kreatorze.
                "uwagi": ["elektrody pediatryczne w szafce", "kasa"]}},
            {"wiersz": 5, "pola": {"dostepny_24_7": "tak", "godziny_pn": "X", "data_weryfikacji": "2025-10-01",
                                   "tryb_pediatryczny": "false"}},
        ],
        "komunikaty": {
            "musza_byc": [],
            "nie_moze_byc": ["POZA_POLSKA", "DOMYSLNA_DATA_WERYFIKACJI", "ZAMIENIONE_WSPOLRZEDNE"],
        },
        "uwagi": (
            "Pusty wiersz 3 w środku (pomijany; numery wierszy zostają jak w arkuszu: 2, 4, 5). Dwie kolumny 'Uwagi' → druga "
            "'Uwagi (2)'. Współrzędne 'lat, lon' w jednej kolumnie → _geometria. 'Dostępny' NIE/nie/'całą dobę' → dostepny_24_7 nie/nie/tak. "
            "Godziny OSM-podobne po polsku. 'parter' → 0. Telefon ze spacjami → 9 cyfr. Daty tekstem DD.MM.RRRR i ISO. "
            "'Obiekt' łączy nazwę z adresem ('Hala sportowa OSiR, ul. Sportowa 1'): akceptujemy nazwa_obiektu."),
    })


if __name__ == "__main__":
    OCZEKIWANE.mkdir(exist_ok=True)
    gmina()
    powiat()
    osir()
    print("OK: syntetyczny_gmina.xlsx, syntetyczny_powiat.xlsx, syntetyczny_osir.xlsx + oczekiwane/*.json")
