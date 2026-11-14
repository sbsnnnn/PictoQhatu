# Resumen del modelo (Hito 2)

Todos los números de este documento salen del código de `codigo/ia_models/` y de los archivos guardados en `datos/modelos/`. Cuando un dato no se guardó, se marca como **no disponible**.

## 1. Entorno

El agente decide qué ayuda dar en cada turno de una partida de cocina con pictogramas. La partida tiene tres fases (`codigo/ia_models/env/entorno.py`):

| Fase | Qué hace el jugador | Quién arma la pantalla |
|---|---|---|
| 1. Reunir ingredientes | Elige ingredientes hasta que solo queda un plato compatible | ID3 |
| 2. El pedido | Sigue los pasos que pide el NPC ([PONER] + [PAN]) | La receta del plato |
| 3. Armar el plato | Arma el plato solo, en un orden válido | A* |

- Catálogo (`datos/catalogo/pictos.json`): 13 ingredientes, 5 acciones, 3 pictos de control y 5 platos.
- Platos (`datos/escenarios/platos.json`): ensalada de frutas, arroz con pollo, sándwich, ensalada y desayuno. Todos tienen 4 ingredientes y 4 pasos.
- En pantalla hay 4 opciones (`N_OPCIONES = 4`).
- La partida termina con el plato armado o a los 30 turnos (`MAX_TURNOS = 30`).

## 2. Espacio de estados (162)

El estado completo es `s = (f, d, I, k, e, h, t, u)`. El agente solo ve el estado reducido `s' = (f, e, h, t, u)`:

| Dimensión | Valores | Qué representa |
|---|---|---|
| `f` | 1, 2, 3 | Fase de la partida |
| `e` | 0, 1, 2+ | Errores seguidos en el paso actual |
| `h` | 0, 1, 2+ | Ayudas dadas en el paso actual |
| `t` | rápido, lento | Tiempo de la última respuesta; lento si pasa de 4 s (`UMBRAL_LENTO`) |
| `u` | color, categoría, otro | Tipo del último error |

3 × 3 × 3 × 2 × 3 = **162 estados**. `indice_estado()` convierte cada `s'` en una fila de la tabla Q. El plato `d`, los ingredientes elegidos `I` y el paso `k` quedan fuera del estado del agente: los manejan ID3 y A*.

El tipo de error `u` se calcula comparando lo que tocó el jugador con la respuesta correcta más parecida. Si es de la misma categoría pero de otro color (tomate en vez de zanahoria), el error es de **color**. En los demás casos con ingrediente es de **categoría**. Un paso fuera de orden en la Fase 3, o una acción como MEZCLAR, cuenta como **otro**.

## 3. Acciones (6)

| Acción | Ayuda |
|---|---|
| a0 | Sin ayuda |
| a1 | Repetir el pedido por voz |
| a2 | Resaltar la respuesta |
| a3 | Reducir las opciones a dos: la respuesta y la incorrecta menos parecida |
| a4 | Mostrar la respuesta |
| a5 | Pista por atributo ("es de color ROJO", "es una FRUTA"). El atributo lo elige la ganancia de información de ID3 |

En la Fase 3, si el jugador no tiene errores (`e = 0`), la única acción permitida es a0 (`acciones_permitidas`). Así el jugador arma el plato solo hasta que se equivoca.

## 4. Función de recompensa

Valores en `entorno.py`, aplicados en `EntornoPictoCocina.paso()`:

| Evento | Recompensa |
|---|---|
| Acierto sin ayuda (a0) | +1.0 (`R_SIN_AYUDA`) |
| Acierto con ayuda | +0.5 (`R_CON_AYUDA`) |
| Plato terminado | +10.0 (`R_PLATO`) |
| Costo de la ayuda | a1 −0.1, a2 −0.2, a3 −0.3, a4 −0.6, a5 −0.2 (`COSTO_PISTA`) |
| Repetir la misma ayuda que en el turno anterior | −1.0 (`R_REPETIR`) |
| Frustración: error con `e ≥ 2` y `h ≥ 2` | −5.0 (`R_FRUSTRACION`) |

