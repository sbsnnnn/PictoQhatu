"""descargar_arasaac.py sin red: la búsqueda y la descarga se reemplazan por funciones falsas."""

import json

from ia_models.env import descargar_arasaac as da

PICTOS = {
    "ingredientes": {
        "naranja": {"etiqueta": "NARANJA", "arasaac_id": None, "img": "/pictos/naranja.png"},
        "palta": {"etiqueta": "PALTA", "arasaac_id": None, "img": "/pictos/palta.png"},
        "pan": {"etiqueta": "PAN", "arasaac_id": 999, "img": "/pictos/pan.png"},
    },
    "control": {
        "SI": {"etiqueta": "SÍ", "arasaac_id": None, "img": "/pictos/si.png"},
    },
}


def test_elegir_id():
    buscados = []

    def buscar(termino):
        buscados.append(termino)
        return [{"_id": 10}, {"_id": 11}]

    assert da.elegir_id("pan", PICTOS["ingredientes"]["pan"], buscar) == 999      # fijado a mano
    assert da.elegir_id("naranja", PICTOS["ingredientes"]["naranja"], buscar) == 2483  # fruta, no color
    assert da.elegir_id("palta", PICTOS["ingredientes"]["palta"], buscar) == 10    # primer resultado
    assert da.elegir_id("SI", PICTOS["control"]["SI"], buscar) == 10
    assert buscados == ["aguacate", "sí"]


def test_descargar_todo_es_idempotente(tmp_path):
    ruta = tmp_path / "pictos.json"
    ruta.write_text(json.dumps(PICTOS, ensure_ascii=False, indent=2), encoding="utf-8")
    (tmp_path / "pan.png").write_bytes(b"ya estaba")
    bajados = []

    def bajar(id_):
        bajados.append(id_)
        return b"png"

    def buscar(termino):
        return [{"_id": 7}]

    da.descargar_todo(ruta, tmp_path, buscar=buscar, bajar=bajar)
    assert sorted(bajados) == [7, 7, 2483]                    # pan no se re-descarga
    assert (tmp_path / "pan.png").read_bytes() == b"ya estaba"
    assert (tmp_path / "si.png").read_bytes() == b"png"

    datos = json.loads(ruta.read_text(encoding="utf-8"))
    assert list(datos["ingredientes"]) == ["naranja", "palta", "pan"]     # orden intacto
    assert list(datos["ingredientes"]["pan"]) == ["etiqueta", "arasaac_id", "img"]
    assert datos["ingredientes"]["palta"]["arasaac_id"] == 7
    assert datos["control"]["SI"]["etiqueta"] == "SÍ"

    bajados.clear()
    da.descargar_todo(ruta, tmp_path, buscar=buscar, bajar=bajar)
    assert bajados == []
