# Fixtury: realne pliki AED (pobrane 21.11.2026)

| Plik | Źródło | Uwagi |
|---|---|---|
| krosno.csv | dane.gov.pl ds 3624 (UM Krosna) | `,`, nagłówki ze spacją na początku, adres w jednym polu |
| marki.csv | dane.gov.pl ds 4955 (UM Marki) | **uszkodzony**: cały wiersz w jednym polu w cudzysłowie, lat/lon zamienione względem nagłówka |
| marki.xlsx | dane.gov.pl ds 4955 | ten sam zbiór w XLSX |
| legionowo.csv | dane.gov.pl ds 40593, zasób 2625221 | wzorcowy: BOM, adres w polach, TERC/SIMC |
| przemysl.csv | przemysl.skycms.com.pl (źródło na żywo) | `;`, BOM, geometria `[lon,lat]` w komórce, opis marketingowy |
| przemysl_2024.csv | kopia na dane.gov.pl ds 4581 | geometria `{"lat","long"}` (inny format niż na żywo) |
| warszawa_19115.geojson | dane/surowe (mapa 19115) | GeoJSON, wejście GeoJSON jest w zakresie dodatkowym |
