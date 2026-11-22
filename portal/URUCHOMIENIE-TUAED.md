# Lokalny portal dane.gov.pl (mcod-backend 2.62.3) dla TuAED

> **Stan: szkic, jeszcze nieuruchomiony.** Pliki konfiguracyjne są gotowe. Budowa obrazów czeka na zgodę użytkownika
> sesji B (uruchamianie kodu z nieoficjalnego mirrora). Po pierwszym udanym uruchomieniu ta sekcja zniknie,
> a kroki zostaną poprawione według tego, co faktycznie zadziałało.

Kod: `portal/` = mirror https://github.com/olekstomek/mcod-backend-dane.gov.pl (commit `00a0813`), bez zmian.
Pominięte pliki: [POMINIETE.md](POMINIETE.md). Nasze przyrosty do uruchomienia:

| Plik | Po co |
|---|---|
| `docker-compose.tuaed.yml` | nakładka na `docker-compose.local.yml`: porty tylko na 127.0.0.1, bez nginx, Discourse i CMS, Celery z beat |
| `env.tuaed` | `.env` dla nakładki: `COMPOSE_PROJECT_NAME=dgp`, adresy `localhost`, forum wyłączone, ustawienia `mcod.settings.tuaed` |
| `mcod/settings/tuaed.py` | jak `local.py.sample`, ale ciasteczka bez domeny `mcod.local` (logowanie przez `http://localhost:8101`) |

## Ograniczenia
- Kontenery mają stałe nazwy (`mcod-db`, `mcod-api`…) i stałą podsieć `172.18.18.0/24`. **Na jednym komputerze działa jeden taki stack.** Testy innych sesji idą na tym samym (projekt `dgp`).
- Obrazy aplikacji są `linux/amd64`: na Macu z Apple Silicon działają przez emulację (OrbStack/Rosetta), wolniej.
- Paczka Fuseki (RDF) nie jest w repo. Przed budową skopiuj ją z mirrora do `docker/rdfdb/fuseki/dist/` (ten katalog jest ignorowany przez git).

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
DC="docker compose -f docker-compose.local.yml -f docker-compose.tuaed.yml"
$DC build mcod-db mcod-rabbitmq mcod-redis mcod-elasticsearch mcod-rdfdb mcod-local-admin
$DC up -d mcod-db mcod-rabbitmq mcod-redis mcod-elasticsearch mcod-rdfdb mcod-smtp
$DC run --rm mcod-local-run python manage.py init_mcod_db      # jednorazowo: migracje i dane startowe
$DC run --rm mcod-local-run python manage.py search_index --rebuild -f   # jednorazowo: indeksy ES
$DC up -d mcod-local-admin mcod-local-api mcod-local-celery mcod-flower
```

## Konta testowe
```bash
$DC run --rm mcod-local-run python manage.py createsuperuser
```
Instytucje dostawców i ich konta: w panelu admina (Instytucje → Dodaj, Użytkownicy → Dodaj z rolą redaktora instytucji). Loginy testowe zostaną dopisane po pierwszym uruchomieniu.

## Zasób-link z TuAED i „Aktualizacja automatyczna”
Panel admina → Zbiory danych → Dodaj (instytucja dostawcy) → Zasoby → Dodaj: link do pliku, np. `https://tuaed.wkrynski.dev/d/<slug>.csv`. W zasobie zaznacz „Aktualizacja automatyczna” (częstotliwość). Pobranie wykonuje zadanie Celery (podgląd: Flower).
