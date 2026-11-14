# PictoQhatu

Juego de cocina con pictogramas (CAA) asistido por IA, para la Asociación Educativa Kallpa. Curso 1ASI0404 Inteligencia Artificial, UPC, 2026-20, Grupo 4.

## Cómo ejecutarlo

Desde `codigo/`:

```bash
python -m venv .venv
.venv\Scripts\activate            # Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt

cd frontend && npm ci && npm run build && cd ..
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
```

El backend sirve el juego (`frontend/dist`), los pictogramas y el WebSocket en un solo proceso: se abre `http://localhost:8000`, o la IP de la PC desde una tablet en la misma red.

Para desarrollar la interfaz: `npm run dev` en `frontend/` (el proxy de Vite manda `/ws` y `/pictos` al puerto 8000). Con `?mock=1` el juego corre sin backend.

Pruebas: `pytest` y `ruff check .` desde `codigo/`; `npm run build` y `npm run lint` desde `codigo/frontend/`.

## Limitaciones conocidas

- **Las salas viven en memoria y no sobreviven a un reinicio del servidor.** Si el servidor se reinicia a mitad de una partida, la pestaña se reconecta sola y empieza una partida nueva desde el inicio.
- Un asiento se juega desde una sola pestaña. Si se abre en otra (mismo `seat_token`), la nueva toma la partida y la anterior muestra "Sigues jugando en otra pestaña".

## Pendiente para el Hito 3

- **Bloqueo en la propia sala.** Si la conexión se corta justo después de que el servidor crea la sala y antes de que llegue `joined`, el cliente no guarda su `seat_token`. Al reconectar, el servidor lo trata como otro jugador y muestra "Esta sala ya tiene un jugador". El jugador tiene que empezar una partida nueva.

## Créditos

Pictogramas: Sergio Palao. Origen: ARASAAC (https://arasaac.org). Licencia: CC BY-NC-SA. Propiedad: Gobierno de Aragón (España).
