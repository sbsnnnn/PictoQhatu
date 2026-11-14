"""Rutas del backend. Se cambian con PICTOQHATU_DATOS, PICTOQHATU_TABLA_Q y PICTOQHATU_DIST."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

RAIZ = Path(__file__).resolve().parents[4]      # raíz del repo (core/app/backend/codigo/<raíz>)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="PICTOQHATU_")

    datos: Path = RAIZ / "datos"
    tabla_q: Path = RAIZ / "datos" / "modelos" / "tabla_q.npy"
    dist: Path = RAIZ / "codigo" / "frontend" / "dist"   # build de Vite (npm run build)
