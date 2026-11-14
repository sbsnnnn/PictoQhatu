// Sonido corto de acierto generado con WebAudio (sin archivos). Si falla, se ignora.
let ctx: AudioContext | null = null

export function sonarAcierto() {
  try {
    ctx ??= new AudioContext()
    const t = ctx.currentTime
    ;[660, 880].forEach((f, i) => {
      const osc = ctx!.createOscillator()
      const vol = ctx!.createGain()
      osc.type = 'triangle'
      osc.frequency.value = f
      vol.gain.setValueAtTime(0.0001, t + i * 0.12)
      vol.gain.exponentialRampToValueAtTime(0.25, t + i * 0.12 + 0.02)
      vol.gain.exponentialRampToValueAtTime(0.0001, t + i * 0.12 + 0.18)
      osc.connect(vol).connect(ctx!.destination)
      osc.start(t + i * 0.12)
      osc.stop(t + i * 0.12 + 0.2)
    })
  } catch {
    /* sin audio: el acierto ya se ve con color, ícono y movimiento */
  }
}
