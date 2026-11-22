"""FastAPI: endpointy z app/KONTRAKT.md. Logika importu w app/importy.py, baza w app/db.py."""

from __future__ import annotations

import os
from contextlib import asynccontextmanager
from typing import Iterator

from fastapi import Depends, FastAPI, File, Form, Query, Response, UploadFile
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import FileResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from starlette.exceptions import HTTPException as StarletteHTTPException

from . import importy, publiczne, synchronizacja
from .api_models import (
    ImportOut,
    PoleSchematu,
    PozycjaSlownika,
    PublikacjaOut,
    SchematOut,
    SynchronizacjaIn,
    SynchronizacjaOut,
    WalidacjaIn,
    WalidacjaOut,
    ZbiorOut,
    ZbiorPublicznyOut,
    ZdrowieOut,
)
from .config import STATIC_DIR, ZAKRES_DIR
from .db import SessionLocal, db_ok, init_db
from .importy import SCHEMA

_baza_gotowa = False


def _init() -> None:
    global _baza_gotowa
    if not _baza_gotowa:
        _baza_gotowa = init_db()


@asynccontextmanager
async def _lifespan(_app: FastAPI):
    _init()
    stop = synchronizacja.start_harmonogramu() if os.environ.get("SYNC", "1") == "1" else None
    yield
    if stop:
        stop.set()


app = FastAPI(title="Misja AED: konwerter danych dostawców", version="0.2.0", lifespan=_lifespan)
app.add_middleware(GZipMiddleware, minimum_size=1024)  # agregat GeoJSON: 11 MB → ok. 1 MB


def get_db() -> Iterator[Session]:
    _init()
    with SessionLocal() as s:
        yield s


@app.get("/api/zdrowie", response_model=ZdrowieOut)
def zdrowie() -> ZdrowieOut:
    return ZdrowieOut(status="ok", baza=db_ok(), wersja_zakresu=SCHEMA.wersja)


@app.get("/api/schemat", response_model=SchematOut)
def schemat() -> SchematOut:
    return SchematOut(
        wersja=SCHEMA.wersja,
        pola=[PoleSchematu(**{k: getattr(f, k) for k in PoleSchematu.model_fields}) for f in SCHEMA.pola],
        slowniki={n: [PozycjaSlownika(kod=k, znaczenie=z) for k, z in v] for n, v in SCHEMA.slowniki.items()},
    )


# --- Import → walidacja → publikacja (B2) ---------------------------------------------------------


@app.post("/api/importy", response_model=ImportOut)
async def utworz_import(
    plik: UploadFile = File(...), arkusz: str | None = Form(None), db: Session = Depends(get_db)
) -> ImportOut:
    tresc = await importy.wczytaj_upload(plik)
    return importy.nowy_import(db, plik.filename or "plik", tresc, arkusz)


@app.post("/api/importy/{import_id}/walidacja", response_model=WalidacjaOut)
def waliduj(import_id: str, body: WalidacjaIn, db: Session = Depends(get_db)) -> WalidacjaOut:
    return importy.waliduj(db, import_id, body)


@app.post("/api/importy/{import_id}/publikacja", response_model=PublikacjaOut)
def publikuj(import_id: str, db: Session = Depends(get_db)) -> PublikacjaOut:
    return importy.publikuj(db, import_id)


# --- Edycja przez prywatny link -------------------------------------------------------------------


@app.get("/api/zbiory", response_model=list[ZbiorPublicznyOut])
def lista_zbiorow(response: Response, db: Session = Depends(get_db)) -> list[ZbiorPublicznyOut]:
    response.headers.update(publiczne.NAGLOWKI)  # jak /d/*: CORS *, bez cache
    return publiczne.lista_zbiorow(db)


@app.get("/api/zbiory/{slug}", response_model=ZbiorOut)
def zbior(slug: str, token: str = Query(""), db: Session = Depends(get_db)) -> ZbiorOut:
    return importy.zbior_out(db, importy.zbior_z_tokenem(db, slug, token))


@app.post("/api/zbiory/{slug}/importy", response_model=ImportOut)
async def import_do_zbioru(
    slug: str,
    token: str = Query(""),
    plik: UploadFile = File(...),
    arkusz: str | None = Form(None),
    db: Session = Depends(get_db),
) -> ImportOut:
    z = importy.zbior_z_tokenem(db, slug, token)
    tresc = await importy.wczytaj_upload(plik)
    return importy.nowy_import(db, plik.filename or "plik", tresc, arkusz, zbior=z)


# --- S1: synchronizacja z URL źródła -------------------------------------------------------------


@app.get("/api/zbiory/{slug}/zrodlo", response_model=SynchronizacjaOut)
def zrodlo(slug: str, token: str = Query(""), db: Session = Depends(get_db)) -> SynchronizacjaOut:
    return synchronizacja.out(db, importy.zbior_z_tokenem(db, slug, token))


@app.put("/api/zbiory/{slug}/zrodlo", response_model=SynchronizacjaOut)
def ustaw_zrodlo(slug: str, body: SynchronizacjaIn, token: str = Query(""), db: Session = Depends(get_db)) -> SynchronizacjaOut:
    return synchronizacja.ustaw(db, importy.zbior_z_tokenem(db, slug, token), body)


@app.post("/api/zbiory/{slug}/synchronizacja", response_model=SynchronizacjaOut)
def synchronizuj(slug: str, token: str = Query(""), wymus: bool = Query(False), db: Session = Depends(get_db)) -> SynchronizacjaOut:
    return synchronizacja.synchronizuj(db, importy.zbior_z_tokenem(db, slug, token), wymus=wymus)


# --- Pliki publiczne (B3, B4) ---------------------------------------------------------------------


@app.get("/d/{nazwa}")
def plik_publiczny(nazwa: str, db: Session = Depends(get_db)):
    return publiczne.plik(db, nazwa)


@app.get("/szablon.csv")
def szablon_csv() -> FileResponse:
    return FileResponse(ZAKRES_DIR / "szablon-aed-publiczny.csv", media_type="text/csv; charset=utf-8", filename="szablon-aed.csv")


@app.get("/szablon.xlsx")
def szablon_xlsx() -> FileResponse:
    return FileResponse(
        ZAKRES_DIR / "szablon-aed-publiczny.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename="szablon-aed.xlsx",
    )


# --- Front (zbudowany Vite) -----------------------------------------------------------------------

class _Spa(StaticFiles):
    """Trasy frontu (np. /edycja/{slug}) nie są plikami: zwracamy index.html, żeby router Reacta je obsłużył."""

    async def get_response(self, path, scope):
        try:
            return await super().get_response(path, scope)
        except StarletteHTTPException as e:
            if e.status_code != 404 or path.startswith(("api/", "d/")):
                raise
            return await super().get_response("index.html", scope)


if STATIC_DIR.exists():
    app.mount("/", _Spa(directory=STATIC_DIR, html=True), name="front")
else:

    @app.get("/", response_class=PlainTextResponse)
    def brak_frontu() -> str:
        return "Backend działa. Front nie jest zbudowany (app/frontend: npm run build) albo uruchom go przez `npm run dev`."
