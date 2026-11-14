import type { Picto } from '../lib/protocol'
import { FrasePictos } from './FrasePictos'
import { IconoCheck } from './Iconos'

/** Paso que el vendedor prepara ahora ([PONER] + [POLLO]), con franja índigo; lleva ✓ cuando el paso salió bien. */
export function TarjetaPaso({ pictos, hecho = false, className = '' }: { pictos: Picto[]; hecho?: boolean; className?: string }) {
  return (
    <div
      className={`@container flex items-center gap-2 rounded-tarjeta border-4 border-t-[12px] border-tinta border-t-indigo bg-blanco p-2 shadow-suave bajo:border-t-8 bajo:p-1 lg:gap-3 lg:p-3 ${className}`}
    >
      <div className="min-w-0 flex-1">
        <FrasePictos pictos={pictos} altavoz={false} alto="h-[4rem] bajo:h-11 lg:h-24" />
      </div>
      <span
        className={`grid size-14 shrink-0 place-items-center rounded-full border-4 border-tinta bg-verde text-blanco bajo:size-11 lg:size-16 ${hecho ? '' : 'invisible'}`}
      >
        <IconoCheck className="size-8 lg:size-9" />
        <span className="sr-only">Paso hecho</span>
      </span>
    </div>
  )
}
