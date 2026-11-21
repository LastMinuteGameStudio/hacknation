"""Konfiguracja ze zmiennych środowiskowych (patrz app/.env.example)."""

from __future__ import annotations

import os
from pathlib import Path

# Katalog główny repo: w dockerze /srv/repo, lokalnie 3 poziomy wyżej (app/backend/app -> repo).
REPO_DIR = Path(os.environ.get("REPO_DIR", Path(__file__).resolve().parents[3]))
ZAKRES_DIR = REPO_DIR / "zakres-danych"
DANE_WYNIK_DIR = REPO_DIR / "dane" / "wynik"
STATIC_DIR = Path(os.environ.get("STATIC_DIR", REPO_DIR / "app" / "frontend" / "dist"))

BASE_URL = os.environ.get("BASE_URL", "http://localhost:8000").rstrip("/")
# W dockerze: Postgres (docker-compose.yml). Lokalnie bez dockera: plik SQLite obok backendu.
DATABASE_URL = os.environ.get("DATABASE_URL", f"sqlite:///{Path(__file__).resolve().parents[1] / 'aed-dev.db'}")

# Tryb atrap: gdy rdzeń (aed_core) jeszcze nie jest gotowy, endpointy zwracają przykładowe dane z kontraktu.
MOCK = os.environ.get("MOCK", "auto")  # "1" = zawsze atrapy, "0" = nigdy, "auto" = gdy NotImplementedError

MAX_BAJTOW = 10 * 1024 * 1024
MAX_WIERSZY = 20_000
LICENCJA = "CC0 1.0"
