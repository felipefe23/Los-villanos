from flask import render_template, jsonify, session, redirect, url_for, request, abort
from utils.helpers import _prefers_json
from app import app
from utils.decoradores import login_required
from persistencia.base_datos import obtener_usuario_por_id
from servicios.usuario_service import leer_usuarios, rol_legible
from servicios.propiedad_service import leer_propiedades
from httpx import TimeoutException
from utils.helpers import obtener_valor_uf_actual

## TESTING DE MANEJO DE ERRORES !


@app.route('/test-500')
def test_error_500():
    # Forzamos un error de Python (ZeroDivisionError)
    x = 1 / 0
    return "No deberías ver esto"


@app.route('/test-403')
@login_required('admin') # Solo 'admin' puede ver esto
def test_error_403():
    # Esta ruta está protegida, pero la usaremos de otra forma.
    # Simplemente la visitaremos con un usuario no-admin.
    return "No deberías ver esto"



# Una forma más directa de probar el manejador 403 es:
@app.route('/test-403-directo')
def test_error_403_directo():
    abort(403) # Forzamos el error 403


@app.route('/test-401')
def test_error_401():
    abort(401) # Forzamos el error 401

    

@app.route('/test-400')
def test_error_400():
    abort(400) # Forzamos el error 400



# Funcionamiento: Es la página de inicio (y login).
# Limpia cualquier sesión existente (cierra sesión).
# Muestra un mensaje de error si fue redirigido (ej. login fallido).
# Renderiza la plantilla principal 'landing.html'.
@app.route('/')
def landing():
    mensaje_error = session.pop('error_message', '')
    session.clear()
    return render_template('landing.html', error_message=mensaje_error)


# Funcionamiento: Alias de la ruta principal ('/').
# Limpia la sesión y muestra la página de login.
# Útil si el usuario intenta acceder a /login directamente.
@app.get('/login')
def login_view():
    mensaje_error = session.pop('error_message', '')
    session.clear()
    return render_template('landing.html', error_message=mensaje_error)


# Funcionamiento: Redirige cualquier intento de login
# por roles (ej. /admin/login) a la página
# de login principal ('landing').
@app.get("/admin/login")
def admin_login_view():
    return redirect(url_for('landing'))


# Funcionamiento: Redirige cualquier intento de login
# por roles (ej. /admin/login) a la página
# de login principal ('landing').
@app.get("/vendedor/login")
def vendedor_login_view():
    return redirect(url_for('landing'))


# Funcionamiento: Redirige cualquier intento de login
# por roles (ej. /admin/login) a la página
# de login principal ('landing').
@app.get("/comprador/login")
def comprador_login_view():
    return redirect(url_for('landing'))


# Funcionamiento: Muestra la página de registro
# específica para nuevos compradores.
@app.get("/comprador/register")
def comprador_register_view():
    return render_template("comprador_register.html")


# Funcionamiento: Protegido por login (comprador/admin).
# Obtiene todas las propiedades y usuarios.
# Filtra las propiedades para mostrar solo las 'activas'.
# Asocia el nombre del propietario a cada propiedad.
# Renderiza el panel del comprador con la lista filtrada.
@app.get("/comprador")
@login_required('comprador', 'administrador', 'admin')
def comprador_dashboard_view():  
    # Inicio del bloque try para capturar errores
    try:
        valor_uf_actual = obtener_valor_uf_actual()
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
        return render_template("comprador_dashboard.html", propiedades=propiedades_filtradas, valor_uf=valor_uf_actual)
    
    # Bloque para capturar el Timeout (devuelve HTML)
    except TimeoutException:
        print(f"ERROR: Timeout en la ruta {request.path}")
        return render_template("error.html", message="La base de datos tardó demasiado en responder (Timeout)."), 504
    # Bloque para capturar errores generales
    except Exception as e:
        print(f"ERROR: Error general en {request.path}: {e}")
        return render_template("error.html", message=f"Ocurrió un error inesperado: {e}"), 500


# Funcionamiento: Protegido por login (solo admin).
# Obtiene TODAS las propiedades y TODOS los usuarios.
# Asocia nombres de propietario a propiedades y roles legibles a usuarios.
# A diferencia del comprador, muestra propiedades activas e inactivas.
# Renderiza el panel de admin con ambas listas completas.
@app.get("/admin")
@login_required('admin', 'administrador')
def admin_dashboard_view():
    # Inicio del bloque try para capturar errores
    try:
        valor_uf_actual = obtener_valor_uf_actual()
        #raise TimeoutException("Forzando demo de Timeout")
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
            usuarios=usuarios,
            valor_uf=valor_uf_actual
        )
        
    # Bloque para capturar el Timeout (devuelve HTML)
    except TimeoutException:
        print(f"ERROR: Timeout en la ruta {request.path}")
        return render_template("error.html", message="La base de datos tardó demasiado en responder (Timeout)."), 504
    #Bloque para capturar errores generales
    except Exception as e:
        print(f"ERROR: Error general en {request.path}: {e}")
        return render_template("error.html", message=f"Ocurrió un error inesperado: {e}"), 500


