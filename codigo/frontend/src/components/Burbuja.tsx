import type { ReactNode } from 'react'

/** Globo de diálogo del personaje: el pico apunta a la izquierda en móvil y hacia arriba en tablet. */
export function Burbuja({ children, className = '' }: { children: ReactNode; className?: string }) {
  return (
    <div className={`relative rounded-tarjeta border-4 border-tinta bg-blanco p-3 shadow-suave sm:p-4 ${className}`}>
      <span
        aria-hidden
        className="absolute size-7 rotate-45 border-tinta bg-blanco max-md:top-1/2 max-md:-left-[18px] max-md:-translate-y-1/2 max-md:border-b-4 max-md:border-l-4 md:-top-[18px] md:left-[74px] md:border-t-4 md:border-l-4"
      />
      {children}
    </div>
  )
}
