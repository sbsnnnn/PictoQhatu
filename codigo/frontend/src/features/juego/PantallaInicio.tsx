import puesto from '../../assets/ilustraciones/puesto.svg'
import { IconoAltavoz, IconoPlay } from '../../components/Iconos'
import type { MensajeCliente } from '../../lib/protocol'
import { leerToken } from '../../lib/socket'
import { desbloquearVoz } from '../../lib/tts'
import { useJuego } from './store'

// Frutas ARASAAC sobre el mostrador del puesto. Posición en % del viewBox 560×420 de puesto.svg.
const FRUTAS = [
  { id: 'manzana', v: 2462, left: 24.5, top: 59, width: 8.5 },
  { id: 'platano', v: 2530, left: 66.5, top: 58, width: 9.5 },
  { id: 'naranja', v: 2483, left: 84, top: 45.5, width: 7.5 },
]

/** Onda que recorta una banda de color: se pinta en crema encima del borde de la banda. */
function Onda({ abajo = false }: { abajo?: boolean }) {
  const d = abajo
    ? 'M0 0h1200v40C1000 70 800 0 600 30S200 70 0 40z' // borde inferior de la banda de arriba
    : 'M0 0h1200v40C1000 10 800 70 600 40S150 0 0 50z' // borde superior de la banda de abajo
  return (
    <svg viewBox="0 0 1200 80" preserveAspectRatio="none" className={`absolute inset-x-0 h-12 w-full sm:h-16 ${abajo ? '-bottom-px rotate-180' : '-top-px'}`} aria-hidden>
      <path d={d} className="fill-crema" />
    </svg>
  )
}

export function PantallaInicio({ enviar }: { enviar: (m: MensajeCliente) => void }) {
  const jugar = () => {
    desbloquearVoz() // primer toque: los navegadores solo permiten la voz después de un gesto
    useJuego.setState({ aviso: 'Vamos a jugar' }) // se dice antes del primer prompt; suelto, el prompt lo cortaba
    // Sin nombre ni dibujo (§2: no se piden datos del jugador); avatar fijo hasta el modo cooperativo
    enviar({ type: 'join', alias: '', avatar: 'manzana', seat_token: leerToken() })
  }

  return (
    <div className="flex h-dvh flex-col overflow-hidden bg-crema">
      <header className="textil relative shrink-0 bg-qhatu px-4 pt-6 pb-16 sm:pt-10 sm:pb-24">
        <h1 className="text-center text-6xl leading-none font-black tracking-tight sm:text-8xl">
          <span className="text-blanco">Picto</span>
          <span className="text-maiz">Qhatu</span>
        </h1>
        <Onda abajo />
      </header>

      <main className="flex min-h-0 flex-1 flex-col items-center gap-4 px-4">
        {/* El puesto ocupa el alto que sobra y mantiene 4:3 (cqw/cqh: unidades del contenedor) */}
        <div className="grid min-h-0 w-full flex-1 place-items-center pt-2" style={{ containerType: 'size' }}>
          <div className="relative aspect-[4/3] w-[min(100cqw,133cqh,36rem)]">
            <img src={puesto} alt="Puesto de comida del mercado con una vendedora" className="absolute inset-0 size-full" />
            {FRUTAS.map((f) => (
              <img
                key={f.id}
                src={`/pictos/${f.id}.png?v=${f.v}`}
                alt=""
                className="absolute aspect-square object-contain"
                style={{ left: `${f.left}%`, top: `${f.top}%`, width: `${f.width}%` }}
              />
            ))}
          </div>
        </div>

        <button
          type="button"
          onClick={jugar}
          className="relative z-10 -mb-8 flex min-h-28 shrink-0 w-full max-w-md items-center justify-center gap-5 rounded-pildora border-4 border-tinta bg-maiz px-6 font-titulo text-5xl font-black text-tinta shadow-bloque active:translate-y-1.5 active:shadow-none sm:text-6xl"
        >
          <span className="grid size-16 shrink-0 place-items-center rounded-pildora bg-tinta text-maiz sm:size-20" aria-hidden>
            <IconoPlay className="size-10 translate-x-0.5 sm:size-12" />
          </span>
          JUGAR
          <IconoAltavoz className="size-10 shrink-0 sm:size-12" />
        </button>
      </main>

      <footer className="textil relative h-20 shrink-0 bg-indigo sm:h-28">
        <Onda />
        <svg viewBox="0 0 1200 80" preserveAspectRatio="none" className="absolute inset-x-0 top-1 h-12 w-full sm:h-16" aria-hidden>
          <path d="M0 58C150 8 400 52 600 46S1000 18 1200 48" fill="none" strokeWidth="8" className="stroke-maiz" />
        </svg>
      </footer>
    </div>
  )
}
