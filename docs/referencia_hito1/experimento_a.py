"""
experimento_a.py
----------------
Experimento A del Hito 1: lógica del agente en consola desde un estado inicial.

Pasos:
  1. Verifica el catálogo (26 pictogramas y 5 platos).
  2. Muestra el baseline: entropía y ganancias de ID3, árbol ID3 y planes A*.
  3. Entrena la tabla Q con los tres jugadores simulados y la guarda en /datos.
  4. Demo: una partida turno a turno (semilla fija).
  5. Validación: 100 partidas por perfil, baseline vs baseline + Q-Learning.

Uso (desde la carpeta codigo/ia_models):
    python experimento_a.py
    python experimento_a.py --perfil distraido --semilla 3
    python experimento_a.py --episodios 50000 --partidas 200
"""

import argparse
import csv
import os
import random
import statistics

from catalogo import PLATOS, INGREDIENTES, ETIQUETAS, texto, verificar_catalogo
from baseline import (entropia, ordenar_por_ganancia, construir_arbol_id3,
                      imprimir_arbol, astar_plan)
from entorno import EntornoPictoCocina, NOMBRES_FASE, ACCIONES_AGENTE, MAX_TURNOS
from jugador_simulado import JugadorSimulado, PERFILES
from agente_q import AgenteQ, AgenteReglaFija, jugar_partida, entrenar, guardar_tabla_q

# Carpeta /datos en la raíz del proyecto (dos niveles arriba de este archivo)
RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CARPETA_DATOS = os.path.join(RAIZ, "datos")


def titulo(texto_titulo):
    print("\n" + "=" * 78)
    print(texto_titulo)
    print("=" * 78)


def mostrar_turno(entorno, s, a, ronda, indice, tiempo, r, info):
    """Imprime un turno de la partida en consola."""
    f, e, h, t, u = s
    print(f"\nTurno {entorno.turno:>2} | Fase {ronda['fase']} ({NOMBRES_FASE[ronda['fase']]}) "
          f"| Pedido: {ronda['pedido']}")
    if ronda["fase"] == 1:
        nombres = ", ".join(PLATOS[p]["nombre"] for p in ronda["compatibles"])
        print(f"  C(I) = {{{nombres}}}  |  ID3 sugiere: {texto(ronda['opciones'][ronda['objetivo']])}")
    print(f"  Estado s' = (f={f}, e={e}, h={h}, t={t}, u={u})")
    print(f"  Agente  -> {ACCIONES_AGENTE[a]}: {ronda['texto_pista']}")
    print("  Opciones: " + "  ".join(f"[{texto(o)}]" for o in ronda["opciones"]))
    resultado = "ACIERTO" if info["acierto"] else f"ERROR (tipo: {info['tipo_error']})"
    print(f"  Jugador -> toca {info['elegido']} ({tiempo} s)  {resultado}  "
          f"NPC: {info['respuesta_npc']}  | recompensa = {r:+.2f}")
    if info["cambio_fase"] and not entorno.victoria:
        if entorno.f == 2:
            print(f"\n  >>> Plato fijado: {PLATOS[entorno.d]['nombre']}. "
                  f"NPC: [QUIERO] + [{PLATOS[entorno.d]['nombre'].upper()}]. Pasa a la Fase 2.")
        else:
            print("\n  >>> Pedido terminado. Pasa a la Fase 3: ahora arma el plato solo.")


def mostrar_baseline():
    titulo("2. BASELINE: ID3 (Fase 1) y A* (Fase 3)")
    C = list(PLATOS)
    print(f"H(C) con 5 platos equiprobables = log2(5) = {entropia(C):.2f} bits\n")
    print("Ganancia de información de cada ingrediente:")
    for x, g in ordenar_por_ganancia(C, list(INGREDIENTES)):
        print(f"  G(C, {ETIQUETAS[x]:<9}) = {g:.3f}")
    print("\nÁrbol ID3 para identificar el plato:")
    imprimir_arbol(construir_arbol_id3(C))
    print("\nPlan A* de cada plato (h = pasos pendientes):")
    for clave, plato in PLATOS.items():
        plan = astar_plan(clave)
        print(f"  {plato['nombre']:<19}: " + " -> ".join(texto(plato["pasos"][i]) for i in plan))


