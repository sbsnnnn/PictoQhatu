/** Onda que recorta una banda de color: se pinta en crema sobre su borde. Se alarga 1 px para que no quede una línea. */
export function Onda({ abajo = false, alto = 'h-12 sm:h-16' }: { abajo?: boolean; alto?: string }) {
  const d = abajo
    ? 'M0 0h1200v40C1000 70 800 0 600 30S200 70 0 40z' // borde inferior de una banda de arriba
    : 'M0 0h1200v40C1000 10 800 70 600 40S150 0 0 50z' // borde superior de una banda de abajo
  return (
    <svg
      viewBox="0 0 1200 80"
      preserveAspectRatio="none"
      className={`absolute inset-x-0 w-full ${alto} ${abajo ? '-bottom-px rotate-180' : '-top-px'}`}
      aria-hidden
    >
      <path d={d} className="fill-crema" />
    </svg>
  )
}
