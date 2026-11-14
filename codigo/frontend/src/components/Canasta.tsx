import type { Picto } from '../lib/protocol'
import { IconoCanasta } from './Iconos'
import { ImagenPicto } from './Pictograma'

/** MI CANASTA: los ingredientes ya pedidos. Panel 2×2 en tablet, fila bajo las tarjetas en móvil. */
export function Canasta({ pictos, huecos = 4 }: { pictos: Picto[]; huecos?: number }) {
  const casillas = Array.from({ length: Math.max(huecos, pictos.length) }, (_, i) => pictos[i] ?? null)
  return (
    <section className="flex items-center gap-3 md:flex-col md:gap-4">
      <h2 className="flex shrink-0 items-center gap-2 font-titulo text-2xl font-black whitespace-nowrap">
        <IconoCanasta className="size-11 md:size-10" />
        <span className="max-md:sr-only">MI CANASTA</span>
      </h2>
      <ul className="grid flex-1 grid-cols-4 gap-3 md:w-full md:grid-cols-2 md:gap-4 md:rounded-tarjeta md:border-4 md:border-tinta md:bg-blanco md:p-5 md:shadow-suave">
        {casillas.map((p, i) => (
          <li
            key={i}
            className={`grid aspect-square place-items-center rounded-2xl border-4 p-2 ${p ? 'border-tinta bg-blanco' : 'border-dashed border-tinta/50'}`}
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
