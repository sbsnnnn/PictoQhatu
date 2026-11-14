import { useState } from 'react'
import type { Picto } from '../lib/protocol'

/** Imagen del picto; si falta o no carga, no se dibuja nada (la etiqueta siempre está). */
export function ImagenPicto({ picto, className = '' }: { picto: Picto; className?: string }) {
  const [rota, setRota] = useState(false)
  if (!picto.img || rota) return null
  return (
    <img
      src={picto.img}
      alt=""
      draggable={false}
      onError={() => setRota(true)}
      className={`min-h-0 object-contain select-none ${className}`}
    />
  )
}

interface Props {
  picto: Picto
  /** "md" para frases y resúmenes; "sm" para listas largas */
  tamano?: 'sm' | 'md'
}

/** Tarjeta crema con borde tinta: imagen + etiqueta en MAYÚSCULAS. El id "?" es la casilla vacía. */
export function Pictograma({ picto, tamano = 'md' }: Props) {
  // Ancho mínimo y no fijo: las etiquetas largas (ZANAHORIA) no se cortan
  const caja = tamano === 'md' ? 'min-w-28 h-32 sm:min-w-32 sm:h-36' : 'min-w-22 h-26 sm:min-w-24 sm:h-28'
  if (picto.id === '?') {
    return (
      <div
        role="img"
        aria-label="casilla vacía"
        className={`${caja} grid shrink-0 place-items-center rounded-tarjeta border-4 border-dashed border-tinta bg-blanco font-titulo text-6xl font-black text-tinta`}
      >
        ?
      </div>
    )
  }
  return (
    <div
      className={`${caja} flex shrink-0 flex-col items-center justify-center gap-1 rounded-tarjeta border-4 border-tinta bg-blanco p-2`}
    >
      <ImagenPicto picto={picto} className="w-full flex-1" />
      <span className="text-center text-2xl leading-tight font-bold uppercase">{picto.label}</span>
    </div>
  )
}
