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
    {/* mano levantada */}
    <path d="M8 13V6.5a1.5 1.5 0 013 0V12M11 11V4.5a1.5 1.5 0 013 0V12M14 11.5V6a1.5 1.5 0 013 0v7.5c0 4-2.5 7-6.5 7-3 0-4.5-1.5-6-4l-1.8-3a1.5 1.5 0 012.5-1.6L8 14" />
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
