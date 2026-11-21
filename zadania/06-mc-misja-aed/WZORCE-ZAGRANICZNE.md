# Zagraniczne rejestry AED jako wzorce

Stan na 21.11.2026, research subagenta. Plik zawiera tylko fakty, bez rozwiązań. ❔ oznacza informację niepotwierdzoną.

## Francja: Géo'DAE (najlepiej udokumentowany)

- **Podstawa prawna:** ustawa z 28.06.2018 o defibrylatorach (operatorzy AED mają obowiązek je zgłaszać) i arrêté z 29.10.2019 o działaniu bazy (JO 13.11.2019).
- **Operator:** Ministère de la Santé. Zgłoszenia przyjmuje geodae.atlasante.fr.
- **Otwarte dane:** data.gouv.fr, „Géo'DAE – Base nationale des défibrillateurs” (id 61556e1e9d6adb2df86eb0fc).
  - Licencja: **Licence Ouverte 2.0** (nie ODbL).
  - Formaty: CSV (ok. 77 MB) i JSON (ok. 210 MB).
  - Aktualizacja kilka razy dziennie.
  - Publikowane są tylko AED oznaczone jako dostępne publicznie.
- **Schemat:** schema.data.gouv.fr/schemas/atlasante/schema-dae (v1.0.8, Table Schema), repozytorium gitlab.com/arsante/atlasante/schema-dae. W CSV nazwy pól mają prefiks `c_`. Pola (* = wymagane):
  - **Identyfikacja i lokalizacja:** `nom`*, `lat_coor1`*, `long_coor1`*, `adr_num`, `adr_voie`, `com_cp`, `com_insee`, `com_nom`
  - **Dostęp:** `acc`* (wewnątrz/na zewnątrz), `acc_lib`* (dostęp wolny, bool), `acc_pcsec` (posterunek ochrony), `acc_acc` (recepcja), `acc_etg` (piętro), `acc_complt` (opis dojścia), `dae_mobile`, `dispo_horaires`* (godziny w składni OSM `opening_hours`), `disp_complt`
  - **Zdjęcia:** `photo1`, `photo2` (URL)
  - **Kontakt w miejscu:** `tel1`*, `tel2`, `site_email`
  - **Stan:** `date_instal`, `etat` (aktywny / do usunięcia / niezidentyfikowany), `etat_fonct`* (działa / nie działa / usunięty na stałe / chwilowo nieobecny / nieznany)
  - **Urządzenie:** `fab_siren`, `fab_rais`* (producent), `modele`*, `num_serie`*, `id_euro`, `lc_ped` (elektrody pediatryczne)
  - **Ważność i konserwacja:** `dtpr_lcped`, `dtpr_lcad`, `dtpr_bat` (ważność elektrod pediatrycznych, elektrod dla dorosłych i baterii), `freq_mnt`, `dispsurv`, `dermnt`* (data ostatniej konserwacji), `mnt_siren`, `mnt_rais` (serwisant)
  - **Eksploatujący (dysponent):** `expt_siren`*, `expt_siret`, `expt_rais`*, `expt_tel1`*, `expt_tel2`, `expt_email`*

## Wielka Brytania: The Circuit (British Heart Foundation)

- Operatorem jest BHF razem z Resus Council UK i St John Ambulance. Od 2022 jest podłączonych wszystkie 14 służb ambulansowych.
- Rejestracja jest dobrowolna. Rejestr ma ponad 100 tys. AED według BHF (inne źródło podaje 82 108).
- **Dane:** plik z lokalizacjami (tylko AED z wyznaczonym opiekunem, „Guardian”) można pobrać po wypełnieniu formularza na bhf.org.uk/defibdata. Aktualizacja następuje 1. dnia roboczego miesiąca.
  - **To nie jest otwarta licencja:** nie wolno używać danych komercyjnie ani budować aplikacji bez zgody BHF.
  - Zakres: lokalizacja, dostępność, typ dostępu.

## Dania: Hjertestarter.dk (TrygFonden)

- 26 393 AED (09.2025), z czego 72% jest dostępnych 24/7.
- Brak publicznego API i otwartych danych. Wewnętrzna usługa HJEDAWS udostępnia regionom adres, geolokalizację, godziny i status.

## Holandia: HartslagNu

- Rejestr fundacyjny (Hartstichting i inni). Obejmuje tylko AED z certyfikatem, każdy przypisany do opiekuna.
- Liczba: ok. 25 800 (2022). Otwartych danych nie znaleźliśmy.

## Szwajcaria: Defikarte.ch

- Prywatna inicjatywa oparta na OSM, bez obowiązku prawnego.
- 14 446 AED (12.2024), z czego 5 666 jest dostępnych publicznie.
- Na opendata.swiss jest tylko zbiór kantonu Schwyz (źródło OSM).

## Niemcy

- Brak krajowego rejestru i obowiązku zgłaszania. W OSM jest ok. 18 500 AED (06.2026).
- Istnieje prywatna baza Defikataster. Dyskutowany jest jednolity kataster połączony z dyspozytorniami ❔.

## Czechy

- Brak oficjalnego rejestru. W praktyce służy do tego aplikacja Záchranka, z ok. 4 500 AED. Wpis zatwierdza regionalna służba ratownicza. Eksportu brak.

## Irlandia, Belgia, Hiszpania, Włochy

- **Irlandia:** National AED Network (National Ambulance Service), formularz online, od 2025 połączony z dyspozytornią. Szacunkowo ok. 9 000 AED, z czego zarejestrowana jest mała część.
- **Belgia:** publiczne AED zgłasza się do FPS Health (KR z 21.04.2007 ❔).
- **Hiszpania:**
  - Katalonia: obowiązkowy rejestr (Decreto 151/2012), zbiór na datos.gob.es („Registro de desfibriladores instalados en Cataluña fuera del ámbito sanitario”).
  - Madryt: obowiązkowy rejestr (Decreto 78/2017), ok. 6 621 aktywnych AED.
  - Schematów pól nie pobraliśmy.
- **Włochy, Lombardia:** AREU, platforma „Paddles”, ok. 23 tys. AED. Ustawa 116/2021 i otwarte dane ❔.

## USA i Japonia

- **USA, PulsePoint AED Registry** (z ZOLL): pola to opis lokalizacji, godziny, ograniczenia dostępu, kod do szafki, kontakt do opiekuna, dane urządzenia i materiałów z przypomnieniami o ważności, GPS i zdjęcia. API jest dostępne tylko dla dyspozytorni i producentów, a otwartych danych nie ma.
- **Japonia:** Japan Foundation for Emergency Medicine prowadzi mapę qqzaidanmap.jp. Za zgodą właściciela dane trafiają do samorządów. Wiele prefektur publikuje CSV (np. Ishikawa: współrzędne, godziny, wyposażenie pediatryczne).

## Poziom UE

- **EENA** („AED mapping emergency response”, aktualizacja 2023): zaleca rejestr wszystkich publicznie dostępnych AED, udostępniany dyspozytorniom (PSAP). Dokument ma załącznik z formularzem rejestracji, którego nie przeczytaliśmy. EENA porównuje też przepisy o AED w 22 krajach („AED legislation document”).
- **ERC 2021** („Systems Saving Lives”): zaleca jednolite raportowanie sieci AED. Listy pól nie znaleźliśmy.
