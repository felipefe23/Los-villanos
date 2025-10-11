import json
import os
from typing import Any, Dict, List, Optional

try:
    from supabase import Client, create_client
except ImportError as exc:  # pragma: no cover - la librería se valida en tiempo de ejecución
    Client = None  # type: ignore
    create_client = None  # type: ignore
    _IMPORT_ERROR = exc
else:
    _IMPORT_ERROR = None


BASE_DIR = os.path.join("Testing", "datos")
USERS_JSON = os.path.join(BASE_DIR, "users.json")
PROPIEDADES_JSON = os.path.join(BASE_DIR, "propiedades.json")

_SUPABASE_URL_KEYS = ("SUPABASE_URL", "SUPABASE_PROJECT_URL")
_SUPABASE_KEY_KEYS = (
    "SUPABASE_SERVICE_KEY",
    "SUPABASE_SECRET_KEY",
    "SUPABASE_KEY",
    "SUPABASE_ANON_KEY",
)


def _env_lookup(keys: List[str]) -> Optional[str]:
    for key in keys:
        value = os.environ.get(key)
        if value:
            return value
    return None


SUPABASE_URL = _env_lookup(list(_SUPABASE_URL_KEYS))
SUPABASE_KEY = _env_lookup(list(_SUPABASE_KEY_KEYS))
USERS_TABLE = os.environ.get("SUPABASE_USERS_TABLE", "users")
PROPIEDADES_TABLE = os.environ.get("SUPABASE_PROPIEDADES_TABLE", "propiedades")

_client: Optional["Client"] = None


def _require_supabase() -> None:
    if create_client is None or Client is None or _IMPORT_ERROR is not None:
        raise RuntimeError(
            "La librería 'supabase' no está instalada. Ejecuta 'pip install supabase'."
        ) from _IMPORT_ERROR
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise RuntimeError(
            "Debes configurar las variables de entorno SUPABASE_URL y SUPABASE_SERVICE_KEY "
            "(o SUPABASE_KEY) con credenciales del proyecto."
        )


def _get_client() -> "Client":
    global _client
    if _client is None:
        _require_supabase()
        _client = create_client(SUPABASE_URL, SUPABASE_KEY)  # type: ignore[arg-type]
    return _client


def _handle_response(response: Any) -> List[Dict[str, Any]]:
    error = getattr(response, "error", None)
    if error:
        message = getattr(error, "message", None) or str(error)
        raise RuntimeError(f"Error de Supabase: {message}")
    data = getattr(response, "data", None)
    if data is None:
        return []
    if isinstance(data, list):
        return data
    return [data]


def _cargar_json(ruta: str) -> List[Dict[str, Any]]:
    if not os.path.exists(ruta):
        return []
    try:
        with open(ruta, "r", encoding="utf-8") as archivo:
            contenido = archivo.read().strip()
            if not contenido:
                return []
            datos = json.loads(contenido)
            return datos if isinstance(datos, list) else []
    except (IOError, json.JSONDecodeError):
        return []


def _count_rows(client: "Client", table: str) -> int:
    response = client.table(table).select("id", count="exact").limit(1).execute()
    _handle_response(response)
    count = getattr(response, "count", None)
    return int(count or 0)


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


def _prepare_usuario_payload(usuario: Dict[str, Any]) -> Dict[str, Any]:
    payload: Dict[str, Any] = {}
    if usuario.get("id") is not None:
        payload["id"] = usuario["id"]
    campos = [
        "email",
        "password",
        "nombre",
        "apellido",
        "telefono",
        "rut",
        "direccion",
        "ciudad",
        "tipo_usuario",
        "fecha_registro",
    ]
    for campo in campos:
        if campo not in usuario or usuario[campo] is None:
            continue
        valor = usuario[campo]
        if campo == "email":
            valor = str(valor).strip().lower()
        elif campo in {"nombre", "apellido", "telefono", "direccion", "ciudad"}:
            valor = str(valor).strip()
        elif campo == "rut":
            valor = str(valor).strip().upper()
        payload[campo] = valor
    return payload


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
        if clave not in propiedad or propiedad[clave] is None:
            continue
        valor = propiedad[clave]
        if columna == "activo":
            valor = _normalizar_activo(valor)
        payload[columna] = valor
    return payload


def _row_to_usuario(row: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": row.get("id"),
        "email": row.get("email"),
        "password": row.get("password"),
        "nombre": row.get("nombre"),
        "apellido": row.get("apellido"),
        "telefono": row.get("telefono"),
        "rut": row.get("rut"),
        "direccion": row.get("direccion"),
        "ciudad": row.get("ciudad"),
        "tipo_usuario": row.get("tipo_usuario"),
        "fecha_registro": row.get("fecha_registro"),
    }


def _to_bool(valor: Any) -> bool:
    if isinstance(valor, bool):
        return valor
    if isinstance(valor, str):
        return valor.strip().lower() in {"true", "1", "si", "sí", "on"}
    if isinstance(valor, (int, float)):
        return bool(valor)
    return False


def _row_to_propiedad(row: Dict[str, Any]) -> Dict[str, Any]:
    banos_val = row.get("baños")
    if banos_val is None:
        banos_val = row.get("banos")
    return {
        "id": row.get("id"),
        "nombre": row.get("nombre"),
        "descripcion": row.get("descripcion"),
        "precio": row.get("precio"),
        "localizacion": row.get("localizacion"),
        "dormitorios": row.get("dormitorios"),
        "baños": banos_val,
        "area": row.get("area"),
        "tipo": row.get("tipo"),
        "estado": row.get("estado"),
        "activo": _to_bool(row.get("activo", True)),
        "img": row.get("img"),
        "coordenadas": row.get("coordenadas"),
        "propietario": row.get("propietario"),
    }


