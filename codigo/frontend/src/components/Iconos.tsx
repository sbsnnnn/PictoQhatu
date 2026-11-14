// Íconos propios en SVG. Heredan el color del texto (currentColor) para mantener el contraste del botón.
const base = {
  viewBox: '0 0 24 24',
  fill: 'none',
  stroke: 'currentColor',
  strokeWidth: 3.5,
  strokeLinecap: 'round',
  strokeLinejoin: 'round',
  'aria-hidden': true,
} as const

export const IconoCheck = ({ className = 'size-8' }: { className?: string }) => (
  <svg {...base} className={className}>
    <path d="M4 12.5l5 5L20 6.5" />
  </svg>
)

export const IconoCruz = ({ className = 'size-8' }: { className?: string }) => (
  <svg {...base} className={className}>
    <path d="M6 6l12 12M18 6L6 18" />
  </svg>
)

export const IconoAltavoz = ({ className = 'size-9' }: { className?: string }) => (
  <svg {...base} strokeWidth={2.5} className={className}>
    <path d="M4 9.5h3.5L12 5v14l-4.5-4.5H4z" fill="currentColor" />
    <path d="M15.5 9a4 4 0 010 6M18.5 6.5a7.5 7.5 0 010 11" />
  </svg>
)

export const IconoAyuda = ({ className = 'size-9' }: { className?: string }) => (
  <svg {...base} strokeWidth={2.5} className={className}>
    {/* signo de pregunta en un círculo */}
    <circle cx="12" cy="12" r="9.5" />
    <path d="M9.3 9.3a2.8 2.8 0 015.4 1c0 1.9-2.7 2.4-2.7 4" />
    <circle cx="12" cy="17.6" r="0.6" fill="currentColor" />
  </svg>
)

export const IconoMira = ({ className = 'size-8' }: { className?: string }) => (
  <svg {...base} strokeWidth={3} className={className}>
    {/* flecha hacia abajo: "mira aquí" */}
    <path d="M12 3v15M5.5 11.5L12 18l6.5-6.5" />
  </svg>
)

export const IconoPlay = ({ className = 'size-9' }: { className?: string }) => (
  <svg {...base} strokeWidth={2} className={className}>
    <path d="M8 5.5v13l10.5-6.5z" fill="currentColor" />
  </svg>
)

export const IconoCanasta = ({ className = 'size-9' }: { className?: string }) => (
  <svg {...base} strokeWidth={2.5} className={className}>
    <path d="M8 10l4-5 4 5" />
    <path d="M3 10h18l-2 9.5H5z" />
    <path d="M9 13.5v3M12 13.5v3M15 13.5v3" />
  </svg>
)

export const IconoPuesto = ({ className = 'size-9' }: { className?: string }) => (
  <svg {...base} strokeWidth={2.5} className={className}>
    {/* toldo y mostrador del puesto */}
    <path d="M3 9l2-5h14l2 5c0 1.5-1.2 2.5-2.6 2.5S16 10.5 16 9c0 1.5-1.4 2.5-2.7 2.5S10.7 10.5 10.7 9c0 1.5-1.3 2.5-2.7 2.5S5.4 10.5 5.4 9c0 1.5-1 2.5-2.4 0" />
    <path d="M5 12v8h14v-8" />
  </svg>
)

export const IconoRepetir = ({ className = 'size-9' }: { className?: string }) => (
  <svg {...base} strokeWidth={2.5} className={className}>
    <path d="M4 10.5V9a3 3 0 013-3h12M16 3l3 3-3 3M20 13.5V15a3 3 0 01-3 3H5M8 21l-3-3 3-3" />
  </svg>
)
