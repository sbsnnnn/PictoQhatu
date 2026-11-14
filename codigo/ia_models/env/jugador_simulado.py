"""
jugador_simulado.py
-------------------
Jugadores simulados para entrenar y evaluar al agente (sección 2.4).

  - rapido:    acierta el 90 % y responde rápido.
  - distraido: acierta el 50 % y responde lento.
  - confunde:  "confunde colores": acierta el 40 % cuando en pantalla hay
               otro ingrediente del mismo color, y el 85 % en el resto.

Efecto de las ayudas del agente (valores iniciales, a calibrar):
  a1 repetir por voz : +0.25 al distraído, +0.05 al resto
  a2 resaltar        : reduce el error en 60 %
  a3 reducir opciones: quedan menos opciones incorrectas
  a4 mostrar         : acierta el 98 %
  a5 pista atributo  : el jugador solo mira las opciones con ese atributo.
                       Si la pista quita el ingrediente del mismo color,
                       el que confunde colores vuelve a acertar el 85 %.
"""

import random

from ia_models.env.catalogo import PLATOS, atributo

PERFILES = {
    "rapido":    {"nombre": "Rápido",           "acierto": 0.90, "tiempo": (2.0, 0.5)},
    "distraido": {"nombre": "Distraído",        "acierto": 0.50, "tiempo": (6.0, 1.5)},
    "confunde":  {"nombre": "Confunde colores", "acierto": 0.85, "acierto_mismo_color": 0.40,
                  "tiempo": (3.0, 1.0)},
}


class JugadorSimulado:

    def __init__(self, perfil, rng=None):
        self.perfil = perfil
        self.datos = PERFILES[perfil]
        self.rng = rng if rng is not None else random.Random()
        self.plato_deseado = None

    def nueva_partida(self):
        """En la Fase 1 el jugador "piensa" en un plato."""
        self.plato_deseado = self.rng.choice(list(PLATOS))

    def _elegir_meta(self, ronda, accion, buenos):
        """Qué opción correcta intenta tocar el jugador."""
        objetivo = ronda["objetivo"]
        if accion in (2, 4) and objetivo in buenos:      # sigue lo que el agente resalta o muestra
            return objetivo
        if ronda["fase"] == 1:
            if self.plato_deseado not in ronda["compatibles"]:   # cambia de idea
                self.plato_deseado = self.rng.choice(ronda["compatibles"])
            ingredientes = PLATOS[self.plato_deseado]["ingredientes"]
            preferidos = [i for i in buenos if ronda["opciones"][i] in ingredientes]
            if preferidos:
                return self.rng.choice(preferidos)
        if ronda["fase"] == 3 and buenos:                # cualquier paso válido
            return self.rng.choice(buenos)
        if objetivo in buenos or not buenos:
            return objetivo
        return self.rng.choice(buenos)

    def responder(self, ronda, accion):
        """Devuelve (índice de la opción tocada, tiempo en segundos)."""
        opciones = ronda["opciones"]
        candidatos = list(range(len(opciones)))

        # a5: solo mira las opciones que cumplen la pista ("es una FRUTA")
        if ronda.get("pista_atributo"):
            nombre, valor = ronda["pista_atributo"]
            candidatos = [i for i in candidatos if atributo(opciones[i], nombre) == valor]

        buenos = [i for i in candidatos if i in ronda["correctas"]]
        malos = [i for i in candidatos if i not in ronda["correctas"]]
        meta = self._elegir_meta(ronda, accion, buenos)

        color_meta = atributo(opciones[meta], "color")
        mismo_color = [i for i in malos
                       if color_meta is not None and atributo(opciones[i], "color") == color_meta]
        confusion_color = self.perfil == "confunde" and len(mismo_color) > 0

        # Probabilidad de acierto
        if accion == 4:
            p_error = 0.02
        else:
            p = self.datos["acierto"]
            if confusion_color:
                p = self.datos["acierto_mismo_color"]
            if accion == 1:
                p += 0.25 if self.perfil == "distraido" else 0.05
            if accion == 2:
                p += (1 - p) * 0.6
            p = min(p, 0.98)
            if confusion_color:
                p_error = 1 - p
            else:
                # con menos opciones incorrectas en pantalla, hay menos errores
                p_error = (1 - p) * min(1.0, len(malos) / 3)

        if malos and self.rng.random() < p_error:
            if confusion_color:
                indice = self.rng.choice(mismo_color)
            else:
                indice = self.rng.choice(malos)
        else:
            indice = meta

        media, desviacion = self.datos["tiempo"]
        tiempo = round(max(0.5, self.rng.gauss(media, desviacion)), 1)
        return indice, tiempo