# Funcionamiento: Protegido por login (vendedor/admin).
# Muestra la página principal o panel del vendedor.
@app.get("/vendedor")
@login_required('vendedor', 'administrador', 'admin')
def vendedor_view():
    return render_template("vendedor.html")


# Funcionamiento: Muestra la página de registro
# específica para nuevos vendedores.
@app.get("/vendedor/register")
def vendedor_register_view():
    return render_template("vendedor_register.html")


# Funcionamiento: Endpoint de API (para el frontend).
# Revisa la sesión para ver quién está logueado.
# Obtiene los datos de ese usuario desde la BD.
# Quita el password por seguridad y retorna el
# objeto del usuario actual en formato JSON.
@app.route('/api/me', methods=['GET'])
def api_me():
    # Inicio del bloque try para capturar errores
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({"error": "No autenticado."}), 401

        user = obtener_usuario_por_id(user_id)
        if not user:
            return jsonify({"error": "Usuario no encontrado."}), 404

        user_copy = user.copy()
        user_copy.pop('password', None)
        return jsonify(user_copy)
        
    # Bloque para capturar el Timeout (devuelve JSON)
    except TimeoutException:
        print(f"ERROR: Timeout en la ruta {request.path}")
        return jsonify({"error": "La base de datos tardó demasiado en responder (Timeout)."}), 504
    # Bloque para capturar errores generales
    except Exception as e:
        print(f"ERROR: Error general en {request.path}: {e}")
        return jsonify({"error": f"Ocurrió un error inesperado: {e}"}), 500


# Funcionamiento: Página pública.
# Obtiene todas las propiedades del sistema.
# Filtra la lista para incluir solo aquellas
# cuyo estado es 'venta'.
# Renderiza la plantilla 'ventas.html' con esa lista.
@app.get("/ventas")
def ventas_view():
    # Inicio del bloque try para capturar errores
    try:
        valor_uf_actual = obtener_valor_uf_actual()
        propiedades = leer_propiedades()
        propiedades_venta = [p for p in propiedades if p.get("estado", "").lower() == "venta"]
        return render_template("ventas.html", propiedades=propiedades_venta, valor_uf=valor_uf_actual)
        
    # Bloque para capturar el Timeout (devuelve HTML)
    except TimeoutException:
        print(f"ERROR: Timeout en la ruta {request.path}")
        return render_template("error.html", message="La base de datos tardó demasiado en responder (Timeout)."), 504
    # Bloque para capturar errores generales
    except Exception as e:
        print(f"ERROR: Error general en {request.path}: {e}")
        return render_template("error.html", message=f"Ocurrió un error inesperado: {e}"), 500


# Funcionamiento: Manejador de errores global.
# Se activa automáticamente cuando Flask no
# encuentra una ruta (error 404).
# Muestra la plantilla 'error.html' personalizada.
@app.errorhandler(404)
def not_found_error(error):
    return render_template("error.html", message="La página que buscas no existe (Error 404)."), 404


# Funcionamiento: Manejador de errores global para 500.
# Se activa si hay un error de programación o un fallo inesperado en el servidor.
@app.errorhandler(500)
def internal_server_error(error):
    return render_template("error.html", message="Ha ocurrido un error inesperado en el servidor (Error 500)."), 500


# Funcionamiento: Manejador de errores global para 403.
# Se activa cuando un usuario autenticado no tiene los permisos para acceder a una página.
@app.errorhandler(403)
def forbidden_error(error):
    return render_template("error.html", message="No tienes permiso para acceder a esta página (Error 403)."), 403


# Funcionamiento: Manejador de errores global para 401.
# Se activa si se requiere autenticación pero el usuario no ha iniciado sesión.
@app.errorhandler(401)
def unauthorized_error(error):
    # El decorador login_required ya maneja esto redirigiendo al login,
    # pero este es un "seguro" en caso de que se llame a la API sin sesión.
    if _prefers_json(): # Función que esta en utils/helpers.py
        return jsonify({"error": "Autenticación requerida."}), 401
    return render_template("error.html", message="Necesitas iniciar sesión para ver esta página (Error 401)."), 401


# Funcionamiento: Manejador de errores global para 400.
# Se activa si el navegador envía una petición mal formada.
@app.errorhandler(400)
def bad_request_error(error):
    # Generalmente las APIs manejan esto con JSON, pero esto capturaría el resto
    if _prefers_json(): # Función que esta en utils/helpers.py
        return jsonify({"error": "Petición incorrecta."}), 400
    return render_template("error.html", message="La petición que enviaste es incorrecta (Error 400)."), 400
