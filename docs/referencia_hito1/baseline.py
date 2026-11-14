"""
baseline.py
-----------
Baseline del agente (sección 2.4 del documento):

1. ID3 (Fase 1), escrito a mano con NumPy:
     H(C)    = - sum p_i * log2(p_i)
     G(C, x) = H(C) - sum_v (|C_v| / |C|) * H(C_v)
   - Elige el ingrediente de mayor ganancia sobre los platos compatibles C(I).
   - Con la misma medida, la pista a5 elige el atributo (color o categoría)
     que mejor separa la respuesta del resto de opciones en pantalla.

2. A* (Fase 3) sobre el grafo de precedencias de la receta:
     f(n) = g(n) + h(n),  g = pasos ya hechos en el camino,
                          h = número de pasos pendientes.
"""

import heapq
import numpy as np

from catalogo import INGREDIENTES, PLATOS, ETIQUETAS, atributo


# ==================================================================
# PARTE 1: ID3
# ==================================================================
def entropia(etiquetas):
    """H = -sum p*log2(p) de una lista de etiquetas."""
    etiquetas = np.array(etiquetas)
    if len(etiquetas) == 0:
        return 0.0
    _, cuentas = np.unique(etiquetas, return_counts=True)
    p = cuentas / cuentas.sum()
    return float(-(p * np.log2(p)).sum())


def platos_compatibles(I):
    """C(I) = platos que contienen TODOS los ingredientes elegidos I."""
    return [p for p in PLATOS if set(I) <= set(PLATOS[p]["ingredientes"])]


def ganancia_ingrediente(C, ingrediente):
    """
    Ganancia de información de preguntar "¿lleva este ingrediente?"
    sobre el conjunto de platos C (todos equiprobables).
    """
    platos = np.array(C)
    lleva = np.array([ingrediente in PLATOS[p]["ingredientes"] for p in C])
    h_total = entropia(platos)
    h_despues = 0.0
    for valor in (True, False):
        subconjunto = platos[lleva == valor]
        if len(subconjunto) > 0:
            h_despues += len(subconjunto) / len(platos) * entropia(subconjunto)
    return h_total - h_despues


def ordenar_por_ganancia(C, candidatos):
    """Lista de (ingrediente, ganancia) de mayor a menor ganancia.
    En empate se respeta el orden del catálogo."""
    pares = [(x, round(ganancia_ingrediente(C, x), 3)) for x in candidatos]
    return sorted(pares, key=lambda par: -par[1])


def construir_arbol_id3(C, ingredientes=None):
    """Árbol ID3 que identifica el plato con preguntas "¿lleva X?"."""
    if ingredientes is None:
        ingredientes = list(INGREDIENTES)
    if len(C) == 1:
        return PLATOS[C[0]]["nombre"]
    ranking = ordenar_por_ganancia(C, ingredientes)
    if not ranking or ranking[0][1] == 0:
        return " / ".join(PLATOS[p]["nombre"] for p in C)
    mejor, g = ranking[0]
    resto = [x for x in ingredientes if x != mejor]
    si = [p for p in C if mejor in PLATOS[p]["ingredientes"]]
    no = [p for p in C if mejor not in PLATOS[p]["ingredientes"]]
    return {"pregunta": mejor, "ganancia": g,
            "si": construir_arbol_id3(si, resto),
            "no": construir_arbol_id3(no, resto)}


def imprimir_arbol(arbol, sangria=""):
    """Muestra el árbol ID3 en consola."""
    if isinstance(arbol, str):
        print(sangria + "=> " + arbol)
        return
    print(f"{sangria}¿Lleva {ETIQUETAS[arbol['pregunta']]}? (G = {arbol['ganancia']:.3f})")
    print(sangria + "  SÍ:")
    imprimir_arbol(arbol["si"], sangria + "    ")
    print(sangria + "  NO:")
    imprimir_arbol(arbol["no"], sangria + "    ")


def mejor_atributo(opciones, objetivo, preferido=None):
    """
    Pista a5: elige el atributo (color o categoría) con mayor ganancia
    para separar la opción correcta (objetivo) del resto en pantalla.
    En empate se usa el atributo del último error (preferido).
    Devuelve (atributo, valor, ganancias).
    """
    etiquetas = np.array([1 if i == objetivo else 0 for i in range(len(opciones))])
    h_total = entropia(etiquetas)
    ganancias = {}
    for nombre in ("color", "categoria"):
        valores = np.array([str(atributo(op, nombre)) for op in opciones])
        h_despues = 0.0
        for v in np.unique(valores):
            mascara = valores == v
            h_despues += mascara.mean() * entropia(etiquetas[mascara])
        ganancias[nombre] = round(h_total - h_despues, 3)

    if atributo(opciones[objetivo], "color") is None:   # p. ej. MEZCLAR
        return None, None, ganancias

    maximo = max(ganancias.values())
    empatados = [a for a in ("color", "categoria") if ganancias[a] == maximo]
    elegido = preferido if preferido in empatados else empatados[0]
    return elegido, atributo(opciones[objetivo], elegido), ganancias


# ==================================================================
# PARTE 2: A* sobre el grafo de precedencias
# ==================================================================
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
    C = list(PLATOS)
    print(f"H(C) con 5 platos = {entropia(C):.2f} bits")
    for x, g in ordenar_por_ganancia(C, list(INGREDIENTES)):
        print(f"  G(C, {x}) = {g:.3f}")
    imprimir_arbol(construir_arbol_id3(C))
    for p in PLATOS:
        print(p, "->", astar_plan(p))
