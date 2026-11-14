"""
agente_q.py
-----------
Modelo principal: Q-Learning (sección 2.4).

  Q(s, a) <- Q(s, a) + alfa * [ r + gamma * max_a' Q(s', a') - Q(s, a) ]

  Tabla Q: 162 estados x 6 acciones = 972 valores.
  alfa decreciente de 0.1 a 0.01, gamma = 0.9, epsilon decreciente de 1.0 a 0.05.

También incluye:
  - AgenteReglaFija: la ayuda del baseline (sin aprendizaje), para comparar.
  - jugar_partida(): el bucle percibir -> decidir -> responder de un turno.
  - entrenar(): entrenamiento offline con los tres jugadores simulados.
"""

import csv
import random
import numpy as np

from entorno import (EntornoPictoCocina, N_ESTADOS, N_ACCIONES, ACCIONES_AGENTE,
                     TIPOS_ERROR, VELOCIDADES, indice_estado, acciones_permitidas)
from jugador_simulado import JugadorSimulado, PERFILES


class AgenteQ:
    nombre = "Baseline + Q-Learning"

    def __init__(self, alfa=0.1, gamma=0.9, eps_inicial=1.0, eps_final=0.05,
                 alfa_final=0.01, semilla=0):
        self.q = np.zeros((N_ESTADOS, N_ACCIONES))
        self.alfa_inicial = alfa
        self.alfa_final = alfa_final
        self.alfa = alfa
        self.gamma = gamma
        self.eps_inicial = eps_inicial
        self.eps_final = eps_final
        self.epsilon = eps_inicial
        self.rng = random.Random(semilla)

    def elegir(self, s, explorar=False):
        """Epsilon-greedy: explora al azar o toma la mejor acción de la tabla."""
        permitidas = acciones_permitidas(s)
        if explorar and self.rng.random() < self.epsilon:
            return self.rng.choice(permitidas)
        fila = self.q[indice_estado(s)]
        return max(permitidas, key=lambda a: fila[a])   # en empate gana la de menor índice

    def actualizar(self, s, a, r, s2, terminado):
        """Regla de actualización de Q-Learning."""
        i = indice_estado(s)
        if terminado:
            objetivo = r
        else:
            fila2 = self.q[indice_estado(s2)]
            objetivo = r + self.gamma * max(fila2[b] for b in acciones_permitidas(s2))
        self.q[i, a] += self.alfa * (objetivo - self.q[i, a])


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


def jugar_partida(entorno, jugador, agente, aprender=False, mostrar=None):
    """Juega una partida completa. Devuelve un diccionario con métricas."""
    s = entorno.reiniciar()
    jugador.nueva_partida()
    total = 0.0
    while not entorno.terminado:
        a = agente.elegir(s, explorar=aprender)          # decidir
        ronda = entorno.nueva_ronda(a)                   # responder con pictogramas
        indice, tiempo = jugador.responder(ronda, a)     # percibir el toque
        r, info = entorno.paso(ronda, a, indice, tiempo)
        s2 = entorno.estado_reducido()
        if aprender:
            agente.actualizar(s, a, r, s2, entorno.terminado)
        if mostrar is not None:
            mostrar(entorno, s, a, ronda, indice, tiempo, r, info)
        total += r
        s = s2
    return {"victoria": entorno.victoria, "turnos": entorno.turno,
            "ayudas": entorno.ayudas, "errores": entorno.errores, "recompensa": total}


def entrenar(agente, episodios=30000, semilla=42):
    """Entrenamiento offline: alterna los tres perfiles simulados."""
    rng = random.Random(semilla)
    perfiles = list(PERFILES)
    victorias = 0
    for ep in range(episodios):
        # epsilon baja en línea recta de 1.0 a 0.05 durante el 80 % del entrenamiento,
        # y alfa baja de 0.1 a 0.01 para que la tabla Q se estabilice al final
        avance = min(1.0, ep / (0.8 * episodios))
        agente.epsilon = agente.eps_inicial - (agente.eps_inicial - agente.eps_final) * avance
        agente.alfa = agente.alfa_inicial - (agente.alfa_inicial - agente.alfa_final) * avance
        entorno = EntornoPictoCocina(rng)
        jugador = JugadorSimulado(perfiles[ep % len(perfiles)], rng)
        resultado = jugar_partida(entorno, jugador, agente, aprender=True)
        victorias += resultado["victoria"]
        if (ep + 1) % (episodios // 5) == 0:
            print(f"  Episodio {ep + 1:>6}/{episodios} | epsilon = {agente.epsilon:.2f} | "
                  f"victorias acumuladas = {victorias / (ep + 1):.1%}")
    agente.epsilon = 0.0
    return agente


def nombre_estado(i):
    """Texto del estado s' que corresponde a la fila i de la tabla Q."""
    for f in (1, 2, 3):
        for e in range(3):
            for h in range(3):
                for t in VELOCIDADES:
                    for u in TIPOS_ERROR:
                        s = (f, e, h, t, u)
                        if indice_estado(s) == i:
                            return s
    return None


def guardar_tabla_q(agente, ruta_csv, ruta_npy):
    """Exporta la tabla Q (162 x 6) en CSV legible y en .npy."""
    np.save(ruta_npy, agente.q)
    with open(ruta_csv, "w", newline="", encoding="utf-8") as archivo:
        escritor = csv.writer(archivo)
        escritor.writerow(["f", "e", "h", "t", "u"] + ACCIONES_AGENTE + ["mejor_accion"])
        for i in range(N_ESTADOS):
            s = nombre_estado(i)
            fila = [round(v, 3) for v in agente.q[i]]
            mejor = ACCIONES_AGENTE[agente.elegir(s)]
            escritor.writerow(list(s) + fila + [mejor])