El costo de cada ayuda crece con lo que revela de la respuesta. Por eso a4 (mostrar) es la más cara: el agente debe aprender a dar la ayuda mínima que funcione.

## 5. Hiperparámetros

De `codigo/ia_models/agent/q_learning.py`:

| Parámetro | Valor |
|---|---|
| Regla | `Q(s,a) ← Q(s,a) + α [r + γ · max_a' Q(s',a') − Q(s,a)]` |
| Tabla Q | 162 × 6 = 972 valores, inicializada en cero |
| α (tasa de aprendizaje) | Baja en línea recta de 0.1 a 0.01 |
| γ (descuento) | 0.9 |
| ε (exploración, ε-greedy) | Baja en línea recta de 1.0 a 0.05 |
| Decaimiento | α y ε llegan a su valor final al 80 % del entrenamiento (episodio 24 000) y se quedan ahí |
| Episodios | 30 000 |
| Jugadores en el entrenamiento | Se alternan los tres perfiles simulados, uno por episodio |
| Semilla de entrenamiento | 42 |
| Evaluación | Política greedy (ε = 0), 100 partidas por perfil, semilla 2026 |

Perfiles simulados (`codigo/ia_models/env/jugador_simulado.py`):

| Perfil | Acierto base | Tiempo (media, desv.) |
|---|---|---|
| Rápido | 90 % | 2.0 s, 0.5 |
| Distraído | 50 % | 6.0 s, 1.5 |
| Confunde colores | 85 %, o 40 % si en pantalla hay otro ingrediente del mismo color | 3.0 s, 1.0 |

Efecto de las ayudas sobre el jugador: a1 suma +0.25 al distraído y +0.05 a los demás; a2 reduce el error en 60 %; a3 deja menos opciones incorrectas; a4 lleva el acierto a 98 %; a5 hace que el jugador mire solo las opciones con ese atributo. El código marca estos valores como iniciales, a calibrar.

## 6. Resultados: Q-Learning frente a la regla fija

La regla fija (`codigo/ia_models/agent/regla_fija.py`) no aprende: sin errores no ayuda, con 1 error repite por voz (a1) y con 2 o más muestra la respuesta (a4). Los dos agentes usan el mismo ID3 y el mismo A*; solo cambia cómo eligen la ayuda.

Fuente: `datos/modelos/metricas/baseline_vs_q.csv` (100 partidas por perfil). "Turnos" son los pasos promedio por partida.

| Perfil | Agente | Éxito | Turnos | Ayudas | Errores | Recompensa | Frustración (eventos) |
|---|---|---|---|---|---|---|---|
| Rápido | Regla fija | 100 % | 12.80 | 1.09 | 1.09 | 21.06 | 0 |
| Rápido | Q-Learning | 100 % | 12.83 | 0.72 | 1.12 | 21.21 | 0 |
| Distraído | Regla fija | 100 % | 17.54 | 5.83 | 5.83 | 18.03 | 3 |
| Distraído | Q-Learning | 100 % | 18.01 | 4.69 | 6.30 | 18.84 | 0 |
| Confunde colores | Regla fija | 100 % | 19.33 | 7.60 | 7.60 | 17.05 | 2 |
| Confunde colores | Q-Learning | 99 % | 18.14 | 5.30 | 6.38 | 17.96 | 2 |

Lo que muestran los datos:
- Q-Learning da menos ayudas en los tres perfiles: −34 % con el rápido, −20 % con el distraído y −30 % con el que confunde colores.
- Obtiene más recompensa en los tres perfiles.
- Con el distraído elimina los eventos de frustración (3 → 0). Con el que confunde colores quedan igual (2 y 2).
- Con el distraído hace un poco más de errores y turnos (6.30 frente a 5.83 errores). Da menos ayudas y el jugador se equivoca algo más antes de acertar.
- Pierde una partida de 100 con el que confunde colores (99 %).

