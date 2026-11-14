# Preguntas probables del docente (Hito 2)

Respuestas cortas, con las cifras del informe técnico de modelado.

1. **¿Por qué Q-Learning tabular y no una red neuronal?**  
   El estado reducido tiene 162 valores y 6 acciones: la tabla cabe completa, entrena en minutos sin GPU y cada decisión se puede explicar a un educador.
2. **Si las dos políticas tienen 99–100 % de éxito, ¿qué aporta el agente?**  
   Da entre 20 % y 34 % menos ayudas, obtiene más recompensa con los tres perfiles y con el perfil distraído bajó la frustración de 3 a 0 eventos. El éxito no discrimina por cómo está diseñado el entorno.
3. **¿Cómo saben que convergió?**  
   max|ΔQ| baja de 9,58 a 0,18 y la recompensa por bloque queda a menos de 2 % de la media final desde el episodio 22 500.
4. **¿Los jugadores simulados representan a los usuarios de Kallpa?**  
   Todavía no. Sus parámetros los fijamos nosotros; calibrarlos con partidas reales y anónimas es la primera tarea del Hito 3.
5. **¿Qué pasa en los 70 estados que nunca se visitaron?**  
   La fila sigue en cero y el agente elige a0. El jugador puede tocar AYUDA en cualquier momento y entonces el agente elige una ayuda entre a1 y a5 según la tabla; en un estado sin visitar, empate, sale a1.
6. **¿El agente aprende mientras juegan?**  
   No. La tabla Q es de solo lectura en el juego. El plan es registrar transiciones anónimas y reentrenar fuera de línea.
7. **¿Para qué ID3 y A* si ya tienen Q-Learning?**  
   Hacen cosas distintas: ID3 decide qué preguntar y qué atributo usar en la pista a5, y A* da el siguiente paso válido. Q-Learning decide cuánta ayuda dar.
8. **¿Cómo eligieron α y γ?**  
   Partimos del Hito 1 y probamos α ∈ {0,05; 0,1; 0,2} y γ ∈ {0,8; 0,9; 0,99} con 3 semillas. Con γ = 0,99 el éxito baja a 98,4 %; nos quedamos con α = 0,1 y γ = 0,9.
9. **¿Qué datos personales guardan?**  
   Ninguno. El jugador no escribe nombre; el alias se envía vacío y las métricas son anónimas (Ley 29733).
10. **¿Qué pasa si se corta la conexión de la tablet?**  
   Al reconectar con su seat_token el servidor reenvía la última ronda y la partida sigue. Si el servidor se reinicia, la sala se pierde porque vive en memoria.
