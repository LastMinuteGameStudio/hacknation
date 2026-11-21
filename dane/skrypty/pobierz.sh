#!/usr/bin/env bash
# Pobiera surowe dane o AED ze źródeł maszynowych do dane/surowe/.
# Opis źródeł: zadania/06-mc-misja-aed/ZESTAWIENIE-ZRODEL.md
set -euo pipefail
cd "$(dirname "$0")/../surowe"
Q='query?where=1%3D1&outFields=*&outSR=4326&f=geojson'

curl -sfL -o osm_pl.geojson https://openaedmap.org/api/v1/countries/PL.geojson
curl -sf  -o warszawa_19115.geojson 'https://warszawa19115.pl/urzadzenia-aed?p_p_id=portalCKMaedportlet_WAR_portalCKMaedportlet&p_p_lifecycle=2&p_p_resource_id=get_bw_data&_portalCKMaedportlet_WAR_portalCKMaedportlet_type=published'
curl -sfL -o inpost.geojson https://inpost.pl/aed-points
curl -sf  -o krakow_wasniowskip.geojson "https://services6.arcgis.com/w8Sm3ehkmwzR6bQc/arcgis/rest/services/AED_zestawy/FeatureServer/0/$Q"
curl -sf  -o krakow_pica.geojson "https://services-eu1.arcgis.com/svTzSt3AvH7sK6q9/arcgis/rest/services/AED_zestawy_2022_sierpien/FeatureServer/0/$Q"
curl -sf  -o mikolow.geojson "https://services9.arcgis.com/E1ZsJFZqsk2tR9yK/arcgis/rest/services/Defibrylatory_AED/FeatureServer/0/$Q"
curl -sf  -o pwr_defibrylatory.geojson "https://services3.arcgis.com/rrLByHvJ7zuJQDVw/ArcGIS/rest/services/defibrylatory/FeatureServer/0/$Q"
curl -sf  -o pwr_Defibrylatory_2023.geojson "https://services3.arcgis.com/rrLByHvJ7zuJQDVw/ArcGIS/rest/services/Defibrylatory_2023/FeatureServer/0/$Q"
curl -sfL -o koszalin.kml 'https://www.google.com/maps/d/kml?forcekml=1&mid=1AQwJAfeZsGGB7fhz0-yBSxab83DwyIw'
curl -sfL -o gdansk_pojazdy.json 'https://files.cloudgdansk.pl/d/otwarte-dane/ztm/baza-pojazdow.json?v=2'
curl -sfL -o lodz_um.kml 'https://www.google.com/maps/d/kml?forcekml=1&mid=1FMKFbebKJPYqD4C87pXWPqNjEHuEswE'

# Wykazy bez współrzędnych (parsuje i geokoduje skrypty/wykazy.py)
mkdir -p wykazy
UA='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36'
curl -sfL -A "$UA" -o wykazy/gdansk.html https://www.gdansk.pl/wiadomosci/Defibrylatory,a,216952
curl -sfL -A "$UA" -o wykazy/gliwice.html https://gliwice.eu/aktualnosci/bezpieczne-gliwice/wykaz-defibrylatorow-aed-aktualizowany
curl -sfL -A "$UA" -o wykazy/wopr_zp.html https://woprwz.pl/zachodniopomorska-siec-defibrylatorow-aed/
curl -sfL -A "$UA" -o wykazy/chelm.html https://samorzad.gov.pl/web/miasto-chelm/defibrylatory-aed-w-miejskiej-przestrzeni-publicznej
curl -sfL -A "$UA" -o wykazy/lublin.pdf https://lublin.eu/download/gfx/lublin/userfiles/_public/mieszkancy/zdrowie/aktualnosci/2026/aed_lublin_stan_17.03.2026.pdf
# lublin.txt = tekst z lublin.pdf (pypdf: PdfReader(...).pages[i].extract_text())

date -u +%Y-%m-%dT%H:%M:%SZ > POBRANO.txt
ls -la
