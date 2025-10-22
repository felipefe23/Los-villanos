from flask import request, jsonify, session
from app import app
from utils.decoradores import login_required
from persistencia.base_datos import (
    obtener_propiedades, obtener_propiedad_por_id,
    crear_propiedad, actualizar_propiedad as actualizar_propiedad_db,
    eliminar_propiedad as eliminar_propiedad_db
)
from servicios.propiedad_service import (
    leer_propiedades, _validar_y_normalizar_propiedad, _es_admin
)
from servicios.usuario_service import leer_usuarios

@app.route('/api/propiedades', methods=['GET'])
def get_propiedades():
    propiedades = leer_propiedades()
    usuarios = leer_usuarios()
    nombres = {u.get('id'): f"{u.get('nombre','').strip()} {u.get('apellido','').strip()}".strip() for u in usuarios}
    propiedades_enriquecidas = []
    for p in propiedades:
        copia = p.copy()
        prop_id = copia.get('propietario')
        nombre = nombres.get(prop_id)
        copia['propietario_nombre'] = nombre if nombre else None
        propiedades_enriquecidas.append(copia)
    return jsonify(propiedades_enriquecidas)

@app.route('/api/propiedades/editar/<int:propiedad_id>', methods=['POST'])
@login_required('vendedor', 'administrador', 'admin')
def editar_propiedad(propiedad_id):
    data = request.get_json(silent=True) or {}
    propiedad = obtener_propiedad_por_id(propiedad_id)
    if not propiedad:
        return jsonify({"error": "Propiedad no encontrada."}), 404

    # Verificar permisos (solo admin puede editar cualquier propiedad, vendedores solo las suyas)
    user_id = session.get('user_id')
    user_role = session.get('user_role')
    if not _es_admin(user_role) and propiedad.get('propietario') != user_id:
        return jsonify({"error": "No tienes permiso para editar esta propiedad."}), 403

    try:
        # Usar validación completa para la edición
        cambios = _validar_y_normalizar_propiedad(
            data,
            parcial=True,  # Permitir edición parcial
            propiedades_existentes=leer_propiedades(),
            propiedad_actual=propiedad
        )
    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    if not cambios:
        return jsonify({"error": "No se proporcionaron campos para actualizar."}), 400

    actualizada = actualizar_propiedad_db(propiedad_id, cambios)
    if not actualizada:
        return jsonify({"error": "Propiedad no encontrada."}), 404

    return jsonify({"message": "Propiedad actualizada con éxito.", "propiedad": actualizada}), 200

@app.route('/api/propiedades', methods=['POST'])
@login_required('vendedor', 'administrador', 'admin')
def add_propiedad():
    data = request.get_json(silent=True) or {}
    try:
        campos = _validar_y_normalizar_propiedad(
            data,
            parcial=False,
            propiedades_existentes=leer_propiedades()
        )
    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    user_id = session.get('user_id')
    if user_id is None:
        return jsonify({"error": "Autenticación requerida para crear propiedades."}), 401

    campos['propietario'] = user_id
    nueva = crear_propiedad(campos)
    propiedades = leer_propiedades()
    return jsonify({
        "message": "Propiedad ingresada con éxito.",
        "propiedad": nueva,
        "propiedades": propiedades
    }), 201

@app.route('/api/propiedades/<int:propiedad_id>', methods=['PUT', 'PATCH'])
@login_required('vendedor', 'administrador', 'admin')
def update_propiedad(propiedad_id):
    propiedad_actual = obtener_propiedad_por_id(propiedad_id)
    if not propiedad_actual:
        return jsonify({"error": "Propiedad no encontrada."}), 404

    user_id = session.get('user_id')
    user_role = session.get('user_role')
    if not _es_admin(user_role) and propiedad_actual.get('propietario') != user_id:
        return jsonify({"error": "No tienes permiso para modificar esta propiedad."}), 403

    data = request.get_json(silent=True) or {}
    parcial = request.method == 'PATCH'
    try:
        campos_actualizados = _validar_y_normalizar_propiedad(
            data,
            parcial=parcial,
            propiedades_existentes=leer_propiedades(),
            propiedad_actual=propiedad_actual
        )
    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    if not campos_actualizados:
        return jsonify({"error": "No se proporcionaron campos para actualizar."}), 400

    propiedad_actualizada = actualizar_propiedad_db(propiedad_id, campos_actualizados)
    if not propiedad_actualizada:
        return jsonify({"error": "Propiedad no encontrada."}), 404

    return jsonify({"message": "Propiedad actualizada con éxito.", "propiedad": propiedad_actualizada})

@app.route('/api/propiedades/<int:propiedad_id>', methods=['DELETE'])
@login_required('vendedor', 'administrador', 'admin')
def delete_propiedad(propiedad_id):
    propiedad_actual = obtener_propiedad_por_id(propiedad_id)
    if not propiedad_actual:
        return jsonify({"error": "Propiedad no encontrada."}), 404

    user_id = session.get('user_id')
    user_role = session.get('user_role')
    if not _es_admin(user_role) and propiedad_actual.get('propietario') != user_id:
        return jsonify({"error": "No tienes permiso para eliminar esta propiedad."}), 403

    eliminado = eliminar_propiedad_db(propiedad_id)
    if not eliminado:
        return jsonify({"error": "Propiedad no encontrada."}), 404

    return jsonify({"message": "Propiedad eliminada con éxito."})

@app.route('/api/propiedades/eliminar/<int:propiedad_id>', methods=['POST'])
@login_required('vendedor', 'administrador', 'admin')
def eliminar_propiedad(propiedad_id):
    propiedad = obtener_propiedad_por_id(propiedad_id)
    if not propiedad:
        return jsonify({"error": "Propiedad no encontrada."}), 404

    # Verificar permisos (solo admin puede eliminar cualquier propiedad, vendedores solo las suyas)
    user_id = session.get('user_id')
    user_role = session.get('user_role')
    if not _es_admin(user_role) and propiedad.get('propietario') != user_id:
        return jsonify({"error": "No tienes permiso para eliminar esta propiedad."}), 403

    try:
        eliminado = eliminar_propiedad_db(propiedad_id)
        if not eliminado:
            return jsonify({"error": "Propiedad no encontrada."}), 404
        return jsonify({"message": "Propiedad eliminada correctamente."}), 200
    except Exception as e:
        return jsonify({"error": f"Error al eliminar propiedad: {str(e)}"}), 500



