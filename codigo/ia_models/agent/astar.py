"""
astar.py
--------
Baseline del agente, parte 2 (sección 2.4 del documento). Portado de baseline.py.

A* (Fase 3) sobre el grafo de precedencias de la receta:
     f(n) = g(n) + h(n),  g = pasos ya hechos en el camino,
                          h = número de pasos pendientes.
"""

import heapq

from ia_models.env.catalogo import PLATOS


def pasos_validos(plato, hechos):
    """Pasos pendientes cuyas precedencias ya se cumplieron."""
    receta = PLATOS[plato]
    validos = []
    for i in range(len(receta["pasos"])):
        requisitos = receta["precedencias"].get(i, [])
        if i not in hechos and all(j in hechos for j in requisitos):
            validos.append(i)
    return validos


def astar_plan(plato, hechos=()):
    """Devuelve la lista de pasos (índices) para terminar el plato."""
    n = len(PLATOS[plato]["pasos"])
    inicio = frozenset(hechos)
    contador = 0                                   # desempate en la cola
    frontera = [(n - len(inicio), 0, contador, inicio, [])]
    visitados = set()
    while frontera:
        f, g, _, estado, camino = heapq.heappop(frontera)
        if len(estado) == n:                       # meta: todos los pasos hechos
            return camino
        if estado in visitados:
            continue
        visitados.add(estado)
        for paso in pasos_validos(plato, estado):
            nuevo = estado | {paso}
            g2 = g + 1
            h2 = n - len(nuevo)                    # h = pasos pendientes
            contador += 1
            heapq.heappush(frontera, (g2 + h2, g2, contador, nuevo, camino + [paso]))
    return []


def astar_siguiente_paso(plato, hechos):
    """Siguiente paso válido según A* (se usa para las pistas)."""
    plan = astar_plan(plato, hechos)
    return plan[0] if plan else None


if __name__ == "__main__":
    for p in PLATOS:
        print(p, "->", astar_plan(p))