Política aprendida (`datos/modelos/tabla_q.csv`): de los 162 estados, 92 se visitaron al menos una vez y 70 quedaron en cero. En los 92 visitados la mejor acción es a0 en 38, a4 en 17, a5 en 13, a2 en 10, a1 en 8 y a3 en 6. En los 70 no visitados la tabla elige a0 por desempate (gana el menor índice).

## 7. Convergencia

Fuente: `datos/modelos/metricas/curva_entrenamiento.csv` y `datos/modelos/curvas/{recompensa,exito,convergencia_q}.png`. La curva es la **recompensa media por bloque de 500 episodios** durante el entrenamiento, con exploración. La recompensa de cada episodio individual no se guardó: **no disponible**.

| Momento | Episodio | Recompensa media del bloque | max\|ΔQ\| del bloque |
|---|---|---|---|
| Inicio | 500 | 12.91 | 9.58 |
| Mitad | 15 000 | 17.00 | 1.00 |
| Final | 30 000 | 19.06 | 0.18 |

- **Estabilización:** la media de los últimos 10 bloques es 19.09 (entre 18.98 y 19.26). Desde el episodio **22 500** todos los bloques quedan a menos de 2 % de ese valor (desde el 20 000 si se acepta 5 %). El máximo es 19.27, en el bloque que termina en el episodio 24 500, el primero completo con ε = 0.05.
- **Tabla Q:** max|ΔQ| entre bloques baja de 9.58 a 0.18. Queda por debajo de 1.0 desde el episodio 11 500 y por debajo de 0.5 desde el 20 000. No llega a cero porque α final es 0.01 y ε final es 0.05: la tabla se sigue moviendo un poco hasta el final.
- **Éxito durante el entrenamiento:** 100 % en 55 de los 60 bloques y 99.8 % en los otros 5. Es 100 % ya en el primer bloque, cuando el agente casi solo explora al azar. La sección 9 explica por qué.

Sensibilidad (`datos/modelos/metricas/sensibilidad.csv`, 3 semillas: 42, 43 y 44; un factor a la vez):

| α | γ | Éxito (media ± desv.) | Recompensa (media ± desv.) |
|---|---|---|---|
| 0.1 | 0.9 (base) | 0.999 ± 0.002 | 19.25 ± 0.12 |
| 0.05 | 0.9 | 1.000 ± 0.000 | 18.88 ± 0.13 |
| 0.2 | 0.9 | 1.000 ± 0.000 | 19.78 ± 0.22 |
| 0.1 | 0.8 | 1.000 ± 0.000 | 19.49 ± 0.16 |
| 0.1 | 0.99 | 0.984 ± 0.010 | 20.11 ± 0.10 |

Con α = 0.2 y con γ = 0.99 la recompensa es mayor que con la base. Con γ = 0.99 el éxito baja a 98.4 %. No hubo una segunda ronda de ajuste: la tabla que usa el juego es la de la base (α = 0.1, γ = 0.9).

## 8. Baseline: ID3 y A*

### ID3 (Fase 1 y pista a5)
`codigo/ia_models/agent/id3.py`, escrito a mano con NumPy:

- `H(C) = −Σ pᵢ log₂ pᵢ` y `G(C, x) = H(C) − Σ_v (|C_v|/|C|) H(C_v)`.
- Con los platos compatibles `C(I)`, ordena los ingredientes por ganancia. La pantalla muestra los de mayor ganancia y cuida que cada plato compatible tenga al menos un ingrediente a la vista. El resto se completa con distractores del mismo color o categoría.
- Con la misma ganancia, la pista a5 elige el atributo (color o categoría) que mejor separa la respuesta de las otras opciones.

Métricas, de `python -m ia_models.agent.id3`:
- Con los 5 platos equiprobables, `H(C) = 2.32 bits`.
- Ganancia de la primera pregunta: 0.971 para pan, pollo, lechuga, tomate y zanahoria; 0.722 para los demás ingredientes.
- El árbol ID3 identifica cualquiera de los 5 platos con 2 o 3 preguntas. La raíz es ¿PAN? (G = 0.971). Con PAN, ¿POLLO? separa sándwich y desayuno (G = 1.000). Sin PAN, ¿POLLO? (G = 0.918) separa arroz con pollo, y luego ¿LECHUGA? (G = 1.000) separa ensalada y ensalada de frutas.
- Exactitud de ID3 con jugadores o tasa de acierto propia: **no disponible**. ID3 no se evaluó por separado del agente.

