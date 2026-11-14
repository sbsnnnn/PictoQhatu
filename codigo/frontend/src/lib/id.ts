// Id aleatorio de 32 hex. No usa crypto.randomUUID: solo existe en https o localhost, y las tablets entran por http://IP.
export const nuevoId = () =>
  Array.from(crypto.getRandomValues(new Uint8Array(16)), (b) => b.toString(16).padStart(2, '0')).join('')

