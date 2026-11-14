import type { Picto } from '../lib/protocol'
import { decir, textoFrase } from '../lib/tts'
import { IconoAltavoz } from './Iconos'
import { Pictograma } from './Pictograma'

/** Frase de hasta 3 pictos, de izquierda a derecha, con botón de altavoz que la dice. */
export function FrasePictos({ pictos, texto }: { pictos: Picto[]; texto?: string }) {
  const dicho = texto ?? textoFrase(pictos)
  return (
    <div className="flex items-center gap-3">
      <ol className="flex items-center gap-2 sm:gap-3" aria-label={dicho}>
        {pictos.slice(0, 3).map((p, i) => (
          <li key={`${p.id}-${i}`}>
            <Pictograma picto={p} />
          </li>
        ))}
      </ol>
      <button
        type="button"
        onClick={() => decir(dicho)}
        aria-label={`Escuchar: ${dicho}`}
        className="grid size-24 shrink-0 place-items-center rounded-pildora border-4 border-tinta bg-maiz text-tinta shadow-bloque-sm active:translate-y-1 active:shadow-none"
      >
        <IconoAltavoz className="size-11" />
      </button>
    </div>
  )
}
