"""Salas en memoria (un proceso). Solitario = 1 humano + IA."""

import random
import uuid
from dataclasses import dataclass

from backend.app.game.protocol import Joined
from backend.app.game.session import GameSession


class SalaOcupada(Exception):
    """La sala ya tiene un humano y el seat_token no coincide."""


@dataclass
class Sala:
    sesion: GameSession
    token: str
    conexion: object = None     # WebSocket que maneja el asiento ahora: gana la última


class RoomManager:

    def __init__(self, agente):
        self.agente = agente
        # shortcut: salas sin expiración, limpiar en el Hito 3
        self.salas: dict[str, Sala] = {}

    def join(self, sala_id: str, token: str | None):
        """Devuelve (sala, mensajes). Token válido = reconexión: reenvía lo último pendiente."""
        sala = self.salas.get(sala_id)
        if sala is None:
            sala = Sala(GameSession(self.agente, random.Random()), str(uuid.uuid4()))
            self.salas[sala_id] = sala
            return sala, [Joined(seat=sala.sesion.seat, seat_token=sala.token)] + sala.sesion.start_round()
        if token != sala.token:
            raise SalaOcupada
        return sala, [Joined(seat=sala.sesion.seat, seat_token=sala.token), sala.sesion.ultimo]
