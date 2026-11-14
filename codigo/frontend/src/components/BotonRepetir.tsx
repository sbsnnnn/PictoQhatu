import { IconoAltavoz, IconoRepetir } from './Iconos'

/** Vuelve a decir la frase del personaje (solo voz en el navegador; no pide ayuda al servidor). */
export function BotonRepetir({ onClick, className = '' }: { onClick: () => void; className?: string }) {
  return (
    <button
      type="button"
      onClick={onClick}
      aria-label="Escuchar otra vez"
      className={`flex min-h-24 min-w-0 items-center bajo:min-h-[4.5rem] justify-center gap-4 rounded-pildora border-4 border-tinta bg-blanco px-8 text-tinta shadow-suave active:translate-y-1.5 active:shadow-none ${className}`}
    >
      <IconoAltavoz className="size-12" />
      <IconoRepetir className="size-11" />
    </button>
  )
}
