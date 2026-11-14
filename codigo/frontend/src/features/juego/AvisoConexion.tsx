import { useEffect } from 'react'
import { nuevaPartida } from '../../lib/socket'
import { decir } from '../../lib/tts'

const TEXTOS = {
  // Recargar vuelve al inicio; al tocar JUGAR el join con el token recupera el asiento
  reemplazada: { frase: 'Sigues jugando en otra pestaña', boton: 'JUGAR AQUÍ', accion: () => location.reload() },
  ocupada: { frase: 'Esta sala ya tiene un jugador', boton: 'NUEVA PARTIDA', accion: nuevaPartida },
}

/** La conexión se cerró a propósito (no es un error del jugador): se explica con calma y se ofrece seguir. */
export function AvisoConexion({ motivo }: { motivo: keyof typeof TEXTOS }) {
  const { frase, boton, accion } = TEXTOS[motivo]

  useEffect(() => {
    decir(frase)
  }, [frase])

  return (
    <div className="flex min-h-dvh flex-col bg-indigo text-blanco">
      <main className="mx-auto flex w-full max-w-3xl flex-1 flex-col items-center justify-center gap-10 px-4 py-8">
        <p role="status" className="text-center text-5xl font-black sm:text-6xl">
          {frase}
        </p>
        <button
          type="button"
          onClick={accion}
          className="min-h-28 w-full max-w-md rounded-pildora border-4 border-tinta bg-maiz px-10 font-titulo text-4xl font-black text-tinta shadow-bloque active:translate-y-1.5 active:shadow-none"
        >
          {boton}
        </button>
      </main>
    </div>
  )
}
