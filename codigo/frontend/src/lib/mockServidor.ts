// Servidor simulado (?mock=1): una partida A→B guionada que respeta el contrato de protocol.ts.
// Sirve para trabajar la interfaz sin backend. Con &final=solucion termina con victory=false.
import type { Conexion } from './socket'
import type { Fase, Hint, MensajeCliente, MensajeServidor, Option, Picto, Seat } from './protocol'

const picto = (id: string, label: string): Picto => ({ id, label, img: `/pictos/${id.toLowerCase()}.png` })

// Copiados de datos/catalogo/pictos.json
const P = {
  pan: picto('pan', 'PAN'),
  pollo: picto('pollo', 'POLLO'),
  lechuga: picto('lechuga', 'LECHUGA'),
  tomate: picto('tomate', 'TOMATE'),
  manzana: picto('manzana', 'MANZANA'),
  platano: picto('platano', 'PLÁTANO'),
  naranja: picto('naranja', 'NARANJA'),
  queso: picto('queso', 'QUESO'),
  QUIERO: picto('QUIERO', 'QUIERO'),
  PONER: picto('PONER', 'PONER'),
  CORTAR: picto('CORTAR', 'CORTAR'),
  MEZCLAR: picto('MEZCLAR', 'MEZCLAR'),
  PREPARAR: picto('PREPARAR', 'PREPARAR'),
  SI: picto('SI', 'SÍ'),
  NO: picto('NO', 'NO'),
  sandwich: picto('sandwich', 'SÁNDWICH'),
}
const HUECO: Picto = { id: '?', label: '?', img: '' }

const ingr = (p: Picto): Option => ({ id: p.id, label: p.label, pictos: [p] })
const paso = (p: Picto): Option => ({ id: `PONER:${p.id}`, label: `PONER ${p.label}`, pictos: [P.PONER, p] })
const hint = (action: Hint['action'], target: string | null = null, speech = ''): Hint => ({
  action,
  kind: ({ a1: 'repetir', a2: 'resaltar', a3: 'reducir', a4: 'mostrar', a5: 'atributo' } as const)[action],
  target,
  speech,
  attribute: action === 'a5' ? { name: 'categoria', value: 'verdura' } : null,
})

interface Ronda {
  phase: Fase
  prompt: Picto[]
  options: Option[]
  correcta: string
  hint: Hint | null
}

const SANDWICH = [P.pan, P.pollo, P.lechuga, P.tomate]

// Tramo A (cliente, fase 1): el jugador pide los ingredientes; cada ronda muestra una ayuda distinta
const tramoA = (): Ronda[] => [
  { phase: 1, prompt: [P.QUIERO, HUECO], options: [P.pan, P.manzana, P.queso, P.naranja].map(ingr), correcta: 'pan', hint: null },
  { phase: 1, prompt: [P.QUIERO, HUECO], options: [P.platano, P.pollo, P.manzana, P.queso].map(ingr), correcta: 'pollo', hint: hint('a1', null, 'QUIERO') },
  { phase: 1, prompt: [P.QUIERO, HUECO], options: [P.naranja, P.queso, P.lechuga, P.platano].map(ingr), correcta: 'lechuga', hint: hint('a2', 'lechuga') },
  { phase: 1, prompt: [P.QUIERO, HUECO], options: [P.manzana, P.tomate].map(ingr), correcta: 'tomate', hint: hint('a3') },
]

// Tramo B (vendedor): fase 2 guiada y fase 3 con tarjetas de paso
const tramoB = (): Ronda[] => [
  { phase: 2, prompt: [P.PONER, P.pan], options: [P.pan, P.manzana, P.queso, P.platano].map(ingr), correcta: 'pan', hint: null },
  { phase: 2, prompt: [P.PONER, P.pollo], options: [P.naranja, P.pollo, P.queso, P.tomate].map(ingr), correcta: 'pollo', hint: hint('a4', 'pollo') },
  // shortcut: el sándwich no lleva frutas, así que la pista de atributo dice VERDURA en vez de FRUTA
  { phase: 2, prompt: [P.PONER, P.lechuga], options: [P.manzana, P.platano, P.lechuga, P.naranja].map(ingr), correcta: 'lechuga', hint: hint('a5', null, 'Es una VERDURA') },
  { phase: 2, prompt: [P.PONER, P.tomate], options: [P.tomate, P.pan, P.queso, P.manzana].map(ingr), correcta: 'tomate', hint: null },
]

