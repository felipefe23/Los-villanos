from flask import Blueprint, jsonify, request, session
from persistencia.base_datos import (
    obtener_usuarios,
    obtener_usuario_por_id,
    obtener_usuario_por_email,
    actualizar_usuario as actualizar_usuario_db,
    eliminar_usuario as eliminar_usuario_db,
)
from servicios.usuario_service import validar_email, TIPOS_USUARIO_PERMITIDOS, rol_legible
from servicios.propiedad_service import _validar_y_normalizar_propiedad
from utils.decoradores import login_required
from utils.helpers import _prefers_json

usuario_bp = Blueprint('usuario', __name__)

@usuario_bp.get("/api/usuarios")
@login_required('admin', 'administrador')
def api_usuarios():
    try:
        usuarios = obtener_usuarios()
        respuesta = []
        for usuario in usuarios:
            usuario_copy = usuario.copy()
            usuario_copy.pop("password", None)
            usuario_copy["rol_legible"] = rol_legible(usuario.get("tipo_usuario"))
            respuesta.append(usuario_copy)
        return jsonify(respuesta)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@usuario_bp.route("/api/usuarios/<int:user_id>", methods=["PUT"])
@login_required('admin', 'administrador')
def actualizar_usuario(user_id):
    data = request.get_json(silent=True) or {}
    usuario = obtener_usuario_por_id(user_id)
    if not usuario:
        return jsonify({"error": "Usuario no encontrado."}), 404

    try:
        cambios = {}

        email = data.get("email")
        if email is not None:
            email = email.strip()
            if not validar_email(email):
                return jsonify({"error": "Correo inválido (mínimo 2 caracteres antes del @)."}), 400
            email_normalizado = email.lower()
            existente = obtener_usuario_por_email(email_normalizado)
            if existente and existente.get("id") != user_id:
                return jsonify({"error": "El correo ya está registrado."}), 400
            cambios["email"] = email

        campos_texto = {
            "nombre": lambda v: v.strip() if len(v.strip()) >= 2 else None,
            "apellido": lambda v: v.strip() if len(v.strip()) >= 2 else None,
            "telefono": lambda v: v.strip(),
            "rut": lambda v: v.strip().upper(),
            "direccion": lambda v: v.strip() if len(v.strip()) >= 5 else None,
            "ciudad": lambda v: v.strip() if len(v.strip()) >= 2 else None,
        }

        for campo, normalizador in campos_texto.items():
            if campo in data and data[campo] is not None:
                valor = str(data[campo])
                valor_normalizado = normalizador(valor)
                if valor_normalizado is None:
                    return jsonify({"error": f"El campo '{campo}' no cumple con los requisitos mínimos."}), 400
                cambios[campo] = valor_normalizado

        tipo_usuario_enviado = data.get("tipo_usuario")
        if tipo_usuario_enviado is not None:
            tipo_normalizado = str(tipo_usuario_enviado).strip().lower()
            tipo_canonico = TIPOS_USUARIO_PERMITIDOS.get(tipo_normalizado)
            if not tipo_canonico:
                return jsonify({"error": "Tipo de usuario inválido."}), 400
            cambios["tipo_usuario"] = tipo_canonico

        if cambios:
            usuario_actualizado = actualizar_usuario_db(user_id, cambios)
        else:
            usuario_actualizado = usuario

        if not usuario_actualizado:
            return jsonify({"error": "Usuario no encontrado."}), 404

        usuario_sin_password = usuario_actualizado.copy()
        usuario_sin_password.pop("password", None)
        usuario_sin_password["rol_legible"] = rol_legible(usuario_actualizado.get("tipo_usuario"))
        return jsonify({"message": "Usuario actualizado correctamente.", "user": usuario_sin_password}), 200

    except Exception as e:
        return jsonify({"error": f"Error al actualizar usuario: {str(e)}"}), 500


@usuario_bp.route("/api/usuarios/<int:user_id>", methods=["DELETE"])
@login_required('admin', 'administrador')
def eliminar_usuario(user_id):
    from persistencia.base_datos import obtener_propiedades
    current_user_id = session.get('user_id')
    if current_user_id == user_id:
        return jsonify({"error": "No puedes eliminar tu propia cuenta."}), 400

    usuario = obtener_usuario_por_id(user_id)
    if not usuario:
        return jsonify({"error": "Usuario no encontrado."}), 404

    try:
        propiedades = obtener_propiedades()
        propiedades_usuario = [p for p in propiedades if p.get('propietario') == user_id]
        if propiedades_usuario:
            return jsonify({
                "error": f"No se puede eliminar el usuario porque tiene {len(propiedades_usuario)} propiedades asociadas."
            }), 400

        eliminado = eliminar_usuario_db(user_id)
        if not eliminado:
            return jsonify({"error": "Usuario no encontrado."}), 404

        return jsonify({
            "message": f"Usuario {usuario.get('nombre', '')} {usuario.get('apellido', '')} eliminado correctamente."
        }), 200
    except Exception as e:
        return jsonify({"error": f"Error al eliminar usuario: {str(e)}"}), 500

from app import app  # noqa: E402
app.register_blueprint(usuario_bp)
