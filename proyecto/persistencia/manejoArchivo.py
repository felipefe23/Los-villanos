# persistencia/manejoArchivo.py

import json
import os

RUTA_ARCHIVO = os.path.join('datos', 'propiedades.json')

def leer_propiedades():
    """
    Lee el archivo JSON y retorna una lista de propiedades.
    Si el archivo no existe o esta vacio, retorna una lista vacia.
    """
    if not os.path.exists(RUTA_ARCHIVO):
        return []

    try:
        with open(RUTA_ARCHIVO, 'r', encoding='utf-8') as archivo:
            contenido = archivo.read().strip()
            if not contenido:
                return []
            return json.loads(contenido)
    except (json.JSONDecodeError, IOError) as error:
        print(f"[Error al leer JSON] {error}")
        return []

def guardar_propiedades(lista_propiedades):
    """
    Guarda la lista de propiedades en el archivo JSON.
    Sobrescribe el contenido anterior.
    """
    try:
        with open(RUTA_ARCHIVO, 'w', encoding='utf-8') as archivo:
            json.dump(lista_propiedades, archivo, indent=2, ensure_ascii=False)
    except IOError as error:
        print(f"[Error al guardar JSON] {error}")

if __name__ == '__main__':
    propiedades = leer_propiedades()
    print(propiedades)

