from flask import Flask, render_template, request, jsonify
from flask import redirect, url_for, session
from functools import wraps
from persistencia.manejoArchivo import leer_propiedades, guardar_propiedades, coordenadas_repetidas, siguiente_id
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
    data = request.json or {}
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
    data = request.json or {}
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
        return jsonify({"error": "ContraseÃ±a incorrecta."}), 400

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
    propiedades_filtradas = [p for p in propiedades if p.get("activo", True)]
    return render_template("comprador_dashboard.html", propiedades=propiedades_filtradas)

@app.get("/admin")
@login_required('admin', 'administrador')
def admin_dashboard_view():
    return render_template("admin_dashboard.html")

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



@app.route('/api/propiedades', methods=['GET'])
def get_propiedades():
    propiedades = leer_propiedades()
    return jsonify(propiedades)

@app.route('/api/propiedades', methods=['POST'])
def add_propiedad():
    data = request.json
    nombre = data.get('nombre')
    descripcion = data.get('descripcion')
    if not descripcion:
        descripcion = "Sin descripción"
    precio = data.get('precio')
    propietario = data.get('propietario')
    localizacion = data.get('localizacion')
    dormitorios = data.get('dormitorios')
    baños = data.get('baños')
    area = data.get('area')
    tipo = data.get('tipo')
    estado = data.get('estado')
    activo = data.get('activo', True)
    img = data.get('img')
    coordenadas = data.get('coordenadas')



 ## VALIDACIONES !!!!!!!
 
    try:
        precio = int(precio)
    except (ValueError, TypeError):
        return jsonify({"error": "El precio debe ser un número."}), 400
    
    try:
        dormitorios = int(dormitorios)
    except (ValueError, TypeError):
        return jsonify({"error": "Los dormitorios deben ser un número."}), 400
    
    try:
        baños = int(baños)
    except (ValueError, TypeError):
        return jsonify({"error": "Los baños deben ser un número."}), 400

    try:
        area = int(area)
    except (ValueError, TypeError):
        return jsonify({"error": "El área debe ser un número."}), 400 
    
    
    estado= estado.lower()
    if estado != "venta" and estado != "arriendo":
        return jsonify({"error": "El estado debe ser 'venta' o 'arriendo'."}), 400
    

    if coordenadas_repetidas(leer_propiedades(), coordenadas):
        return jsonify({"error": "Las coordenadas ya existen en otra propiedad."}), 400
    

    if precio is None or precio <= 0:
        return jsonify({"error": "El precio debe ser un número entero positivo o mayor a 0."}), 400
    
    if dormitorios is None or dormitorios <= 0:
        return jsonify({"error": "El número de dormitorios debe ser un entero no negativo."}), 400
    
    if baños is None or baños <= 0:
        return jsonify({"error": "El número de baños debe ser un entero no negativo."}), 400

    if area is None or area <= 0:
        return jsonify({"error": "El área debe ser un entero no negativo ni 0."}), 400

    if descripcion.strip() == "":
        descripcion = "Sin descripción"


    
    propiedades = leer_propiedades()
    nueva = {
        "id": siguiente_id(propiedades),
        "nombre": nombre,
        "descripcion": descripcion,
        "precio": precio,
        "propietario": propietario,
        "localizacion": localizacion,
        "dormitorios": dormitorios,
        "baños": baños,
        "area": area,
        "tipo": tipo,
        "estado": estado,
        "activo": activo,
        "img": img,
        "coordenadas": coordenadas
    }
    propiedades.append(nueva)
    guardar_propiedades(propiedades)
    return jsonify({"message": "Propiedad ingresada con éxito.", "propiedades": propiedades})


@app.errorhandler(404)
def not_found_error(error):
    return render_template("error.html", message="La página que buscas no existe (Error 404)."), 404

def convertir_a_base64(ruta_imagen):
    with open(ruta_imagen, "rb") as img:
        return base64.b64encode(img.read()).decode("utf-8")



if __name__ == '__main__':

    app.run(debug=True)
