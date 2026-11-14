import { motion, useReducedMotion, type TargetAndTransition } from 'motion/react'
import { useEffect, useRef } from 'react'
import { BotonAyuda } from '../../components/BotonAyuda'
import { BotonSiNo } from '../../components/BotonSiNo'
import { FrasePictos } from '../../components/FrasePictos'
import { IconoCheck, IconoCruz, IconoMira } from '../../components/Iconos'
import { Personaje } from '../../components/Personaje'
import { ImagenPicto, Pictograma } from '../../components/Pictograma'
import type { MensajeCliente, Option, Picto } from '../../lib/protocol'
import { sonarAcierto } from '../../lib/sonido'
import { decir, textoFrase } from '../../lib/tts'
import { useJuego } from './store'

type Estado = 'normal' | 'resaltar' | 'mostrar' | 'ok' | 'no'

/** ms desde que terminó la voz del prompt; 0 si se toca antes. */
const msDesde = (t: number | null) => (t === null ? 0 : Math.round(performance.now() - t))

const pausa = (ms: number) => new Promise((r) => setTimeout(r, ms))

/** [QUIERO, SÁNDWICH] del confirm se muestra y se dice como pregunta: ¿QUIERES SÁNDWICH? */
const comoPregunta = (prompt: Picto[]): Picto[] =>
  prompt.map((p, i) => ({
    ...p,
    label: `${i === 0 ? '¿' : ''}${p.id === 'QUIERO' ? 'QUIERES' : p.label}${i === prompt.length - 1 ? '?' : ''}`,
  }))

