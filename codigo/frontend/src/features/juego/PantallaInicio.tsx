import { useState } from 'react'
import { IconoCheck } from '../../components/Iconos'
import { ImagenPicto } from '../../components/Pictograma'
import type { MensajeCliente, Picto } from '../../lib/protocol'
import { leerToken } from '../../lib/socket'
import { desbloquearVoz } from '../../lib/tts'
import { Atribucion } from './Atribucion'
import { useJuego } from './store'

// Avatar = un picto de ingrediente (no se guardan datos personales, §2). Máximo 4 opciones.
const AVATARES: Picto[] = [
  { id: 'manzana', label: 'MANZANA', img: '/pictos/manzana.png' },
  { id: 'platano', label: 'PLÁTANO', img: '/pictos/platano.png' },
  { id: 'pan', label: 'PAN', img: '/pictos/pan.png' },
  { id: 'queso', label: 'QUESO', img: '/pictos/queso.png' },
]

export function PantallaInicio({ enviar }: { enviar: (m: MensajeCliente) => void }) {
  const [alias, setAlias] = useState('')
  const [avatar, setAvatar] = useState(AVATARES[0].id)

  const jugar = () => {
    desbloquearVoz() // primer toque: los navegadores solo permiten la voz después de un gesto
    useJuego.setState({ aviso: 'Vamos a jugar' }) // se dice antes del primer prompt; suelto, el prompt lo cortaba
    enviar({ type: 'join', alias: alias.trim().slice(0, 20), avatar, seat_token: leerToken() })
  }

  return (
    <div className="flex min-h-dvh flex-col bg-qhatu text-blanco">
      <main className="mx-auto flex w-full max-w-3xl flex-1 flex-col items-center justify-center gap-8 px-4 py-8">
        <h1 className="text-center text-6xl font-black tracking-tight sm:text-7xl">PictoQhatu</h1>
        <p className="text-center text-2xl">El puesto de comida del mercado</p>

        <div className="flex w-full flex-col gap-5 rounded-tarjeta border-4 border-tinta bg-crema p-5 text-tinta shadow-bloque sm:p-7">
          <label className="flex flex-col gap-2 text-2xl font-bold">
            Tu nombre (si quieres)
            <input
              value={alias}
              onChange={(e) => setAlias(e.target.value)}
              maxLength={20}
              autoComplete="off"
              className="min-h-16 rounded-pildora border-4 border-tinta bg-blanco px-5 text-2xl"
            />
          </label>

          <fieldset className="flex flex-col gap-3">
            <legend className="mb-2 text-2xl font-bold">Elige tu dibujo</legend>
            <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
              {AVATARES.map((p) => {
                const elegido = p.id === avatar
                return (
                  <button
                    key={p.id}
                    type="button"
                    aria-pressed={elegido}
                    onClick={() => setAvatar(p.id)}
                    className={`relative flex min-h-32 flex-col items-center justify-center gap-1 rounded-tarjeta border-4 border-tinta bg-blanco p-2 ${elegido ? 'ring-8 ring-maiz' : ''}`}
                  >
                    <ImagenPicto picto={p} className="h-16 w-full" />
                    <span className="text-2xl font-bold">{p.label}</span>
                    {elegido && (
                      <span className="absolute -top-3 -right-3 grid size-11 place-items-center rounded-pildora border-4 border-tinta bg-verde text-blanco">
                        <IconoCheck className="size-6" />
                      </span>
                    )}
                  </button>
                )
              })}
            </div>
          </fieldset>
        </div>

        <button
          type="button"
          onClick={jugar}
          className="min-h-28 w-full max-w-md rounded-pildora border-4 border-tinta bg-maiz px-10 font-titulo text-5xl font-black text-tinta shadow-bloque active:translate-y-1.5 active:shadow-none"
        >
          JUGAR
        </button>
      </main>
      <Atribucion className="text-blanco" />
    </div>
  )
}
