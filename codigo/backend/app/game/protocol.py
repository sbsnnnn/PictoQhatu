"""Contrato del WebSocket /ws/{sala}. Espejo a mano: frontend/src/lib/protocol.ts.

El front solo envía intenciones (join, tap, help, answer); el servidor es
autoritativo y responde con lo que hay que dibujar y decir.
"""

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter

Seat = Literal["cliente", "vendedor"]

# Códigos de cierre del WebSocket (el cliente no reintenta con ninguno de los dos)
CIERRE_SALA_OCUPADA = 4002      # otro jugador ya tiene la sala (no 1008: un proxy también lo usa)
CIERRE_REEMPLAZADA = 4001       # el mismo asiento se abrió en otra pestaña o dispositivo
Fase = Literal[1, 2, 3]


class _Mensaje(BaseModel):
    model_config = ConfigDict(extra="forbid")


# ------------------------------------------------------------------
# Tipos compartidos
# ------------------------------------------------------------------
class Picto(_Mensaje):
    id: str                     # "pan", "CORTAR", "sandwich", "SI"
    label: str                  # "PAN" (MAYÚSCULAS, estilo ARASAAC)
    img: str                    # "/pictos/pan.png"


class Option(_Mensaje):
    id: str                     # "pan" | "MEZCLAR" | "CORTAR:manzana" (único en la ronda)
    label: str                  # "CORTAR MANZANA"
    pictos: list[Picto]         # 1 o 2 pictogramas


class Atributo(_Mensaje):
    name: Literal["color", "categoria"]
    value: str                  # "rojo", "fruta"


class Hint(_Mensaje):
    """Ayuda a1–a5 del agente; el front solo la dibuja. a0 = hint null."""
    action: Literal["a1", "a2", "a3", "a4", "a5"]
    kind: Literal["repetir", "resaltar", "reducir", "mostrar", "atributo"]
    target: str | None = None   # option_id a resaltar (a2) o mostrar (a4)
    speech: str = ""            # texto para TTS (a1: el prompt; a5: "Es una FRUTA")
    attribute: Atributo | None = None


class Summary(_Mensaje):
    turnos: int
    ayudas: int
    errores: int
    plato: Picto
    solucion: list[Option] = []  # solo si victory=false: se muestra con amabilidad


# ------------------------------------------------------------------
# Cliente -> servidor
# ------------------------------------------------------------------
class Join(_Mensaje):
    type: Literal["join"]
    alias: str = Field(default="", max_length=20)   # opcional: el nombre no es obligatorio
    avatar: str                 # id de un ingrediente
    seat_token: str | None = None


class Tap(_Mensaje):
    type: Literal["tap"]
    option_id: str              # id, no índice: a3 cambia las opciones en vuelo
    ms: int = Field(ge=0)       # el servidor lo limita a 600000


class Help(_Mensaje):
    type: Literal["help"]


class Answer(_Mensaje):
    type: Literal["answer"]
    value: Literal["SI", "NO"]


MensajeCliente = Annotated[Join | Tap | Help | Answer, Field(discriminator="type")]
mensaje_cliente = TypeAdapter(MensajeCliente)   # mensaje_cliente.validate_json(texto)


# ------------------------------------------------------------------
# Servidor -> cliente
# ------------------------------------------------------------------
class Joined(_Mensaje):
    type: Literal["joined"] = "joined"
    seat: Seat
    seat_token: str


class Round(_Mensaje):
    type: Literal["round"] = "round"
    seat: Seat
    phase: Fase
    turn: int                   # turno del tramo actual (0..29)
    prompt: list[Picto]         # F1 [QUIERO, ?] | F2 [PONER, PAN] | F3 [PREPARAR, plato]
    options: list[Option]
    hint: Hint | None = None


class Feedback(_Mensaje):
    type: Literal["feedback"] = "feedback"
    ok: bool
    npc: list[Picto]            # [SI] o [NO]
    option_id: str | None = None


class Confirm(_Mensaje):
    """[¿QUIERES] + [PLATO]? al cerrar el Modo A; se responde con Answer."""
    type: Literal["confirm"] = "confirm"
    prompt: list[Picto]


class RoleSwap(_Mensaje):
    type: Literal["role_swap"] = "role_swap"
    seat: Seat                  # asiento nuevo del jugador
    order: list[Picto]          # lo que pide la IA clienta: [QUIERO, plato del Modo B]


class PhaseChange(_Mensaje):
    type: Literal["phase_change"] = "phase_change"
    phase: Fase


class GameOver(_Mensaje):
    type: Literal["game_over"] = "game_over"
    victory: bool
    summary: Summary


class Error(_Mensaje):
    """Mensaje inválido del cliente. Nunca se muestra como fracaso."""
    type: Literal["error"] = "error"
    message: str


MensajeServidor = Annotated[
    Joined | Round | Feedback | Confirm | RoleSwap | PhaseChange | GameOver | Error,
    Field(discriminator="type"),
]
