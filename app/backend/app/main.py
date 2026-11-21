"""FastAPI: endpointy z app/KONTRAKT.md. T0 = szkielet z atrapami; ścieżka B podmienia atrapy na logikę + bazę."""

from __future__ import annotations

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles

from aed_core.schema import load_schema

from . import mock
from .api_models import (
    ImportOut,
    PoleSchematu,
    PozycjaSlownika,
    PublikacjaOut,
    SchematOut,
    WalidacjaIn,
    WalidacjaOut,
    ZdrowieOut,
)
from .config import STATIC_DIR, ZAKRES_DIR
from .db import db_ok, init_db

app = FastAPI(title="Misja AED: konwerter danych dostawców", version="0.1.0")
SCHEMA = load_schema(ZAKRES_DIR)


@app.on_event("startup")
def _startup() -> None:
    init_db()


def _blad(status: int, kod: str, komunikat: str) -> HTTPException:
    return HTTPException(status_code=status, detail={"kod": kod, "komunikat": komunikat})


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


# --- Import → walidacja → publikacja (B2: podmienić atrapy) ---------------------------------------


@app.post("/api/importy", response_model=ImportOut)
async def utworz_import(plik: UploadFile = File(...), arkusz: str | None = Form(None)) -> ImportOut:
    return mock.import_out(plik.filename or "plik")


@app.post("/api/importy/{import_id}/walidacja", response_model=WalidacjaOut)
def waliduj(import_id: str, body: WalidacjaIn) -> WalidacjaOut:
    return mock.walidacja_out()


@app.post("/api/importy/{import_id}/publikacja", response_model=PublikacjaOut)
def publikuj(import_id: str) -> PublikacjaOut:
    return mock.publikacja_out()


# --- Pliki publiczne (B3, B4) ---------------------------------------------------------------------


@app.get("/d/{nazwa}")
def plik_publiczny(nazwa: str):
    raise _blad(404, "NIE_ZNALEZIONO", "Zbiór jeszcze nie istnieje (T0: atrapa).")


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

if STATIC_DIR.exists():
    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="front")
else:

    @app.get("/", response_class=PlainTextResponse)
    def brak_frontu() -> str:
        return "Backend działa. Front nie jest zbudowany (app/frontend: npm run build) albo uruchom go przez `npm run dev`."
