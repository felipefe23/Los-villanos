from flask import Flask, render_template, request, jsonify
from flask import redirect, url_for, session
from functools import wraps
from persistencia.manejoArchivo import leer_propiedades, guardar_propiedades, siguiente_id
import os
import re
import json
from argon2 import PasswordHasher
from datetime import datetime
import base64



app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key')
app.config.setdefault('SESSION_COOKIE_HTTPONLY', True)
app.config.setdefault('SESSION_COOKIE_SAMESITE', 'Lax')

# HASHEADO EN ARGON2 TESTING

USERS_FILE = os.path.join('Testing', 'datos', 'users.json')
ph = PasswordHasher()

def validar_email(email):
    # Mínimo 2 caracteres antes del @ y formato básico
    return re.match(r'^[^@]{2,}@[^@]+\.[^@]+$', email)

def validar_password(password):
    # Al menos 8 caracteres y 1 número
    return re.match(r'^(?=.*\d).{8,}$', password)

def leer_usuarios():
    if not os.path.exists(USERS_FILE):
        return []
    try:
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            contenido = f.read().strip()
            if not contenido:
                return []
            return json.loads(contenido)
    except Exception:
        return []

def guardar_usuarios(lista_usuarios):
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(lista_usuarios, f, indent=2, ensure_ascii=False)


def _prefers_json():
    best = request.accept_mimetypes.best
    if not best:
        return False
    if best != 'application/json':
        return False
    return request.accept_mimetypes[best] >= request.accept_mimetypes['text/html']


def _es_admin(role):
    return (role or '').lower() in {'admin', 'administrador'}


def _normalizar_bool(valor, campo):
    if isinstance(valor, bool):
        return valor
    if isinstance(valor, str):
        valor_normalizado = valor.strip().lower()
        if valor_normalizado in {'true', '1', 'si', 'sí', 'on'}:
            return True
        if valor_normalizado in {'false', '0', 'no', 'off'}:
            return False
    raise ValueError(f"El campo '{campo}' debe ser booleano.")


