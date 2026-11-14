// Voz en español con Web Speech API. Si no hay voz, todo sigue funcionando: el texto siempre está visible.
import type { Picto } from './protocol'

const PREFERIDAS = ['es-PE', 'es-419', 'es-US', 'es-MX', 'es-ES']
const sintesis = typeof window !== 'undefined' && 'speechSynthesis' in window ? window.speechSynthesis : null

let voz: SpeechSynthesisVoice | null = null

function elegirVoz() {
  if (!sintesis) return
  const voces = sintesis.getVoices().filter((v) => v.lang.toLowerCase().startsWith('es'))
  const norm = (l: string) => l.replace('_', '-').toLowerCase()
  voz =
    PREFERIDAS.map((p) => voces.find((v) => norm(v.lang) === p.toLowerCase())).find(Boolean) ?? voces[0] ?? null
}

if (sintesis) {
  elegirVoz()
  sintesis.addEventListener?.('voiceschanged', elegirVoz)
}

/** Los navegadores móviles solo permiten audio tras un toque: se llama desde el botón [JUGAR]. */
export function desbloquearVoz() {
  if (!sintesis) return
  const u = new SpeechSynthesisUtterance(' ')
  u.volume = 0
  sintesis.speak(u)
}

/** Dice el texto y resuelve al terminar (o enseguida si no hay voz). Nunca rechaza. */
export function decir(texto: string): Promise<void> {
  if (!sintesis || !texto.trim()) return Promise.resolve()
  return new Promise((resolve) => {
    let hecho = false
    const fin = () => {
      if (!hecho) {
        hecho = true
        resolve()
      }
    }
    sintesis.cancel() // la frase anterior resuelve por su onerror/onend
    // En minúsculas: algunos motores deletrean las palabras cortas en MAYÚSCULAS
    const u = new SpeechSynthesisUtterance(texto.toLocaleLowerCase('es'))
    u.lang = voz?.lang ?? 'es-419'
    if (voz) u.voice = voz
    u.rate = 0.9
    u.onend = fin
    u.onerror = fin
    sintesis.speak(u)
    // Algunos Chrome no disparan onend: se resuelve igual tras una estimación generosa
    setTimeout(fin, 1500 + texto.length * 150)
  })
}

/** Frase de pictos de izquierda a derecha; el hueco "?" no se lee. */
export function textoFrase(pictos: Picto[]) {
  return pictos
    .filter((p) => p.id !== '?')
    .map((p) => p.label)
    .join(' ')
}
