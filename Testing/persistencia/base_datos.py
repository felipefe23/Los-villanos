import json
import os
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv
from pathlib import Path

# CARGA DEL ARCHIVO .env DE FORMA FIABLE

_script_path = Path(__file__).resolve()
_env_candidates = []

for idx in (1, 2):
    try:
        _env_candidates.append(_script_path.parents[idx] / ".env")
    except IndexError:
        pass

_env_candidates.append(Path.cwd() / ".env")

dotenv_path = next((path for path in _env_candidates if path.exists()), None)

if dotenv_path:
    load_dotenv(dotenv_path=dotenv_path)
    print(f"Archivo .env cargado desde: {dotenv_path}")
else:
    print("No se encontró el archivo .env en las ubicaciones esperadas.")


# IMPORTACIÓN DE SUPABASE

try:
    from supabase import create_client, Client
except ImportError as exc:
    raise RuntimeError(
        "No se pudo importar la librería 'supabase'. "
        "Instálala con: pip install supabase"
    ) from exc

# VARIABLES DE ENTORNO

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError(
        "Las variables SUPABASE_URL o SUPABASE_SERVICE_KEY no están configuradas correctamente en el .env"
    )

print("Variables de entorno cargadas correctamente.")

# CONFIGURACIÓN DE RUTAS

BASE_DIR = Path(__file__).resolve().parents[1] / "datos"
USERS_JSON = BASE_DIR / "users.json"
PROPIEDADES_JSON = BASE_DIR / "propiedades.json"

USERS_TABLE = os.getenv("SUPABASE_USERS_TABLE", "users")
PROPIEDADES_TABLE = os.getenv("SUPABASE_PROPIEDADES_TABLE", "propiedades")

# CLIENTE SUPABASE

_client: Optional["Client"] = None

def _get_client() -> "Client":
    global _client
    if _client is None:
        print("Conectando con Supabase")
        
        # Creación simple del cliente
        _client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Retornara advertencias debido a que es un metodo "obsoleto"
        _client.postgrest.timeout = 10.0

        print(f"Conectado a Supabase. Timeout configurado a 10s.")
    return _client

# UTILIDADES INTERNAS

def _handle_response(response: Any) -> List[Dict[str, Any]]:
    if hasattr(response, "error") and response.error:
        # Evita mostrar mensajes en la consola
        # raise RuntimeError(f"Error de Supabase: {response.error}")
        return [] 
    if hasattr(response, "data"):
        return response.data or []
    return []

def _cargar_json(ruta: Path) -> List[Dict[str, Any]]:
    if not ruta.exists():
        return []
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            contenido = f.read().strip()
            return json.loads(contenido) if contenido else []
    except Exception as e:
        print(f"Error al leer {ruta.name}: {e}")
        return []

# MIGRACIÓN DE DATOS

# Funcionamiento: Inicializa la base de datos (seeding).
# Si 'seed_from_files' es True, lee los archivos locales 'users.json' y 'propiedades.json'.
# Sube (upsert) esos datos a las tablas de Supabase para poblar la base de datos.
def init_db(seed_from_files: bool = True) -> None:
    client = _get_client()
    if not seed_from_files:
        return

    try:
        usuarios = _cargar_json(USERS_JSON)
        propiedades = _cargar_json(PROPIEDADES_JSON)
        if usuarios:
            client.table(USERS_TABLE).upsert(usuarios, on_conflict="id").execute()
            print(f"{len(usuarios)} usuarios migrados.")
        if propiedades:
            client.table(PROPIEDADES_TABLE).upsert(propiedades, on_conflict="id").execute()
            print(f"{len(propiedades)} propiedades migradas.")
    except Exception as e:
        print(f"Error en la migración: {e}")

# CRUD DE USUARIOS (Crear, Obtener, Actualizar, Eliminar)

# Funcionamiento: Recibe un diccionario (usuario).
# Inserta ese diccionario como un nuevo registro en la tabla de usuarios de Supabase.
# Retorna el objeto del usuario recién creado.
def crear_usuario(usuario: Dict[str, Any]) -> Dict[str, Any]:
    client = _get_client()
    payload = usuario.copy()
    response = client.table(USERS_TABLE).insert(payload).execute()
    data = _handle_response(response)
    return data[0] if data else payload


# Funcionamiento: Realiza un 'SELECT *' a la tabla de usuarios en Supabase.
# Retorna una lista con todos los usuarios, ordenados por su ID.
def obtener_usuarios() -> List[Dict[str, Any]]:
    client = _get_client()
    response = client.table(USERS_TABLE).select("*").order("id").execute()
    return _handle_response(response)


# Funcionamiento: Busca en Supabase un usuario donde el 'id' coincida con el 'user_id' recibido.
# Retorna el diccionario del usuario si lo encuentra, o None si no existe.
def obtener_usuario_por_id(user_id: int) -> Optional[Dict[str, Any]]:
    client = _get_client()
    response = (
        client.table(USERS_TABLE)
        .select("*")
        .eq("id", user_id)
        .limit(1)
        .execute()
    )
    data = _handle_response(response)
    return data[0] if data else None


# Funcionamiento: Normaliza el email (minúsculas, sin espacios).
# Busca en Supabase un usuario donde el 'email' coincida.
# Retorna el diccionario del usuario si lo encuentra, o None si no existe.
def obtener_usuario_por_email(email: str) -> Optional[Dict[str, Any]]:
    email = (email or "").strip().lower()
    if not email:
        return None
    client = _get_client()
    response = (
        client.table(USERS_TABLE)
        .select("*")
        .eq("email", email)
        .limit(1)
        .execute()
    )
    data = _handle_response(response)
    return data[0] if data else None


