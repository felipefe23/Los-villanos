from flask import request, jsonify, session, redirect, url_for
from app import app
from utils.helpers import _prefers_json
from servicios.auth_service import ph
from servicios.usuario_service import validar_email, validar_password
from persistencia.base_datos import (
    obtener_usuario_por_email, crear_usuario,
)
from datetime import datetime
import re

# Ruta para el registro de usuario
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json(silent=True) or {}
    email_original = data.get('email', '').strip()
    email = email_original.lower()
    password = data.get('password', '').strip()
    nombre = data.get('nombre', '').strip()
    apellido = data.get('apellido', '').strip()
    telefono = data.get('telefono', '').strip()
    rut = data.get('rut', '').strip()
    direccion = data.get('direccion', '').strip()
    ciudad = data.get('ciudad', '').strip()
    tipo_usuario = data.get('tipo_usuario', '').strip().lower()

    # Validaciones para el registro
    if not validar_email(email_original):
        return jsonify({"error": "Correo inválido (mínimo 2 caracteres antes del @)."}), 400
    if not validar_password(password):
        return jsonify({"error": "Contraseña debe tener al menos 8 caracteres y 1 número."}), 400
    if len(nombre) < 2:
        return jsonify({"error": "El nombre debe tener al menos 2 caracteres."}), 400
    if len(apellido) < 2:
        return jsonify({"error": "El apellido debe tener al menos 2 caracteres."}), 400

    telefono_digitos = re.sub(r'\D', '', telefono)
    if len(telefono_digitos) < 8:
        return jsonify({"error": "El teléfono debe incluir al menos 8 dígitos."}), 400

    rut_pattern = re.compile(r'^[0-9]{7,8}-[0-9kK]$')
    if not rut_pattern.match(rut):
        return jsonify({"error": "El RUT debe tener el formato 12345678-9."}), 400

    if len(direccion) < 5:
        return jsonify({"error": "La dirección debe contener al menos 5 caracteres."}), 400
    if len(ciudad) < 2:
        return jsonify({"error": "La ciudad debe contener al menos 2 caracteres."}), 400

    if tipo_usuario not in {"vendedor", "comprador"}:
        return jsonify({"error": "El tipo de usuario debe ser 'vendedor' o 'comprador'."}), 400

    # Verificar si el usuario ya existe en Supabase
    existente = obtener_usuario_por_email(email)
    if existente:
        return jsonify({"error": "El correo ya está registrado."}), 400

    try:
        # Crear usuario en Supabase con contraseña hasheada usando Argon2
        hash_pw = ph.hash(password)
        usuario = {
            'email': email,
            'password': hash_pw,
            'nombre': nombre,
            'apellido': apellido,
            'telefono': telefono,
            'rut': rut.upper(),
            'direccion': direccion,
            'ciudad': ciudad,
            'tipo_usuario': tipo_usuario,  # Ya no hasheamos el tipo_usuario
            'fecha_registro': datetime.utcnow().isoformat() + 'Z'
        }
        usuario_creado = crear_usuario(usuario)
        usuario_sin_password = usuario_creado.copy()
        usuario_sin_password.pop('password', None)
        return jsonify({"message": "Usuario registrado con éxito.", "user": usuario_sin_password})
    except Exception as e:
        return jsonify({"error": f"Error al crear usuario: {str(e)}"}), 500

# Ruta para el login de usuario
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json(silent=True) or {}
    email = data.get('email', '').strip().lower()
    password = data.get('password', '').strip()
    tipo_enviado = (data.get('tipo_usuario') or '').strip().lower()

    # Obtener usuario desde Supabase
    user = obtener_usuario_por_email(email)
    if not user:
        return jsonify({"error": "Correo no encontrado."}), 400

    # Verificar contraseña usando Argon2
    try:
        ph.verify(user['password'], password)
    except Exception:
        return jsonify({"error": "Contraseña incorrecta."}), 400

    # Obtener tipo de usuario (ya no está hasheado)
    stored_tipo = (user.get('tipo_usuario') or '').strip().lower()
    matched_tipo = None

    # Verificar si el tipo enviado coincide con el almacenado
    if tipo_enviado and tipo_enviado == stored_tipo:
        matched_tipo = tipo_enviado
    elif not tipo_enviado:
        # Si no se especifica tipo, usar el almacenado
        matched_tipo = stored_tipo

    # Validar que el tipo sea válido
    if not matched_tipo or matched_tipo not in ['admin', 'administrador', 'vendedor', 'comprador']:
        return jsonify({"error": "Tipo de usuario incorrecto."}), 400

    # Configurar sesión
    session.clear()
    session['user_id'] = user.get('id')
    session['user_role'] = matched_tipo
    session['user_email'] = user.get('email')
    session.permanent = True

    # Preparar respuesta del usuario
    usuario_respuesta = user.copy()
    usuario_respuesta.pop('password', None)
    usuario_respuesta.setdefault('nombre', '')
    usuario_respuesta.setdefault('apellido', '')
    usuario_respuesta.setdefault('telefono', '')
    usuario_respuesta.setdefault('rut', '')
    usuario_respuesta.setdefault('direccion', '')
    usuario_respuesta.setdefault('ciudad', '')
    usuario_respuesta.setdefault('tipo_usuario', matched_tipo)
    usuario_respuesta.setdefault('fecha_registro', '')

    # Determinar URL de redirección
    if matched_tipo in ('admin', 'administrador'):
        redirect_url = url_for('admin_dashboard_view')
    elif matched_tipo == 'vendedor':
        redirect_url = url_for('vendedor_view')
    else:
        redirect_url = url_for('comprador_dashboard_view')

    return jsonify({"message": "Login exitoso.", "user": usuario_respuesta, "redirect": redirect_url})

# Ruta que hace logout y sesionclear para cerrar sesion correctamente
@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    if request.method == 'POST' or _prefers_json():
        return jsonify({"message": "Sesión cerrada."})
    return redirect(url_for('login_view'))
