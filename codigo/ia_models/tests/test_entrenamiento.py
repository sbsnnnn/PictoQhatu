"""Prueba rápida de entrenamiento.py (pocos episodios, salida en carpeta temporal)."""

import csv
import random
from types import SimpleNamespace

import numpy as np

from ia_models.agent.q_learning import AgenteQ, entrenar, jugar_partida
from ia_models.agent.regla_fija import AgenteReglaFija
from ia_models.env.entorno import MAX_TURNOS, EntornoPictoCocina
from ia_models.experimentos import entrenamiento as ent
from ia_models.experimentos.experimento_a import evaluar


def _columnas(ruta):
    with open(ruta, encoding="utf-8") as archivo:
        return next(csv.reader(archivo))


def test_snapshots_no_cambian_la_tabla_q():
    """Entrenar con snapshots da la misma tabla Q que entrenar() a secas."""
    normal = entrenar(AgenteQ(semilla=42), episodios=200, semilla=42)
    agente, historial, snapshots = ent.entrenar_con_snapshots(200, 42, cada=50)
    assert np.array_equal(agente.q, normal.q)
    assert len(historial) == 200
    assert len(snapshots) == 5           # tabla inicial + 4 bloques
    assert np.array_equal(snapshots[-1], normal.q)


def test_es_frustracion():
    assert ent.es_frustracion(SimpleNamespace(e=2, h=2), {"acierto": False})
    assert not ent.es_frustracion(SimpleNamespace(e=2, h=1), {"acierto": False})
    assert not ent.es_frustracion(SimpleNamespace(e=1, h=2), {"acierto": False})
    assert not ent.es_frustracion(SimpleNamespace(e=2, h=2), {"acierto": True})


class _AgenteAlterna:
    """Da a1 y a2 alternados: desde el turno 2 hay e>=2 y h>=2."""
    def __init__(self):
        self.n = 0

    def elegir(self, s, explorar=False):
        self.n += 1
        return 1 if self.n % 2 else 2


class _JugadorFallaSiPuede:
    """Toca una opción incorrecta siempre que haya una en pantalla."""
    def nueva_partida(self):
        pass

    def responder(self, ronda, accion):
        malos = [i for i in range(len(ronda["opciones"])) if i not in ronda["correctas"]]
        return (malos or [0])[0], 1.0


def test_cuenta_de_frustracion_controlada():
    """El contador coincide con los turnos que reciben R_FRUSTRACION (recompensa < -3:
    sin frustración un turno nunca baja de -1.6)."""
    cuenta = ent.ContadorFrustracion()
    recompensas = []

    def mostrar(entorno, s, a, ronda, indice, tiempo, r, info):
        cuenta(entorno, s, a, ronda, indice, tiempo, r, info)
        recompensas.append(r)

    res = jugar_partida(EntornoPictoCocina(random.Random(0)), _JugadorFallaSiPuede(), _AgenteAlterna(),
                        mostrar=mostrar)
    assert res["turnos"] == MAX_TURNOS
    assert cuenta.eventos == sum(r < -3 for r in recompensas) > 10


def test_evaluar_con_frustracion_coincide_con_evaluar():
    m = ent.evaluar_con_frustracion(AgenteReglaFija(), "distraido", 5, semilla=2026)
    base = evaluar(AgenteReglaFija(), "distraido", 5, semilla=2026)
    for clave in base:
        assert m[clave] == base[clave]
    assert m["frustracion"] >= 0


def test_filas_de_factor_no_mezcla_factores():
    filas = [{"factor": f, "alfa": a, "gamma": g} for f, a, g in ent.configuraciones()]
    assert [f["gamma"] for f in ent.filas_de_factor(filas, "gamma")] == list(ent.GAMMAS)
    assert [f["alfa"] for f in ent.filas_de_factor(filas, "alfa")] == list(ent.ALFAS)


def test_ejecutar_rapido_escribe_csv_y_png(tmp_path):
    ent.ejecutar(episodios=60, partidas=2, semillas=(42,), salida=tmp_path)
    metricas, curvas = tmp_path / "metricas", tmp_path / "curvas"
    assert _columnas(metricas / "curva_entrenamiento.csv") == [
        "episodio", "recompensa_media", "tasa_exito", "max_delta_q"]
    assert _columnas(metricas / "baseline_vs_q.csv") == [
        "perfil", "agente", "tasa_exito", "turnos_prom", "ayudas_prom", "errores_prom",
        "recompensa_prom", "frustracion_prom", "frustracion_total"]
    assert _columnas(metricas / "sensibilidad.csv") == [
        "factor", "alfa", "gamma", "semillas", "exito_media", "exito_desv",
        "recompensa_media", "recompensa_desv"]
    for nombre in ("recompensa", "exito", "convergencia_q", "sensibilidad_alfa", "sensibilidad_gamma"):
        assert (curvas / f"{nombre}.png").stat().st_size > 0
    assert not (tmp_path / "tabla_q.npy").exists()


def test_rapido_no_escribe_en_la_carpeta_de_la_corrida_completa(monkeypatch):
    llamadas = []
    monkeypatch.setattr(ent, "ejecutar", lambda **kw: llamadas.append(kw))
    monkeypatch.setattr("sys.argv", ["entrenamiento", "--rapido"])
    ent.main()
    assert llamadas[0]["salida"] == ent.SALIDA_RAPIDA
    assert ent.SALIDA_RAPIDA != ent.Path(ent.CARPETA_DATOS)
