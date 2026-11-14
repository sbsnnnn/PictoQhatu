import { IconoAyuda } from './Iconos'

export function BotonAyuda({ onClick, className = '' }: { onClick: () => void; className?: string }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`flex min-h-24 items-center justify-center gap-2 rounded-pildora border-4 border-tinta bg-naranja px-3 font-titulo text-[1.65rem] sm:gap-4 sm:px-7 sm:text-4xl font-black text-tinta shadow-suave active:translate-y-1.5 active:shadow-none ${className}`}
    >
      <IconoAyuda className="size-9 shrink-0 sm:size-12" />
      AYUDA
    </button>
  )
}
