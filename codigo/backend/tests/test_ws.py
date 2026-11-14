import json

import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from backend.app.game.protocol import CIERRE_REEMPLAZADA
from backend.app.game.session import option_id
from backend.app.main import create_app

JOIN = {"type": "join", "alias": "Ana", "avatar": "manzana"}
ESPERA = {"round", "confirm", "game_over"}     # mensajes tras los que el servidor espera al jugador


@pytest.fixture
def app():
    return create_app()


def hasta_espera(ws):
    """Lee mensajes hasta uno que pide una intención del jugador."""
    msgs = [ws.receive_json()]
    while msgs[-1]["type"] not in ESPERA:
        msgs.append(ws.receive_json())
    return msgs


def correcta(app, sala):
    r = app.state.rooms.salas[sala].sesion.ronda
    return option_id(r["opciones"][min(r["correctas"])])


def test_partida_completa_por_ws(app):
    with TestClient(app) as client, client.websocket_connect("/ws/sala1") as ws:
        ws.send_json(JOIN)
        joined = ws.receive_json()
        assert joined["type"] == "joined" and joined["seat"] == "cliente" and joined["seat_token"]
        msgs = hasta_espera(ws)
        tipos = []
        while msgs[-1]["type"] != "game_over":
            assert len(tipos) < 500
            if msgs[-1]["type"] == "confirm":
                ws.send_json({"type": "answer", "value": "SI"})
            else:
                ws.send_json({"type": "tap", "option_id": correcta(app, "sala1"), "ms": 2000})
            msgs = hasta_espera(ws)
            tipos += [m["type"] for m in msgs]
        assert "role_swap" in tipos and "phase_change" in tipos
        assert msgs[-1]["victory"] is True


def test_reconexion_con_seat_token_reenvia_la_ronda(app):
    with TestClient(app) as client:
        with client.websocket_connect("/ws/sala2") as ws:
            ws.send_json(JOIN)
            token = ws.receive_json()["seat_token"]
            ronda = ws.receive_json()
        with client.websocket_connect("/ws/sala2") as ws:
            ws.send_json({**JOIN, "seat_token": token})
            joined = ws.receive_json()
            assert joined == {"type": "joined", "seat": "cliente", "seat_token": token}
            assert ws.receive_json() == ronda


def test_json_invalido_da_error_y_sigue(app):
    with TestClient(app) as client, client.websocket_connect("/ws/sala3") as ws:
        ws.send_text("{no es json")
        assert ws.receive_json()["type"] == "error"
        ws.send_text(json.dumps({"type": "tap", "option_id": "pan", "ms": 1}))   # antes de join
        assert ws.receive_json()["type"] == "error"
        ws.send_json(JOIN)
        assert ws.receive_json()["type"] == "joined"


def test_segundo_humano_sin_token_recibe_error(app):
    with TestClient(app) as client:
        with client.websocket_connect("/ws/sala4") as ws:
            ws.send_json(JOIN)
            ws.receive_json()
        with client.websocket_connect("/ws/sala4") as ws:
            ws.send_json(JOIN)
            assert ws.receive_json()["type"] == "error"
            with pytest.raises(WebSocketDisconnect):
                ws.receive_json()


def test_la_ultima_conexion_con_el_token_reemplaza_a_la_anterior(app):
    with TestClient(app) as client, client.websocket_connect("/ws/sala5") as vieja:
        vieja.send_json(JOIN)
        token = vieja.receive_json()["seat_token"]
        ronda = vieja.receive_json()
        with client.websocket_connect("/ws/sala5") as nueva:
            nueva.send_json({**JOIN, "seat_token": token})
            assert nueva.receive_json()["type"] == "joined"
            assert nueva.receive_json() == ronda
            with pytest.raises(WebSocketDisconnect) as cierre:
                vieja.receive_json()
            assert cierre.value.code == CIERRE_REEMPLAZADA
            nueva.send_json({"type": "tap", "option_id": correcta(app, "sala5"), "ms": 1})
            assert nueva.receive_json()["type"] == "feedback"
