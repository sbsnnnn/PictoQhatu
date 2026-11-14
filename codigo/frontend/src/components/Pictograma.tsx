import { useState, type CSSProperties } from 'react'
import { anchoEm } from '../lib/etiqueta'
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

/**
 * Picto que se ajusta al ancho de su contenedor (@container: burbuja o tarjeta de paso).
 * El alto lo fija `className`. La etiqueta deja 6 px de margen por lado y se ajusta a su ancho real
 * (lib/etiqueta.ts) para no tocar el borde, hasta 24 px.
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
    <div className={`${caja} gap-0.5 py-1`}>
      <ImagenPicto picto={picto} className="w-full flex-1" />
      <span
        style={{ '--em': anchoEm(picto.label) } as CSSProperties}
        className="w-full px-1.5 text-center text-[min(1.5rem,calc((100cqw-0.75rem)/var(--em)))] leading-tight font-bold whitespace-nowrap uppercase"
      >
        {picto.label}
      </span>
    </div>
  )
}
