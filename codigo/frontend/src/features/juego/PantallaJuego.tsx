import { motion, useReducedMotion, type TargetAndTransition } from 'motion/react'
import { useEffect, useRef, type CSSProperties } from 'react'
import { BotonAyuda } from '../../components/BotonAyuda'
import { BotonRepetir } from '../../components/BotonRepetir'
import { BotonSiNo } from '../../components/BotonSiNo'
import { Burbuja } from '../../components/Burbuja'
import { Canasta } from '../../components/Canasta'
import { EncabezadoRol } from '../../components/EncabezadoRol'
import { FrasePictos } from '../../components/FrasePictos'
import { IconoAltavoz, IconoAyuda, IconoCheck, IconoCruz } from '../../components/Iconos'
import { Personaje } from '../../components/Personaje'
import { Plato } from '../../components/Plato'
import { TarjetaPaso } from '../../components/TarjetaPaso'
import { ImagenPicto, Pictograma } from '../../components/Pictograma'
import type { MensajeCliente, Option, Picto } from '../../lib/protocol'
import { sonarAcierto } from '../../lib/sonido'
import { anchoEm } from '../../lib/etiqueta'
import { decir, textoFrase } from '../../lib/tts'
import { FrasePregunta } from './FrasePregunta'
import { PistaAtributo, PistaMira } from './PistaAyuda'
import { useJuego } from './store'

type Estado = 'normal' | 'resaltar' | 'mostrar' | 'ok' | 'no'

/** ms desde que terminó la voz del prompt; 0 si se toca antes. */
const msDesde = (t: number | null) => (t === null ? 0 : Math.round(performance.now() - t))

const pausa = (ms: number) => new Promise((r) => setTimeout(r, ms))

/** [QUIERO] del confirm se muestra como [QUIERES]: es la IA vendedora la que pregunta. Sin "¿?" en las etiquetas. */
const comoPregunta = (prompt: Picto[]): Picto[] => prompt.map((p) => (p.id === 'QUIERO' ? { ...p, label: 'QUIERES' } : p))

