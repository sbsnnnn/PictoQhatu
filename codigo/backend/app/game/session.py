"""GameSession: el bucle pull del MVP (jugar_partida) partido en eventos (CLAUDE §10).

El entorno es el del MVP, intacto. Cada método recibe una intención del jugador
y devuelve la lista de mensajes del protocolo que hay que enviar.
"""

import logging
import random
from pathlib import Path

import numpy as np

from backend.app.game.protocol import (
    Atributo,
    Confirm,
    Error,
    Feedback,
    GameOver,
    Hint,
    Option,
    PhaseChange,
    Picto,
    RoleSwap,
    Round,
    Summary,
)
from ia_models.agent.astar import astar_plan
from ia_models.agent.id3 import platos_compatibles
from ia_models.agent.q_learning import AgenteQ
from ia_models.agent.regla_fija import AgenteReglaFija
from ia_models.env.catalogo import FRASE_CATEGORIA, PICTOS, PLATOS, texto
from ia_models.env.entorno import EntornoPictoCocina, indice_estado

log = logging.getLogger(__name__)

TRAMOS = [("A", "cliente"), ("B", "vendedor")]   # B→A queda para el Hito 3: agregar aquí
MAX_MS = 600_000
HUECO = Picto(id="?", label="?", img="")        # casilla vacía de [QUIERO] + [ ? ]
TIPO_HINT = {1: "repetir", 2: "resaltar", 3: "reducir", 4: "mostrar", 5: "atributo"}


def cargar_agente(ruta: Path):
    """Tabla Q de solo lectura (epsilon = 0); sin archivo, la regla fija."""
    if not Path(ruta).exists():
        log.warning("No existe %s: se usa AgenteReglaFija", ruta)
        return AgenteReglaFija()
    agente = AgenteQ()
    agente.q = np.load(ruta)
    agente.epsilon = 0.0
    return agente


def picto(id_: str) -> Picto:
    p = PICTOS[id_]
    return Picto(id=id_, label=p["etiqueta"], img=p["img"])


def option_id(op) -> str:
    """"pan" | "MEZCLAR" | "CORTAR:manzana" (tarjeta de paso)."""
    if isinstance(op, tuple):
        accion, ing = op
        return accion if ing is None else f"{accion}:{ing}"
    return op


def a_option(op) -> Option:
    ids = [x for x in op if x is not None] if isinstance(op, tuple) else [op]
    return Option(id=option_id(op), label=texto(op), pictos=[picto(x) for x in ids])


def _entorno_modo_b(rng, plato):
    """Entorno que arranca en la Fase 2 con `plato`: lo mismo que fija _avanzar al salir de la Fase 1."""
    env = EntornoPictoCocina(rng)
    env.f, env.d, env.k = 2, plato, 0
    return env