def evaluar(agente, perfil, partidas, semilla):
    """Juega varias partidas con semillas fijas y devuelve promedios."""
    resultados = []
    for i in range(partidas):
        rng = random.Random(semilla * 1000 + i)
        entorno = EntornoPictoCocina(rng)
        jugador = JugadorSimulado(perfil, rng)
        resultados.append(jugar_partida(entorno, jugador, agente))
    return {
        "exito": sum(r["victoria"] for r in resultados) / partidas,
        "turnos": statistics.mean(r["turnos"] for r in resultados),
        "ayudas": statistics.mean(r["ayudas"] for r in resultados),
        "errores": statistics.mean(r["errores"] for r in resultados),
        "recompensa": statistics.mean(r["recompensa"] for r in resultados),
    }


def main():
    parser = argparse.ArgumentParser(description="Experimento A - PictoCocina")
    parser.add_argument("--perfil", default="confunde", choices=list(PERFILES),
                        help="perfil del jugador simulado en la demo")
    parser.add_argument("--semilla", type=int, default=7, help="semilla de la demo")
    parser.add_argument("--episodios", type=int, default=30000, help="episodios de entrenamiento")
    parser.add_argument("--partidas", type=int, default=100, help="partidas por perfil en la validación")
    args = parser.parse_args()
    os.makedirs(CARPETA_DATOS, exist_ok=True)

    # 1. Catálogo
    titulo("1. CATÁLOGO")
    verificar_catalogo()

    # 2. Baseline
    mostrar_baseline()

    # 3. Entrenamiento
    titulo(f"3. ENTRENAMIENTO Q-LEARNING ({args.episodios} episodios, alfa=0.1, gamma=0.9)")
    agente_q = entrenar(AgenteQ(semilla=42), episodios=args.episodios, semilla=42)
    ruta_csv = os.path.join(CARPETA_DATOS, "tabla_q.csv")
    ruta_npy = os.path.join(CARPETA_DATOS, "tabla_q.npy")
    guardar_tabla_q(agente_q, ruta_csv, ruta_npy)
    print(f"  Tabla Q (162 x 6) guardada en: {ruta_csv}")

    # 4. Demo
    titulo(f"4. DEMO: una partida con el jugador '{PERFILES[args.perfil]['nombre']}' "
           f"(semilla {args.semilla})")
    rng = random.Random(args.semilla)
    entorno = EntornoPictoCocina(rng)
    jugador = JugadorSimulado(args.perfil, rng)
    res = jugar_partida(entorno, jugador, agente_q, mostrar=mostrar_turno)
    print()
    if res["victoria"]:
        print(f"*** VICTORIA: {PLATOS[entorno.d]['nombre']} completado en {res['turnos']} turnos, "
              f"con {res['ayudas']} ayudas y {res['errores']} errores. ***")
    else:
        print(f"Fin a los {MAX_TURNOS} turnos (sin pantalla de fracaso).")
        print("El NPC muestra la solución con amabilidad -> " + entorno.solucion())

    # 5. Validación
    titulo(f"5. VALIDACIÓN: {args.partidas} partidas por perfil")
    agentes = [AgenteReglaFija(), agente_q]
    filas = []
    print(f"{'Perfil':<17}{'Agente':<24}{'Éxito':>7}{'Turnos':>8}{'Ayudas':>8}{'Errores':>9}{'Recomp.':>9}")
    print("-" * 82)
    for perfil in PERFILES:
        for agente in agentes:
            m = evaluar(agente, perfil, args.partidas, semilla=2026)
            filas.append([PERFILES[perfil]["nombre"], agente.nombre, round(m["exito"], 3),
                          round(m["turnos"], 2), round(m["ayudas"], 2),
                          round(m["errores"], 2), round(m["recompensa"], 2)])
            print(f"{PERFILES[perfil]['nombre']:<17}{agente.nombre:<24}{m['exito']:>7.0%}"
                  f"{m['turnos']:>8.1f}{m['ayudas']:>8.1f}{m['errores']:>9.1f}{m['recompensa']:>9.1f}")
    ruta_res = os.path.join(CARPETA_DATOS, "resultados_experimento_a.csv")
    with open(ruta_res, "w", newline="", encoding="utf-8") as archivo:
        escritor = csv.writer(archivo)
        escritor.writerow(["perfil", "agente", "tasa_exito", "turnos_prom",
                           "ayudas_prom", "errores_prom", "recompensa_prom"])
        escritor.writerows(filas)
    print(f"\nResultados guardados en: {ruta_res}")


if __name__ == "__main__":
    main()
