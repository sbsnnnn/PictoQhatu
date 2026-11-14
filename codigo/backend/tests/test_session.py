import random

import numpy as np

from backend.app.game.protocol import (
    Confirm,
    Error,
    Feedback,
    GameOver,
    PhaseChange,
    RoleSwap,
    Round,
)
from backend.app.game.session import GameSession, cargar_agente, option_id
from ia_models.agent.regla_fija import AgenteReglaFija
from ia_models.env.catalogo import PLATOS


class AgenteStub:
    """Siempre elige `a`; su tabla Q prefiere `mejor` cuando se pide ayuda."""

    def __init__(self, a=0, mejor=3):
        self.a = a
        self.q = np.zeros((162, 6))
        self.q[:, mejor] = 1.0

    def elegir(self, s, explorar=False):
        return self.a


def ids(ronda_msg):
    return [o.id for o in ronda_msg.options]


def correcta(sesion):
    r = sesion.ronda
    return option_id(r["opciones"][min(r["correctas"])])


def incorrecta(sesion):
    r = sesion.ronda
    malas = [i for i in range(len(r["opciones"])) if i not in r["correctas"]]
    return option_id(r["opciones"][(malas or sorted(r["correctas"]))[0]])


def jugar(sesion, elegir, respuesta="SI", max_msgs=500):
    """Juega hasta game_over; devuelve todos los mensajes emitidos."""
    msgs = sesion.start_round()
    todos = list(msgs)
    while not isinstance(msgs[-1], GameOver):
        assert len(todos) < max_msgs
        if isinstance(msgs[-1], Confirm):
            msgs = sesion.answer(respuesta() if callable(respuesta) else respuesta)
        else:
            msgs = sesion.submit(elegir(sesion), 1500)
        todos += msgs
    return todos


def test_partida_a_confirm_b_hasta_victoria():
    sesion = GameSession(AgenteReglaFija(), random.Random(1))
    todos = jugar(sesion, correcta)

    tipos = [type(m) for m in todos]
    assert tipos.index(Confirm) < tipos.index(RoleSwap) < tipos.index(PhaseChange) < tipos.index(GameOver)
    confirm = next(m for m in todos if isinstance(m, Confirm))
    assert confirm.prompt[0].id == "QUIERO" and confirm.prompt[1].id in PLATOS
    swap = tipos.index(RoleSwap)
    assert todos[swap].seat == "vendedor"
    assert all(m.seat == "cliente" and m.phase == 1 for m in todos[:swap] if isinstance(m, Round))
    primera_b = todos[swap + 1]
    assert isinstance(primera_b, Round) and primera_b.seat == "vendedor" and primera_b.phase == 2
    paso0 = PLATOS[sesion.env.d]["pasos"][0]
    assert [p.id for p in primera_b.prompt] == [x for x in paso0 if x is not None]
    fin = todos[-1]
    assert fin.victory and fin.summary.solucion == [] and fin.summary.plato.id == sesion.env.d
    assert fin.summary.turnos == sum(isinstance(m, Feedback) and m.option_id is not None for m in todos)
    assert fin.summary.errores == 0


def test_no_reinicia_a_sin_contar_error():
    sesion = GameSession(AgenteReglaFija(), random.Random(2))
    respuestas = iter(["NO", "SI"])
    todos = jugar(sesion, correcta, respuesta=lambda: next(respuestas))

    i = next(i for i, m in enumerate(todos) if isinstance(m, Confirm))
    fb, ronda = todos[i + 1], todos[i + 2]
    assert isinstance(fb, Feedback) and fb.ok and fb.npc[0].id == "SI" and fb.option_id is None
    assert isinstance(ronda, Round) and ronda.phase == 1 and ronda.turn == 0 and ronda.seat == "cliente"
    assert sum(isinstance(m, Confirm) for m in todos) == 2
    fin = todos[-1]
    assert fin.victory and fin.summary.errores == 0
    assert fin.summary.turnos == sum(isinstance(m, Feedback) and m.option_id is not None for m in todos)


def test_help_conserva_opciones_y_resalta():
    sesion = GameSession(AgenteStub(a=0, mejor=2), random.Random(3))
    antes = sesion.start_round()[-1]
    despues = sesion.help()[-1]
    assert antes.hint is None
    assert ids(antes) == ids(despues)
    assert despues.hint.action == "a2" and despues.hint.kind == "resaltar"
    assert despues.hint.target in ids(despues)


def test_help_a3_deja_dos_opciones_de_las_mismas():
    sesion = GameSession(AgenteStub(a=0, mejor=3), random.Random(4))
    antes = sesion.start_round()[-1]
    despues = sesion.help()[-1]
    assert despues.hint.action == "a3" and despues.hint.kind == "reducir"
    assert len(despues.options) == 2 and set(ids(despues)) <= set(ids(antes))


def test_help_excluye_la_accion_actual():
    sesion = GameSession(AgenteStub(a=3, mejor=3), random.Random(5))
    sesion.start_round()
    assert sesion.help()[-1].hint.action == "a1"     # empate en 0 -> menor índice distinto de 3


def test_help_con_regla_fija_avanza_a_la_siguiente():
    sesion = GameSession(AgenteReglaFija(), random.Random(5))
    sesion.start_round()
    assert sesion.help()[-1].hint.action == "a1"
    assert sesion.help()[-1].hint.action == "a2"


def test_30_turnos_por_tramo_sin_victoria_muestra_solucion():
    sesion = GameSession(AgenteReglaFija(), random.Random(6))
    todos = jugar(sesion, incorrecta)
    fin = todos[-1]
    assert not fin.victory
    plato = fin.summary.plato.id
    assert len(fin.summary.solucion) == len(PLATOS[plato]["pasos"])
    assert sesion.env.turno == 30
    assert fin.summary.errores >= 30


def test_tap_con_id_inexistente_se_ignora():
    sesion = GameSession(AgenteReglaFija(), random.Random(7))
    sesion.start_round()
    assert sesion.submit("no-existe", 100) == []
    assert sesion.env.turno == 0


def test_mensajes_fuera_de_lugar_dan_error():
    sesion = GameSession(AgenteReglaFija(), random.Random(8))
    sesion.start_round()
    assert isinstance(sesion.answer("SI")[0], Error)              # answer sin confirm
    msgs = sesion.submit(correcta(sesion), 1000)
    while not isinstance(msgs[-1], Confirm):
        msgs = sesion.submit(correcta(sesion), 1000)
    assert isinstance(sesion.submit("pan", 1000)[0], Error)       # tap durante confirm
    assert isinstance(sesion.help()[0], Error)                    # help durante confirm
    msgs = sesion.answer("SI")
    while not isinstance(msgs[-1], GameOver):
        msgs = sesion.submit(correcta(sesion), 1000)
    for respuesta in (sesion.submit("pan", 1), sesion.help(), sesion.answer("NO")):
        assert isinstance(respuesta[0], Error)                    # tras game_over
    assert isinstance(sesion.ultimo, GameOver)


def test_hint_a5_dice_atributo_o_repite():
    sesion = GameSession(AgenteStub(a=5), random.Random(9))
    hint = sesion.start_round()[-1].hint
    assert hint.action == "a5"
    if hint.kind == "atributo":
        assert hint.speech.startswith("Es ") and hint.attribute is not None
    else:
        assert hint.kind == "repetir" and hint.speech


def test_sin_tabla_q_usa_regla_fija(tmp_path):
    assert isinstance(cargar_agente(tmp_path / "no_hay.npy"), AgenteReglaFija)
