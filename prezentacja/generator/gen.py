import json, sys
RAW="https://raw.githubusercontent.com/LastMinuteGameStudio/hacknation/main/prezentacja/"
KV="https://raw.githubusercontent.com/LastMinuteGameStudio/hacknation/kvba/visual/"
F="Noto Sans"; TX="#101820"; GR="#006B10"; G="#008C15"; BL="#1A4E8A"; MU="#5F6B66"; TINT="#E6F4E8"; LG="#F3F7F4"
EMU=914400
def T(id,x,y,w,h,text,size=16,bold=False,color=TX,align="START",**k):
    d=dict(id=id,type="text",x=x,y=y,w=w,h=h,text=text,size=size,bold=bold,color=color,font=F,align=align); d.update(k); return d
def title(s,text): return T(s+"_t",0.5,0.28,9.0,1.08,text,size=26,bold=True)
def card(id,x,y,w,h,fill=TINT): return dict(id=id,type="round_rect",x=x,y=y,w=w,h=h,fill=fill)
def num(s,i,x,y,w,big,label,h=1.15):
    return [card(f"{s}_c{i}",x,y,w,h), T(f"{s}_n{i}",x+0.12,y+0.06,w-0.24,0.68,big,size=28,bold=True,color=GR),
            T(f"{s}_l{i}",x+0.12,y+0.7,w-0.24,h-0.72,label,size=14,color=TX)]
images={}  # slide -> list of (id,url,x,y,w,h,iw,ih)
def img(s,id,url,bx,by,bw,bh,iw,ih,align="center"):
    sc=min(bw/iw,bh/ih); w,h=iw*sc,ih*sc
    x=bx+(bw-w)/2 if align=="center" else bx; y=by+(bh-h)/2 if align!="top" else by
    images.setdefault(s,[]).append((id,url,x,y,w,h))
slides=[]
def S(id,els): slides.append(dict(id="sld"+id[1:],layout="BLANK",elements=els))

# 1 tytul
img("s01","s01_logo",KV+"logo_text_no_bg.png",0.75,0.7,4.2,1.25,4803,1361,align="left")
S("s01",[T("s01_t",0.75,2.1,8.5,1.45,"Opublikuj dane o defibrylatorach na dane.gov.pl",size=36,bold=True),
         T("s01_s",0.75,3.65,8.5,0.55,"W 3 PROSTYCH KROKACH",size=20,bold=True,color=GR),
         T("s01_f",0.75,4.75,8.5,0.4,"HackNation 2026 · Wyzwanie 06: Misja AED · demo: tuaed.wkrynski.dev",size=12,color=MU)])
# 2 problem
S("s02",[title("s02","Dane o AED leżą w kilkunastu źródłach i każde ma inny format"),
  dict(id="s02_tab",type="table",x=0.5,y=1.45,w=5.6,size=14,header=True,col_widths=[2.0,3.6],
       rows=[["Źródło","Jak publikuje dane o AED"],["Warszawa 19115","API z tokenem"],["Kraków","prywatne konto ArcGIS Online"],
             ["Łódź","Google My Maps na stronie urzędu"],["Gliwice, Gdańsk, WOPR","tabela HTML"],["Lublin","PDF"],
             ["Przemyśl","CSV z „;” i współrzędnymi jako JSON w komórce"]]),
  card("s02_box",6.45,1.45,3.05,3.6,LG),
  T("s02_b",6.6,1.6,2.75,3.3,"Nie ma krajowego rejestru AED.\n5 zbiorów AED na dane.gov.pl ma 5 różnych schematów.\nPrzemyśl deklaruje aktualizację codziennie, a portal pokazuje kopię z 2024 r.",size=15,space_below=10)])
