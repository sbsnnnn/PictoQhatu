"""
entrenamiento.py
----------------
Curvas y métricas del Hito 2 para el informe de modelado.

  1. Entrena Q-Learning como el MVP (30 000 episodios, semilla 42, alfa=0.1, gamma=0.9)
     y guarda por bloque de 500 episodios: recompensa media, tasa de éxito y max|ΔQ|.
  2. Baseline (regla fija) vs Q por perfil, 100 partidas, semilla 2026, con eventos
     de frustración (error con e>=2 y h>=2, la condición de R_FRUSTRACION).
  3. Sensibilidad, un factor a la vez, 3 semillas: alfa en {0.05, 0.1, 0.2} con gamma=0.9
     y gamma en {0.8, 0.9, 0.99} con alfa=0.1 (alfa_final = alfa/10, como el MVP).

Salidas: datos/modelos/curvas/*.png y datos/modelos/metricas/*.csv.
Con --rapido van a datos/modelos/prueba_rapida/ para no pisar la corrida completa.
No toca tabla_q.npy ni tabla_q.csv (los genera experimento_a).

Uso (desde la carpeta codigo/):
    python -m ia_models.experimentos.entrenamiento
    python -m ia_models.experimentos.entrenamiento --rapido
"""

import argparse
import csv
import random
import statistics
import time
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from ia_models.agent.q_learning import AgenteQ, entrenar, jugar_partida  # noqa: E402
from ia_models.agent.regla_fija import AgenteReglaFija  # noqa: E402
from ia_models.env.entorno import EntornoPictoCocina  # noqa: E402
from ia_models.env.jugador_simulado import PERFILES, JugadorSimulado  # noqa: E402
from ia_models.experimentos.experimento_a import CARPETA_DATOS, evaluar  # noqa: E402

SALIDA_RAPIDA = Path(CARPETA_DATOS) / "prueba_rapida"   # ignorada por git
SEMILLA_ENTRENAMIENTO = 42
SEMILLA_EVALUACION = 2026
ALFAS = (0.05, 0.1, 0.2)
GAMMAS = (0.8, 0.9, 0.99)
ALFA_BASE, GAMMA_BASE = 0.1, 0.9
COLOR_Q, COLOR_BASELINE = "#0072B2", "#D55E00"


# ------------------------------------------------------------------
# Entrenamiento con snapshots de la tabla Q
# ------------------------------------------------------------------
class _HistorialConSnapshots(list):
    """Lista que entrenar() llena episodio a episodio; cada `cada` episodios copia la tabla Q.
    Así se toman snapshots sin replicar ni modificar entrenar()."""

    def __init__(self, agente, cada):
        super().__init__()
        self.agente = agente
        self.cada = cada
        self.snapshots = [agente.q.copy()]

    def append(self, resultado):
        super().append(resultado)
        if len(self) % self.cada == 0:
            self.snapshots.append(self.agente.q.copy())


def entrenar_con_snapshots(episodios, semilla, cada, alfa=ALFA_BASE, gamma=GAMMA_BASE):
    agente = AgenteQ(alfa=alfa, gamma=gamma, alfa_final=alfa / 10, semilla=semilla)
    historial = _HistorialConSnapshots(agente, cada)
    entrenar(agente, episodios=episodios, semilla=semilla, historial=historial)
    return agente, list(historial), historial.snapshots


