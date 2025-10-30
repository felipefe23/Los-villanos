from functools import wraps
from flask import session, jsonify, redirect, url_for
from utils.helpers import _prefers_json


# Funcionamiento: Decorador para proteger rutas de Flask.
# Se usa encima de una ruta (ej. @login_required('admin')).
# Primero, revisa si 'user_id' existe en la sesión.
# Si no hay sesión, redirige al login (o da error 401 JSON).
# Segundo, revisa si el rol del usuario (ej. 'vendedor') iene permiso, basado en los roles pasados al decorador.
# Si no tiene permiso, lo redirige (o da error 403 JSON).
# Excepción: Un rol 'admin' o 'administrador' siempre tiene acceso, sin importar los roles que pida el decorador.
def login_required(*roles):
    roles_normalizados = {r.lower() for r in roles if isinstance(r, str)} if roles else set()
    
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(*args, **kwargs):
            user_id = session.get('user_id')
            user_role = (session.get('user_role') or '').lower()

            if not user_id:
                if _prefers_json():
                    return jsonify({"error": "Autenticación requerida."}), 401
                return redirect(url_for('login_view'))

            if roles_normalizados and user_role not in roles_normalizados:
                if user_role not in {'admin', 'administrador'}:
                    if _prefers_json():
                        return jsonify({"error": "Permisos insuficientes."}), 403
                    return redirect(url_for('landing'))

            return view_func(*args, **kwargs)

        return wrapped_view

    return decorator