# 3 rozwiazanie
img("s03","s03_img",RAW+"slajdy/schemat-przeplywu.png",0.5,1.3,9.0,4.0,2880,1620)
S("s03",[title("s03","TuAED zamienia plik dysponenta w stały, otwarty zbiór na dane.gov.pl")])
# 4 kreator
shots=[("09-krok1-dysponent",2880,1860,"1. Dysponent: nazwa i typ instytucji, kontakt niepubliczny"),
       ("09-krok2-mapowanie",2880,1512,"2. Dane: plik w dowolnym układzie, podpowiedź pól, sprawdzenie"),
       ("09-krok3-publikacja",2880,2408,"3. Publikacja: stały URL i instrukcja dla dane.gov.pl")]
els=[title("s04","Urzędnik publikuje swój arkusz w 3 krokach, bez znajomości CSV")]
for i,(f,iw,ih,cap) in enumerate(shots):
    x=0.5+i*3.07
    img("s04",f"s04_i{i}",RAW+f"zrzuty/{f}-1440.png",x,1.45,2.86,2.45,iw,ih,align="top")
    els.append(T(f"s04_c{i}",x,4.05,2.86,0.95,cap,size=14))
S("s04",els)
# 5 jak dziala
cards=[("Wczytuje","CSV, XLSX i GeoJSON, także z tytułem nad tabelą, scalonymi komórkami i stopką"),
       ("Mapuje","synonimy z realnych plików i analiza zawartości kolumn"),
       ("Normalizuje","daty ISO 8601, godziny pn–nd, adres rozbity na pola"),
       ("Geokoduje","brakujące współrzędne z geokodera GUGiK, do 200 adresów na plik"),
       ("Waliduje","brak pola obowiązkowego blokuje, brak zalecanego ostrzega"),
       ("Publikuje","CSV RFC 4180, JSON, GeoJSON i CSVW, licencja CC0 1.0")]
