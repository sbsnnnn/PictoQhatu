"""
descargar_arasaac.py
--------------------
Descarga los pictogramas de ARASAAC (CC BY-NC-SA) a datos/catalogo/ y completa
los arasaac_id de pictos.json.

  - Si un picto ya tiene arasaac_id, se respeta (así se fija a mano).
  - Si no, se busca por su etiqueta (o por TERMINOS) y se toma el primer resultado.
  - No vuelve a descargar una imagen que ya existe.

Uso (desde la carpeta codigo/):
    python -m ia_models.env.descargar_arasaac
"""

import json
import urllib.parse
import urllib.request
from pathlib import Path

from ia_models.env.catalogo import CARPETA_DATOS

URL_BUSQUEDA = "https://api.arasaac.org/v1/pictograms/es/search/"
URL_IMAGEN = "https://static.arasaac.org/pictograms/{id}/{id}_500.png"
AGENTE_HTTP = {"User-Agent": "PictoQhatu-descarga/1.0"}

# Término de búsqueda cuando la etiqueta no da el pictograma correcto como primer resultado
TERMINOS = {
    "palta": "aguacate",
    "AYUDA": "ayudar",                  # "ayuda" devuelve primero "apoyo"
}
# Ids fijos cuando ningún término sirve: "naranja" devuelve primero el color y
# no hay "arroz con pollo" (27945 es paella de pollo; "paella" da primero la de mariscos)
IDS_FIJOS = {"naranja": 2483, "arroz_con_pollo": 27945}


def _buscar(termino):
    url = URL_BUSQUEDA + urllib.parse.quote(termino)
    with urllib.request.urlopen(urllib.request.Request(url, headers=AGENTE_HTTP), timeout=30) as r:
        return json.load(r)


def _bajar(id_arasaac):
    url = URL_IMAGEN.format(id=id_arasaac)
    with urllib.request.urlopen(urllib.request.Request(url, headers=AGENTE_HTTP), timeout=30) as r:
        return r.read()


def elegir_id(id_picto, picto, buscar=_buscar):
    if picto["arasaac_id"] is not None:
        return picto["arasaac_id"]
    if id_picto in IDS_FIJOS:
        return IDS_FIJOS[id_picto]
    return buscar(TERMINOS.get(id_picto, picto["etiqueta"].lower()))[0]["_id"]


def descargar_todo(ruta_json, carpeta, buscar=_buscar, bajar=_bajar):
    ruta_json, carpeta = Path(ruta_json), Path(carpeta)
    datos = json.loads(ruta_json.read_text(encoding="utf-8"))
    for grupo in datos.values():
        for id_picto, picto in grupo.items():
            picto["arasaac_id"] = elegir_id(id_picto, picto, buscar)
            destino = carpeta / Path(picto["img"]).name
            if not destino.exists():
                destino.write_bytes(bajar(picto["arasaac_id"]))
            print(f"  {id_picto:<16} -> {picto['arasaac_id']:>6}  {destino.name}")
            # se guarda tras cada picto: si la red falla a mitad, no se pierden los ids ya elegidos
            ruta_json.write_text(json.dumps(datos, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    carpeta = CARPETA_DATOS / "catalogo"
    descargar_todo(carpeta / "pictos.json", carpeta)


if __name__ == "__main__":
    main()
