"""Genera los valores de referencia del MVP del Hito 1 (se corre una sola vez).

Ejecuta el código original de docs/referencia_hito1/ en un subproceso, sin
importarlo desde el paquete, y guarda en esta carpeta:
  traza_demo.json, tabla_q_2000.npy, evaluar_20.json   (prueba rápida)
  resultados_mvp.csv, tabla_q_mvp.npy                  (Experimento A completo, --completo)

Uso (desde codigo/):
    python -m ia_models.tests.referencia.generar_referencia [--completo]
"""

import subprocess
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
MVP = AQUI.parents[3] / "docs" / "referencia_hito1"

RAPIDO = f"""
import json, sys
sys.path[:0] = [{str(MVP)!r}, {str(AQUI)!r}]
import numpy as np
from entorno import EntornoPictoCocina
from jugador_simulado import JugadorSimulado
from agente_q import AgenteQ, AgenteReglaFija, jugar_partida, entrenar
from experimento_a import evaluar
from calculo import calcular
trazas, q, metricas = calcular(EntornoPictoCocina, JugadorSimulado, AgenteQ, AgenteReglaFija,
                               jugar_partida, entrenar, evaluar)
json.dump(trazas, open({str(AQUI / "traza_demo.json")!r}, "w", encoding="utf-8"), ensure_ascii=False)
np.save({str(AQUI / "tabla_q_2000.npy")!r}, q)
json.dump(metricas, open({str(AQUI / "evaluar_20.json")!r}, "w", encoding="utf-8"), indent=1)
"""

COMPLETO = f"""
import os, shutil, sys, tempfile
sys.path.insert(0, {str(MVP)!r})
import experimento_a
tmp = tempfile.mkdtemp()
experimento_a.CARPETA_DATOS = tmp
sys.argv = ["experimento_a"]
experimento_a.main()
shutil.copy(os.path.join(tmp, "resultados_experimento_a.csv"), {str(AQUI / "resultados_mvp.csv")!r})
shutil.copy(os.path.join(tmp, "tabla_q.npy"), {str(AQUI / "tabla_q_mvp.npy")!r})
shutil.rmtree(tmp)
"""


def main():
    # cwd en el MVP: así ningún archivo que escriba cae dentro del repo
    subprocess.run([sys.executable, "-c", RAPIDO], cwd=MVP, check=True)
    if "--completo" in sys.argv:
        subprocess.run([sys.executable, "-c", COMPLETO], cwd=MVP, check=True)
    print("Referencia guardada en", AQUI)


if __name__ == "__main__":
    main()
