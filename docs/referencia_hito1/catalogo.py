"""
catalogo.py
-----------
Catálogo de PictoCocina: 26 pictogramas (13 ingredientes, 5 platos,
5 acciones y 3 de control) y el banco de 5 platos (Tabla 2 y Tabla 3
del documento).

Cada ingrediente tiene dos atributos: categoría y color. Con ellos se
clasifican los errores (Tabla 4) y se da la pista a5.
"""

# ------------------------------------------------------------------
# 1. Ingredientes: nombre -> (categoría, color)
# ------------------------------------------------------------------
INGREDIENTES = {
    "pan":       ("cereal",   "marrón"),
    "pollo":     ("proteína", "marrón"),
    "lechuga":   ("verdura",  "verde"),
    "tomate":    ("verdura",  "rojo"),
    "zanahoria": ("verdura",  "naranja"),
    "palta":     ("fruta",    "verde"),
    "manzana":   ("fruta",    "rojo"),
    "platano":   ("fruta",    "amarillo"),
    "naranja":   ("fruta",    "naranja"),
    "huevo":     ("proteína", "blanco"),
    "leche":     ("lácteo",   "blanco"),
    "queso":     ("lácteo",   "amarillo"),
    "arroz":     ("cereal",   "blanco"),
}

# Nombre que se muestra en pantalla (y que diría la síntesis de voz)
ETIQUETAS = {
    "pan": "PAN", "pollo": "POLLO", "lechuga": "LECHUGA", "tomate": "TOMATE",
    "zanahoria": "ZANAHORIA", "palta": "PALTA", "manzana": "MANZANA",
    "platano": "PLÁTANO", "naranja": "NARANJA", "huevo": "HUEVO",
    "leche": "LECHE", "queso": "QUESO", "arroz": "ARROZ",
}

# ------------------------------------------------------------------
# 2. Acciones y control (pictogramas que no son ingredientes)
# ------------------------------------------------------------------
ACCIONES = ["QUIERO", "PREPARAR", "PONER", "CORTAR", "MEZCLAR"]
CONTROL = ["SÍ", "NO", "AYUDA"]

# ------------------------------------------------------------------
# 3. Banco de platos (Tabla 3)
#    pasos: lista de (acción, ingrediente). MEZCLAR no lleva ingrediente.
#    precedencias: paso -> lista de pasos que deben hacerse antes.
#      - Ensaladas y arroz con pollo: los pasos de ingredientes en
#        cualquier orden, y el último paso al final.
#      - Sándwich y desayuno: orden fijo.
# ------------------------------------------------------------------
PLATOS = {
    "ensalada_frutas": {
        "nombre": "Ensalada de frutas",
        "nivel": 1,
        "ingredientes": ["manzana", "platano", "naranja"],
        "pasos": [("CORTAR", "manzana"), ("CORTAR", "platano"),
                  ("CORTAR", "naranja"), ("MEZCLAR", None)],
        "precedencias": {3: [0, 1, 2]},
    },
    "arroz_con_pollo": {
        "nombre": "Arroz con pollo",
        "nivel": 1,
        "ingredientes": ["arroz", "pollo", "zanahoria"],
        "pasos": [("PONER", "arroz"), ("PONER", "pollo"),
                  ("PONER", "zanahoria"), ("MEZCLAR", None)],
        "precedencias": {3: [0, 1, 2]},
    },
    "sandwich": {
        "nombre": "Sándwich",
        "nivel": 2,
        "ingredientes": ["pan", "pollo", "lechuga", "tomate"],
        "pasos": [("PONER", "pan"), ("PONER", "pollo"),
                  ("PONER", "lechuga"), ("PONER", "tomate")],
        "precedencias": {1: [0], 2: [1], 3: [2]},
    },
    "ensalada": {
        "nombre": "Ensalada",
        "nivel": 2,
        "ingredientes": ["lechuga", "tomate", "zanahoria", "palta"],
        "pasos": [("CORTAR", "lechuga"), ("CORTAR", "tomate"),
                  ("CORTAR", "zanahoria"), ("PONER", "palta")],
        "precedencias": {3: [0, 1, 2]},
    },
    "desayuno": {
        "nombre": "Desayuno",
        "nivel": 2,
        "ingredientes": ["pan", "queso", "huevo", "leche"],
        "pasos": [("PONER", "pan"), ("PONER", "queso"),
                  ("PONER", "huevo"), ("PONER", "leche")],
        "precedencias": {1: [0], 2: [1], 3: [2]},
    },
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
    for clave, plato in PLATOS.items():
        pasos = " -> ".join(texto(p) for p in plato["pasos"])
        print(f"  Nivel {plato['nivel']} | {plato['nombre']:<19} | {pasos}")
    return total


if __name__ == "__main__":
    verificar_catalogo()
