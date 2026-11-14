import senor from '../assets/ilustraciones/senor.svg'
import senora from '../assets/ilustraciones/senora.svg'
import type { Seat } from '../lib/protocol'

/** Interlocutor IA: la señora vende (el jugador es cliente) y el señor compra (el jugador vende). */
export function Personaje({ rol, className = '' }: { rol: Seat; className?: string }) {
  const vendedora = rol === 'vendedor'
  return (
    <img
      src={vendedora ? senora : senor}
      alt={vendedora ? 'La vendedora' : 'El cliente'}
      draggable={false}
      className={`shrink-0 object-contain select-none ${className}`}
    />
  )
}
