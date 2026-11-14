import type { Picto } from '../lib/protocol'
import { IconoCheck, IconoPuesto } from './Iconos'
import { ImagenPicto } from './Pictograma'

/** EL PLATO del vendedor: un plato redondo con un hueco por paso (todos los platos tienen 4). */
export function Plato({ pictos, recien = false }: { pictos: Picto[]; recien?: boolean }) {
  const casillas = Array.from({ length: Math.max(4, pictos.length) }, (_, i) => pictos[i] ?? null)
  return (
    <section className="flex w-full flex-col items-center gap-4">
      <h2 className="flex items-center gap-2 font-titulo text-2xl font-black whitespace-nowrap">
        <IconoPuesto className="size-10" />
        EL PLATO
      </h2>
      <div className="grid aspect-square w-full place-items-center rounded-full border-4 border-tinta bg-blanco shadow-suave">
        <div className="grid size-[88%] place-items-center rounded-full bg-crema">
          {/* 2×2 al 68 % del diámetro: las esquinas quedan dentro del círculo */}
          <ul className="grid w-[77%] grid-cols-2 gap-2">
            {casillas.map((p, i) => {
              const ultimo = recien && p !== null && i === pictos.length - 1
              return (
                <li
                  key={i}
                  className={`relative grid aspect-square place-items-center rounded-2xl border-4 p-1 ${p ? `bg-blanco ${ultimo ? 'border-verde' : 'border-tinta'}` : 'border-dashed border-tinta/50'}`}
                >
                  {p && (
                    <>
                      <ImagenPicto picto={p} className="size-full" />
                      <span className="sr-only">{p.label}</span>
                    </>
                  )}
                  {ultimo && (
                    <span aria-hidden className="absolute -top-3 right-0 grid size-8 place-items-center rounded-full border-[3px] border-tinta bg-verde text-blanco">
                      <IconoCheck className="size-5" />
                    </span>
                  )}
                </li>
              )
            })}
          </ul>
        </div>
      </div>
    </section>
  )
}
