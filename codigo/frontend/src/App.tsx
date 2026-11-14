import { useState } from 'react'
import { AvisoConexion } from './features/juego/AvisoConexion'
import { PantallaInicio } from './features/juego/PantallaInicio'
import { PantallaJuego } from './features/juego/PantallaJuego'
import { PantallaVictoria } from './features/juego/PantallaVictoria'
import { useJuego } from './features/juego/store'
import { nuevoId } from './lib/id'
import { useGameSocket } from './lib/socket'

const CLAVE_SALA = 'pictoqhatu.sala'

/** La sala se guarda en la pestaña para que una recarga vuelva al mismo asiento. */
function salaInicial() {
  const deUrl = new URLSearchParams(location.search).get('sala')
  if (deUrl) return deUrl
  try {
    const guardada = sessionStorage.getItem(CLAVE_SALA)
    if (guardada) return guardada
    const nueva = nuevoId()
    sessionStorage.setItem(CLAVE_SALA, nueva)
    return nueva
  } catch {
    return nuevoId()
  }
}

export default function App() {
  const [sala] = useState(salaInicial)
  const { enviar } = useGameSocket(sala)
  const pantalla = useJuego((s) => s.pantalla)
  const cerrada = useJuego((s) => s.cerrada)

  if (cerrada) return <AvisoConexion motivo={cerrada} />
  if (pantalla === 'final') return <PantallaVictoria />
  if (pantalla === 'juego') return <PantallaJuego enviar={enviar} />
  return <PantallaInicio enviar={enviar} />
}