def curva_por_bloques(historial, snapshots, cada):
    filas = []
    for b in range(len(historial) // cada):
        bloque = historial[b * cada:(b + 1) * cada]
        filas.append({
            "episodio": (b + 1) * cada,
            "recompensa_media": statistics.mean(r["recompensa"] for r in bloque),
            "tasa_exito": sum(r["victoria"] for r in bloque) / cada,
            "max_delta_q": float(np.max(np.abs(snapshots[b + 1] - snapshots[b]))),
        })
    return filas


# ------------------------------------------------------------------
# Evaluación con eventos de frustración
# ------------------------------------------------------------------
def es_frustracion(entorno, info):
    """Misma condición que R_FRUSTRACION en entorno.paso(), leída después del turno."""
    return not info["acierto"] and entorno.e >= 2 and entorno.h >= 2


class ContadorFrustracion:
    """Callback `mostrar` de jugar_partida que cuenta eventos de frustración."""

    def __init__(self):
        self.eventos = 0

    def __call__(self, entorno, s, a, ronda, indice, tiempo, r, info):
        self.eventos += es_frustracion(entorno, info)


def evaluar_con_frustracion(agente, perfil, partidas, semilla):
    """Igual que experimento_a.evaluar (mismas semillas por partida) + frustración promedio."""
    resultados, eventos = [], []
    for i in range(partidas):
        rng = random.Random(semilla * 1000 + i)
        cuenta = ContadorFrustracion()
        resultados.append(jugar_partida(EntornoPictoCocina(rng), JugadorSimulado(perfil, rng),
                                        agente, mostrar=cuenta))
        eventos.append(cuenta.eventos)
    return {
        "exito": sum(r["victoria"] for r in resultados) / partidas,
        "turnos": statistics.mean(r["turnos"] for r in resultados),
        "ayudas": statistics.mean(r["ayudas"] for r in resultados),
        "errores": statistics.mean(r["errores"] for r in resultados),
        "recompensa": statistics.mean(r["recompensa"] for r in resultados),
        "frustracion": statistics.mean(eventos),
        "frustracion_total": sum(eventos),
    }


# ------------------------------------------------------------------
# Sensibilidad
# ------------------------------------------------------------------
def configuraciones():
    """(factor, alfa, gamma): un factor a la vez alrededor de alfa=0.1, gamma=0.9."""
    confs = [("alfa", a, GAMMA_BASE) for a in ALFAS if a != ALFA_BASE]
    confs += [("gamma", ALFA_BASE, g) for g in GAMMAS if g != GAMMA_BASE]
    return [("base", ALFA_BASE, GAMMA_BASE)] + confs


def _desv(valores):
    return statistics.stdev(valores) if len(valores) > 1 else 0.0


def sensibilidad(episodios, partidas, semillas, agente_base=None):
    """Entrena 5 configuraciones x semillas y evalúa greedy en los tres perfiles."""
    filas = []
    for factor, alfa, gamma in configuraciones():
        exitos, recompensas = [], []
        for semilla in semillas:
            if agente_base is not None and (alfa, gamma, semilla) == (
                    ALFA_BASE, GAMMA_BASE, SEMILLA_ENTRENAMIENTO):
                agente = agente_base          # mismo entrenamiento que la curva principal
            else:
                print(f"  alfa={alfa} gamma={gamma} semilla={semilla}")
                agente = entrenar(AgenteQ(alfa=alfa, gamma=gamma, alfa_final=alfa / 10, semilla=semilla),
                                  episodios=episodios, semilla=semilla)
            ms = [evaluar(agente, p, partidas, SEMILLA_EVALUACION) for p in PERFILES]
            exitos.append(statistics.mean(m["exito"] for m in ms))
            recompensas.append(statistics.mean(m["recompensa"] for m in ms))
        filas.append({"factor": factor, "alfa": alfa, "gamma": gamma,
                      "semillas": ";".join(map(str, semillas)),
                      "exito_media": statistics.mean(exitos), "exito_desv": _desv(exitos),
                      "recompensa_media": statistics.mean(recompensas),
                      "recompensa_desv": _desv(recompensas)})
    return filas


# ------------------------------------------------------------------
# Salidas
# ------------------------------------------------------------------
def _escribir_csv(ruta, filas):
    with open(ruta, "w", newline="", encoding="utf-8") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=list(filas[0]))
        escritor.writeheader()
        for fila in filas:
            escritor.writerow({k: round(v, 4) if isinstance(v, float) else v for k, v in fila.items()})


def _grafico_linea(ruta, x, y, titulo, eje_y, log=False):
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.plot(x, y, color=COLOR_Q, linewidth=2, marker="o", markersize=3)
    if log:
        ax.set_yscale("log")
    ax.set_title(titulo)
    ax.set_xlabel("Episodio de entrenamiento")
    ax.set_ylabel(eje_y)
    ax.grid(alpha=0.3)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(ruta, dpi=120)
    plt.close(fig)


def filas_de_factor(filas, parametro):
    """Filas donde solo varía `parametro` (las de su factor + la base), ordenadas por su valor."""
    return sorted((f for f in filas if f["factor"] in (parametro, "base")), key=lambda f: f[parametro])