export function crearMock(alRecibir: (m: MensajeServidor) => void): Conexion {
  const finalConSolucion = new URLSearchParams(location.search).get('final') === 'solucion'
  let timers: ReturnType<typeof setTimeout>[] = []
  const emitir = (m: MensajeServidor, ms = 250) => timers.push(setTimeout(() => alRecibir(m), ms))

  let seat: Seat = 'cliente'
  let rondas = tramoA()
  let actual: Ronda | null = null
  let fase3Hechos = 0
  let turno = 0
  let ayudas = 0
  let errores = 0

  const enviarRonda = (r: Ronda, ms = 600) => {
    actual = r
    if (r.hint) ayudas += 1
    emitir({ type: 'round', seat, phase: r.phase, turn: turno, prompt: r.prompt, options: r.options, hint: r.hint }, ms)
  }

  const rondaFase3 = (h: Hint | null = null): Ronda => {
    const restantes = SANDWICH.slice(fase3Hechos)
    // Las tarjetas que faltan, en otro orden para que no baste con tocar la primera
    const options = [...restantes].reverse().map(paso)
    return { phase: 3, prompt: [P.PREPARAR, P.sandwich], options, correcta: `PONER:${restantes[0].id}`, hint: h }
  }

  const siguiente = () => {
    if (actual?.phase === 3) {
      fase3Hechos += 1
      if (fase3Hechos === SANDWICH.length) {
        emitir({
          type: 'game_over',
          victory: !finalConSolucion,
          summary: {
            turnos: turno,
            ayudas,
            errores,
            plato: P.sandwich,
            solucion: finalConSolucion ? SANDWICH.map(paso) : [],
          },
        })
        return
      }
      return enviarRonda(rondaFase3())
    }
    const r = rondas.shift()
    if (r) return enviarRonda(r)
    if (seat === 'cliente') {
      actual = null
      return emitir({ type: 'confirm', prompt: [P.QUIERO, P.sandwich] }, 600)
    }
    // Fin de la fase 2
    emitir({ type: 'phase_change', phase: 3 }, 400)
    fase3Hechos = 0
    enviarRonda(rondaFase3(), 500)
  }

  // [AYUDA] y los errores suben un escalón de ayuda sobre el mismo tablero
  const escalar = () => {
    if (!actual) return
    const orden: Hint['action'][] = ['a1', 'a2', 'a3', 'a4']
    const prev = actual.hint ? orden.indexOf(actual.hint.action) : -1
    const accion = orden[Math.min(prev + 1, orden.length - 1)]
    let options = actual.options
    if (accion === 'a3' && options.length > 2) {
      const otra = options.find((o) => o.id !== actual!.correcta)!
      options = options.filter((o) => o.id === actual!.correcta || o === otra)
    }
    const speech = accion === 'a1' ? actual.prompt.map((p) => p.label).join(' ') : ''
    const target = accion === 'a2' || accion === 'a4' ? actual.correcta : null
    enviarRonda({ ...actual, options, hint: hint(accion, target, speech) }, 300)
  }

  const recibir = (m: MensajeCliente) => {
    switch (m.type) {
      case 'join':
        emitir({ type: 'joined', seat, seat_token: m.seat_token ?? crypto.randomUUID() })
        if (actual) enviarRonda(actual)
        else siguiente()
        return
      case 'tap': {
        if (!actual || !actual.options.some((o) => o.id === m.option_id)) return // id ausente: se ignora
        turno += 1
        const ok = m.option_id === actual.correcta
        emitir({ type: 'feedback', ok, npc: [ok ? P.SI : P.NO], option_id: m.option_id }, 150)
        if (ok) siguiente()
        else {
          errores += 1
          escalar()
        }
        return
      }
      case 'help':
        escalar()
        return
      case 'answer':
        if (m.value === 'NO') {
          // El pedido se reinicia con amabilidad, sin contar error
          emitir({ type: 'feedback', ok: true, npc: [], option_id: null }, 150)
          rondas = tramoA()
          siguiente()
          return
        }
        seat = 'vendedor'
        emitir({ type: 'role_swap', seat }, 150)
        rondas = tramoB()
        siguiente()
        return
    }
  }

  return {
    enviar: (m) => recibir(m),
    cerrar: () => {
      timers.forEach(clearTimeout)
      timers = []
    },
  }
}