export function PantallaJuego({ enviar }: { enviar: (m: MensajeCliente) => void }) {
  const seat = useJuego((s) => s.seat) ?? 'cliente'
  const round = useJuego((s) => s.round)
  const avisoRonda = useJuego((s) => s.avisoRonda)
  const feedback = useJuego((s) => s.feedback)
  const confirm = useJuego((s) => s.confirm)
  const pedido = useJuego((s) => s.pedido)
  const reducir = useReducedMotion() ?? false

  const finVoz = useRef<number | null>(null)
  const tocadoEn = useRef<object | null>(null)

  // Cada ronda nueva: aviso (si hay) → prompt → pista de atributo. ms se mide desde que termina el prompt.
  useEffect(() => {
    if (!round) return
    let vigente = true
    finVoz.current = null
    ;(async () => {
      if (avisoRonda) await decir(avisoRonda)
      if (!vigente) return
      await decir(textoFrase(round.prompt))
      if (!vigente) return
      finVoz.current = performance.now()
      if (round.hint?.action === 'a5' && round.hint.speech) await decir(round.hint.speech)
    })()
    return () => {
      vigente = false
    }
  }, [round, avisoRonda])

  useEffect(() => {
    if (confirm) decir(textoFrase(comoPregunta(confirm)))
  }, [confirm])

  // Feedback: se dice el npc y una frase amable; al terminar se aplican los mensajes en espera
  useEffect(() => {
    if (!feedback) return
    let vigente = true
    if (feedback.ok && feedback.option_id) sonarAcierto()
    ;(async () => {
      await Promise.all([decir([textoFrase(feedback.npc), fraseFeedback(feedback.ok, feedback.option_id)].join('. ')), pausa(700)])
      if (vigente) useJuego.getState().terminarFeedback()
    })()
    return () => {
      vigente = false
    }
  }, [feedback])

  const tocar = (id: string) => {
    if (!round || feedback || tocadoEn.current === round) return
    tocadoEn.current = round // un toque por ronda: evita dobles toques mientras llega el feedback
    const ms = msDesde(finVoz.current)
    enviar({ type: 'tap', option_id: id, ms })
  }

  const responder = (v: 'SI' | 'NO') => {
    useJuego.setState({ confirm: null, round: null }) // la ronda del tramo A ya no vale
    enviar({ type: 'answer', value: v })
  }

  const estadoDe = (o: Option): Estado => {
    if (feedback?.option_id === o.id) return feedback.ok ? 'ok' : 'no'
    if (round?.hint?.target === o.id) return round.hint.action === 'a4' ? 'mostrar' : 'resaltar'
    return 'normal'
  }

  const ia = seat === 'cliente' ? 'vendedor' : 'cliente'
  const banda = seat === 'cliente' ? 'bg-qhatu' : 'bg-indigo'
  const titulo = seat === 'cliente' ? 'Tú pides la comida' : 'Tú preparas la comida'

  // Lo que dice el personaje: feedback > confirmación > prompt
  let frase: Picto[] = round?.prompt ?? []
  if (confirm) frase = comoPregunta(confirm)
  if (feedback) frase = feedback.npc

  return (
    <div className="flex h-dvh flex-col bg-crema">
      {/* Banda de rol: color fuerte arriba, área de juego limpia abajo */}
      <header className={`relative ${banda} px-4 pt-3 pb-6 text-blanco transition-colors`}>
        <h1 className="text-center text-2xl font-black sm:text-3xl">{titulo}</h1>
        <svg
          viewBox="0 0 1200 24"
          preserveAspectRatio="none"
          className="absolute inset-x-0 -bottom-[23px] h-6 w-full"
          aria-hidden
        >
          <path d="M0 0h1200v8c-100 16-200 16-300 0s-200-16-300 0-200 16-300 0S100-8 0 8z" className={seat === 'cliente' ? 'fill-qhatu' : 'fill-indigo'} />
        </svg>
      </header>

      <main className="mx-auto flex min-h-0 w-full max-w-4xl flex-1 flex-col gap-4 px-4 pt-8 pb-4">
        {/* Personaje con su frase en pictos */}
        <section aria-live="polite" className="flex items-end gap-3">
          <Personaje rol={ia} />
          <div
            className={`relative flex min-w-0 flex-1 flex-col gap-2 rounded-tarjeta border-4 border-tinta bg-blanco p-3 shadow-bloque-sm ${frase.length || feedback || avisoRonda ? '' : 'invisible'}`}
          >
            {seat === 'vendedor' && pedido && !feedback && <FrasePictos pictos={pedido} />}
            {avisoRonda && !feedback && <p className="text-2xl font-bold">{avisoRonda}</p>}
            {feedback ? (
              <div className="flex flex-wrap items-center gap-3">
                <Sello ok={feedback.ok} />
                {frase.length > 0 && <FrasePictos pictos={frase} />}
                <p className="text-2xl font-bold">{fraseFeedback(feedback.ok, feedback.option_id)}</p>
              </div>
            ) : (
              frase.length > 0 && <FrasePictos pictos={frase} />
            )}
            {!feedback && !confirm && round?.hint?.speech && round.hint.action === 'a5' && (
              <p className="text-2xl font-bold">{round.hint.speech}</p>
            )}
          </div>
        </section>

        {/* Un solo foco: las opciones, o el plato que se confirma */}
        {confirm ? (
          <div className="grid flex-1 place-items-center">
            <Pictograma picto={confirm[confirm.length - 1]} />
          </div>
        ) : (
          round && (
            <ul
              className={`grid min-h-0 flex-1 auto-rows-fr gap-4 ${round.options.length > 1 ? 'grid-cols-2' : 'grid-cols-1'}`}
            >
              {round.options.slice(0, 4).map((o) => (
                <li key={o.id} className="min-h-0">
                  <TarjetaOpcion opcion={o} estado={estadoDe(o)} reducir={reducir} onTocar={() => tocar(o.id)} />
                </li>
              ))}
            </ul>
          )
        )}
      </main>

      <footer className="flex justify-center gap-4 border-t-4 border-tinta bg-blanco px-4 py-3">
        {confirm ? <BotonSiNo onRespuesta={responder} /> : <BotonAyuda onClick={() => enviar({ type: 'help' })} />}
      </footer>
    </div>
  )
}

function fraseFeedback(ok: boolean, optionId: string | null) {
  if (!optionId) return 'Está bien. Pide otra vez'
  return ok ? '¡Muy bien!' : 'Casi. Mira otra vez'
}

