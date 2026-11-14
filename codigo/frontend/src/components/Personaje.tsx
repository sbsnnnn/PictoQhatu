import type { Seat } from '../lib/protocol'

/**
 * Interlocutor IA, forma propia y simple. Cuando el jugador es cliente, la IA es la vendedora
 * (índigo, gorro de cocina); cuando el jugador es vendedor, la IA es la clienta (granate, chullo).
 */
export function Personaje({ rol }: { rol: Seat }) {
  const vendedor = rol === 'vendedor'
  const cuerpo = vendedor ? 'var(--color-indigo)' : 'var(--color-qhatu)'
  return (
    <svg
      viewBox="0 0 120 140"
      className="h-28 w-24 shrink-0 sm:h-36 sm:w-32"
      role="img"
      aria-label={vendedor ? 'La vendedora' : 'La clienta'}
    >
      <g stroke="var(--color-tinta)" strokeWidth="5" strokeLinejoin="round" strokeLinecap="round">
        {/* cuerpo: bloque redondeado */}
        <rect x="18" y="82" width="84" height="54" rx="22" fill={cuerpo} />
        {vendedor && <path d="M42 96h36v40H42z" fill="var(--color-crema)" />}
        {/* cara */}
        <circle cx="60" cy="62" r="32" fill="var(--color-crema)" />
        {vendedor ? (
          // gorro de cocina
          <path
            d="M34 40c-12-2-14-22 0-24 2-12 22-14 26-4 6-10 26-6 24 6 14 2 12 22 0 22z"
            fill="var(--color-blanco)"
          />
        ) : (
          // chullo con orejeras y franja de maíz
          <>
            <path d="M28 54c0-26 64-26 64 0v16H84V54H36v16h-8z" fill="var(--color-qhatu)" />
            <path d="M33 44h54" stroke="var(--color-maiz)" strokeWidth="6" />
            <circle cx="60" cy="20" r="7" fill="var(--color-maiz)" />
          </>
        )}
        {/* ojos y sonrisa */}
        <circle cx="49" cy="64" r="3" fill="var(--color-tinta)" />
        <circle cx="71" cy="64" r="3" fill="var(--color-tinta)" />
        <path d="M49 76q11 9 22 0" fill="none" />
      </g>
    </svg>
  )
}
