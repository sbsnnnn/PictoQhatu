import { motion, useReducedMotion } from 'motion/react'
import { useEffect, type CSSProperties } from 'react'
import { IconoAltavoz, IconoRepetir } from '../../components/Iconos'
import { Personaje } from '../../components/Personaje'
import { ImagenPicto } from '../../components/Pictograma'
import { anchoEm } from '../../lib/etiqueta'
import type { Picto } from '../../lib/protocol'
import { nuevaPartida } from '../../lib/socket'
import { decir } from '../../lib/tts'
import { useJuego } from './store'

/**
 * Final de la partida: el plato terminado entre el cliente y la vendedora, sobre el mostrador de maíz.
 * Con victory=false el mismo plato muestra la receta numerada, con cariño: nunca "perdiste".
 */
export function PantallaVictoria() {
  const victory = useJuego((s) => s.victory)
  const summary = useJuego((s) => s.summary)
  const armado = useJuego((s) => s.plato)
  const reducir = useReducedMotion() ?? false
  const plato = summary?.plato
  const nombre = plato?.label ?? ''
  // Sin victoria, los ingredientes salen de la receta (último picto de cada paso: PONER + PAN → PAN)
  const ingredientes = victory ? armado : (summary?.solucion ?? []).map((o) => o.pictos[o.pictos.length - 1])
  const frase = victory ? `¡Listo! Preparaste ${nombre}` : `Así se prepara ${nombre}. Lo hacemos juntos otra vez`

  useEffect(() => {
    decir(frase)
  }, [frase])

  return (
    // --d: diámetro del plato, --pj: ancho de cada personaje. El plato usa lo que queda de ancho entre los dos
    // personajes (huecos de 3cqw y 1rem de margen por lado) para que la fila nunca desborde de 360 px a tablet.
    <div className="h-dvh overflow-hidden bg-crema [container-type:size]">
      <div className="relative grid h-full grid-rows-[auto_minmax(0,1fr)_auto] [--d:min(42cqh,62cqw,25rem,calc(100cqw-2*var(--pj)-6cqw-2rem))] [--pj:min(15cqw,11rem)] max-sm:[--d:min(36cqh,78cqw)]">
        {victory && <Confeti reducir={reducir} />}

        <header className="relative flex items-center justify-center gap-4 px-4 pt-6 bajo:pt-3 sm:gap-6">
          <h1 className="text-center font-titulo text-[min(5.5rem,9cqh,15cqw)] leading-none font-black text-qhatu">
            {victory ? '¡LISTO!' : '¡ASÍ SE HACE!'}
          </h1>
          <button
            type="button"
            onClick={() => decir(frase)}
            aria-label="Escuchar otra vez"
            className="grid size-24 shrink-0 place-items-center rounded-full border-4 border-tinta bg-maiz text-tinta shadow-suave-sm active:translate-y-1 active:shadow-none"
          >
            <IconoAltavoz className="size-12" />
          </button>
        </header>

        {/* Escena: los dos personajes a los lados; el plato baja un 20 % sobre el mostrador.
            En teléfono no caben a los lados: van juntos encima del plato. */}
        <main className="relative flex items-end justify-center gap-[3cqw] px-4 max-sm:grid max-sm:grid-cols-2 max-sm:content-end max-sm:justify-items-center">
          <Personaje rol="cliente" className="h-[calc(var(--d)*0.62)] max-w-(--pj) max-sm:h-[20cqh] max-sm:max-w-none" />
          <motion.div
            initial={reducir ? { opacity: 0 } : { opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
            className="relative z-10 -mb-[calc(var(--d)*0.2)] grid size-(--d) max-sm:order-last max-sm:col-span-2 shrink-0 place-items-center rounded-full border-4 border-tinta bg-blanco shadow-suave"
          >
            <div className="grid size-[88%] place-items-center rounded-full bg-crema">
              {plato && <TarjetaPlato plato={plato} ingredientes={ingredientes} numerar={!victory} />}
            </div>
          </motion.div>
          <Personaje rol="vendedor" className="h-[calc(var(--d)*0.62)] max-w-(--pj) max-sm:h-[20cqh] max-sm:max-w-none" />
        </main>

        {/* Mostrador: deja libre la parte del plato que baja sobre él */}
        <div className="textil flex justify-center border-t-[6px] border-tinta bg-maiz px-4 pt-[calc(var(--d)*0.2+1.5rem)] pb-8 bajo:pb-4">
          <button
            type="button"
            onClick={nuevaPartida}
            className="flex min-h-24 w-full max-w-md items-center justify-center gap-4 rounded-pildora border-4 border-tinta bg-qhatu px-8 font-titulo text-[min(2.75rem,10cqw)] font-black whitespace-nowrap text-blanco shadow-bloque active:translate-y-1.5 active:shadow-none sm:min-h-28"
          >
            <IconoRepetir className="size-11 shrink-0" />
            OTRA VEZ
          </button>
        </div>
      </div>
    </div>
  )
}

/** Tarjeta del plato: sus ingredientes en 2×2 y el nombre. Cuadrada y al 70 % del círculo crema: las esquinas quedan dentro. */
function TarjetaPlato({ plato, ingredientes, numerar }: { plato: Picto; ingredientes: Picto[]; numerar: boolean }) {
  return (
    <div className="@container flex aspect-square w-[70%] flex-col items-center gap-1 rounded-tarjeta border-4 border-tinta bg-crema px-[3%] py-[5%]">
      {ingredientes.length > 0 ? (
        // El orden importa: es la receta (sin victoria se ve numerada)
        <ol className="grid min-h-0 w-full flex-1 grid-cols-2 grid-rows-2 gap-1" aria-label={`Ingredientes de ${plato.label}`}>
          {ingredientes.slice(0, 4).map((p, i) => (
            <li key={`${p.id}-${i}`} className="relative flex min-h-0 min-w-0">
              <ImagenPicto picto={p} className="min-h-0 w-full" />
              <span className="sr-only">{p.label}</span>
              {numerar && (
                <span aria-hidden className="absolute top-0 left-0 grid size-7 place-items-center rounded-full border-2 border-tinta bg-blanco text-base font-bold">
                  {i + 1}
                </span>
              )}
            </li>
          ))}
        </ol>
      ) : (
        <ImagenPicto picto={plato} className="min-h-0 w-full flex-1" />
      )}
      <span
        style={{ '--em': anchoEm(plato.label) } as CSSProperties}
        className="w-full px-1 text-center text-[min(2rem,calc((100cqw-0.5rem)/var(--em)))] leading-tight font-bold whitespace-nowrap uppercase"
      >
        {plato.label}
      </span>
    </div>
  )
}

const COLORES = ['bg-qhatu', 'bg-verde', 'bg-naranja', 'bg-maiz', 'bg-indigo']
// Posiciones fijas (% de la pantalla) en la zona crema, bajo el título y lejos del plato.
const PIEZAS: [number, number, number][] = [
  [4, 18, -20], [9, 30, 10], [15, 22, 30], [12, 36, -15], [22, 17, 45], [27, 28, 0], [3, 33, 60],
  [72, 20, -30], [78, 30, 20], [86, 17, -10], [92, 26, 35], [95, 34, 0], [83, 36, -40], [66, 23, 15],
]

/** Confeti quieto: aparece una vez (≤ 300 ms). Con movimiento reducido solo cambia la opacidad. Solo desde sm. */
function Confeti({ reducir }: { reducir: boolean }) {
  return (
    // En teléfono los personajes ocupan la zona crema: no queda sitio libre para el confeti
    <div aria-hidden className="pointer-events-none absolute inset-0 max-sm:hidden">
      {PIEZAS.map(([x, y, giro], i) => (
        <motion.span
          key={i}
          initial={reducir ? { opacity: 0 } : { opacity: 0, y: -16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: (i % 5) * 0.04 }}
          style={{ left: `${x}%`, top: `${y}%`, rotate: giro }}
          className={`absolute border-2 border-tinta ${COLORES[i % COLORES.length]} ${i % 3 === 0 ? 'size-4 rounded-full' : 'h-6 w-3 rounded-sm'}`}
        />
      ))}
    </div>
  )
}
