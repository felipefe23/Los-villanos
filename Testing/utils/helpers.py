from flask import request
import base64

# Funcionamiento: Helper para peticiones de API.
# Revisa las cabeceras HTTP (Accept) para determinar si el cliente (ej. un frontend) prefiere una respuesta JSON en lugar de HTML.
# Se usa para enviar errores JSON (401/403) en vez de redirigir a una página.
def _prefers_json():
    best = request.accept_mimetypes.best
    if not best:
        return False
    if best != 'application/json':
        return False
    return request.accept_mimetypes[best] >= request.accept_mimetypes['text/html']


# Funcionamiento: Toma la ruta de un archivo (ej. una imagen).
# Lee el contenido binario (bytes) de ese archivo.
# Codifica esos bytes en un string de texto Base64 y lo retorna.
def convertir_a_base64(ruta_imagen):
    with open(ruta_imagen, "rb") as img:
        return base64.b64encode(img.read()).decode("utf-8")
