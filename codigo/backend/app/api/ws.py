"""WebSocket /ws/{sala}: valida intenciones del cliente y responde con mensajes del protocolo."""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import ValidationError

from backend.app.game.protocol import Answer, Error, Help, Join, Tap, mensaje_cliente
from backend.app.game.rooms import SalaOcupada

router = APIRouter()


async def _enviar(ws: WebSocket, msgs):
    for msg in msgs:
        await ws.send_json(msg.model_dump(mode="json"))


@router.websocket("/ws/{sala_id}")
async def ws_sala(ws: WebSocket, sala_id: str):
    await ws.accept()
    rooms = ws.app.state.rooms
    sesion = None
    try:
        while True:
            try:
                msg = mensaje_cliente.validate_json(await ws.receive_text())
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
                        await ws.close(code=1008)
                        return
                    sesion = sala.sesion
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
