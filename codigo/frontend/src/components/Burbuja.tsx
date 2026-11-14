import type { ReactNode } from 'react'

/** Globo de diálogo del personaje: el pico apunta a la izquierda en una columna y hacia arriba en tablet horizontal. */
export function Burbuja({ children, className = '' }: { children: ReactNode; className?: string }) {
  return (
    <div className={`@container relative rounded-tarjeta border-4 border-tinta bg-blanco p-3 shadow-suave lg:p-4 ${className}`}>
      <span
        aria-hidden
        className="absolute size-7 rotate-45 border-tinta bg-blanco max-lg:top-1/2 max-lg:-left-[18px] max-lg:-translate-y-1/2 max-lg:border-b-4 max-lg:border-l-4 lg:-top-[18px] lg:left-[70px] lg:border-t-4 lg:border-l-4"
      />
      {children}
    </div>
  )
}
