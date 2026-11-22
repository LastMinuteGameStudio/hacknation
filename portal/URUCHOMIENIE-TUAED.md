# Lokalny portal dane.gov.pl (mcod-backend 2.62.3) dla TuAED

> **Stan (22.11, ok. 08:45): uruchomione na Macu (OrbStack, Apple Silicon) według kroków poniżej.** Admin, API, Celery
> z beat i pobieranie zasobów-linków działają. Wykaz AED (kod ścieżki A) ma jeszcze błędy do poprawki, patrz tablica.

Kod: `portal/` = mirror https://github.com/olekstomek/mcod-backend-dane.gov.pl (commit `00a0813`), bez zmian.
Pominięte pliki: [POMINIETE.md](POMINIETE.md). Nasze przyrosty do uruchomienia:

| Plik | Po co |
|---|---|
| `docker-compose.tuaed.yml` | nakładka na `docker-compose.local.yml`: porty tylko na 127.0.0.1, bez nginx, Discourse i CMS, Celery z beat |
| `env.tuaed` | `.env` dla nakładki: `COMPOSE_PROJECT_NAME=dgp`, adresy `localhost`, forum wyłączone, ustawienia `mcod.settings.tuaed` |
| `mcod/settings/tuaed.py` | jak `local.py.sample`, ale ciasteczka bez domeny `mcod.local` (logowanie przez `http://localhost:8101`) i bez `index.timeout` (ES 6.8 go odrzuca) |
| `logs/README.md` | katalog `logs/` (upstream ma go w `.gitignore`, a bez niego budowa obrazu pada na `kibana_statistics.log`) |

## Ograniczenia
- Kontenery mają stałe nazwy (`mcod-db`, `mcod-api`…) i stałą podsieć `172.18.18.0/24`. **Na jednym komputerze działa jeden taki stack.** Testy innych sesji idą na tym samym (projekt `dgp`).
- Obrazy aplikacji są `linux/amd64`: na Macu z Apple Silicon działają przez emulację (OrbStack/Rosetta), wolniej.
- Paczka Fuseki (RDF) nie jest w repo. Przed budową skopiuj ją z mirrora do `docker/rdfdb/fuseki/dist/` (ten katalog jest ignorowany przez git).
- **Kod jest w obrazie, nie montowany z hosta.** Na macOS docker nie może czytać `~/Desktop` (ochrona prywatności: „Operation not permitted”), więc nakładka wyłącza bind mounty. Po każdej zmianie kodu: `dc build mcod-local-admin && dc up -d --no-build mcod-local-admin mcod-local-api mcod-local-celery` (ok. 1 min). Media są w wolumenie `dgp_tuaed_media`.
- **Miejsce na dysku:** obraz aplikacji ma ok. 1,4 GB (Python 3.8, Firefox, ffmpeg, Node), Elasticsearch 1,6 GB. Każda przebudowa zostawia cache, więc przy małej ilości miejsca po budowie zrób `docker builder prune -af`.
- Obrazu testów (`docker/tests`) nie budujemy: `mcod-local-run` używa obrazu aplikacji, a pytest doinstalowujemy w kontenerze.
- W logach są komunikaty `--- Logging error --- socket.gaierror`: jeden z handlerów logów łączy się z hostem, którego lokalnie nie ma. Nie przeszkadzają.

## Adresy (tylko 127.0.0.1)
| Usługa | Adres |
|---|---|
| Panel admina | http://localhost:8101 |
| API | http://localhost:8100 (np. `/1.4/datasets`) |
| MailHog (maile) | http://localhost:8025 |
| Flower (zadania Celery) | http://localhost:5555 |

## Uruchomienie
```bash
cd portal
cp env.tuaed .env
# paczka Fuseki z mirrora (nie ma jej w repo):
curl -L -o docker/rdfdb/fuseki/dist/apache-jena-fuseki-6.2.0.tar.gz \
  https://github.com/olekstomek/mcod-backend-dane.gov.pl/raw/main/docker/rdfdb/fuseki/dist/apache-jena-fuseki-6.2.0.tar.gz
dc() { docker compose -f docker-compose.local.yml -f docker-compose.tuaed.yml "$@"; }   # bash i zsh
dc build mcod-db mcod-rabbitmq mcod-redis mcod-elasticsearch mcod-rdfdb mcod-local-admin   # pierwsza budowa: kilkanaście minut
dc up -d mcod-db mcod-rabbitmq mcod-redis mcod-elasticsearch mcod-rdfdb mcod-smtp
dc run --rm --no-deps mcod-local-run python manage.py init_mcod_db              # jednorazowo: migracje (w tym 0075 wykaz AED) i dane startowe
dc run --rm --no-deps mcod-local-run python manage.py search_index --rebuild -f # jednorazowo: indeksy ES
dc up -d --no-build mcod-local-admin mcod-local-api mcod-local-celery mcod-flower
curl -I http://localhost:8101/            # 302 → logowanie
curl -s http://localhost:8100/1.4/datasets | head -c 200
```