def _validar_y_normalizar_propiedad(data, parcial, propiedades_existentes, propiedad_actual=None):
    if not isinstance(data, dict):
        raise ValueError("Formato de datos inválido para la propiedad.")

    resultado = {}
    campos_texto_obligatorios = ['nombre', 'localizacion', 'tipo']
    campos_numericos = ['precio', 'dormitorios', 'baños', 'area']
    campos_permitidos = {
        'nombre', 'descripcion', 'precio', 'localizacion', 'dormitorios', 'baños',
        'area', 'tipo', 'estado', 'activo', 'img', 'coordenadas'
    }

    for campo in campos_texto_obligatorios:
        if campo not in data:
            if parcial:
                continue
            raise ValueError(f"El campo '{campo}' es obligatorio.")
        valor = data.get(campo)
        if valor is None:
            raise ValueError(f"El campo '{campo}' no puede estar vacío.")
        valor = str(valor).strip()
        if not valor:
            raise ValueError(f"El campo '{campo}' no puede estar vacío.")
        resultado[campo] = valor

    for campo in campos_numericos:
        if campo not in data:
            if parcial:
                continue
            raise ValueError(f"El campo '{campo}' es obligatorio.")
        valor = data.get(campo)
        if isinstance(valor, str):
            valor = valor.strip()
        if valor in (None, ''):
            raise ValueError({
                'precio': "El precio debe ser un número.",
                'dormitorios': "Los dormitorios deben ser un número.",
                'baños': "Los baños deben ser un número.",
                'area': "El área debe ser un número."
            }[campo])
        try:
            valor_entero = int(valor)
        except (TypeError, ValueError):
            raise ValueError({
                'precio': "El precio debe ser un número.",
                'dormitorios': "Los dormitorios deben ser un número.",
                'baños': "Los baños deben ser un número.",
                'area': "El área debe ser un número."
            }[campo])
        if valor_entero <= 0:
            raise ValueError({
                'precio': "El precio debe ser un número entero positivo o mayor a 0.",
                'dormitorios': "El número de dormitorios debe ser un entero no negativo.",
                'baños': "El número de baños debe ser un entero no negativo.",
                'area': "El área debe ser un entero no negativo ni 0."
            }[campo])
        resultado[campo] = valor_entero

    if 'descripcion' in data:
        descripcion = data.get('descripcion')
        if descripcion is None or (isinstance(descripcion, str) and not descripcion.strip()):
            resultado['descripcion'] = "Sin descripción"
        else:
            resultado['descripcion'] = str(descripcion).strip()
    elif not parcial:
        resultado['descripcion'] = "Sin descripción"

    if 'estado' in data:
        estado = data.get('estado')
        if estado is None:
            raise ValueError("El estado debe ser 'venta' o 'arriendo'.")
        estado_normalizado = str(estado).strip().lower()
        if estado_normalizado not in {'venta', 'arriendo'}:
            raise ValueError("El estado debe ser 'venta' o 'arriendo'.")
        resultado['estado'] = estado_normalizado
    elif not parcial:
        raise ValueError("El campo 'estado' es obligatorio.")

    if 'coordenadas' in data:
        coordenadas = data.get('coordenadas')
        if coordenadas is None:
            raise ValueError("Las coordenadas no pueden estar vacías.")
        coordenadas_normalizadas = str(coordenadas).strip()
        if not coordenadas_normalizadas:
            raise ValueError("Las coordenadas no pueden estar vacías.")
        propiedad_id_actual = propiedad_actual.get('id') if propiedad_actual else None
        for propiedad in propiedades_existentes:
            if propiedad.get('coordenadas') == coordenadas_normalizadas and propiedad.get('id') != propiedad_id_actual:
                raise ValueError("Las coordenadas ya existen en otra propiedad.")
        resultado['coordenadas'] = coordenadas_normalizadas
    elif not parcial:
        raise ValueError("El campo 'coordenadas' es obligatorio.")

    if 'activo' in data:
        resultado['activo'] = _normalizar_bool(data.get('activo'), 'activo')
    elif not parcial:
        resultado['activo'] = True

    if 'img' in data:
        img = data.get('img')
        if img is None:
            resultado['img'] = None
        else:
            resultado['img'] = str(img)
    elif not parcial:
        resultado['img'] = None

    campos_extra = set(data.keys()) - campos_permitidos - {'id', 'propietario'}
    if campos_extra:
        raise ValueError(f"Campos no permitidos: {', '.join(sorted(campos_extra))}.")

    return resultado

