import { IconoAyuda } from './Iconos'

export function BotonAyuda({ onClick }: { onClick: () => void }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="flex min-h-24 items-center gap-3 rounded-pildora border-4 border-tinta bg-naranja px-7 font-titulo text-3xl font-black text-tinta shadow-bloque active:translate-y-1.5 active:shadow-none"
    >
      <IconoAyuda className="size-11" />
      AYUDA
    </button>
  )
}
