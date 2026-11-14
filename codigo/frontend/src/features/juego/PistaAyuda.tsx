import { IconoAyuda } from '../../components/Iconos'
import { PictoFluido } from '../../components/Pictograma'
import type { Picto } from '../../lib/protocol'

/** Círculo naranja con el ícono de ayuda: marca todo lo que viene del botón [AYUDA]. */
const Sello = () => (
  <span className="grid size-12 shrink-0 place-items-center rounded-full border-4 border-tinta bg-naranja text-tinta">
    <IconoAyuda className="size-8" />
  </span>
)

/** Pista de atributo (a5): "Es una VERDURA" queda escrita además de dicha. La lee el aria-live de la pantalla. */
export function PistaAtributo({ texto, className = '' }: { texto: string; className?: string }) {
  return (
    <p aria-hidden className={`flex max-w-full items-center gap-3 font-titulo text-2xl leading-tight font-black ${className}`}>
      <Sello />
      {texto}
    </p>
  )
}

/** ¡MIRA! + el picto de la respuesta, dentro de la burbuja (a2 resaltar, a4 mostrar). */
export function PistaMira({ picto, className = '' }: { picto: Picto; className?: string }) {
  return (
    <div className={`flex flex-col gap-2 ${className}`}>
      <p className="flex items-center gap-3 font-titulo text-3xl font-black">
        <Sello />
        ¡MIRA!
      </p>
      <div className="w-36">
        <PictoFluido picto={picto} className="h-28" />
      </div>
    </div>
  )
}
