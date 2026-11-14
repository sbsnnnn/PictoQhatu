import { motion, useReducedMotion } from 'motion/react'
import { useEffect } from 'react'
import { Pictograma } from '../../components/Pictograma'
import { nuevaPartida } from '../../lib/socket'
import { decir } from '../../lib/tts'
import { useJuego } from './store'

/** Final de la partida. Con victory=false se muestra la receta con cariño: nunca "perdiste". */
export function PantallaVictoria() {
  const victory = useJuego((s) => s.victory)
  const summary = useJuego((s) => s.summary)
  const reducir = useReducedMotion()
  const plato = summary?.plato

  const titulo = victory ? '¡Muy bien! Preparaste:' : 'Así se prepara:'
  const nombre = plato?.label ?? ''

  useEffect(() => {
    decir(victory ? `¡Muy bien! Preparaste ${nombre}` : `Así se prepara ${nombre}. Lo hacemos juntos otra vez`)
  }, [victory, nombre])

  return (
    <div className="flex min-h-dvh flex-col bg-indigo text-blanco">
      <main className="mx-auto flex w-full max-w-4xl flex-1 flex-col items-center justify-center gap-6 px-4 py-8">
        {victory && <Estrellas reducir={reducir ?? false} />}
        <h1 className="text-center text-5xl font-black sm:text-6xl">{titulo}</h1>

        {plato && (
          <motion.div
            initial={reducir ? { opacity: 0 } : { opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.3 }}
            className="text-tinta"
          >
            <Pictograma picto={plato} />
          </motion.div>
        )}

        {!victory && summary && summary.solucion.length > 0 && (
          // La receta es una secuencia: aquí sí van números
          <ol className="flex flex-wrap justify-center gap-4 text-tinta" aria-label="Los pasos">
            {summary.solucion.map((o, i) => (
              <li key={o.id} className="flex flex-col items-center gap-1 rounded-tarjeta border-4 border-tinta bg-crema p-3">
                <span className="font-titulo text-2xl font-black">{i + 1}</span>
                <div className="flex gap-2">
                  {o.pictos.map((p) => (
                    <Pictograma key={p.id} picto={p} tamano="sm" />
                  ))}
                </div>
              </li>
            ))}
          </ol>
        )}

        {summary && (
          <p className="text-center text-2xl">
            Jugaste {summary.turnos} turnos con {summary.ayudas} {summary.ayudas === 1 ? 'ayuda' : 'ayudas'}.
          </p>
        )}

        <button
          type="button"
          onClick={nuevaPartida}
          className="min-h-28 w-full max-w-md rounded-pildora border-4 border-tinta bg-maiz px-10 font-titulo text-4xl font-black text-tinta shadow-bloque active:translate-y-1.5 active:shadow-none"
        >
          JUGAR OTRA VEZ
        </button>
      </main>
    </div>
  )
}

/** Celebración corta (≤ 300 ms): estrellas de maíz que aparecen una vez. */
function Estrellas({ reducir }: { reducir: boolean }) {
  return (
    <div className="flex gap-4" aria-hidden>
      {[0, 1, 2].map((i) => (
        <motion.svg
          key={i}
          viewBox="0 0 24 24"
          className={i === 1 ? 'size-24' : 'size-16'}
          initial={reducir ? { opacity: 0 } : { opacity: 0, scale: 0.3, rotate: -30 }}
          animate={{ opacity: 1, scale: 1, rotate: 0 }}
          transition={{ duration: 0.3, delay: i * 0.08 }}
        >
          <path
            d="M12 2.5l2.9 6 6.6.9-4.8 4.6 1.2 6.5L12 17.4l-5.9 3.1 1.2-6.5L2.5 9.4l6.6-.9z"
            className="fill-maiz stroke-tinta"
            strokeWidth="1.8"
            strokeLinejoin="round"
          />
        </motion.svg>
      ))}
    </div>
  )
}