def _grafico_sensibilidad(ruta, filas, parametro):
    filas = filas_de_factor(filas, parametro)
    etiquetas = [str(f[parametro]) for f in filas]
    simbolo = "α" if parametro == "alfa" else "γ"
    fijo = f"γ = {GAMMA_BASE}" if parametro == "alfa" else f"α = {ALFA_BASE}"
    fig, ejes = plt.subplots(1, 2, figsize=(9, 4))
    for ax, clave, nombre in ((ejes[0], "exito", "Tasa de éxito"),
                              (ejes[1], "recompensa", "Recompensa media por partida")):
        ax.errorbar(etiquetas, [f[clave + "_media"] for f in filas], yerr=[f[clave + "_desv"] for f in filas],
                    color=COLOR_Q, linewidth=2, marker="o", markersize=8, capsize=5)
        ax.set_xlabel(simbolo)
        ax.set_ylabel(nombre)
        ax.set_title(nombre)
        ax.grid(alpha=0.3)
        ax.spines[["top", "right"]].set_visible(False)
    fig.suptitle(f"Sensibilidad a {simbolo} ({fijo}; media ± desviación entre semillas)")
    fig.tight_layout()
    fig.savefig(ruta, dpi=120)
    plt.close(fig)


def ejecutar(episodios=30000, partidas=100, semillas=(42, 43, 44), salida=None):
    salida = Path(salida) if salida is not None else Path(CARPETA_DATOS)
    curvas, metricas = salida / "curvas", salida / "metricas"
    curvas.mkdir(parents=True, exist_ok=True)
    metricas.mkdir(parents=True, exist_ok=True)
    cada = min(500, max(1, episodios // 10))
    inicio = time.time()

    print(f"1. Entrenamiento con snapshots ({episodios} episodios, bloques de {cada})")
    agente_q, historial, snapshots = entrenar_con_snapshots(episodios, SEMILLA_ENTRENAMIENTO, cada)
    curva = curva_por_bloques(historial, snapshots, cada)
    _escribir_csv(metricas / "curva_entrenamiento.csv", curva)
    x = [f["episodio"] for f in curva]
    _grafico_linea(curvas / "recompensa.png", x, [f["recompensa_media"] for f in curva],
                   f"Recompensa media por bloque de {cada} episodios", "Recompensa media")
    _grafico_linea(curvas / "exito.png", x, [f["tasa_exito"] for f in curva],
                   f"Tasa de éxito por bloque de {cada} episodios", "Tasa de éxito")
    _grafico_linea(curvas / "convergencia_q.png", x, [f["max_delta_q"] for f in curva],
                   f"Convergencia: max|ΔQ| entre snapshots cada {cada} episodios", "max|ΔQ| (escala log)",
                   log=True)

    print(f"2. Baseline vs Q ({partidas} partidas por perfil)")
    filas = []
    for perfil in PERFILES:
        for agente in (AgenteReglaFija(), agente_q):
            m = evaluar_con_frustracion(agente, perfil, partidas, SEMILLA_EVALUACION)
            filas.append({"perfil": PERFILES[perfil]["nombre"], "agente": agente.nombre,
                          "tasa_exito": m["exito"], "turnos_prom": m["turnos"], "ayudas_prom": m["ayudas"],
                          "errores_prom": m["errores"], "recompensa_prom": m["recompensa"],
                          "frustracion_prom": m["frustracion"], "frustracion_total": m["frustracion_total"]})
            print(f"  {filas[-1]['perfil']:<17}{agente.nombre:<24} éxito={m['exito']:.0%} "
                  f"frustración={m['frustracion']:.2f}")
    _escribir_csv(metricas / "baseline_vs_q.csv", filas)

    print(f"3. Sensibilidad ({len(configuraciones())} configuraciones x {len(semillas)} semillas)")
    sens = sensibilidad(episodios, partidas, semillas, agente_base=agente_q)
    _escribir_csv(metricas / "sensibilidad.csv", sens)
    for f in sens:
        print(f"  alfa={f['alfa']:<5} gamma={f['gamma']:<5} "
              f"éxito={f['exito_media']:.3f}±{f['exito_desv']:.3f} "
              f"recompensa={f['recompensa_media']:.2f}±{f['recompensa_desv']:.2f}")
    _grafico_sensibilidad(curvas / "sensibilidad_alfa.png", sens, "alfa")
    _grafico_sensibilidad(curvas / "sensibilidad_gamma.png", sens, "gamma")
    print(f"Listo en {(time.time() - inicio) / 60:.1f} min. Salidas en {salida}")


def main():
    parser = argparse.ArgumentParser(description="Curvas y métricas de entrenamiento - PictoQhatu")
    parser.add_argument("--episodios", type=int, default=30000, help="episodios por entrenamiento")
    parser.add_argument("--rapido", action="store_true", help="prueba corta: 300 episodios, 10 partidas")
    args = parser.parse_args()
    if args.rapido:   # carpeta aparte: no pisa las curvas de la corrida completa
        ejecutar(episodios=300, partidas=10, salida=SALIDA_RAPIDA)
    else:
        ejecutar(episodios=args.episodios)


if __name__ == "__main__":
    main()