export function PantallaJuego({ enviar }: { enviar: (m: MensajeCliente) => void }) {
  const seat = useJuego((s) => s.seat) ?? 'cliente'
  const round = useJuego((s) => s.round)
  const avisoRonda = useJuego((s) => s.avisoRonda)
  const feedback = useJuego((s) => s.feedback)
  const confirm = useJuego((s) => s.confirm)
  const pedido = useJuego((s) => s.pedido)
  const reducir = useReducedMotion() ?? false
  // [QUIERO, SÁNDWICH] del confirm se dice como pregunta: ¿QUIERES SÁNDWICH?
  const pregunta = confirm ? `¿${textoFrase(comoPregunta(confirm))}?` : ''

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
    if (pregunta) decir(pregunta)
  }, [pregunta])

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
  const canasta = useJuego((s) => s.canasta)
  const plato = useJuego((s) => s.plato)

  // Burbuja: el cliente ve la pregunta o el prompt; el vendedor, el pedido de la IA clienta
  const vendedor = seat === 'vendedor'
  let burbuja: Picto[] = vendedor ? (pedido ?? []) : (round?.prompt ?? [])
  if (confirm) burbuja = comoPregunta(confirm)
  // El paso que se prepara ahora ([PONER] + [POLLO]) va aparte, en su tarjeta
  const paso = vendedor && round && !confirm ? round.prompt : null
  const hecho = vendedor && !!feedback?.ok && !!feedback.option_id
  const ayuda = !feedback && !confirm ? round?.hint : null
  const pista = ayuda?.action === 'a5' ? ayuda.speech : ''
  // a1 (volver a decir): la frase dicha se enmarca en maíz mientras dura la ronda
  const eco = ayuda?.action === 'a1' ? 'ring-8 ring-maiz' : ''
  // En tablet horizontal la burbuja muestra la pista (como en el diseño): ¡MIRA! + el picto de la respuesta (a2/a4)
  // o el atributo (a5). En una columna el a5 ocupa el lugar del plato o la canasta: no le quita alto a las tarjetas.
  const mira = ayuda?.target ? round?.options.find((o) => o.id === ayuda.target)?.pictos.at(-1) : undefined

  // Mismo tamaño de etiqueta en todas las tarjetas de la ronda: lo fija la palabra más larga
  const letras = Math.max(2, ...(round?.options ?? []).flatMap((o) => o.label.split(' ').map(anchoEm)))

  const repetir = () => decir(textoFrase(paso ? [...burbuja, ...paso] : burbuja))

  return (
    <div className="flex h-dvh flex-col overflow-hidden bg-crema">
      <EncabezadoRol seat={seat} />
      {/* El cambio de rol y las pistas de atributo se dicen en voz alta; aquí quedan para el lector de pantalla */}
      <p aria-live="polite" className="sr-only">
        {[avisoRonda, pista].filter(Boolean).join('. ')}
      </p>

      {/* Tablet horizontal: personaje | tarjetas | panel. Una columna en móvil y tablet vertical. */}
      <main className="flex min-h-0 flex-1 flex-col gap-3 px-4 pt-3 bajo:gap-2 bajo:pt-2 lg:grid lg:grid-cols-[minmax(15rem,23rem)_minmax(26rem,1fr)_minmax(10rem,13rem)] lg:grid-rows-[minmax(0,1fr)] lg:gap-x-6 lg:px-6 lg:pt-4">
        <div className="flex shrink-0 flex-col gap-5 lg:min-h-0 lg:justify-center">
          <section aria-live="polite" className="flex items-center gap-5 lg:flex-col lg:items-start">
            <div className="flex shrink-0 items-center gap-6 lg:ml-6">
              <Personaje rol={ia} className="h-24 w-14 bajo:h-14 bajo:w-10 lg:h-36 lg:w-28" />
              {/* Vendedor en tablet horizontal: la respuesta del cliente va junto a él y la burbuja sigue con el pedido */}
              {vendedor && feedback?.option_id && <Respuesta ok={feedback.ok} className="max-lg:hidden" />}
            </div>
            <Burbuja
              className={`min-w-0 flex-1 lg:w-full lg:flex-none ${burbuja.length || feedback ? '' : 'invisible'} ${paso && !feedback ? 'max-lg:hidden' : ''} ${eco}`}
            >
              {vendedor && feedback?.option_id && (
                <div className="max-lg:hidden">
                  <FrasePictos pictos={burbuja} />
                </div>
              )}
              {feedback ? (
                <div className={`flex min-w-0 items-center justify-center gap-3 ${vendedor && feedback.option_id ? 'lg:hidden' : ''}`}>
                  <Sello ok={feedback.ok} />
                  {feedback.npc.length > 0 && (
                    <div className="w-24 shrink-0 lg:w-28">
                      <FrasePictos pictos={feedback.npc} altavoz={false} />
                    </div>
                  )}
                  <p className="min-w-0 text-center text-2xl leading-tight font-bold max-sm:sr-only">{fraseFeedback(feedback.ok, feedback.option_id)}</p>
                </div>
              ) : confirm ? (
                <FrasePregunta pictos={burbuja} dicho={pregunta} />
              ) : mira || pista ? (
                <>
                  <div className="lg:hidden">
                    <FrasePictos pictos={burbuja} />
                  </div>
                  {pista ? <PistaAtributo texto={pista} className="max-lg:hidden" /> : mira && <PistaMira picto={mira} className="max-lg:hidden" />}
                </>
              ) : (
                <FrasePictos pictos={burbuja} />
              )}
            </Burbuja>
            {/* En una columna el paso ocupa el lugar de la burbuja (el pedido queda en EL PLATO): así las tarjetas
                miden lo mismo que en el cliente. La burbuja vuelve para la respuesta del cliente. */}
            {paso && !feedback && <TarjetaPaso pictos={paso} className={`min-w-0 flex-1 lg:hidden ${eco}`} />}
          </section>
          {paso && <TarjetaPaso pictos={paso} hecho={hecho} className={`max-lg:hidden ${eco}`} />}
        </div>

        {/* Tarjetas de tamaño fijo (proporción 220×244) que se achican solo si no caben; nunca se estiran */}
        <div className="min-h-0 flex-1 px-3 pt-4 pb-1 [container-type:size] lg:h-full">
          {confirm ? (
            <div className="grid h-full grid-cols-[minmax(0,1fr)_auto] place-items-center gap-6">
              <Pictograma picto={confirm[confirm.length - 1]} />
              <button
                type="button"
                onClick={() => decir(pregunta)}
                aria-label={`Escuchar: ${pregunta}`}
                className="grid size-24 shrink-0 place-items-center rounded-pildora border-4 border-tinta bg-maiz text-tinta shadow-suave-sm active:translate-y-1 active:shadow-none"
              >
                <IconoAltavoz className="size-10" />
              </button>
            </div>
          ) : (
            <ul
              className="mx-auto flex h-full max-w-[calc(var(--carta)*2+var(--hueco))] flex-wrap content-center justify-center gap-(--hueco) [--carta:min(13.75rem,calc((100cqw-var(--hueco))/2),calc((100cqh-var(--hueco))/2*0.9))] [--hueco:1rem] lg:[--hueco:1.5rem]"
            >
              {round?.options.slice(0, 4).map((o) => (
                <li key={o.id} className="aspect-[220/244] w-(--carta)">
                  <TarjetaOpcion opcion={o} letras={letras} estado={estadoDe(o)} reducir={reducir} onTocar={() => tocar(o.id)} />
                </li>
              ))}
            </ul>
          )}
        </div>

        {/* Panel: la canasta del cliente o el plato del vendedor (fila de 4 casillas en una columna) */}
        <div className="flex h-24 shrink-0 items-center justify-center bajo:h-16 lg:h-auto lg:self-center">
          {pista && (
            <PistaAtributo
              texto={pista}
              className="rounded-pildora border-4 border-tinta bg-blanco py-1 pr-5 pl-1 shadow-suave-sm lg:hidden"
            />
          )}
          <div className={`contents ${pista ? 'max-lg:hidden' : ''}`}>
            {vendedor ? <Plato pictos={plato} recien={hecho} pedido={pedido?.at(-1)} /> : <Canasta pictos={canasta} />}
          </div>
        </div>
      </main>

      <footer className="shrink-0 px-4 pt-3 pb-4 bajo:pt-2 bajo:pb-3 sm:pb-6">
        <div className="mx-auto grid max-w-2xl grid-cols-[1.15fr_1fr] gap-3 lg:flex lg:max-w-none lg:justify-center lg:gap-8">
          {confirm ? (
            <div className="col-span-2 flex justify-center">
              <BotonSiNo onRespuesta={responder} />
            </div>
          ) : (
            <>
              <BotonAyuda onClick={() => enviar({ type: 'help' })} className="lg:w-80" />
              <BotonRepetir onClick={repetir} className="lg:w-72" />
            </>
          )}
        </div>
      </footer>
    </div>
  )
}

