"""Wykaz AED: czysta logika (bez Django i bazy), używana przez portal.

- schema.py: wzorcowy zakres danych o AED v0.5 (zakres/zakres-pol.csv, zakres/slowniki.csv),
- reader.py: odczyt CSV/XLSX wykazu dostawcy do listy wierszy (tekst),
- validation.py: walidacja wykazu wg zakresu v0.5 (nagłówki, pola obowiązkowe, formaty, słowniki),
- merge.py: scalanie wykazów od różnych dostawców w jeden wykaz zbiorczy z oznaczeniem duplikatów.

Integracja z portalem (model, zadanie Celery, formularz) jest w mcod/resources/aed_utils.py i tasks/aed.py.
Opis zmian: portal/WYKAZ-AED.md.
"""
