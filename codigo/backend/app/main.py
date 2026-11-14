"""Aplicación FastAPI: WebSocket del juego, pictogramas y build del frontend (una sola unidad)."""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from backend.app.api.ws import router as ws_router
from backend.app.core.config import RAIZ, Settings
from backend.app.game.rooms import RoomManager
from backend.app.game.session import cargar_agente

DIST = RAIZ / "codigo" / "frontend" / "dist"


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings()
    app = FastAPI(title="PictoQhatu")
    app.state.rooms = RoomManager(cargar_agente(settings.tabla_q))   # agente cargado una vez
    app.include_router(ws_router)
    pictos = settings.datos / "catalogo"
    if pictos.is_dir():
        app.mount("/pictos", StaticFiles(directory=pictos), name="pictos")
    if DIST.is_dir():                                # al final: "/" captura todo lo demás
        app.mount("/", StaticFiles(directory=DIST, html=True), name="frontend")
    return app


app = create_app()
