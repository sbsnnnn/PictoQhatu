// Ancho de cada letra de Andika negrita en em, medido con canvas en el navegador.
// Sirve para elegir el tamaño de una etiqueta que debe caber en su casilla sin cortarse.
const ANCHO: Record<string, number> = {
  A: 0.73, B: 0.68, C: 0.68, D: 0.73, E: 0.59, F: 0.59, G: 0.72, H: 0.74, I: 0.51, J: 0.5, K: 0.7, L: 0.55, M: 0.91,
  N: 0.75, O: 0.73, P: 0.62, Q: 0.75, R: 0.67, S: 0.61, T: 0.62, U: 0.73, V: 0.72, W: 1.04, X: 0.67, Y: 0.67, Z: 0.61,
  Á: 0.73, É: 0.59, Í: 0.51, Ó: 0.73, Ú: 0.73, Ñ: 0.75, Ü: 0.73, '¿': 0.53, '?': 0.53, '¡': 0.38, '!': 0.38, ' ': 0.27,
}

/** Ancho del texto en MAYÚSCULAS, en em. Una letra desconocida cuenta como una ancha. */
export const anchoEm = (texto: string) => [...texto.toUpperCase()].reduce((s, c) => s + (ANCHO[c] ?? 0.8), 0)
