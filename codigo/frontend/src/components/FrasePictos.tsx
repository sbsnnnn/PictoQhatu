import { Fragment } from 'react'
import type { Picto } from '../lib/protocol'
import { decir, textoFrase } from '../lib/tts'
import { IconoAltavoz } from './Iconos'
import { Pictograma } from './Pictograma'

/** Frase de hasta 3 pictos, de izquierda a derecha y unidos con "+", con botón de altavoz que la dice. */
export function FrasePictos({ pictos, texto }: { pictos: Picto[]; texto?: string }) {
  const dicho = texto ?? textoFrase(pictos)
  return (
    <div className="flex items-center gap-2 sm:gap-3">
      <ol className="flex items-center gap-1.5 sm:gap-2" aria-label={dicho}>
        {pictos.slice(0, 3).map((p, i) => (
          <Fragment key={`${p.id}-${i}`}>
            {i > 0 && (
              <li aria-hidden className="font-titulo text-3xl font-black">
                +
              </li>
            )}
            <li>
              <Pictograma picto={p} tamano="sm" />
            </li>
          </Fragment>
        ))}
      </ol>
      {/* En móvil no cabe junto a la frase con etiquetas de 24 px: lo cubre el botón de repetir de la barra inferior */}
      <button
        type="button"
        onClick={() => decir(dicho)}
        aria-label={`Escuchar: ${dicho}`}
        className="grid size-20 shrink-0 max-sm:hidden place-items-center rounded-pildora border-4 border-tinta bg-maiz text-tinta shadow-suave-sm active:translate-y-1 active:shadow-none"
      >
        <IconoAltavoz className="size-10" />
      </button>
    </div>
  )
}
