import type { Picto } from '../lib/protocol'
import { FrasePictos } from './FrasePictos'
import { IconoCheck } from './Iconos'

/** Paso que el vendedor prepara ahora ([PONER] + [POLLO]), con franja índigo; lleva ✓ cuando el paso salió bien. */
export function TarjetaPaso({ pictos, hecho = false, className = '' }: { pictos: Picto[]; hecho?: boolean; className?: string }) {
  return (
    <div
      className={`@container relative rounded-tarjeta border-4 border-t-[12px] border-tinta border-t-indigo bg-blanco p-2 shadow-suave bajo:border-t-8 bajo:p-1 lg:p-3 ${className}`}
    >
      {/* h-24: imágenes de unos 48 px o más aun con etiqueta de 24 px */}
      <FrasePictos pictos={pictos} altavoz={false} alto="h-24" />
      {/* Sello sobre la franja índigo (top se mide desde dentro del borde): no le quita ancho a las etiquetas */}
      {hecho && (
        <span className="absolute -top-8 right-4 grid size-10 place-items-center rounded-full border-4 border-tinta bg-verde text-blanco">
          <IconoCheck className="size-6" />
          <span className="sr-only">Paso hecho</span>
        </span>
      )}
    </div>
  )
}
