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
from httpx import TimeoutException

# Funcionamiento: Obtiene todas las propiedades y usuarios.
# Crea un mapa de IDs de usuario a nombres completos.
# "Enriquece" cada propiedad agregando el nombre del propietario ('propietario_nombre').
# Retorna la lista de propiedades enriquecidas en JSON.
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


# Funcionamiento: Protegido (vendedor/admin).
# Recibe datos JSON para crear una propiedad nueva.
# Valida todos los campos (modo 'parcial=False'). Si falla (ej. campo obligatorio falta), retorna 400.
# Revisa si el admin envió un 'propietario' desde el dropdown.
# Si no se envió (o si el que crea es un vendedor), asigna la propiedad al usuario logueado.
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
        user_id = session.get('user_id')
        if user_id is None:
            return jsonify({"error": "Autenticación requerida para crear propiedades."}), 401

        propietario_id_enviado = campos.pop('propietario', None)

        if propietario_id_enviado:
            # Si el admin seleccionó a alguien, se usa ese ID
            campos['propietario'] = propietario_id_enviado
        else:
            # Si no (dejó "Asignar a mí"), se usa el ID de la sesión
            campos['propietario'] = user_id

        nueva = crear_propiedad(campos)
        propiedades = leer_propiedades()
        
        # Quitamos la imagen de la respuesta para una API limpia
        nueva_sin_img = nueva.copy()
        nueva_sin_img.pop('img', None)
        
        return jsonify({
            "message": "Propiedad ingresada con éxito.",
            "propiedad": nueva_sin_img,
            "propiedades": propiedades
        }), 201

    except ValueError as error:
        return jsonify({"error": str(error)}), 400
    except TimeoutException:
        print(f"ERROR: Timeout en la ruta {request.path}")
        return jsonify({"error": "La base de datos tardó demasiado en responder (Timeout)."}), 504
    except Exception as e:
        print(f"ERROR INESPERADO en add_propiedad: {e}")
        return jsonify({"error": f"Error al crear propiedad: {str(e)}"}), 500


# Funcionamiento: Ruta PUT/PATCH para actualizar una propiedad.
# Protegido (vendedor/admin).
# Busca la propiedad por ID; si no la encuentra, retorna 404.
# Valida los datos del JSON en modo 'parcial=True' (acepta campos sueltos).
# Maneja la lógica de reasignación del 'propietario' por separado.
# Si el 'propietario' enviado es None o "", lo asigna al admin logueado.
@app.route('/api/propiedades/<int:propiedad_id>', methods=['PUT', 'PATCH'])
@login_required('vendedor', 'administrador', 'admin')
def update_propiedad(propiedad_id):
    
    propiedad_actualizada = None # Previene el UnboundLocalError
    
    print("\n--- INICIANDO ACTUALIZACIÓN (PUT/PATCH) ---")
    data = request.get_json(silent=True) or {}
    
    data_log = data.copy()
    data_log.pop('img', None)

    propiedad_actual = obtener_propiedad_por_id(propiedad_id)
    if not propiedad_actual:
        return jsonify({"error": "Propiedad no encontrada."}), 404

    try:
        # Las actualizaciones (PUT/PATCH) deben ser siempre parciales
        campos_actualizados = _validar_y_normalizar_propiedad(
            data,
            parcial=True,
            propiedades_existentes=leer_propiedades(),
            propiedad_actual=propiedad_actual
        )
        
        if 'propietario' in data:
            propietario_id_enviado = data.get('propietario') # Puede ser un ID, None, o ""
            
            if propietario_id_enviado:
                # El admin seleccionó un vendedor, se usa ese ID
                campos_actualizados['propietario'] = int(propietario_id_enviado)
            else:
                # El admin seleccionó "(Asignar a mí)", se usa el ID de la sesión
                user_id = session.get('user_id')
                campos_actualizados['propietario'] = user_id

        if not campos_actualizados:
            print("ERROR: 'campos_actualizados' está vacío.")
            return jsonify({"error": "No se proporcionaron campos para actualizar."}), 400

        propiedad_actualizada = actualizar_propiedad_db(propiedad_id, campos_actualizados)
        
        if propiedad_actualizada:
            debug_data = propiedad_actualizada.copy()
            debug_data.pop('img', None)
        else:
            print("RESPUESTA DE LA BD: None (Falló el update en Supabase)")
        
        if not propiedad_actualizada:
            return jsonify({"error": "Propiedad no encontrada."}), 404

        respuesta_json = propiedad_actualizada.copy()
        respuesta_json.pop('img', None)

        return jsonify({
            "message": "Propiedad actualizada con éxito.", 
            "propiedad": respuesta_json
        })

    except ValueError as error:
        return jsonify({"error": str(error)}), 400
    except TimeoutException:
        print(f"ERROR: Timeout en la ruta {request.path}")
        return jsonify({"error": "La base de datos tardó demasiado en responder (Timeout)."}), 504
    except Exception as e:
        print(f"ERROR INESPERADO en update_propiedad: {e}")
        return jsonify({"error": f"Error al actualizar propiedad: {str(e)}"}), 500
    

# Funcionamiento: Ruta estándar REST (DELETE) para eliminar.
# Verifica que la propiedad exista.
# Verifica permisos (solo Admin o el propietario).
# Llama a la BD para eliminar la propiedad.
# Retorna un mensaje de éxito en JSON.
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


# Funcionamiento: Ruta POST para eliminar (alternativa a DELETE).
# Verifica que la propiedad exista.
# Verifica permisos (solo Admin o el propietario).
# Llama a la BD para eliminar la propiedad.
# Retorna un mensaje de éxito en JSON.
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
        # Captura el error de Timeout ANTES del 'Exception' genérico.
    except TimeoutException:
        # Imprime un log en el servidor
        print(f"ERROR: Timeout en la ruta {request.path}")
        return jsonify({"error": "La base de datos tardó demasiado en responder (Timeout)."}), 504 # 504 Gateway Timeout
    except Exception as e:
        return jsonify({"error": f"Error al eliminar propiedad: {str(e)}"}), 500



