import type { Seat } from '../lib/protocol'
import { IconoCanasta, IconoPuesto } from './Iconos'
import { Onda } from './Onda'

// Picto de cada rol, copiado de datos/catalogo/pictos.json (?v = arasaac_id)
const PICTO_ROL = { cliente: '/pictos/quiero.png?v=5441', vendedor: '/pictos/poner.png?v=32757' }

/** Banda de rol: granate para el cliente, índigo para el vendedor, con píldora picto + ícono + nombre. */
export function EncabezadoRol({ seat }: { seat: Seat }) {
  const cliente = seat === 'cliente'
  return (
    <header className={`textil relative shrink-0 px-4 pt-2 pb-10 sm:px-8 sm:pt-4 sm:pb-16 ${cliente ? 'bg-qhatu' : 'bg-indigo'}`}>
      <h1 className="inline-flex items-center gap-3 rounded-pildora border-4 border-blanco py-1.5 pr-6 pl-1.5 text-blanco sm:gap-4 sm:pr-8">
        <span className="grid size-14 shrink-0 place-items-center overflow-hidden rounded-pildora border-4 border-tinta bg-crema sm:size-20">
          <img src={PICTO_ROL[seat]} alt="" className="size-full object-contain p-1.5" />
        </span>
        {cliente ? <IconoCanasta className="size-9 sm:size-11" /> : <IconoPuesto className="size-9 sm:size-11" />}
        <span className="font-titulo text-[1.75rem] font-black tracking-wide sm:text-4xl">{cliente ? 'CLIENTE' : 'VENDEDOR'}</span>
        <span className="sr-only">{cliente ? ': tú pides la comida' : ': tú preparas la comida'}</span>
      </h1>
      <Onda abajo />
    </header>
  )
}