## Dane testowe (konta, instytucje, zbiory)
Skrypt [`mcod/tuaed_dane_testowe.py`](mcod/tuaed_dane_testowe.py) (idempotentny, można uruchamiać wielokrotnie):
```bash
docker exec mcod-admin python manage.py shell -c "from mcod.tuaed_dane_testowe import main; main()"
```
| Konto | Rola | Hasło |
|---|---|---|
| `admin@tuaed.local` | superuser | `TuAED-test-2026!` |
| `redaktor.przemysl@tuaed.local` | redaktor instytucji „Urząd Miejski w Przemyślu (test TuAED)” | jw. |
| `redaktor.krosno@tuaed.local` | redaktor instytucji „Urząd Miasta Krosna (test TuAED)” | jw. |
| `redaktor.szpital@tuaed.local` | redaktor instytucji „Szpital Wojewódzki w Przemyślu (test TuAED)” | jw. |

Skrypt zakłada też instytucję-właściciela zbiorczego wykazu „Ministerstwo Cyfryzacji (test TuAED)” o pk 9001 (`MAIN_AED_DATASET_OWNER_ORGANIZATION_PK` w `env.tuaed`). Każda instytucja dostawcy dostaje zbiór „Defibrylatory AED w …” (CC0 1.0) z zasobem „Wykaz AED” (`is_aed_list`) jako linkiem do CSV z TuAED (domyślnie demo: `/d/kznsks42.csv` i `/d/qy7g6px5.csv`, szpital: fixtura sesji D `app/backend/tests/fixtury/wykaz/szpital_przemysl_v05.csv` z GitHuba, licencja CC BY 4.0; inne adresy: zmienne `TUAED_URL_1`–`TUAED_URL_3`). Szpital ma AED 15 m od „ADM Centrum” z wykazu Przemyśla, więc scalenie pokazuje duplikat (oczekiwane wg sesji D: 45 rekordów, 1 duplikat) i włączoną „Aktualizacją automatyczną” (codziennie, bez końca). Fixture `init_mcod_db` dodaje też konta `admin@mcod.local` i `pelnomocnik@mcod.local` z nieznanym hasłem (nie używamy ich).

## Wykaz AED: scalenie i testy (ścieżka A)
```bash
# scalenie wykazów dostawców w zbiór zbiorczy (normalnie robi to Celery beat):
docker exec mcod-admin python manage.py shell -c "from mcod.resources.tasks import create_main_aed_resource_task as t; print(t.apply().result)"
# testy wykazu AED:
docker exec mcod-admin pip install -q pytest pytest-django   # raz na kontener
docker exec mcod-admin python -m pytest mcod/resources/tests/test_aed_merge.py mcod/resources/tests/test_aed_list.py -x -q
```

## Zasób-link i „Aktualizacja automatyczna”: jak to działa w kodzie
- W panelu: Zbiory danych → zbiór → Zasoby → Dodaj → link do pliku. Pole „Aktualizacja automatyczna” (`Resource.is_auto_data_date`) z okresem (codziennie / co tydzień / co miesiąc), datą startu i opcją „bez końca”.
- Zapis opublikowanego zasobu wysyła sygnał `revalidate_resource`. Wtedy `process_resource` planuje zadanie okresowe w Celery beat (`Resource.schedule_data_date_update`, tabele `django_celery_beat`), a dla nowego linku uruchamia pobranie i walidację (`entrypoint_process_resource_validation_task`).
- Zadanie okresowe `mcod.resources.tasks.update_data_date` ustawia datę danych i dla zasobu-linku ponownie pobiera plik.
- Podgląd: Flower (http://localhost:5555), w panelu zasób → „Zadania pobierania”.
- Wzór scalania wykazów (dla „wykazu AED”, ścieżka A): `resources/tasks/dga.py` (`create_main_dga_resource_task`), `resources/dga_utils.py`, harmonogram `celeryapp.py` („dga_main_resource_creation”).
