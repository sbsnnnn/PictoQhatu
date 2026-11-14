"""
entorno.py
----------
Entorno del juego PictoQhatu (sección 2.1 del documento). Portado 1:1 del MVP del Hito 1.

Estado completo:  s  = (f, d, I, k, e, h, t, u)
Estado reducido:  s' = (f, e, h, t, u)  -> 3 x 3 x 3 x 2 x 3 = 162 estados

  f: fase (1, 2, 3)              e: errores seguidos (0, 1, 2+)
  d: plato objetivo              h: ayudas en el paso actual (0, 1, 2+)
  I: ingredientes elegidos       t: tiempo de respuesta (rapido, lento)
  k: paso actual (Fase 2)        u: tipo del último error (color, categoria, otro)

Cada turno:
  1. El agente elige una acción a0..a5 mirando s'.
  2. nueva_ronda(accion) arma la pantalla (opciones) y aplica la ayuda.
  3. El jugador toca una opción.
  4. paso(...) actualiza el estado y devuelve la recompensa.
"""

import random

from ia_models.agent.astar import astar_plan, astar_siguiente_paso, pasos_validos
from ia_models.agent.id3 import mejor_atributo, ordenar_por_ganancia, platos_compatibles
from ia_models.env.catalogo import (
    ETIQUETAS,
    FRASE_CATEGORIA,
    INGREDIENTES,
    PLATOS,
    atributo,
    ingrediente_de,
    similitud,
    texto,
)

# ------------------------------------------------------------------
# Constantes
# ------------------------------------------------------------------
NOMBRES_FASE = {1: "Reunir ingredientes", 2: "El pedido", 3: "Armar el plato"}
ACCIONES_AGENTE = ["a0 sin ayuda", "a1 repetir por voz", "a2 resaltar",
                   "a3 reducir opciones", "a4 mostrar respuesta", "a5 pista por atributo"]
TIPOS_ERROR = ["color", "categoria", "otro"]
VELOCIDADES = ["rapido", "lento"]

MAX_TURNOS = 30        # término alternativo
UMBRAL_LENTO = 4.0     # segundos: más que esto cuenta como "lento"
N_OPCIONES = 4         # pictogramas en pantalla
N_ESTADOS = 3 * 3 * 3 * 2 * 3   # 162
N_ACCIONES = 6

# Recompensas (sección 2.4)
R_PLATO = 10.0
R_SIN_AYUDA = 1.0
R_CON_AYUDA = 0.5
R_REPETIR = -1.0
# Costo de cada pista según cuánto revela la respuesta (valores a calibrar).
# Así el agente aprende a dar la ayuda mínima necesaria y no siempre a4.
COSTO_PISTA = {1: -0.1, 2: -0.2, 3: -0.3, 4: -0.6, 5: -0.2}
R_FRUSTRACION = -5.0


def indice_estado(s):
    """Convierte s' = (f, e, h, t, u) en un número de fila 0..161."""
    f, e, h, t, u = s
    return ((((f - 1) * 3 + e) * 3 + h) * 2 + VELOCIDADES.index(t)) * 3 + TIPOS_ERROR.index(u)


def acciones_permitidas(s):
    """En la Fase 3 el agente solo interviene después de un error."""
    f, e = s[0], s[1]
    if f == 3 and e == 0:
        return [0]
    return list(range(N_ACCIONES))


