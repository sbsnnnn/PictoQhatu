"""Cálculo común para comparar el MVP con el port.

No importa nada: recibe las clases y funciones como argumentos, así el mismo
código corre contra el MVP original (generar_referencia.py) y contra ia_models.
"""

import json
import random

PERFILES = ["rapido", "distraido", "confunde"]
EPISODIOS = 2000
PARTIDAS = 20


def a_json(x):
    """Normaliza tuplas y sets para comparar por igualdad después de JSON."""
    return json.loads(json.dumps(x, default=sorted))


def traza_demo(EntornoPictoCocina, JugadorSimulado, jugar_partida, agente, semilla=7, perfil="confunde"):
    """Turno a turno de una partida: detecta cualquier diferencia de RNG u orden."""
    turnos = []

    def mostrar(entorno, s, a, ronda, indice, tiempo, r, info):
        turnos.append({"s": s, "a": a, "opciones": ronda["opciones"], "correctas": ronda["correctas"],
                       "objetivo": ronda["objetivo"], "pista": ronda["pista_atributo"],
                       "indice": indice, "tiempo": tiempo, "r": r, "info": info})

    rng = random.Random(semilla)
    resultado = jugar_partida(EntornoPictoCocina(rng), JugadorSimulado(perfil, rng), agente, mostrar=mostrar)
    return a_json({"turnos": turnos, "resultado": resultado})


def calcular(EntornoPictoCocina, JugadorSimulado, AgenteQ, AgenteReglaFija, jugar_partida, entrenar, evaluar):
    """Devuelve (trazas, tabla_q, metricas)."""
    trazas = {"regla_fija": traza_demo(EntornoPictoCocina, JugadorSimulado, jugar_partida, AgenteReglaFija())}
    agente_q = entrenar(AgenteQ(semilla=42), episodios=EPISODIOS, semilla=42)
    trazas["q"] = traza_demo(EntornoPictoCocina, JugadorSimulado, jugar_partida, agente_q)
    metricas = {f"{perfil}|{nombre}": evaluar(agente, perfil, PARTIDAS, semilla=2026)
                for perfil in PERFILES
                for nombre, agente in (("regla_fija", AgenteReglaFija()), ("q", agente_q))}
    return trazas, agente_q.q, a_json(metricas)
