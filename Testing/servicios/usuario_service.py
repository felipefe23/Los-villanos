import re
from persistencia.base_datos import obtener_usuarios

# Funciones que se utilizan en la ruta de los usuarios

# Funcionamiento: Un diccionario para estandarizar roles.
# Permite que 'administrador' sea tratado igual que 'admin'.
# Se usa para limpiar y validar los tipos de usuario.
TIPOS_USUARIO_PERMITIDOS = {
    "admin": "admin",
    "administrador": "admin",
    "vendedor": "vendedor",
    "comprador": "comprador"
}


# Funcionamiento: Valida un string de email usando Regex.
# Exige al menos 2 caracteres antes del '@'.
# Verifica un formato básico (ej. a@b.c).
def validar_email(email):
    # Mínimo 2 caracteres antes del @ y formato básico
    return re.match(r'^[^@]{2,}@[^@]+\.[^@]+$', email)


# Funcionamiento: Valida un string de password usando Regex.
# Exige un largo mínimo de 8 caracteres.
# También exige que contenga al menos un número.
def validar_password(password):
    # Al menos 8 caracteres y 1 número
    return re.match(r'^(?=.*\d).{8,}$', password)


# Funcionamiento: Abstracción simple para leer usuarios.
# Llama a 'obtener_usuarios' de la capa de
# persistencia (base_datos.py) y retorna la lista.
def leer_usuarios():
    return obtener_usuarios()


# Funcionamiento: Convierte un rol (ej. "administrador") a su versión canónica (ej. "admin").
# Usa el diccionario 'TIPOS_USUARIO_PERMITIDOS' para hacer la traducción.
def rol_legible(tipo_usuario):
    if not tipo_usuario:
        return "desconocido"
    # Si el tipo_usuario ya no está hasheado, devolver directamente
    tipo_limpio = str(tipo_usuario).strip().lower()
    return TIPOS_USUARIO_PERMITIDOS.get(tipo_limpio, tipo_limpio)
