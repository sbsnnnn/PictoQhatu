import type { Picto } from '../lib/protocol'
import { IconoCanasta } from './Iconos'
import { ImagenPicto } from './Pictograma'

/** MI CANASTA: los ingredientes ya pedidos. Panel 2×2 en tablet horizontal, fila bajo las tarjetas en una columna. */
export function Canasta({ pictos, huecos = 4 }: { pictos: Picto[]; huecos?: number }) {
  const casillas = Array.from({ length: Math.max(huecos, pictos.length) }, (_, i) => pictos[i] ?? null)
  return (
    <section className="flex w-full items-center justify-center gap-3 lg:flex-col lg:gap-4">
      <h2 className="flex shrink-0 items-center gap-2 font-titulo text-2xl font-black whitespace-nowrap">
        <IconoCanasta className="size-11 lg:size-10" />
        <span className="max-lg:sr-only">MI CANASTA</span>
      </h2>
      <ul className="flex min-w-0 flex-1 justify-center gap-3 lg:grid lg:w-full lg:grid-cols-2 lg:gap-4 lg:rounded-tarjeta lg:border-4 lg:border-tinta lg:bg-blanco lg:p-4 lg:shadow-suave">
        {casillas.map((p, i) => (
          <li
            key={i}
            className={`grid aspect-square max-w-[4.5rem] min-w-0 flex-1 place-items-center rounded-2xl border-4 p-1.5 bajo:max-w-14 lg:max-w-none ${p ? 'border-tinta bg-blanco' : 'border-dashed border-tinta/50'}`}
          >
            {p && (
              <>
                <ImagenPicto picto={p} className="size-full" />
                <span className="sr-only">{p.label}</span>
              </>
            )}
          </li>
        ))}
      </ul>
    </section>
  )
}
