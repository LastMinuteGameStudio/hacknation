# Pliki pominięte w pierwszym commicie portal/

Kod pochodzi z nieoficjalnego mirrora backendu dane.gov.pl: https://github.com/olekstomek/mcod-backend-dane.gov.pl, commit `00a0813` („backend 2.62.3 from shared zip file”), pobrany 22.11.2026 (`git clone --depth 1`). Skopiowano go bez `.git` i bez zmian, z wyjątkiem dwóch plików poniżej. Pominięto je, bo przekraczają 20 MB i nie są potrzebne do uruchomienia backendu, panelu admina, API ani Celery (decyzja hacknacja-3f, 22.11).

| Plik | Rozmiar | Do czego służy | Skąd pobrać |
|---|---|---|---|
| `docker/rdfdb/fuseki/dist/apache-jena-fuseki-6.2.0.tar.gz` | 51,4 MB | triplestore Apache Jena Fuseki dla RDF/SPARQL (`docker-compose.addons.yml`, serwis rdfdb) | mirror (ścieżka jak obok) albo https://archive.apache.org/dist/jena/binaries/apache-jena-fuseki-6.2.0.tar.gz |
| `mcod/resources/tests/media/test_geo/iglaste.dbf` | 30,3 MB | dane testowe do testów plików geo (shapefile) w `mcod/resources/tests` | mirror (ścieżka jak obok) |

Przywrócenie: skopiuj plik z mirrora pod tę samą ścieżkę. Testy jednostkowe, które używają `iglaste.dbf`, bez niego nie przejdą.
