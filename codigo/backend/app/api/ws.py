"""WebSocket /ws/{sala}: valida intenciones del cliente y responde con mensajes del protocolo."""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import ValidationError

from backend.app.game.protocol import (
    CIERRE_REEMPLAZADA,
    CIERRE_SALA_OCUPADA,
    Answer,
    Error,
    Help,
    Join,
    Tap,
    mensaje_cliente,
)
from backend.app.game.rooms import SalaOcupada

router = APIRouter()


async def _enviar(ws: WebSocket, msgs):
    for msg in msgs:
        await ws.send_json(msg.model_dump(mode="json"))


async def _cerrar(ws: WebSocket, codigo: int):
    try:
        await ws.close(code=codigo)
    except Exception:            # se cerró justo ahora: no debe frenar el join de la nueva
        pass


@router.websocket("/ws/{sala_id}")
async def ws_sala(ws: WebSocket, sala_id: str):
    await ws.accept()
    rooms = ws.app.state.rooms
    sala = sesion = None
    try:
        while True:
            try:
                texto = await ws.receive_text()
                if sala is not None and sala.conexion is not ws:
                    return               # otra pestaña tomó el asiento: esta ya no juega
                msg = mensaje_cliente.validate_json(texto)
            except ValidationError:
                await _enviar(ws, [Error(message="Mensaje inválido")])
                continue
            if isinstance(msg, Join):
                if sesion is not None:
                    respuesta = [Error(message="Ya estás en la sala")]
                else:
                    try:
                        sala, respuesta = rooms.join(sala_id, msg.seat_token)
                    except SalaOcupada:
                        await _enviar(ws, [Error(message="La sala ya tiene un jugador")])
                        await ws.close(code=CIERRE_SALA_OCUPADA)
                        return
                    sesion = sala.sesion
                    anterior, sala.conexion = sala.conexion, ws
                    if anterior is not None:
                        await _cerrar(anterior, CIERRE_REEMPLAZADA)
            elif sesion is None:
                respuesta = [Error(message="Primero envía join")]
            elif isinstance(msg, Tap):
                respuesta = sesion.submit(msg.option_id, msg.ms)
            elif isinstance(msg, Help):
                respuesta = sesion.help()
            elif isinstance(msg, Answer):
                respuesta = sesion.answer(msg.value)
            await _enviar(ws, respuesta)
    except WebSocketDisconnect:
        pass                     # la sala sigue en memoria: el jugador puede volver con su seat_token
    finally:
        if sala is not None and sala.conexion is ws:
            sala.conexion = None     # asiento libre: la próxima conexión no cierra nada
