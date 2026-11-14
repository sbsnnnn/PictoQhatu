import { Fragment } from 'react'
import type { Picto } from '../lib/protocol'
import { decir, textoFrase } from '../lib/tts'
import { IconoAltavoz } from './Iconos'
import { PictoFluido } from './Pictograma'

interface Props {
  pictos: Picto[]
  texto?: string
  /** Botón de altavoz al final, solo en tablet vertical. En móvil y en tablet horizontal lo cubre el botón de
   *  repetir de la barra inferior, y así los pictos de la burbuja tienen ancho para etiquetas de 16 px. */
  altavoz?: boolean
  /** Alto de cada picto; el ancho se reparte dentro del contenedor. */
  alto?: string
}

/** Frase de hasta 3 pictos, de izquierda a derecha y unidos con "+". Debe ir dentro de un @container. */
export function FrasePictos({ pictos, texto, altavoz = true, alto = 'h-[5.5rem] bajo:h-14 lg:h-24' }: Props) {
  const dicho = texto ?? textoFrase(pictos)
  return (
    <div className="flex min-w-0 items-center gap-2 lg:gap-3">
      <ol className="flex min-w-0 flex-1 items-center gap-1.5" aria-label={dicho}>
        {pictos.slice(0, 3).map((p, i) => (
          <Fragment key={`${p.id}-${i}`}>
            {i > 0 && (
              <li aria-hidden className="shrink-0 font-titulo text-2xl font-black">
                +
              </li>
            )}
            <li className="min-w-0 max-w-32 flex-1">
              <PictoFluido picto={p} className={alto} />
            </li>
          </Fragment>
        ))}
      </ol>
      {altavoz && (
        <button
          type="button"
          onClick={() => decir(dicho)}
          aria-label={`Escuchar: ${dicho}`}
          className="grid size-24 shrink-0 place-items-center rounded-pildora border-4 border-tinta bg-maiz text-tinta shadow-suave-sm active:translate-y-1 active:shadow-none max-sm:hidden lg:hidden"
        >
          <IconoAltavoz className="size-10" />
        </button>
      )}
    </div>
  )
}
