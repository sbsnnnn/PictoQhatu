"""
regla_fija.py
-------------
Ayuda del baseline sin aprendizaje, para comparar con Q-Learning.
Portado de agente_q.py del MVP.
"""


class AgenteReglaFija:
    """Ayuda del baseline: sin error no ayuda, con 1 error repite por voz,
    con 2 o más errores muestra la respuesta."""
    nombre = "Baseline (regla fija)"

    def elegir(self, s, explorar=False):
        e = s[1]
        if e == 0:
            return 0
        if e == 1:
            return 1
        return 4

    def actualizar(self, *args):
        pass
