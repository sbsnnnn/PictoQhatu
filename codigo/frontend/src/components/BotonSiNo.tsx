import { IconoCheck, IconoCruz } from './Iconos'

/** [SÍ] verde con ✓ y [NO] en tinta con ✗: el NO nunca es rojo de alarma. */
export function BotonSiNo({ onRespuesta }: { onRespuesta: (v: 'SI' | 'NO') => void }) {
  const comun =
    'flex min-h-24 min-w-40 items-center justify-center gap-3 rounded-pildora border-4 border-tinta px-8 font-titulo text-4xl font-black text-blanco shadow-bloque active:translate-y-1.5 active:shadow-none'
  return (
    <div className="flex gap-4">
      <button type="button" onClick={() => onRespuesta('SI')} className={`${comun} bg-verde`}>
        <IconoCheck className="size-10" />
        SÍ
      </button>
      <button type="button" onClick={() => onRespuesta('NO')} className={`${comun} bg-tinta`}>
        <IconoCruz className="size-10" />
        NO
      </button>
    </div>
  )
}