### A* (Fase 3)
`codigo/ia_models/agent/astar.py`:

- Busca sobre el grafo de precedencias de la receta. El nodo es el conjunto de pasos hechos; `f(n) = g(n) + h(n)`, con `g` los pasos ya hechos en el camino y `h` los pasos pendientes.
- En el juego da el siguiente paso válido para las pistas y ordena las tarjetas de la Fase 3: primero los pasos válidos.
- Al final de la partida, `solucion()` muestra la receta en un orden válido.

Métricas, de `python -m ia_models.agent.astar`:
- El plan de los 5 platos es `[0, 1, 2, 3]`: 4 pasos, que es la longitud mínima porque cada plato tiene 4 pasos.
- Nodos expandidos y tiempo de búsqueda: **no disponible**. No se midieron.

### Baseline completo
La fila "Regla fija" de la tabla de la sección 6 es el baseline: ID3 + A* + la regla fija de ayuda.

## 9. Nota sobre el 100 % de éxito

La tasa de éxito está en 99–100 % para los dos agentes y para todas las configuraciones, así que **no sirve para comparar**. Las diferencias reales aparecen en ayudas, errores, recompensa y frustración. Hay tres razones, todas del diseño del entorno:

1. **El entorno perdona mucho.** Hay 30 turnos para un plato que se arma en 12 aciertos (4 ingredientes, 4 pasos guiados y 4 pasos solo). Un error no hace perder: el jugador vuelve a intentar el mismo paso.
2. **Los jugadores son sintéticos.** Sus tasas de acierto (40–90 %) y el efecto de cada ayuda son valores fijados a mano, y el código los marca como "valores iniciales, a calibrar". No vienen de datos de personas de Kallpa.
3. **Ayudar casi siempre funciona.** Con a4 el jugador simulado acierta el 98 % de las veces. Hasta un agente que elige al azar termina el plato, y por eso la curva de éxito está en 100 % desde el primer bloque.

Estos resultados muestran que el agente aprende a dar menos ayuda en este simulador. Todavía no muestran que ayude mejor a personas reales. Para eso hace falta registrar partidas reales de forma anónima y volver a entrenar (regla 4 de la arquitectura, prevista para el Hito 3).

## 10. Cómo reproducir los números

Desde `codigo/`, con el entorno virtual activo:

| Resultado | Comando | Salida |
|---|---|---|
| Tabla Q, Q-Learning frente a la regla fija (Experimento A) | `python -m ia_models.experimentos.experimento_a` | `datos/modelos/tabla_q.npy`, `datos/modelos/tabla_q.csv`, `datos/modelos/metricas/resultados_experimento_a.csv` |
| Curvas, frustración y sensibilidad | `python -m ia_models.experimentos.entrenamiento` | `datos/modelos/curvas/*.png`, `datos/modelos/metricas/{curva_entrenamiento,baseline_vs_q,sensibilidad}.csv` |
| Prueba rápida (300 episodios, no pisa los resultados) | `python -m ia_models.experimentos.entrenamiento --rapido` | `datos/modelos/prueba_rapida/` (ignorada por git) |
| Entropía, ganancias y árbol ID3 | `python -m ia_models.agent.id3` | consola |
| Planes A* | `python -m ia_models.agent.astar` | consola |
| Regresión contra el MVP del Hito 1 | `pytest ia_models/tests` | `ia_models/tests/referencia/` |

Las dos corridas usan la misma semilla de entrenamiento (42) y de evaluación (2026), así que `baseline_vs_q.csv` y `resultados_experimento_a.csv` coinciden (el segundo con dos decimales). No hay notebooks: todo se reproduce con estos scripts.
