import { Fragment, type CSSProperties } from 'react'
import { PictoFluido } from '../../components/Pictograma'
import { anchoEm } from '../../lib/etiqueta'
import type { Picto } from '../../lib/protocol'

/**
 * [QUIERES] + [SÁNDWICH] con un "?" de maíz sobre el primer picto. La pregunta va en el sello y no en la
 * etiqueta, y cada picto toma ancho según su palabra: así las etiquetas llegan a 16 px en un móvil de 390 px.
 * Debe ir dentro de un @container (la burbuja).
 */
export function FrasePregunta({ pictos, dicho }: { pictos: Picto[]; dicho: string }) {
  return (
    <ol className="flex min-w-0 items-center gap-1.5" aria-label={dicho}>
      {pictos.slice(0, 3).map((p, i) => (
        <Fragment key={`${p.id}-${i}`}>
          {i > 0 && (
            <li aria-hidden className="shrink-0 font-titulo text-2xl font-black">
              +
            </li>
          )}
          {/* base fija = bordes + margen de la etiqueta (1.25rem); el resto se reparte por ancho de palabra */}
          <li className="relative max-w-36 min-w-0 basis-5" style={{ flexGrow: anchoEm(p.label) } as CSSProperties}>
            <PictoFluido picto={p} className="h-[5.5rem] bajo:h-14 lg:h-24" />
            {i === 0 && (
              <span
                aria-hidden
                className="absolute -top-3 -left-3 grid size-10 place-items-center rounded-full border-4 border-tinta bg-maiz font-titulo text-2xl font-black text-tinta"
              >
                ?
              </span>
            )}
          </li>
        </Fragment>
      ))}
    </ol>
  )
}