els=[title("s05","Mapowanie kolumn bez AI trafia w 100% na 10 plikach testowych")]
for i,(h,b) in enumerate(cards):
    x=0.5+(i%3)*3.05; y=1.45+(i//3)*1.85
    els+= [card(f"s05_k{i}",x,y,2.85,1.7), T(f"s05_h{i}",x+0.12,y+0.1,2.6,0.45,h,size=18,bold=True,color=GR),
           T(f"s05_b{i}",x+0.12,y+0.55,2.6,1.1,b,size=14)]
els.append(T("s05_f",0.5,5.12,9.0,0.4,"Pliki testowe: 7 realnych z 5 miast (Krosno, Marki, Legionowo, Przemyśl, Warszawa) i 3 syntetyczne arkusze „urzędowe”.",size=10,color=MU))
S("s05",els)
# 6 aktualizacja
els=[title("s06","Aktualizacja nie zmienia adresu, więc portal sam pobiera nowe dane")]
for i,(f,cap) in enumerate([("09-sync-3-zsynchronizowano","Miasto zmieniło format współrzędnych: synchronizacja przeszła sama, te same id_aed"),
                            ("09-sync-5-wstrzymana","Z pliku zniknęła kolumna: synchronizacja wstrzymana, opublikowane dane bez zmian")]):
    x=0.5+i*4.6
    img("s06",f"s06_i{i}",RAW+f"zrzuty/{f}-1440.png",x,1.4,4.4,2.95,1864,1332,align="top")
    els.append(T(f"s06_c{i}",x,4.4,4.4,0.75,cap,size=14))
S("s06",els)
# 7 zgodnosc
img("s07","s07_img",RAW+"zrzuty/08-csv-w-przegladarce-1440.png",5.6,1.45,3.9,3.6,2880,1800)
S("s07",[title("s07","Plik TuAED spełnia wymagania dane.gov.pl: 21 z 21 sprawdzeń"),
  dict(id="s07_tab",type="table",x=0.5,y=1.45,w=4.85,size=14,header=True,col_widths=[1.55,3.3],
       rows=[["Wymaganie","Jak spełniamy"],["Format","CSV RFC 4180, JSON, GeoJSON"],["Kodowanie","UTF-8 bez BOM, przecinek, CRLF"],
             ["Metadane","CSVW, czyli 4 gwiazdki otwartości"],["Daty","ISO 8601"],["Licencja","CC0 1.0"],
             ["Aktualność","stały URL z „Aktualizacją automatyczną”"]]),
  T("s07_f",0.5,5.12,9.0,0.4,"Sprawdzenie: pobranie pliku bez logowania, tak jak robi to portal (prezentacja/zrzuty/DOWOD-URL.md).",size=10,color=MU)])
# 8 zakres
els=[title("s08","Wzorcowy zakres danych v0.5 ma 58 pól, z czego 14 obowiązkowych")]
for i,(n,l) in enumerate([("14","pól obowiązkowych: brak blokuje publikację"),("18","pól zalecanych: brak daje ostrzeżenie"),("26","pól fakultatywnych")]):
    els+=num("s08",i,0.5+i*3.05,1.45,2.85,n,l,h=1.45)
els.append(T("s08_b",0.5,3.15,9.0,2.2,"52 pola są publiczne. Producent, model, numer seryjny, serwisant, telefon i e-mail zostają w ewidencji dysponenta.\nGodziny dostępności są w polach na każdy dzień i święta, nie w wolnym tekście.\nPrzy polach podajemy odpowiedniki z francuskiego rejestru Géo'DAE i tagów OpenStreetMap.",size=16,bullets=True,space_below=10))
S("s08",els)
# 9 agregacja
img("s09","s09_img",RAW+"slajdy/mapa.png",4.6,1.45,4.9,3.6,1864,1402)
els=[title("s09","Agregat łączy 18 858 unikalnych AED z 15 źródeł w jednym pliku")]
for i,(n,l) in enumerate([("19 834","rekordów zebranych z 15 źródeł"),("976","duplikatów połączonych w jeden rekord"),("559","AED spoza OpenStreetMap")]):
    els+=num("s09",i,0.5,1.45+i*1.25,3.85,n,l,h=1.15)
els.append(T("s09_f",0.5,5.12,9.0,0.4,"Duplikat: ten sam AED w promieniu 50 m (OSM) lub 30 m (inne źródła). Źródło: agregacja zespołu, 21.11.2026.",size=10,color=MU))
S("s09",els)
# 10 odbiorcy
img("s10","s10_img",RAW+"slajdy/dane-1440.png",0.5,1.4,5.0,3.8,2880,2000,align="top")
S("s10",[title("s10","Służby, mapy i aplikacje pobierają jeden plik dla całej Polski"),
  T("s10_b",5.8,1.4,3.7,3.8,"Plik zbiorczy CSV i GeoJSON, z OSM i bez OSM\nPrzy każdym AED źródło, licencja, data i status weryfikacji\nAPI z dokumentacją OpenAPI\nMapa i tabela z wyszukiwaniem na stronie TuAED",size=16,bullets=True,space_below=10)])
# 11 wcag
img("s11","s11_i0",RAW+"slajdy/start-1440.png",3.45,1.4,4.6,3.75,2880,1800)
img("s11","s11_i1",RAW+"slajdy/start-320.png",8.2,1.4,1.3,3.75,640,1280,align="top")
els=[title("s11","Strona spełnia WCAG 2.2 AA: 0 naruszeń na 33 ekranach")]
for i,(n,l) in enumerate([("0","naruszeń WCAG 2.2 AA"),("100","Lighthouse: dostępność"),("320 px","ekran bez przewijania")]):
    els+=num("s11",i,0.5,1.45+i*1.25,2.75,n,l,h=1.15)
S("s11",els)
# 12 akcja
img("s12","s12_logo",KV+"logo_vertical.png",0.6,1.45,3.6,3.5,2941,2370)
S("s12",[title("s12","Akcja TuAED zaprasza dysponentów AED do publikacji danych"),
  T("s12_h",4.6,1.5,4.9,1.3,"„Opublikuj dane o defibrylatorach na dane.gov.pl w 3 prostych krokach”",size=22,bold=True,color=GR),
  T("s12_b",4.6,2.95,4.9,2.1,"Do kogo: gminy, urzędy, OSP, szkoły, firmy, czyli dysponenci AED\nCo zyskują: ich AED trafiają do map, aplikacji i do dyspozytorów\nIle to kosztuje: jeden arkusz, który już mają",size=16,bullets=True,space_below=8)])
# 13 ksiega
els=[title("s13","Księga znaku TuAED w skrócie")]
for i,(hexc,name,txt) in enumerate([("#008C15","Główny","#008C15\nPantone 2426 C"),("#1A4E8A","Pomocniczy","#1A4E8A\nPantone 4153 C"),("#FFFFFF","Tło","#FFFFFF"),("#000000","Tekst","#000000")]):
    x=0.5+i*2.28
    els+=([dict(id=f"s13_bd{i}",type="rect",x=x-0.02,y=1.43,w=2.14,h=0.94,fill="#D1E0D7")] if hexc=="#FFFFFF" else [])+[dict(id=f"s13_sw{i}",type="rect",x=x,y=1.45,w=2.1,h=0.9,fill=hexc), T(f"s13_sn{i}",x,2.4,2.1,0.43,name,size=14,bold=True), T(f"s13_sv{i}",x,2.8,2.15,0.72,txt,size=14,color=MU)]
els.append(T("s13_b",0.5,3.6,5.0,1.75,"Czcionka: Noto Sans SemiBold\nPole ochronne: margines 1/6 wysokości sygnetu\nSygnet do logotypu 2:1, odstęp równy szerokości litery „u”",size=16,bullets=True,space_below=8))
img("s13","s13_logo",KV+"logo_text_no_bg.png",5.8,3.7,3.7,1.4,4803,1361)
S("s13",els)
# 14 ograniczenia
S("s14",[title("s14","Ograniczenia prototypu"),
  T("s14_b",0.5,1.4,9.0,3.9,"Bez konta dostawcy nie sprawdziliśmy publikacji na produkcyjnym dane.gov.pl; mechanizm znamy z kodu portalu\nGeokodujemy do 200 adresów na plik; w agregacie 63 AED nie ma współrzędnych\nDane z OpenStreetMap mają licencję ODbL, więc agregat ma też wersję bez OSM\nTen sam urząd może opublikować zbiór dwa razy; duplikatów między dostawcami jeszcze nie oznaczamy\nZgubionego linku edycji nie da się odzyskać, bo MVP nie ma logowania\nAED w pojazdach są poza zakresem",size=16,bullets=True,space_below=8)])
# 15 AI i dalsze kroki
S("s15",[title("s15","AI przyspieszyło budowę, decyzje podjął zespół"),
  T("s15_h1",0.5,1.45,4.3,0.55,"Jak używaliśmy AI",size=20,bold=True,color=GR),
  T("s15_b1",0.5,2.05,4.3,3.2,"Research źródeł danych i kodu portalu dane.gov.pl\nKod aplikacji i testy: Claude Code w 4 równoległych sesjach\nZespół: zakres danych, zasady walidacji, identyfikacja, przegląd wyników",size=16,bullets=True,space_below=8),
  T("s15_h2",5.2,1.45,4.3,0.55,"Dalsze kroki",size=20,bold=True,color=GR),
  T("s15_b2",5.2,2.05,4.3,3.2,"Zasób testowy na dane.gov.pl z Ministerstwem Cyfryzacji\nOznaczanie duplikatów między dostawcami\nOdzyskiwanie linku edycji przez e-mail\nPrzypomnienia o terminach przeglądów i elektrod",size=16,bullets=True,space_below=8)])
json.dump(dict(slides=slides),open("spec.json","w"),ensure_ascii=False,indent=1)
json.dump({k:v for k,v in images.items()},open("images.json","w"),ensure_ascii=False)
print(len(slides),"slajdów")
