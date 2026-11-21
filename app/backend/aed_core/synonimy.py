"""A3: synonimy nazw kolumn per pole v0.5. Klucze znormalizowane (małe litery, bez polskich znaków i separatorów).

Źródła synonimów: Krosno/Marki, Legionowo, Przemyśl, Warszawa 19115, OSM, Géo'DAE (patrz zakres-pol.csv, kolumny osm, warszawa_19115, legionowo_krosno, geodae_fr).
"""

SYNONIMY: dict[str, list[str]] = {}
