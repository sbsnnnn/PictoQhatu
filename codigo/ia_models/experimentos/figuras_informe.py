"""
figuras_informe.py
------------------
Figuras del informe del Hito 2 a partir de los CSV que ya guardaron experimento_a y entrenamiento.
No entrena ni evalúa nada: solo lee datos/modelos/metricas/ y dibuja.

  fig_recompensa.png   recompensa media por bloque de 500 episodios
  fig_delta_q.png      max|ΔQ| entre bloques (escala log)
  fig_ayudas.png       ayudas promedio por perfil, Q-Learning vs regla fija
  fig_comparacion.png  errores, recompensa y frustración por perfil, Q-Learning vs regla fija

Uso (desde codigo/):
    python -m ia_models.experimentos.figuras_informe [carpeta_salida]
"""

import csv
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from ia_models.experimentos.experimento_a import CARPETA_DATOS  # noqa: E402

METRICAS = Path(CARPETA_DATOS) / "metricas"
SALIDA = Path(CARPETA_DATOS).parents[1] / "docs" / "informe" / "figuras"
COLOR_Q, COLOR_REGLA = "#3F4FB8", "#F28C28"   # índigo y naranja de la paleta del juego
EPS_FINAL = 24000                              # ε y α llegan a su valor final al 80 % de 30 000


def _leer(nombre):
    with open(METRICAS / nombre, encoding="utf-8") as archivo:
        return list(csv.DictReader(archivo))


def _ejes(ax, xlabel, ylabel):
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(alpha=0.3)
    ax.spines[["top", "right"]].set_visible(False)


def _guardar(fig, salida, nombre):
    fig.tight_layout()
    fig.savefig(salida / nombre, dpi=200)
    plt.close(fig)


def curvas(salida):
    filas = _leer("curva_entrenamiento.csv")
    x = [int(f["episodio"]) for f in filas]
    graficos = (("fig_recompensa.png", "recompensa_media", "Recompensa media del bloque", False),
                ("fig_delta_q.png", "max_delta_q", "max|ΔQ| (escala logarítmica)", True))
    for nombre, clave, eje, log in graficos:
        fig, ax = plt.subplots(figsize=(7.5, 3.8))
        ax.plot(x, [float(f[clave]) for f in filas], color=COLOR_Q, linewidth=2, marker="o", markersize=3)
        ax.axvline(EPS_FINAL, color="#1F1A2E", linestyle="--", linewidth=1)
        ax.annotate("ε = 0.05 y α = 0.01", (EPS_FINAL, 0.5), xycoords=("data", "axes fraction"),
                    xytext=(-6, 0), textcoords="offset points", ha="right", fontsize=9)
        if log:
            ax.set_yscale("log")
        _ejes(ax, "Episodio de entrenamiento (fin de cada bloque de 500)", eje)
        _guardar(fig, salida, nombre)


def _barras(ax, perfiles, valores_regla, valores_q, decimales=2):
    ancho = 0.38
    pos = range(len(perfiles))
    for desplazamiento, valores, color, etiqueta in ((-ancho / 2, valores_regla, COLOR_REGLA, "Regla fija"),
                                                      (ancho / 2, valores_q, COLOR_Q, "Q-Learning")):
        barras = ax.bar([p + desplazamiento for p in pos], valores, ancho, color=color, label=etiqueta,
                        edgecolor="#1F1A2E", linewidth=0.6)
        ax.bar_label(barras, fmt=f"%.{decimales}f", fontsize=8, padding=2)
    ax.set_xticks(list(pos), perfiles)


def comparacion(salida):
    filas = _leer("baseline_vs_q.csv")
    perfiles = list(dict.fromkeys(f["perfil"] for f in filas))
    por = {(f["perfil"], "Q" if "Q-Learning" in f["agente"] else "R"): f for f in filas}

    def serie(clave, agente):
        return [float(por[(p, agente)][clave]) for p in perfiles]

    fig, ax = plt.subplots(figsize=(7, 3.8))
    _barras(ax, perfiles, serie("ayudas_prom", "R"), serie("ayudas_prom", "Q"))
    _ejes(ax, "Perfil del jugador simulado", "Ayudas promedio por partida")
    ax.legend(frameon=False)
    _guardar(fig, salida, "fig_ayudas.png")

    fig, ejes = plt.subplots(1, 3, figsize=(11, 3.8))
    for ax, clave, titulo, dec in ((ejes[0], "errores_prom", "Errores promedio", 2),
                                   (ejes[1], "recompensa_prom", "Recompensa promedio", 1),
                                   (ejes[2], "frustracion_total", "Eventos de frustración (total)", 0)):
        _barras(ax, perfiles, serie(clave, "R"), serie(clave, "Q"), dec)
        ax.set_title(titulo, fontsize=11)
        ax.tick_params(axis="x", labelsize=8)
        _ejes(ax, "", "")
    ejes[0].legend(frameon=False, fontsize=8)
    _guardar(fig, salida, "fig_comparacion.png")


def main():
    salida = Path(sys.argv[1]) if len(sys.argv) > 1 else SALIDA
    salida.mkdir(parents=True, exist_ok=True)
    curvas(salida)
    comparacion(salida)
    print(f"Figuras en {salida}")


if __name__ == "__main__":
    main()
