import type { Picto } from '../lib/protocol'
import { IconoCheck, IconoPuesto } from './Iconos'
import { ImagenPicto } from './Pictograma'

/**
 * EL PLATO del vendedor: un hueco por paso (todos los platos tienen 4).
 * Tablet horizontal: plato redondo con 2×2. Una columna: el plato pedido y una fila de casillas, como la canasta.
 */
export function Plato({ pictos, recien = false, pedido }: { pictos: Picto[]; recien?: boolean; pedido?: Picto }) {
  const casillas = Array.from({ length: Math.max(4, pictos.length) }, (_, i) => pictos[i] ?? null)
  return (
    <section className="flex w-full items-center justify-center gap-3 lg:flex-col lg:gap-4">
      <h2 className="flex shrink-0 items-center gap-2 font-titulo text-2xl font-black whitespace-nowrap">
        {/* En una columna no hay burbuja con el pedido: el plato pedido encabeza la fila */}
        {pedido ? (
          <span className="grid size-16 place-items-center rounded-2xl border-4 border-tinta bg-blanco p-1 bajo:size-14 lg:hidden">
            <ImagenPicto picto={pedido} className="size-full" />
          </span>
        ) : (
          <IconoPuesto className="size-11 lg:hidden" />
        )}
        <IconoPuesto className="size-10 max-lg:hidden" />
        <span className="max-lg:sr-only">EL PLATO</span>
        {pedido && <span className="sr-only">: {pedido.label}</span>}
      </h2>
      <div className="min-w-0 flex-1 lg:grid lg:aspect-square lg:w-full lg:flex-none lg:place-items-center lg:rounded-full lg:border-4 lg:border-tinta lg:bg-blanco lg:shadow-suave">
        <div className="lg:grid lg:size-[88%] lg:place-items-center lg:rounded-full lg:bg-crema">
          {/* En el plato, 2×2 al 77 % del círculo interior: las esquinas quedan dentro */}
          <ul className="flex justify-center gap-3 lg:grid lg:w-[77%] lg:grid-cols-2 lg:gap-2">
            {casillas.map((p, i) => {
              const ultimo = recien && p !== null && i === pictos.length - 1
              return (
                <li
                  key={i}
                  className={`relative grid aspect-square max-w-[4.5rem] min-w-0 flex-1 place-items-center rounded-2xl border-4 p-1 bajo:max-w-14 lg:max-w-none ${p ? `bg-blanco ${ultimo ? 'border-verde' : 'border-tinta'}` : 'border-dashed border-tinta/50'}`}
                >
                  {p && (
                    <>
                      <ImagenPicto picto={p} className="size-full" />
                      <span className="sr-only">{p.label}</span>
                    </>
                  )}
                  {ultimo && (
                    <span aria-hidden className="absolute -top-3 right-0 grid size-8 place-items-center rounded-full border-[3px] border-tinta bg-verde text-blanco">
                      <IconoCheck className="size-5" />
                    </span>
                  )}
                </li>
              )
            })}
          </ul>
        </div>
      </div>
    </section>
  )
}
