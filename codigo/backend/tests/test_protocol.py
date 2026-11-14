import pytest
from pydantic import ValidationError

from backend.app.game.protocol import Hint, Join, Round, Tap, mensaje_cliente


def test_discrimina_mensajes_del_cliente():
    assert isinstance(mensaje_cliente.validate_json('{"type":"tap","option_id":"pan","ms":3400}'), Tap)
    assert isinstance(mensaje_cliente.validate_json('{"type":"join","alias":"Ana","avatar":"manzana"}'), Join)
    # el nombre es opcional en la pantalla de inicio (solo alias, Ley 29733)
    assert isinstance(mensaje_cliente.validate_json('{"type":"join","alias":"","avatar":"manzana"}'), Join)


@pytest.mark.parametrize("texto", [
    '{"type":"tap","option_id":"pan","ms":-1}',            # ms negativo
    '{"type":"answer","value":"QUIZAS"}',                  # solo SI / NO
    '{"type":"join","alias":"aaaaaaaaaaaaaaaaaaaaa","avatar":"pan"}',  # alias de más de 20
    '{"type":"help","extra":1}',                           # campos de más
    '{"type":"borrar_todo"}',                              # tipo desconocido
])
def test_rechaza_mensajes_invalidos(texto):
    with pytest.raises(ValidationError):
        mensaje_cliente.validate_json(texto)


def test_round_serializa_como_el_contrato():
    r = Round(seat="vendedor", phase=2, turn=0,
              prompt=[{"id": "PONER", "label": "PONER", "img": "/pictos/poner.png"}],
              options=[{"id": "pan", "label": "PAN",
                        "pictos": [{"id": "pan", "label": "PAN", "img": "/pictos/pan.png"}]}],
              hint=Hint(action="a2", kind="resaltar", target="pan"))
    d = r.model_dump()
    assert d["type"] == "round" and d["hint"]["target"] == "pan" and d["hint"]["attribute"] is None
