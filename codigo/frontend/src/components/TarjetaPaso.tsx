import type { Picto } from '../lib/protocol'
import { FrasePictos } from './FrasePictos'

/** Paso que el vendedor prepara ahora ([PONER] + [POLLO]), aparte del pedido de la burbuja. */
export function TarjetaPaso({ pictos, className = '' }: { pictos: Picto[]; className?: string }) {
  return (
    <div className={`@container rounded-tarjeta border-4 border-tinta bg-blanco p-2 shadow-suave bajo:p-1 lg:p-3 ${className}`}>
      <FrasePictos pictos={pictos} altavoz={false} alto="h-[4.25rem] bajo:h-12 lg:h-24" />
    </div>
  )
}