# Funcionamiento: Recibe el 'user_id' y un diccionario con los 'cambios' a aplicar.
# Ejecuta un 'update' en Supabase para actualizar solo esos campos en el usuario correspondiente.
# Retorna el objeto del usuario ya actualizado.
def actualizar_usuario(user_id: int, cambios: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    client = _get_client()
    if not cambios:
        return obtener_usuario_por_id(user_id)

    response = (
        client.table(USERS_TABLE)
        .update(cambios)
        .eq("id", user_id)
        .execute()
    )
    data = _handle_response(response)
    return data[0] if data else obtener_usuario_por_id(user_id)


# Funcionamiento: Ejecuta un 'delete' en Supabase para eliminar al usuario que coincida con el 'user_id' especificado.
# Retorna True si la operación se completó.
def eliminar_usuario(user_id: int) -> bool: 
    client = _get_client()
    response = client.table(USERS_TABLE).delete().eq("id", user_id).execute()
    _handle_response(response)
    return True

# CRUD DE PROPIEDADES (Crear, Obtener, Actualizar, Eliminar)

# Funcionamiento: Recibe un diccionario (propiedad).
# Inserta ese diccionario como un nuevo registro en la tabla de propiedades de Supabase.
# Retorna el objeto de la propiedad recién creada.
def crear_propiedad(propiedad: Dict[str, Any]) -> Dict[str, Any]:
    client = _get_client()
    payload = propiedad.copy()
    response = client.table(PROPIEDADES_TABLE).insert(payload).execute()
    data = _handle_response(response)
    return data[0] if data else payload


# Funcionamiento: Realiza un 'SELECT *' a la tabla de propiedades en Supabase.
# Retorna una lista con todas las propiedades, ordenadas por su ID.
def obtener_propiedades() -> List[Dict[str, Any]]:
    client = _get_client()
    response = client.table(PROPIEDADES_TABLE).select("*").order("id").execute()
    return _handle_response(response)


# Funcionamiento: Busca en Supabase una propiedad donde el 'id' coincida con el 'propiedad_id' recibido.
# Retorna el diccionario de la propiedad si la encuentra, o None si no existe.
def obtener_propiedad_por_id(propiedad_id: int) -> Optional[Dict[str, Any]]:
    client = _get_client()
    response = (
        client.table(PROPIEDADES_TABLE)
        .select("*")
        .eq("id", propiedad_id)
        .limit(1)
        .execute()
    )
    data = _handle_response(response)
    return data[0] if data else None


# Funcionamiento: Recibe el 'propiedad_id' y un diccionario con los 'cambios' a aplicar.
# Ejecuta un 'update' en Supabase para actualizar solo esos campos en la propiedad correspondiente.
# Retorna el objeto de la propiedad ya actualizada.
def actualizar_propiedad(propiedad_id: int, cambios: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    client = _get_client()
    if not cambios:
        return obtener_propiedad_por_id(propiedad_id)

    response = (
        client.table(PROPIEDADES_TABLE)
        .update(cambios)
        .eq("id", propiedad_id)
        .execute()
    )
    data = _handle_response(response)
    return data[0] if data else obtener_propiedad_por_id(propiedad_id)


# Funcionamiento: Ejecuta un 'delete' en Supabase para eliminar la propiedad que coincida con el 'propiedad_id' especificado.
# Retorna True si la operación se completó.
def eliminar_propiedad(propiedad_id: int) -> bool:
    client = _get_client()
    response = client.table(PROPIEDADES_TABLE).delete().eq("id", propiedad_id).execute()
    _handle_response(response)
    return True

# NORMALIZAR VALORES BOOLEANOS (para el campo "activo")

# Funcionamiento: Función interna (helper).
# Convierte cualquier tipo de valor (string, int, bool) a un valor booleano (True/False) estandarizado.
# Ej: "si", "1", "true" se convierten en True.
def _normalizar_activo(valor: Any) -> bool:
    if isinstance(valor, bool):
        return valor
    if isinstance(valor, str):
        normalizado = valor.strip().lower()
        if normalizado in {"true", "1", "si", "sí", "on"}:
            return True
        if normalizado in {"false", "0", "no", "off"}:
            return False
    if isinstance(valor, (int, float)):
        return bool(valor)
    return True 

# Funcionamiento: Función interna (helper).
# Prepara el diccionario de la propiedad antes de enviarlo a Supabase (aunque no se usa actualmente).
# Mapea claves (ej. 'baños' a 'banos'), limpia valores nulos y usa '_normalizar_activo'.
def _prepare_propiedad_payload(propiedad: Dict[str, Any]) -> Dict[str, Any]:
    mapping = {
        "id": "id",
        "nombre": "nombre",
        "descripcion": "descripcion",
        "precio": "precio",
        "localizacion": "localizacion",
        "dormitorios": "dormitorios",
        "baños": "banos",
        "banos": "banos",
        "area": "area",
        "tipo": "tipo",
        "estado": "estado",
        "activo": "activo",
        "img": "img",
        "coordenadas": "coordenadas",
        "propietario": "propietario",
    }

    payload: Dict[str, Any] = {}

    for clave, columna in mapping.items():
        if clave not in propiedad or propiedad[clave] in (None, "", " "):
            continue

        valor = propiedad[clave]
        if columna == "activo":
            valor = _normalizar_activo(valor)

        payload[columna] = valor

    return payload
