// Contrato del WebSocket /ws/{sala}. Espejo a mano de backend/app/game/protocol.py:
// si cambia uno, cambia el otro en el mismo commit. Campos en snake_case, igual que en el cable.

export type Seat = 'cliente' | 'vendedor'

// Códigos de cierre del WebSocket (el cliente no reintenta con ninguno de los dos)
export const CIERRE_SALA_OCUPADA = 1008 // otro jugador ya tiene la sala
export const CIERRE_REEMPLAZADA = 4001 // el mismo asiento se abrió en otra pestaña o dispositivo
export type Fase = 1 | 2 | 3

// ---------------- Tipos compartidos ----------------
export interface Picto {
  id: string // "pan", "CORTAR", "sandwich", "SI"
  label: string // "PAN"
  img: string // "/pictos/pan.png"
}

export interface Option {
  id: string // "pan" | "MEZCLAR" | "CORTAR:manzana" (único en la ronda)
  label: string
  pictos: Picto[] // 1 o 2
}

export interface Atributo {
  name: 'color' | 'categoria'
  value: string
}

/** Ayuda a1–a5 del agente; el front solo la dibuja. a0 = hint null. */
export interface Hint {
  action: 'a1' | 'a2' | 'a3' | 'a4' | 'a5'
  kind: 'repetir' | 'resaltar' | 'reducir' | 'mostrar' | 'atributo'
  target: string | null // option_id a resaltar (a2) o mostrar (a4)
  speech: string
  attribute: Atributo | null
}

export interface Summary {
  turnos: number
  ayudas: number
  errores: number
  plato: Picto
  solucion: Option[] // solo si victory=false
}

// ---------------- Cliente -> servidor ----------------
export type MensajeCliente =
  | { type: 'join'; alias: string; avatar: string; seat_token: string | null }
  | { type: 'tap'; option_id: string; ms: number }
  | { type: 'help' }
  | { type: 'answer'; value: 'SI' | 'NO' }

// ---------------- Servidor -> cliente ----------------
export type MensajeServidor =
  | { type: 'joined'; seat: Seat; seat_token: string }
  | {
      type: 'round'
      seat: Seat
      phase: Fase
      turn: number
      prompt: Picto[]
      options: Option[]
      hint: Hint | null
    }
  | { type: 'feedback'; ok: boolean; npc: Picto[]; option_id: string | null }
  | { type: 'confirm'; prompt: Picto[] }
  | { type: 'role_swap'; seat: Seat }
  | { type: 'phase_change'; phase: Fase }
  | { type: 'game_over'; victory: boolean; summary: Summary }
  | { type: 'error'; message: string }

export type Round = Extract<MensajeServidor, { type: 'round' }>
