from flask import request
import base64
import httpx

VALOR_UF_RESPALDO = 37500.0

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


# Funcionamiento: Obtiene el valor actual de la UF desde la API de Mindicador.cl.
# Si la API no responde o hay un error, retorna un valor de respaldo.
def obtener_valor_uf_actual():
    try:
        # Hacemos la llamada a la API con un timeout corto (5 seg)
        r = httpx.get('https://mindicador.cl/api/uf', timeout=5.0)
        
        # Esto lanzará un error si la API responde con 404, 500, etc.
        r.raise_for_status() 
        
        data = r.json()
        
        # Obtenemos el valor del primer item de la serie
        valor_uf = data['serie'][0]['valor']
        
        # Nos aseguramos de que sea un número (float)
        return float(valor_uf)
        
    except Exception as e:
        # Si algo falla (timeout, error 500, JSON malformado),
        # imprimimos una advertencia en tu consola y usamos el valor de respaldo.
        print(f"ADVERTENCIA: No se pudo obtener el valor de la UF. Usando valor de respaldo. Error: {e}")
        return VALOR_UF_RESPALDO