function Sello({ ok }: { ok: boolean }) {
  return (
    <span
      className={`grid size-16 shrink-0 place-items-center rounded-pildora border-4 border-tinta text-blanco ${ok ? 'bg-verde' : 'bg-tinta'}`}
    >
      {ok ? <IconoCheck className="size-9" /> : <IconoCruz className="size-9" />}
    </span>
  )
}

function TarjetaOpcion({
  opcion,
  estado,
  reducir,
  onTocar,
}: {
  opcion: Option
  estado: Estado
  reducir: boolean
  onTocar: () => void
}) {
  // Movimiento ≤ 300 ms; con prefers-reduced-motion solo cambia la opacidad
  const movimiento: Record<Estado, TargetAndTransition> = reducir
    ? {
        normal: { opacity: 1 },
        resaltar: { opacity: [1, 0.6, 1], transition: { duration: 0.3, repeat: 2 } },
        mostrar: { opacity: [1, 0.6, 1], transition: { duration: 0.3 } },
        ok: { opacity: [1, 0.7, 1], transition: { duration: 0.3 } },
        no: { opacity: [1, 0.7, 1], transition: { duration: 0.3 } },
      }
    : {
        normal: { y: 0, x: 0, scale: 1, opacity: 1 },
        resaltar: { opacity: 1, y: [0, -10, 0], transition: { duration: 0.3, repeat: 2, repeatDelay: 0.2 } },
        mostrar: { opacity: 1, scale: [1, 1.04, 1], transition: { duration: 0.3 } },
        ok: { opacity: 1, scale: [1, 1.06, 1], transition: { duration: 0.3 } },
        no: { opacity: 1, x: [0, -6, 6, 0], transition: { duration: 0.3 } },
      }

  const marco = {
    normal: 'border-tinta',
    resaltar: 'border-tinta ring-8 ring-naranja',
    mostrar: 'border-tinta ring-8 ring-verde',
    ok: 'border-tinta ring-8 ring-verde',
    no: 'border-tinta border-dashed',
  }[estado]
  const extra = { normal: '', resaltar: ', mira aquí', mostrar: ', esta es', ok: ', bien', no: ', otra vez' }[estado]

  return (
    <motion.button
      type="button"
      onClick={onTocar}
      aria-label={`${opcion.label}${extra}`}
      initial={{ opacity: 0 }}
      animate={movimiento[estado]}
      transition={{ duration: 0.2 }}
      className={`relative flex h-full min-h-24 w-full flex-col items-center justify-center gap-2 rounded-tarjeta border-4 bg-blanco p-3 shadow-bloque active:translate-y-1.5 active:shadow-none ${marco}`}
    >
      {/* Sin imagen (aún no descargada o rota) la etiqueta queda sola y centrada */}
      <span className="flex min-h-0 w-full items-center justify-center gap-2 has-[img]:flex-1">
        {opcion.pictos.map((p) => (
          <ImagenPicto key={p.id} picto={p} className="h-full max-h-40 w-auto max-w-[48%] flex-1" />
        ))}
      </span>
      <span className="text-center text-2xl leading-tight font-bold uppercase sm:text-3xl">{opcion.label}</span>
      <Insignia estado={estado} />
    </motion.button>
  )
}

/** Cada estado lleva ícono además de color (§8). */
function Insignia({ estado }: { estado: Estado }) {
  const base = 'absolute -top-4 -right-3 flex items-center gap-1 rounded-pildora border-4 border-tinta px-3 py-1 font-titulo text-xl font-black'
  switch (estado) {
    case 'resaltar':
      return (
        <span className={`${base} bg-maiz text-tinta`} aria-hidden>
          <IconoMira className="size-7" />
        </span>
      )
    case 'mostrar':
      return (
        <span className={`${base} bg-verde text-blanco`} aria-hidden>
          <IconoCheck className="size-7" /> ESTA ES
        </span>
      )
    case 'ok':
      return (
        <span className={`${base} bg-verde text-blanco`} aria-hidden>
          <IconoCheck className="size-8" />
        </span>
      )
    case 'no':
      return (
        <span className={`${base} bg-tinta text-blanco`} aria-hidden>
          <IconoCruz className="size-8" />
        </span>
      )
    default:
      return null
  }
}
