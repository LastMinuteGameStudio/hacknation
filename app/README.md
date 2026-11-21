# app/: konwerter danych AED dla dostawców

Co i dlaczego: [KONTEKST.md](KONTEKST.md). Plan i zadania: [PLAN.md](PLAN.md). **Kontrakt API i interfejs rdzenia: [KONTRAKT.md](KONTRAKT.md).**

## Uruchomienie

**Docker (całość):**
```bash
cd app && cp .env.example .env && docker compose up --build   # http://localhost:8000
```

**Backend lokalnie (bez dockera, bez bazy działają atrapy):**
```bash
cd app/backend && python3.12 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/uvicorn app.main:app --reload            # http://localhost:8000/docs
.venv/bin/python -m pytest -q
```

**Front lokalnie** (wymaga Node 20+, np. `brew install node`):
```bash
cd app/frontend && npm install && npm run dev      # http://localhost:5173, proxy /api → :8000
```

## Struktura i właściciele (ścieżki z PLAN.md)

| Ścieżka | Branch | Pliki (tylko te edytujesz) |
|---|---|---|
| A rdzeń | `app-a-rdzen` | `backend/aed_core/*.py` (poza `types.py`, `schema.py`), `backend/tests/test_core_*.py` |
| B API i baza | `app-b-api` | `backend/app/*` (poza `api_models.py`), `backend/tests/test_api_*.py`, `Dockerfile`, `docker-compose.yml` |
| C front | `app-c-front` | `frontend/**` (poza `src/api/types.ts`) |
| D testy | `app-d-testy` | `backend/tests/fixtury/**`, `backend/tests/test_realne_*.py`, `backend/tests/raport_mapowania.py` |

**Pliki wspólne (kontrakt):** `KONTRAKT.md`, `backend/aed_core/types.py`, `backend/app/api_models.py`, `frontend/src/api/types.ts`. Zmianę zgłoś najpierw na tablicy (`~/Desktop/hacknation-wspolne/TABLICA.md`) i SendMessage do zainteresowanych ścieżek, potem popraw wszystkie cztery naraz.

## Zasady pracy ścieżek
- Pracuj na swoim branchu. Merguj do `main` często i małymi porcjami: `git pull --rebase origin main`, testy zielone, potem merge lub PR.
- Atrapy (`backend/app/mock.py`) pozwalają frontowi działać bez rdzenia. Ścieżka B usuwa je, gdy prawdziwe endpointy działają.
- Nie zmieniaj `zakres-danych/`. To jedno źródło prawdy dla pól (v0.5). Uwagi do zakresu zgłaszaj na tablicy.
- Postęp i blokery zapisuj na tablicy (`ZAJMUJĘ` / `GOTOWE`). Pilne sprawy przez `SendMessage` (nazwy sesji: `ListAgents`).
