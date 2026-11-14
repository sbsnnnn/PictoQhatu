"""El port reproduce exactamente al MVP del Hito 1 (misma semilla, mismos números).

La referencia la genera referencia/generar_referencia.py ejecutando el MVP original.
"""

import json
from pathlib import Path

import numpy as np
import pytest

from ia_models.agent.q_learning import AgenteQ, entrenar, jugar_partida
from ia_models.agent.regla_fija import AgenteReglaFija
from ia_models.env.entorno import EntornoPictoCocina
from ia_models.env.jugador_simulado import JugadorSimulado
from ia_models.experimentos.experimento_a import evaluar
from ia_models.tests.referencia.calculo import calcular

REF = Path(__file__).parent / "referencia"


@pytest.fixture(scope="module")
def port():
    return calcular(EntornoPictoCocina, JugadorSimulado, AgenteQ, AgenteReglaFija,
                    jugar_partida, entrenar, evaluar)


def _json(nombre):
    return json.loads((REF / nombre).read_text(encoding="utf-8"))


def test_traza_turno_a_turno_igual_al_mvp(port):
    trazas, _, _ = port
    esperado = _json("traza_demo.json")
    for agente in ("regla_fija", "q"):
        assert len(trazas[agente]["turnos"]) == len(esperado[agente]["turnos"])
        for i, (t, e) in enumerate(zip(trazas[agente]["turnos"], esperado[agente]["turnos"], strict=True)):
            assert t == e, f"{agente}: el turno {i + 1} difiere del MVP"
        assert trazas[agente]["resultado"] == esperado[agente]["resultado"]


def test_tabla_q_igual_al_mvp(port):
    _, q, _ = port
    assert np.array_equal(q, np.load(REF / "tabla_q_2000.npy"))


def test_metricas_iguales_al_mvp(port):
    _, _, metricas = port
    assert metricas == _json("evaluar_20.json")


def test_historial_no_cambia_el_entrenamiento():
    historial = []
    con = entrenar(AgenteQ(semilla=42), episodios=300, semilla=42, historial=historial)
    sin = entrenar(AgenteQ(semilla=42), episodios=300, semilla=42)
    assert len(historial) == 300
    assert np.array_equal(con.q, sin.q)