class GameSession:

    def __init__(self, agente, rng: random.Random):
        self.agente = agente
        self.rng = rng
        self.tramo = 0
        self.env = EntornoPictoCocina(rng)
        self.estado = "ronda"            # "ronda" | "confirm" | "fin"
        self.ronda = None
        self.a = 0
        self.ultimo = None               # último Round / Confirm / GameOver (reconexión)
        self._totales = [0, 0, 0]        # turnos, ayudas, errores de los entornos ya cerrados
        self._rng_estado = None

    @property
    def seat(self):
        return TRAMOS[self.tramo][1]

    # --------------------------------------------------------------
    # Eventos
    # --------------------------------------------------------------
    def start_round(self):
        self.a = self.agente.elegir(self.env.estado_reducido())
        self._rng_estado = self.rng.getstate()     # foto: help() rearma el mismo tablero
        self.ronda = self.env.nueva_ronda(self.a)
        return [self._round()]

    def help(self):
        if self.estado != "ronda":
            return [Error(message="Ahora no se puede pedir ayuda")]
        self.a = self._mejor_ayuda()
        self.rng.setstate(self._rng_estado)        # solo _ronda_faseX consume RNG
        self.ronda = self.env.nueva_ronda(self.a)
        return [self._round()]

    def submit(self, opcion: str, ms: int):
        if self.estado != "ronda":
            return [Error(message="Ahora no se puede tocar una opción")]
        ids = [option_id(op) for op in self.ronda["opciones"]]
        if opcion not in ids:
            return []                              # toque cruzado con una ronda vieja (a3)
        ms = min(max(ms, 0), MAX_MS)
        _, info = self.env.paso(self.ronda, self.a, ids.index(opcion), ms / 1000)
        msgs = [Feedback(ok=info["acierto"], npc=[picto("SI" if info["acierto"] else "NO")],
                         option_id=opcion)]
        env = self.env
        if TRAMOS[self.tramo][0] == "A":
            if info["cambio_fase"] and env.f == 2:
                return msgs + self._confirmar(env.d)
            if env.terminado:
                return msgs + self._confirmar(platos_compatibles(env.I)[0])
        elif env.terminado:
            return msgs + [self._game_over()]
        elif info["cambio_fase"]:
            msgs.append(PhaseChange(phase=env.f))
        return msgs + self.start_round()

    def answer(self, valor: str):
        if self.estado != "confirm":
            return [Error(message="No hay ninguna pregunta pendiente")]
        self.estado = "ronda"
        if valor == "SI":
            self.tramo += 1
            self.env = _entorno_modo_b(self.rng, self.rng.choice(list(PLATOS)))
            return [RoleSwap(seat=self.seat)] + self.start_round()
        self.env = EntornoPictoCocina(self.rng)    # [NO]: el pedido se reinicia, no cuenta error
        return [Feedback(ok=True, npc=[picto("SI")])] + self.start_round()

    # --------------------------------------------------------------
    # Ayudas y cierre de tramos
    # --------------------------------------------------------------
    def _mejor_ayuda(self):
        """argmax Q[s] sobre a1..a5 sin la acción actual (empate: menor índice).
        Con la regla fija (sin tabla Q) pasa a la siguiente ayuda: a0->a1, a1->a2, ..., a5->a1."""
        candidatas = [a for a in range(1, 6) if a != self.a]
        q = getattr(self.agente, "q", None)
        if q is None:
            return self.a % 5 + 1
        fila = q[indice_estado(self.env.estado_reducido())]
        return max(candidatas, key=lambda a: fila[a])

    def _cerrar_entorno(self):
        env = self.env
        self._totales = [self._totales[0] + env.turno, self._totales[1] + env.ayudas,
                         self._totales[2] + env.errores]

    def _confirmar(self, plato):
        self._cerrar_entorno()
        self.estado = "confirm"
        self.ultimo = Confirm(prompt=[picto("QUIERO"), picto(plato)])
        return [self.ultimo]

    def _game_over(self):
        self._cerrar_entorno()
        self.estado = "fin"
        env, plato = self.env, self.env.d
        pasos = PLATOS[plato]["pasos"]
        solucion = [] if env.victoria else [a_option(pasos[i]) for i in astar_plan(plato)]
        turnos, ayudas, errores = self._totales
        self.ultimo = GameOver(victory=env.victoria, summary=Summary(
            turnos=turnos, ayudas=ayudas, errores=errores, plato=picto(plato), solucion=solucion))
        return self.ultimo

    # --------------------------------------------------------------
    # Entorno -> protocolo
    # --------------------------------------------------------------
    def _prompt(self):
        env = self.env
        if env.f == 1:
            return [picto("QUIERO"), HUECO]
        if env.f == 2:
            return [picto(x) for x in PLATOS[env.d]["pasos"][env.k] if x is not None]
        return [picto("PREPARAR"), picto(env.d)]

    def _hint(self, prompt):
        if self.a == 0:
            return None
        ronda, accion = self.ronda, f"a{self.a}"
        decir = " ".join(p.label for p in prompt if p is not HUECO)
        objetivo = option_id(ronda["opciones"][ronda["objetivo"]])
        if self.a in (2, 4):
            return Hint(action=accion, kind=TIPO_HINT[self.a], target=objetivo)
        if self.a == 5 and ronda["pista_atributo"] is not None:
            nombre, valor = ronda["pista_atributo"]
            frase = "Es de color " + valor.upper() if nombre == "color" else "Es " + FRASE_CATEGORIA[valor]
            return Hint(action=accion, kind="atributo", speech=frase,
                        attribute=Atributo(name=nombre, value=valor))
        if self.a == 3:
            return Hint(action=accion, kind="reducir")
        return Hint(action=accion, kind="repetir", speech=decir)   # a1, o a5 sin atributo útil

    def _round(self):
        prompt = self._prompt()
        self.ultimo = Round(seat=self.seat, phase=self.env.f, turn=self.env.turno, prompt=prompt,
                            options=[a_option(op) for op in self.ronda["opciones"]],
                            hint=self._hint(prompt))
        return self.ultimo
