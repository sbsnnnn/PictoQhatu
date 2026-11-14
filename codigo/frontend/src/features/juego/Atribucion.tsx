/** Atribución obligatoria de ARASAAC (CC BY-NC-SA), visible en la app (§2). */
export function Atribucion({ className = '' }: { className?: string }) {
  return (
    <p className={`px-4 py-3 text-center text-base ${className}`}>
      Pictogramas: Sergio Palao. Origen: ARASAAC (arasaac.org). Licencia: CC BY-NC-SA. Propiedad: Gobierno de Aragón
      (España).
    </p>
  )
}
