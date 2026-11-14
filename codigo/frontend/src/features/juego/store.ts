// Estado de la partida derivado solo de los mensajes del servidor. El front nunca calcula aciertos.
import { create } from 'zustand'
import type { Fase, MensajeServidor, Picto, Round, Seat, Summary } from '../../lib/protocol'

type Feedback = Extract<MensajeServidor, { type: 'feedback' }>

export interface EstadoJuego {
  pantalla: 'inicio' | 'juego' | 'final'
  seat: Seat | null
  phase: Fase | null
  round: Round | null
  feedback: Feedback | null
  confirm: Picto[] | null
  /** Frase que se dice una vez antes del próximo prompt (cambio de rol o de fase). */
  aviso: string | null
  /** Aviso que acompaña a la ronda actual (se dice antes de su prompt). */
  avisoRonda: string | null
  victory: boolean
  summary: Summary | null
  /** Mensajes que llegan mientras se muestra un feedback; se aplican al terminarlo. */
  cola: MensajeServidor[]
  recibir: (m: MensajeServidor) => void
  terminarFeedback: () => void
}

function aplicar(s: EstadoJuego, m: MensajeServidor): Partial<EstadoJuego> {
  switch (m.type) {
    case 'joined':
      return { seat: m.seat, pantalla: 'juego' }
    case 'round':
      return { round: m, seat: m.seat, phase: m.phase, confirm: null, pantalla: 'juego', avisoRonda: s.aviso, aviso: null }
    case 'feedback':
      return { feedback: m }
    case 'confirm':
      return { confirm: m.prompt }
    case 'role_swap':
      return {
        seat: m.seat,
        round: null,
        aviso: m.seat === 'vendedor' ? 'Ahora tú preparas la comida' : 'Ahora tú pides la comida',
      }
    case 'phase_change':
      return { phase: m.phase, round: null, aviso: m.phase === 3 ? 'Ahora arma el plato tú solo' : null }
    case 'game_over':
      return { pantalla: 'final', victory: m.victory, summary: m.summary }
    case 'error':
      // Mensaje inválido: nunca se muestra como fracaso
      console.warn('servidor:', m.message)
      return {}
  }
}

export const useJuego = create<EstadoJuego>()((set, get) => ({
  pantalla: 'inicio',
  seat: null,
  phase: null,
  round: null,
  feedback: null,
  confirm: null,
  aviso: null,
  avisoRonda: null,
  victory: false,
  summary: null,
  cola: [],
  recibir: (m) => {
    if (get().feedback && m.type !== 'joined' && m.type !== 'error') {
      set((s) => ({ cola: [...s.cola, m] }))
      return
    }
    set((s) => aplicar(s, m))
  },
  terminarFeedback: () => {
    set({ feedback: null })
    const cola = get().cola
    set({ cola: [] })
    // Se aplican en orden; si aparece otro feedback, el resto vuelve a esperar
    for (const [i, m] of cola.entries()) {
      set((s) => aplicar(s, m))
      if (get().feedback) {
        set({ cola: cola.slice(i + 1) })
        return
      }
    }
  },
}))