#Funcion para hardcodear la cache
@app.after_request
def harden_cache_headers(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

#Funcion para validar el login
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

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json(silent=True) or {}
    email = data.get('email', '').strip()
    password = data.get('password', '').strip()
    nombre = data.get('nombre', '').strip()
    apellido = data.get('apellido', '').strip()
    telefono = data.get('telefono', '').strip()
    rut = data.get('rut', '').strip()
    direccion = data.get('direccion', '').strip()
    ciudad = data.get('ciudad', '').strip()
    tipo_usuario = data.get('tipo_usuario', '').strip().lower()

    if not validar_email(email):
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

    usuarios = leer_usuarios()
    if any(u.get('email') == email for u in usuarios):
        return jsonify({"error": "El correo ya está registrado."}), 400

    hash_pw = ph.hash(password)
    hash_tipo = ph.hash(tipo_usuario)
    usuarios = leer_usuarios()
    id_user = siguiente_id(usuarios)
    usuario = {
        'id': id_user,
        'email': email,
        'password': hash_pw,
        'nombre': nombre,
        'apellido': apellido,
        'telefono': telefono,
        'rut': rut.upper(),
        'direccion': direccion,
        'ciudad': ciudad,
        'tipo_usuario': hash_tipo,
        'fecha_registro': datetime.utcnow().isoformat() + 'Z'
    }
    usuarios.append(usuario)
    guardar_usuarios(usuarios)
    usuario_sin_password = usuario.copy()
    usuario_sin_password.pop('password', None)
    return jsonify({"message": "Usuario registrado con éxito.", "user": usuario_sin_password})

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json(silent=True) or {}
    email = data.get('email', '').strip().lower()
    password = data.get('password', '').strip()
    tipo_enviado = (data.get('tipo_usuario') or '').strip().lower()

    usuarios = leer_usuarios()
    user = next((u for u in usuarios if (u.get('email') or '').strip().lower() == email), None)
    if not user:
        return jsonify({"error": "Correo no encontrado."}), 400

    try:
        ph.verify(user['password'], password)
    except Exception:
        return jsonify({"error": "Contraseña incorrecta."}), 400

    stored_tipo = (user.get('tipo_usuario') or '').strip()
    possible_types = ['admin', 'administrador', 'vendedor', 'comprador']
    matched_tipo = None

    if stored_tipo.startswith('$argon2'):
        if tipo_enviado:
            try:
                if ph.verify(stored_tipo, tipo_enviado):
                    matched_tipo = tipo_enviado
            except Exception:
                matched_tipo = None
        if not matched_tipo:
            for t in possible_types:
                try:
                    if ph.verify(stored_tipo, t):
                        matched_tipo = t
                        break
                except Exception:
                    continue
    else:
        matched_tipo = None

    if not matched_tipo:
        return jsonify({"error": "Tipo de usuario incorrecto."}), 400

    session.clear()
    session['user_id'] = user.get('id')
    session['user_role'] = matched_tipo
    session['user_email'] = user.get('email')
    session.permanent = True

    usuario_respuesta = user.copy()
    usuario_respuesta.pop('password', None)
    usuario_respuesta.setdefault('nombre', '')
    usuario_respuesta.setdefault('apellido', '')
    usuario_respuesta.setdefault('telefono', '')
    usuario_respuesta.setdefault('rut', '')
    usuario_respuesta.setdefault('direccion', '')
    usuario_respuesta.setdefault('ciudad', '')
    usuario_respuesta.setdefault('tipo_usuario', '')
    usuario_respuesta.setdefault('fecha_registro', '')

    if matched_tipo in ('admin', 'administrador'):
        redirect_url = url_for('admin_dashboard_view')
    elif matched_tipo == 'vendedor':
        redirect_url = url_for('vendedor_view')
    else:
        redirect_url = url_for('comprador_dashboard_view')

    return jsonify({"message": "Login exitoso.", "user": usuario_respuesta, "redirect": redirect_url})

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    if request.method == 'POST' or _prefers_json():
        return jsonify({"message": "Sesión cerrada."})
    return redirect(url_for('login_view'))

# HASHEADO EN ARGON2 TESTING

@app.route('/')
def landing():
    mensaje_error = session.pop('error_message', '')
    session.clear()
    return render_template('landing.html', error_message=mensaje_error)

@app.get('/login')
def login_view():
    mensaje_error = session.pop('error_message', '')
    session.clear()
    return render_template('landing.html', error_message=mensaje_error)

@app.get("/admin/login")
def admin_login_view():
    return redirect(url_for('landing'))

@app.get("/vendedor/login")
def vendedor_login_view():
    return redirect(url_for('landing'))

@app.get("/comprador/login")
def comprador_login_view():
    return redirect(url_for('landing'))

@app.get("/comprador/register")
def comprador_register_view():
    return render_template("comprador_register.html")

@app.get("/comprador")
@login_required('comprador', 'administrador', 'admin')
def comprador_dashboard_view():
    propiedades = leer_propiedades()
    usuarios = leer_usuarios()
    nombres = {u.get('id'): f"{u.get('nombre','').strip()} {u.get('apellido','').strip()}".strip() for u in usuarios}
    propiedades_filtradas = []
    for p in propiedades:
        if not p.get('activo', True):
            continue
        copia = p.copy()
        prop_id = copia.get('propietario')
        copia['propietario_nombre'] = nombres.get(prop_id) if nombres.get(prop_id) else None
        propiedades_filtradas.append(copia)
    return render_template("comprador_dashboard.html", propiedades=propiedades_filtradas)

@app.get("/admin")
@login_required('admin', 'administrador')
def admin_dashboard_view():
    propiedades = leer_propiedades()
    usuarios = leer_usuarios()
    nombres = {
        u.get('id'): f"{u.get('nombre','').strip()} {u.get('apellido','').strip()}".strip()
        for u in usuarios
    }
    propiedades_total = []
    for p in propiedades:
        copia = p.copy()
        prop_id = copia.get('propietario')
        copia['propietario_nombre'] = nombres.get(prop_id) if nombres.get(prop_id) else None
        propiedades_total.append(copia)
    for u in usuarios:
        u['rol_legible'] = rol_legible(u.get('tipo_usuario'))
    return render_template(
        "admin_dashboard.html",
        propiedades=propiedades_total,
        usuarios=usuarios
    )



@app.get("/vendedor")
@login_required('vendedor', 'administrador', 'admin')
def vendedor_view():
    return render_template("vendedor.html")

@app.get("/vendedor/register")
def vendedor_register_view():
    return render_template("vendedor_register.html")



@app.get("/ventas")
def ventas_view():
    propiedades = leer_propiedades()
    propiedades_venta = [p for p in propiedades if p.get("estado", "").lower() == "venta"]
    return render_template("ventas.html", propiedades=propiedades_venta)

@app.get("/api/usuarios")
@login_required('admin', 'administrador')  
def api_usuarios():
    try:
        usuarios = leer_usuarios()
        for u in usuarios:
            u["rol_legible"] = u.get("rol_legible") or "desconocido"
        return jsonify(usuarios)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/usuarios/<int:user_id>", methods=["POST"])
@login_required('admin', 'administrador')
def actualizar_usuario(user_id):
    usuarios = leer_usuarios()  
    data = request.get_json()

    for u in usuarios:
        if u["id"] == user_id:
            u["nombre"] = data.get("nombre", u["nombre"])
            u["apellido"] = data.get("apellido", u["apellido"])
            u["email"] = data.get("email", u["email"])
            u["telefono"] = data.get("telefono", u["telefono"])
            u["rut"] = data.get("rut", u["rut"])
            u["direccion"] = data.get("direccion", u["direccion"])
            u["ciudad"] = data.get("ciudad", u["ciudad"])
            guardar_usuarios(usuarios)
            return jsonify({"message": "Usuario actualizado correctamente."}), 200

    return jsonify({"error": "Usuario no encontrado."}), 404

@app.route("/api/usuarios/<int:user_id>", methods=["POST"])
@login_required('admin', 'administrador')
def eliminar_usuario(user_id):
    usuarios = leer_usuarios()
    indice = next((i for i, u in enumerate(usuarios) if u.get("id") == user_id), None)

    if indice is None:
        return jsonify({"error": "Usuario no encontrado."}), 404
    eliminado = usuarios.pop(indice)
    guardar_usuarios(usuarios)

    return jsonify({"message": f"Usuario {eliminado.get('nombre', '')} eliminado correctamente."}), 200
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
    propiedades = leer_propiedades()
    data = request.get_json()

    for p in propiedades:
        if p["id"] == propiedad_id:
            p["nombre"] = data.get("nombre", p["nombre"])
            p["precio"] = data.get("precio", p["precio"])
            p["localizacion"] = data.get("localizacion", p["localizacion"])
            p["tipo"] = data.get("tipo", p["tipo"])
            p["estado"] = data.get("estado", p["estado"])
            p["dormitorios"] = data.get("dormitorios", p["dormitorios"])
            p["baños"] = data.get("baños", p["baños"])
            p["area"] = data.get("area", p["area"])
            p["descripcion"] = data.get("descripcion", p["descripcion"])
            p["coordenadas"] = data.get("coordenadas", p["coordenadas"])
            p["activo"] = data.get("activo", p["activo"])
            p["img"] = data.get("img", p.get("img"))
            guardar_propiedades(propiedades)
            return jsonify({"message": "Propiedad actualizada con éxito."}), 200

    return jsonify({"error": "Propiedad no encontrada."}), 404

@app.route('/api/propiedades/eliminar/<int:propiedad_id>', methods=['POST'])
@login_required('vendedor', 'administrador', 'admin')
def eliminar_propiedad(propiedad_id):
    propiedades = leer_propiedades()
    indice = next((i for i, p in enumerate(propiedades) if p["id"] == propiedad_id), None)
    if indice is None:
        return jsonify({"error": "Propiedad no encontrada."}), 404

    propiedades.pop(indice)
    guardar_propiedades(propiedades)
    return jsonify({"message": "Propiedad eliminada correctamente."}), 200

@app.route('/api/propiedades', methods=['POST'])
@login_required('vendedor', 'administrador', 'admin')
def add_propiedad():
    data = request.get_json(silent=True) or {}
    propiedades = leer_propiedades()
    try:
        campos = _validar_y_normalizar_propiedad(
            data,
            parcial=False,
            propiedades_existentes=propiedades
        )
    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    user_id = session.get('user_id')
    if user_id is None:
        return jsonify({"error": "Autenticación requerida para crear propiedades."}), 401

    campos['propietario'] = user_id
    nueva = {"id": siguiente_id(propiedades), **campos}
    propiedades.append(nueva)
    guardar_propiedades(propiedades)
    return jsonify({
        "message": "Propiedad ingresada con éxito.",
        "propiedad": nueva,
        "propiedades": propiedades
    }), 201


@app.route('/api/propiedades/<int:propiedad_id>', methods=['PUT', 'PATCH'])
@login_required('vendedor', 'administrador', 'admin')
def update_propiedad(propiedad_id):
    propiedades = leer_propiedades()
    indice = next((i for i, p in enumerate(propiedades) if p.get('id') == propiedad_id), None)
    if indice is None:
        return jsonify({"error": "Propiedad no encontrada."}), 404

    propiedad_actual = propiedades[indice]
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
            propiedades_existentes=propiedades,
            propiedad_actual=propiedad_actual
        )
    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    if not campos_actualizados:
        return jsonify({"error": "No se proporcionaron campos para actualizar."}), 400

    propiedad_actualizada = propiedad_actual.copy()
    propiedad_actualizada.update(campos_actualizados)
    propiedades[indice] = propiedad_actualizada
    guardar_propiedades(propiedades)
    return jsonify({"message": "Propiedad actualizada con éxito.", "propiedad": propiedad_actualizada})


