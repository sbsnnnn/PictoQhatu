"""Rutas de datos del backend. Se pueden cambiar con variables PICTOQHATU_DATOS / PICTOQHATU_TABLA_Q."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

RAIZ = Path(__file__).resolve().parents[4]      # raíz del repo (core/app/backend/codigo/<raíz>)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="PICTOQHATU_")

    datos: Path = RAIZ / "datos"
    tabla_q: Path = RAIZ / "datos" / "modelos" / "tabla_q.npy"
