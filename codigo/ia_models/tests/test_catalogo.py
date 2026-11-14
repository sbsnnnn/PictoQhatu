from ia_models.env.catalogo import PICTOS, PLATOS, texto, verificar_catalogo


def test_26_pictogramas():
    assert verificar_catalogo() == 26


def test_tipos_restaurados_desde_json():
    pasos = PLATOS["ensalada_frutas"]["pasos"]
    assert pasos[0] == ("CORTAR", "manzana") and pasos[3] == ("MEZCLAR", None)
    assert PLATOS["sandwich"]["precedencias"] == {1: [0], 2: [1], 3: [2]}
    assert texto(pasos[0]) == "CORTAR MANZANA"


def test_orden_del_mvp():
    assert list(PLATOS) == ["ensalada_frutas", "arroz_con_pollo", "sandwich", "ensalada", "desayuno"]


def test_todo_picto_tiene_imagen():
    assert all(p["img"].startswith("/pictos/") for p in PICTOS.values())
    assert PICTOS["SI"]["etiqueta"] == "SÍ"