@app.route('/api/propiedades/<int:propiedad_id>', methods=['DELETE'])
@login_required('vendedor', 'administrador', 'admin')
def delete_propiedad(propiedad_id):
    propiedades = leer_propiedades()
    indice = next((i for i, p in enumerate(propiedades) if p.get('id') == propiedad_id), None)
    if indice is None:
        return jsonify({"error": "Propiedad no encontrada."}), 404

    propiedad_actual = propiedades[indice]
    user_id = session.get('user_id')
    user_role = session.get('user_role')
    if not _es_admin(user_role) and propiedad_actual.get('propietario') != user_id:
        return jsonify({"error": "No tienes permiso para eliminar esta propiedad."}), 403

    propiedades.pop(indice)
    guardar_propiedades(propiedades)
    return jsonify({"message": "Propiedad eliminada con éxito."})

# Error de archivos locales
@app.route('/api/me', methods=['GET'])
def api_me():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "No autenticado."}), 401

    usuarios = leer_usuarios()
    user = next((u for u in usuarios if u.get('id') == user_id), None)
    if not user:
        return jsonify({"error": "Usuario no encontrado."}), 404

    user_copy = user.copy()
    user_copy.pop('password', None)
    return jsonify(user_copy)
# Error de archivos locales

@app.errorhandler(404)
def not_found_error(error):
    return render_template("error.html", message="La página que buscas no existe (Error 404)."), 404

def convertir_a_base64(ruta_imagen):
    with open(ruta_imagen, "rb") as img:
        return base64.b64encode(img.read()).decode("utf-8")
ph = PasswordHasher()

ROLES_POSIBLES = ["admin", "vendedor", "comprador"]

def rol_legible(hash_guardado):
    if not hash_guardado:
        return "desconocido"
    for rol in ROLES_POSIBLES:
        try:
            if ph.verify(hash_guardado, rol):
                return rol
        except Exception:
            continue
    return "desconocido"


if __name__ == '__main__':

    app.run(debug=True)
