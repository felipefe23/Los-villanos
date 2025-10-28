import re
from persistencia.base_datos import obtener_usuarios

# Funciones que se utilizan en la ruta de los usuarios

TIPOS_USUARIO_PERMITIDOS = {
    "admin": "admin",
    "administrador": "admin",
    "vendedor": "vendedor",
    "comprador": "comprador"
}
def validar_email(email):
    # Mínimo 2 caracteres antes del @ y formato básico
    return re.match(r'^[^@]{2,}@[^@]+\.[^@]+$', email)

def validar_password(password):
    # Al menos 8 caracteres y 1 número
    return re.match(r'^(?=.*\d).{8,}$', password)

def leer_usuarios():
    return obtener_usuarios()

def rol_legible(tipo_usuario):
    if not tipo_usuario:
        return "desconocido"
    # Si el tipo_usuario ya no está hasheado, devolver directamente
    tipo_limpio = str(tipo_usuario).strip().lower()
    return TIPOS_USUARIO_PERMITIDOS.get(tipo_limpio, tipo_limpio)
