import { useState, type CSSProperties } from 'react'
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

/**
 * Picto que se ajusta al ancho de su contenedor (@container: burbuja o tarjeta de paso).
 * El alto lo fija `className`. La etiqueta se ajusta a su largo y al ancho de la caja para no cortarse
 * (≈0.72 em por letra mayúscula de Andika negrita).
 */
export function PictoFluido({ picto, className = '' }: { picto: Picto; className?: string }) {
  const caja = `@container flex w-full flex-col items-center justify-center rounded-2xl border-4 border-tinta bg-blanco ${className}`
  if (picto.id === '?') {
    return (
      <div role="img" aria-label="casilla vacía" className={`${caja} border-dashed font-titulo text-[min(3.5rem,45cqw)] font-black`}>
        ?
      </div>
    )
  }
  return (
    <div className={`${caja} gap-0.5 p-1`}>
      <ImagenPicto picto={picto} className="w-full flex-1" />
      <span
        style={{ '--n': Math.max(picto.label.length, 5) } as CSSProperties}
        className="text-center text-[min(1.5rem,calc(100cqw/(var(--n)*0.72)))] leading-tight font-bold whitespace-nowrap uppercase"
      >
        {picto.label}
      </span>
    </div>
  )
}