class EntornoPictoCocina:

    def __init__(self, rng=None):
        self.rng = rng if rng is not None else random.Random()
        self.reiniciar()

    # --------------------------------------------------------------
    # Estado
    # --------------------------------------------------------------
    def reiniciar(self):
        self.f = 1
        self.d = None
        self.I = []
        self.k = 0
        self.e = 0
        self.h = 0
        self.t = "rapido"
        self.u = "otro"
        self.hechos = set()        # pasos hechos en la Fase 3
        self.turno = 0
        self.ultima_accion = 0
        self.ayudas = 0
        self.errores = 0
        self.terminado = False
        self.victoria = False
        return self.estado_reducido()

    def estado_reducido(self):
        return (self.f, min(self.e, 2), min(self.h, 2), self.t, self.u)

    # --------------------------------------------------------------
    # Armar la pantalla de cada turno
    # --------------------------------------------------------------
    def _distractores(self, referencias, pool, n):
        """Elige n opciones incorrectas: primero una del mismo color que
        alguna referencia, luego una de la misma categoría, y el resto al azar."""
        pool = list(pool)
        self.rng.shuffle(pool)
        elegidos = []
        for nombre in ("color", "categoria"):
            listo = False
            for ref in referencias:
                for x in pool:
                    if len(elegidos) >= n or listo:
                        break
                    a, b = atributo(x, nombre), atributo(ref, nombre)
                    if x not in elegidos and a is not None and a == b:
                        elegidos.append(x)
                        listo = True
        for x in pool:
            if len(elegidos) >= n:
                break
            if x not in elegidos:
                elegidos.append(x)
        return elegidos[:n]

    def _mezclar(self, opciones, refs, correctas_items, objetivo_item):
        """Baraja las opciones y calcula los índices de correctas y objetivo."""
        orden = list(range(len(opciones)))
        self.rng.shuffle(orden)
        opciones = [opciones[i] for i in orden]
        refs = [refs[i] for i in orden]
        correctas = {i for i, op in enumerate(opciones) if op in correctas_items}
        objetivo = opciones.index(objetivo_item)
        return opciones, refs, correctas, objetivo

    def _ronda_fase1(self):
        """Fase 1 (Modalidad 2): el jugador elige ingredientes.
        ID3 decide qué pictogramas mostrar: los de mayor ganancia sobre C(I),
        cuidando que cada plato compatible tenga al menos un ingrediente en pantalla."""
        C = platos_compatibles(self.I)
        pendientes = [x for x in INGREDIENTES if x not in self.I
                      and any(x in PLATOS[p]["ingredientes"] for p in C)]
        ranking = ordenar_por_ganancia(C, pendientes)

        elegidos, cubiertos = [], set()
        for x, g in ranking:                         # cobertura de platos
            platos_x = {p for p in C if x in PLATOS[p]["ingredientes"]}
            if platos_x - cubiertos and len(elegidos) < N_OPCIONES:
                elegidos.append(x)
                cubiertos |= platos_x
        n_compatibles = max(len(elegidos), min(3, len(pendientes)))
        for x, g in ranking:                         # completar por ganancia
            if len(elegidos) >= n_compatibles:
                break
            if x not in elegidos:
                elegidos.append(x)

        incompatibles = [x for x in INGREDIENTES if x not in self.I and x not in pendientes]
        distractores = self._distractores(elegidos, incompatibles, N_OPCIONES - len(elegidos))
        opciones = elegidos + distractores
        refs = [None] * len(opciones)
        sugerido = ranking[0][0]                     # ingrediente de mayor ganancia
        opciones, refs, correctas, objetivo = self._mezclar(opciones, refs, pendientes, sugerido)
        return {"fase": 1, "opciones": opciones, "refs": refs, "correctas": correctas,
                "objetivo": objetivo, "pedido": "[QUIERO] + [ ? ]  (el jugador elige)",
                "compatibles": C, "ranking": ranking}

    def _ronda_fase2(self):
        """Fase 2 (Modalidad 1): el NPC pide el paso k, p. ej. [PONER] + [PAN]."""
        accion, ing = PLATOS[self.d]["pasos"][self.k]
        if ing is not None:
            pool = [x for x in INGREDIENTES if x != ing]
            opciones = [ing] + self._distractores([ing], pool, N_OPCIONES - 1)
            correcto = ing
            pedido = f"[{accion}] + [{ETIQUETAS[ing]}]"
        else:                                        # MEZCLAR: se elige la acción
            opciones = [accion, "PONER", "CORTAR", "PREPARAR"]
            correcto = accion
            pedido = f"[{accion}]"
        refs = [None] * len(opciones)
        opciones, refs, correctas, objetivo = self._mezclar(opciones, refs, [correcto], correcto)
        return {"fase": 2, "opciones": opciones, "refs": refs, "correctas": correctas,
                "objetivo": objetivo, "pedido": pedido}

    def _ronda_fase3(self):
        """Fase 3: el jugador arma el plato solo. A* da el siguiente paso válido."""
        pasos = PLATOS[self.d]["pasos"]
        pendientes = [i for i in range(len(pasos)) if i not in self.hechos]
        validos = pasos_validos(self.d, self.hechos)
        siguiente = astar_siguiente_paso(self.d, self.hechos)

        orden = validos + [i for i in pendientes if i not in validos]
        mostrados = orden[:N_OPCIONES]
        opciones = [pasos[i] for i in mostrados]
        refs = list(mostrados)

        if len(opciones) < N_OPCIONES:              # tarjetas distractoras
            accion_comun = max(set(a for a, _ in pasos), key=[a for a, _ in pasos].count)
            pool = [(accion_comun, x) for x in INGREDIENTES
                    if x not in PLATOS[self.d]["ingredientes"]]
            referencias = [op for op in opciones if op[1] is not None]
            extra = self._distractores(referencias, pool, N_OPCIONES - len(opciones))
            opciones += extra
            refs += [None] * len(extra)

        correctas_items = [pasos[i] for i in validos]
        opciones, refs, correctas, objetivo = self._mezclar(
            opciones, refs, correctas_items, pasos[siguiente])
        return {"fase": 3, "opciones": opciones, "refs": refs, "correctas": correctas,
                "objetivo": objetivo, "pedido": "Arma el plato tú solo: ¿qué paso sigue?"}

    # --------------------------------------------------------------
    # Aplicar la ayuda del agente sobre la pantalla
    # --------------------------------------------------------------
    def _filtrar(self, ronda, indices):
        objetivo_item = ronda["opciones"][ronda["objetivo"]]
        correctas_items = [ronda["opciones"][i] for i in ronda["correctas"]]
        ronda["opciones"] = [ronda["opciones"][i] for i in indices]
        ronda["refs"] = [ronda["refs"][i] for i in indices]
        ronda["correctas"] = {i for i, op in enumerate(ronda["opciones"]) if op in correctas_items}
        ronda["objetivo"] = ronda["opciones"].index(objetivo_item)

    def nueva_ronda(self, accion):
        if self.f == 1:
            ronda = self._ronda_fase1()
        elif self.f == 2:
            ronda = self._ronda_fase2()
        else:
            ronda = self._ronda_fase3()

        ronda["pista_atributo"] = None
        obj = ronda["objetivo"]
        obj_texto = texto(ronda["opciones"][obj])

        if accion == 0:
            ronda["texto_pista"] = "(sin ayuda)"
        elif accion == 1:
            ronda["texto_pista"] = "Repite por voz: " + ronda["pedido"]
        elif accion == 2:
            ronda["texto_pista"] = "Resalta: " + obj_texto
        elif accion == 3:
            incorrectas = [i for i in range(len(ronda["opciones"])) if i not in ronda["correctas"]]
            if not incorrectas:
                incorrectas = [i for i in range(len(ronda["opciones"])) if i != obj]
            otra = min(incorrectas, key=lambda i: similitud(ronda["opciones"][i], ronda["opciones"][obj]))
            self._filtrar(ronda, sorted([obj, otra]))
            ronda["texto_pista"] = "Reduce a: " + ", ".join(texto(o) for o in ronda["opciones"])
        elif accion == 4:
            ronda["texto_pista"] = "Muestra la respuesta: " + obj_texto
        elif accion == 5:
            preferido = self.u if self.u in ("color", "categoria") else None
            nombre, valor, ganancias = mejor_atributo(ronda["opciones"], obj, preferido)
            if nombre is None:
                ronda["texto_pista"] = "Repite por voz: " + ronda["pedido"]
            else:
                ronda["pista_atributo"] = (nombre, valor)
                frase = ("es de color " + valor.upper()) if nombre == "color" \
                    else ("es " + FRASE_CATEGORIA[valor])
                ronda["texto_pista"] = (f'Pista: "{frase}"  (G color = {ganancias["color"]:.3f}, '
                                        f'G categoría = {ganancias["categoria"]:.3f})')
        return ronda

    # --------------------------------------------------------------
    # Tipo de error (Tabla 4)
    # --------------------------------------------------------------
    def _tipo_error(self, ronda, indice):
        elegido = ronda["opciones"][indice]
        if ronda["fase"] == 3 and ronda["refs"][indice] is not None:
            return "otro"                       # paso del plato, pero fuera de orden
        correctas = [ronda["opciones"][i] for i in ronda["correctas"]]
        if ingrediente_de(elegido) is None or not correctas:
            return "otro"
        objetivo_item = ronda["opciones"][ronda["objetivo"]]
        ref = max(correctas, key=lambda c: (similitud(elegido, c), c == objetivo_item))
        if ingrediente_de(ref) is None:
            return "otro"
        misma_categoria = atributo(elegido, "categoria") == atributo(ref, "categoria")
        mismo_color = atributo(elegido, "color") == atributo(ref, "color")
        if misma_categoria and not mismo_color:
            return "color"        # p. ej. tomate en vez de zanahoria -> pista de color
        return "categoria"        # p. ej. leche en vez de manzana    -> pista de categoría

    # --------------------------------------------------------------
    # Transición: aplicar el toque del jugador
    # --------------------------------------------------------------
    def _avanzar(self, ronda, indice):
        elegido = ronda["opciones"][indice]
        if self.f == 1:
            self.I.append(elegido)
            C = platos_compatibles(self.I)
            if len(C) == 1 and set(self.I) == set(PLATOS[C[0]]["ingredientes"]):
                self.d = C[0]
                self.f = 2
                self.k = 0
        elif self.f == 2:
            self.k += 1
            if self.k == len(PLATOS[self.d]["pasos"]):
                self.f = 3
                self.hechos = set()
        else:
            self.hechos.add(ronda["refs"][indice])
            if len(self.hechos) == len(PLATOS[self.d]["pasos"]):
                self.victoria = True

    def paso(self, ronda, accion, indice, tiempo):
        """Aplica la acción del agente y el toque del jugador.
        Devuelve (recompensa, info)."""
        r = 0.0
        if accion != 0:
            r += COSTO_PISTA[accion]
            self.h += 1
            self.ayudas += 1
            if accion == self.ultima_accion:
                r += R_REPETIR
        self.ultima_accion = accion
        self.t = "lento" if tiempo > UMBRAL_LENTO else "rapido"

        acierto = indice in ronda["correctas"]
        tipo = None
        fase_antes = self.f
        if acierto:
            r += R_SIN_AYUDA if accion == 0 else R_CON_AYUDA
            self.e = 0
            self.h = 0
            self._avanzar(ronda, indice)
        else:
            self.e += 1
            self.errores += 1
            tipo = self._tipo_error(ronda, indice)
            self.u = tipo
            if self.e >= 2 and self.h >= 2:
                r += R_FRUSTRACION

        self.turno += 1
        if self.victoria:
            r += R_PLATO
            self.terminado = True
        elif self.turno >= MAX_TURNOS:
            self.terminado = True

        info = {"acierto": acierto, "tipo_error": tipo,
                "elegido": texto(ronda["opciones"][indice]),
                "respuesta_npc": "[SÍ]" if acierto else "[NO]",
                "cambio_fase": self.f != fase_antes}
        return r, info

    def solucion(self):
        """Texto con la receta en un orden válido (se muestra al terminar)."""
        plato = self.d
        if plato is None:
            C = platos_compatibles(self.I)
            plato = C[0]
        pasos = PLATOS[plato]["pasos"]
        return PLATOS[plato]["nombre"] + ": " + " -> ".join(texto(pasos[i]) for i in astar_plan(plato))
