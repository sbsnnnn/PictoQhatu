"""
catalogo.py
-----------
Catálogo de PictoQhatu: 26 pictogramas (13 ingredientes, 5 platos,
5 acciones y 3 de control) y el banco de 5 platos (Tabla 2 y Tabla 3
del documento).

Los datos viven en JSON para que un educador pueda agregar platos:
  datos/catalogo/pictos.json      pictogramas (etiqueta, categoría, color, imagen)
  datos/escenarios/platos.json    platos (ingredientes, pasos, precedencias)

Cada ingrediente tiene dos atributos: categoría y color. Con ellos se
clasifican los errores (Tabla 4) y se da la pista a5.
"""

import json
from pathlib import Path

CARPETA_DATOS = Path(__file__).resolve().parents[3] / "datos"


def _leer(ruta):
    with open(CARPETA_DATOS / ruta, encoding="utf-8") as archivo:
        return json.load(archivo)   # json conserva el orden: decide desempates de ID3 y del RNG


_PICTOS = _leer("catalogo/pictos.json")

# ------------------------------------------------------------------
# 1. Ingredientes: nombre -> (categoría, color)
# ------------------------------------------------------------------
INGREDIENTES = {x: (p["categoria"], p["color"]) for x, p in _PICTOS["ingredientes"].items()}

# Nombre que se muestra en pantalla (y que diría la síntesis de voz)
ETIQUETAS = {x: p["etiqueta"] for x, p in _PICTOS["ingredientes"].items()}

# ------------------------------------------------------------------
# 2. Acciones y control (pictogramas que no son ingredientes)
# ------------------------------------------------------------------
ACCIONES = list(_PICTOS["acciones"])
CONTROL = list(_PICTOS["control"])

# Todos los pictogramas por id -> {"etiqueta", "img", ...} (lo usa el backend)
PICTOS = {id_: p for grupo in _PICTOS.values() for id_, p in grupo.items()}

# ------------------------------------------------------------------
# 3. Banco de platos (Tabla 3)
#    pasos: lista de (acción, ingrediente). MEZCLAR no lleva ingrediente.
#    precedencias: paso -> lista de pasos que deben hacerse antes.
#    En JSON los pasos son listas y las claves son texto: se vuelven tuplas
#    (texto() e ingrediente_de() distinguen la tarjeta de paso por ser tupla) e int.
# ------------------------------------------------------------------
PLATOS = {
    clave: {
        "nombre": p["nombre"],
        "nivel": p["nivel"],
        "ingredientes": p["ingredientes"],
        "pasos": [tuple(paso) for paso in p["pasos"]],
        "precedencias": {int(k): v for k, v in p["precedencias"].items()},
    }
    for clave, p in _leer("escenarios/platos.json").items()
}

# Artículo para decir la categoría en voz alta ("es una FRUTA")
FRASE_CATEGORIA = {
    "fruta": "una FRUTA", "verdura": "una VERDURA", "proteína": "una PROTEÍNA",
    "cereal": "un CEREAL", "lácteo": "un LÁCTEO",
}


# ------------------------------------------------------------------
# 4. Funciones de ayuda
#    Una "opción" en pantalla puede ser:
#      - un ingrediente        -> "manzana"
#      - una acción            -> "MEZCLAR"
#      - una tarjeta de paso   -> ("CORTAR", "manzana")  (Fase 3)
# ------------------------------------------------------------------
def ingrediente_de(opcion):
    """Devuelve el ingrediente de una opción, o None si no tiene."""
    if isinstance(opcion, tuple):
        return opcion[1]
    if opcion in INGREDIENTES:
        return opcion
    return None


def atributo(opcion, nombre_atributo):
    """Devuelve la categoría o el color de una opción (None si no tiene)."""
    ing = ingrediente_de(opcion)
    if ing is None:
        return None
    categoria, color = INGREDIENTES[ing]
    return categoria if nombre_atributo == "categoria" else color


def similitud(op1, op2):
    """Cuántos atributos comparten dos opciones (0, 1 o 2)."""
    total = 0
    for nombre in ("color", "categoria"):
        a, b = atributo(op1, nombre), atributo(op2, nombre)
        if a is not None and a == b:
            total += 1
    return total


def texto(opcion):
    """Texto en mayúsculas para mostrar una opción en consola."""
    if isinstance(opcion, tuple):
        accion, ing = opcion
        return accion if ing is None else accion + " " + ETIQUETAS[ing]
    if opcion in ETIQUETAS:
        return ETIQUETAS[opcion]
    return opcion


def verificar_catalogo():
    """Imprime el conteo de pictogramas (debe dar 26)."""
    n_ing, n_pla, n_acc, n_con = len(INGREDIENTES), len(PLATOS), len(ACCIONES), len(CONTROL)
    total = n_ing + n_pla + n_acc + n_con
    print(f"Ingredientes: {n_ing} | Platos: {n_pla} | Acciones: {n_acc} | Control: {n_con}")
    print(f"Total de pictogramas: {total}")
    for plato in PLATOS.values():
        pasos = " -> ".join(texto(p) for p in plato["pasos"])
        print(f"  Nivel {plato['nivel']} | {plato['nombre']:<19} | {pasos}")
    return total


if __name__ == "__main__":
    verificar_catalogo()