def init_db(seed_from_files: bool = True) -> None:
    """
    Inicializa el cliente de Supabase y, si se solicita, intenta migrar los datos
    locales JSON a las tablas remotas cuando éstas se encuentren vacías.
    """
    client = _get_client()
    if not seed_from_files:
        return

    try:
        usuarios_count = _count_rows(client, USERS_TABLE)
        propiedades_count = _count_rows(client, PROPIEDADES_TABLE)
    except RuntimeError:
        return

    if usuarios_count == 0:
        usuarios = _cargar_json(USERS_JSON)
        if usuarios:
            payload = [_prepare_usuario_payload(u) for u in usuarios]
            response = client.table(USERS_TABLE).upsert(payload, on_conflict="id").execute()
            _handle_response(response)

    if propiedades_count == 0:
        propiedades = _cargar_json(PROPIEDADES_JSON)
        if propiedades:
            payload = [_prepare_propiedad_payload(p) for p in propiedades]
            response = (
                client.table(PROPIEDADES_TABLE)
                .upsert(payload, on_conflict="id")
                .execute()
            )
            _handle_response(response)


# Operaciones sobre usuarios -------------------------------------------------

def obtener_usuarios() -> List[Dict[str, Any]]:
    client = _get_client()
    response = client.table(USERS_TABLE).select("*").order("id").execute()
    data = _handle_response(response)
    return [_row_to_usuario(row) for row in data]


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
    if not data:
        return None
    return _row_to_usuario(data[0])


def obtener_usuario_por_email(email: str) -> Optional[Dict[str, Any]]:
    email_normalizado = (email or "").strip().lower()
    if not email_normalizado:
        return None
    client = _get_client()
    response = (
        client.table(USERS_TABLE)
        .select("*")
        .eq("email", email_normalizado)
        .limit(1)
        .execute()
    )
    data = _handle_response(response)
    if not data:
        return None
    return _row_to_usuario(data[0])


def crear_usuario(usuario: Dict[str, Any]) -> Dict[str, Any]:
    client = _get_client()
    payload = _prepare_usuario_payload(usuario)
    response = client.table(USERS_TABLE).insert(payload).execute()
    data = _handle_response(response)
    if data:
        return _row_to_usuario(data[0])
    creado = obtener_usuario_por_email(payload["email"])
    if not creado:
        raise RuntimeError("No fue posible confirmar el usuario recién creado.")
    return creado


def actualizar_usuario(user_id: int, cambios: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    payload = _prepare_usuario_payload(cambios)
    if not payload:
        return obtener_usuario_por_id(user_id)
    client = _get_client()
    response = client.table(USERS_TABLE).update(payload).eq("id", user_id).execute()
    _handle_response(response)
    return obtener_usuario_por_id(user_id)


def eliminar_usuario(user_id: int) -> bool:
    client = _get_client()
    response = client.table(USERS_TABLE).delete().eq("id", user_id).execute()
    _handle_response(response)
    return obtener_usuario_por_id(user_id) is None


# Operaciones sobre propiedades ---------------------------------------------

def obtener_propiedades() -> List[Dict[str, Any]]:
    client = _get_client()
    response = client.table(PROPIEDADES_TABLE).select("*").order("id").execute()
    data = _handle_response(response)
    return [_row_to_propiedad(row) for row in data]


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
    if not data:
        return None
    return _row_to_propiedad(data[0])


def crear_propiedad(propiedad: Dict[str, Any]) -> Dict[str, Any]:
    client = _get_client()
    payload = _prepare_propiedad_payload(propiedad)
    response = client.table(PROPIEDADES_TABLE).insert(payload).execute()
    data = _handle_response(response)
    if data:
        return _row_to_propiedad(data[0])
    coordenadas = payload.get("coordenadas")
    if coordenadas:
        creada = (
            client.table(PROPIEDADES_TABLE)
            .select("*")
            .eq("coordenadas", coordenadas)
            .limit(1)
            .execute()
        )
        datos = _handle_response(creada)
        if datos:
            return _row_to_propiedad(datos[0])
    raise RuntimeError("No fue posible confirmar la propiedad recién creada.")


def actualizar_propiedad(propiedad_id: int, cambios: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    payload = _prepare_propiedad_payload(cambios)
    if not payload:
        return obtener_propiedad_por_id(propiedad_id)
    client = _get_client()
    response = (
        client.table(PROPIEDADES_TABLE)
        .update(payload)
        .eq("id", propiedad_id)
        .execute()
    )
    _handle_response(response)
    return obtener_propiedad_por_id(propiedad_id)


def eliminar_propiedad(propiedad_id: int) -> bool:
    client = _get_client()
    response = (
        client.table(PROPIEDADES_TABLE)
        .delete()
        .eq("id", propiedad_id)
        .execute()
    )
    _handle_response(response)
    return obtener_propiedad_por_id(propiedad_id) is None


def propiedades_por_propietario(propietario_id: int) -> List[Dict[str, Any]]:
    client = _get_client()
    response = (
        client.table(PROPIEDADES_TABLE)
        .select("*")
        .eq("propietario", propietario_id)
        .order("id")
        .execute()
    )
    data = _handle_response(response)
    return [_row_to_propiedad(row) for row in data]
