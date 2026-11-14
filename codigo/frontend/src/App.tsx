import { useState } from 'react'
import { PantallaInicio } from './features/juego/PantallaInicio'
import { PantallaJuego } from './features/juego/PantallaJuego'
import { PantallaVictoria } from './features/juego/PantallaVictoria'
import { useJuego } from './features/juego/store'
import { useGameSocket } from './lib/socket'

const CLAVE_SALA = 'pictoqhatu.sala'

/** La sala se guarda en la pestaña para que una recarga vuelva al mismo asiento. */
function salaInicial() {
  const deUrl = new URLSearchParams(location.search).get('sala')
  if (deUrl) return deUrl
  try {
    const guardada = sessionStorage.getItem(CLAVE_SALA)
    if (guardada) return guardada
    const nueva = crypto.randomUUID()
    sessionStorage.setItem(CLAVE_SALA, nueva)
    return nueva
  } catch {
    return crypto.randomUUID()
  }
}

export default function App() {
  const [sala] = useState(salaInicial)
  const { enviar } = useGameSocket(sala)
  const pantalla = useJuego((s) => s.pantalla)

  if (pantalla === 'final') return <PantallaVictoria />
  if (pantalla === 'juego') return <PantallaJuego enviar={enviar} />
  return <PantallaInicio enviar={enviar} />
}
