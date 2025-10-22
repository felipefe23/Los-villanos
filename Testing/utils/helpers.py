from flask import request
import base64

def _prefers_json():
    best = request.accept_mimetypes.best
    if not best:
        return False
    if best != 'application/json':
        return False
    return request.accept_mimetypes[best] >= request.accept_mimetypes['text/html']

def convertir_a_base64(ruta_imagen):
    with open(ruta_imagen, "rb") as img:
        return base64.b64encode(img.read()).decode("utf-8")