/** ✓ ¡SÍ! (verde) o ✗ NO (tinta) junto al cliente: ícono + palabra, nunca solo color. */
function Respuesta({ ok, className = '' }: { ok: boolean; className?: string }) {
  return (
    <p className={`flex flex-col items-center font-titulo text-4xl font-black ${ok ? 'text-verde' : 'text-tinta'} ${className}`}>
      {ok ? <IconoCheck className="size-12" /> : <IconoCruz className="size-12" />}
      {ok ? '¡SÍ!' : 'NO'}
    </p>
  )
}

function fraseFeedback(ok: boolean, optionId: string | null) {
  if (!optionId) return 'Está bien. Pide otra vez'
  return ok ? '¡Muy bien!' : 'Casi. Mira otra vez'
}

function Sello({ ok }: { ok: boolean }) {
  return (
    <span
      className={`grid size-16 shrink-0 place-items-center rounded-pildora border-4 border-tinta text-blanco bajo:size-14 ${ok ? 'bg-verde' : 'bg-tinta'}`}
    >
      {ok ? <IconoCheck className="size-9" /> : <IconoCruz className="size-9" />}
    </span>
  )
}

function TarjetaOpcion({
  opcion,
  letras,
  estado,
  reducir,
  onTocar,
}: {
  opcion: Option
  letras: number
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
        normal: { y: 0, x: 0, opacity: 1 },
        resaltar: { opacity: 1, y: [0, -10, 0], transition: { duration: 0.3, repeat: 2, repeatDelay: 0.2 } },
        // solo hacia arriba o a la izquierda: un rebote nunca desborda la columna
        mostrar: { opacity: 1, y: [0, -6, 0], transition: { duration: 0.3 } },
        ok: { opacity: 1, y: [0, -10, 0], transition: { duration: 0.3 } },
        no: { opacity: 1, x: [0, -8, 0, -4, 0], transition: { duration: 0.3 } },
      }

  const marco = {
    normal: 'border-tinta',
    resaltar: 'border-tinta ring-8 ring-maiz',
    mostrar: 'border-tinta ring-8 ring-verde',
    ok: 'border-verde',
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
      className={`@container relative flex size-full flex-col items-center justify-center gap-1 rounded-tarjeta border-4 bg-crema p-2 shadow-suave sm:p-3 active:translate-y-1.5 active:shadow-none ${marco}`}
    >
      {/* Sin imagen (aún no descargada o rota) la etiqueta queda sola y centrada */}
      <span className="flex min-h-0 w-full flex-1 items-center justify-center gap-2">
        {opcion.pictos.map((p) => (
          <ImagenPicto key={p.id} picto={p} className={`h-full min-w-0 flex-1 ${opcion.pictos.length > 1 ? 'max-w-[48%]' : 'max-w-full'}`} />
        ))}
      </span>
      <span
        // "PONER LECHUGA" parte en dos líneas; la palabra más ancha de la ronda fija el tamaño de todas (lib/etiqueta.ts)
        style={{ '--em': letras } as CSSProperties}
        className="w-full px-2 text-center text-[min(1.875rem,calc((100cqw-1rem)/var(--em)))] leading-tight font-bold uppercase"
      >
        {opcion.label}
      </span>
      <Insignia estado={estado} />
    </motion.button>
  )
}

/** Cada estado lleva ícono además de color (§8). */
function Insignia({ estado }: { estado: Estado }) {
  const base = 'absolute -top-4 right-2 flex items-center gap-1 rounded-pildora border-4 border-tinta px-3 py-1 font-titulo text-xl font-black'
  switch (estado) {
    case 'resaltar':
      return (
        <span className={`${base} bg-naranja text-tinta`} aria-hidden>
          <IconoAyuda className="size-7" />
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
        <span className="absolute -top-4 right-2 grid size-14 place-items-center rounded-full border-4 border-tinta bg-verde text-blanco" aria-hidden>
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
