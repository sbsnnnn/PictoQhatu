// Conexión al WebSocket /ws/{sala} con reconexión por seat_token. Con ?mock=1 usa el servidor simulado.
import { useCallback, useEffect, useRef } from 'react'
import { useJuego } from '../features/juego/store'
import { crearMock } from './mockServidor'
import type { MensajeCliente, MensajeServidor } from './protocol'

export interface Conexion {
  enviar: (m: MensajeCliente) => void
  cerrar: () => void
}

type Join = Extract<MensajeCliente, { type: 'join' }>

const CLAVE_TOKEN = 'pictoqhatu.seat_token'

export const leerToken = () => {
  try {
    return sessionStorage.getItem(CLAVE_TOKEN)
  } catch {
    return null
  }
}
const guardarToken = (t: string) => {
  try {
    sessionStorage.setItem(CLAVE_TOKEN, t)
  } catch {
    /* sin almacenamiento: no habrá reconexión tras recargar, pero se puede jugar */
  }
}

export const usarMock = () =>
  new URLSearchParams(location.search).get('mock') === '1' || Boolean(import.meta.env.VITE_MOCK)

function conectarWs(sala: string, alRecibir: (m: MensajeServidor) => void, alAbrir: () => void): Conexion {
  const url = `${location.protocol === 'https:' ? 'wss:' : 'ws:'}//${location.host}/ws/${encodeURIComponent(sala)}`
  let ws: WebSocket
  let pendientes: MensajeCliente[] = []
  let intentos = 0
  let cerrado = false
  let yaConecto = false
  let reintento: ReturnType<typeof setTimeout>

  const abrir = () => {
    ws = new WebSocket(url)
    ws.onopen = () => {
      if (yaConecto) alAbrir() // solo en reconexiones: el primer join ya va en pendientes
      yaConecto = true
      intentos = 0
      pendientes.forEach((m) => ws.send(JSON.stringify(m)))
      pendientes = []
    }
    ws.onmessage = (e) => {
      try {
        alRecibir(JSON.parse(e.data) as MensajeServidor)
      } catch {
        console.warn('mensaje no válido', e.data)
      }
    }
    // Las tablets se suspenden: se reintenta en silencio, cada vez un poco más tarde
    ws.onclose = () => {
      if (cerrado) return
      intentos += 1
      reintento = setTimeout(abrir, Math.min(intentos, 5) * 1000)
    }
  }
  abrir()

  return {
    enviar: (m) => (ws.readyState === WebSocket.OPEN ? ws.send(JSON.stringify(m)) : pendientes.push(m)),
    cerrar: () => {
      cerrado = true
      clearTimeout(reintento)
      ws.close()
    },
  }
}

export function useGameSocket(sala: string) {
  const conexion = useRef<Conexion | null>(null)
  const ultimoJoin = useRef<Join | null>(null)

  useEffect(() => {
    const recibir = (m: MensajeServidor) => {
      if (m.type === 'joined') guardarToken(m.seat_token)
      useJuego.getState().recibir(m)
    }
    // Al reconectar se repite el join con el token: el servidor reenvía el último round
    const alAbrir = () => {
      if (ultimoJoin.current) c.enviar({ ...ultimoJoin.current, seat_token: leerToken() })
    }
    const c = usarMock() ? crearMock(recibir) : conectarWs(sala, recibir, alAbrir)
    conexion.current = c
    return () => c.cerrar()
  }, [sala])

  const enviar = useCallback((m: MensajeCliente) => {
    if (m.type === 'join') ultimoJoin.current = m
    conexion.current?.enviar(m)
  }, [])

  return { enviar }
}
