import json
import re
from flask import render_template, jsonify, session, redirect, url_for, request, abort
from utils.helpers import _prefers_json
from app import app
from utils.decoradores import login_required
from persistencia.base_datos import obtener_usuario_por_id, obtener_propiedad_por_id
from servicios.usuario_service import leer_usuarios, rol_legible
from servicios.propiedad_service import leer_propiedades
from httpx import TimeoutException
from utils.helpers import obtener_valor_uf_actual

IMAGENES_ESPECIALES = {
    1: "https://images.homify.com/v1492435533/p/photo/image/1958308/_FV_0284.jpg",
    2: "https://images.homify.com/image/upload/a_0/v1483627329/p/photo/image/1759556/3339.jpg",
    3: "https://www.imsa-adportas.cl/web/wp-content/uploads/2021/05/cord3-ch1f.jpg",
    4: "https://dbtotl1p8f93r.cloudfront.net//content/uploads/2021/04/AH_dest_945x650.jpg",
    7: "https://images.homify.com/v1492435533/p/photo/image/1958308/_FV_0284.jpg",
    8: "https://images.adsttc.com/media/images/5a58/a7ca/f197/cc1f/8600/0182/newsletter/S3_CDS-5766.jpg?1515759553",
}


def _imagen_especial(propiedad):
    try:
        prop_id = int(propiedad.get("id"))
    except (TypeError, ValueError):
        return None
    return IMAGENES_ESPECIALES.get(prop_id)

_BASE64_RE = re.compile(r'^[A-Za-z0-9+/=\n\r]+$')
_IMAGE_PATH_RE = re.compile(r'/[^/]+\.(jpe?g|png|webp|gif)(\?.*)?$', re.IGNORECASE)

def _parece_base64(cadena: str) -> bool:
    """Heurística simple para diferenciar base64 crudo de rutas absolutas."""
    texto = (cadena or "").strip()
    if len(texto) < 50:
        return False
    return bool(_BASE64_RE.match(texto))

def _resolver_imagen_src(valor):
    if not valor:
        return None
    dato = str(valor).strip()
    if not dato:
        return None
    if dato.startswith(("http://", "https://", "data:")):
        return dato
    if dato.startswith("/") and _IMAGE_PATH_RE.search(dato):
        return dato
    if _parece_base64(dato):
        return f"data:image/jpeg;base64,{dato}"
    return f"data:image/jpeg;base64,{dato}"


def _galeria_para_propiedad(propiedad):
    if not propiedad:
        return []
    posibles = (
        propiedad.get("galeria")
        or propiedad.get("fotos")
        or propiedad.get("imagenes")
        or propiedad.get("imagenes_urls")
    )
    imagenes = []
    if isinstance(posibles, list):
        imagenes = posibles
    elif isinstance(posibles, dict):
        imagenes = list(posibles.values())
    elif isinstance(posibles, str):
        cadena = posibles.strip()
        if cadena:
            try:
                parsed = json.loads(cadena)
                if isinstance(parsed, list):
                    imagenes = parsed
                elif isinstance(parsed, str):
                    imagenes = [parsed]
            except json.JSONDecodeError:
                separadores = ["|", ";", ","]
                partes = [cadena]
                for separador in separadores:
                    if separador in cadena:
                        partes = [p.strip() for p in cadena.split(separador)]
                        break
                imagenes = [p for p in partes if p]
    if not imagenes and propiedad.get("img"):
        imagenes = [propiedad.get("img")]

    resultado = []
    for imagen in imagenes:
        src = _resolver_imagen_src(imagen)
        if src and src not in resultado:
            resultado.append(src)
    especial = _imagen_especial(propiedad)
    if especial:
        resultado = [especial] + [img for img in resultado if img != especial]
    return resultado


def _imagen_portada(propiedad):
    galeria = _galeria_para_propiedad(propiedad)
    return galeria[0] if galeria else None

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
    return render_template('login.html', error_message=mensaje_error)


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
# Captura los filtros de la URL (request.args).
# Llama a 'leer_propiedades' pasando esos filtros para obtener la lista reducida.
# Filtra adicionalmente para asegurar que solo se vean propiedades 'activas'.
# Asocia el nombre del propietario y renderiza el panel.
@app.get("/comprador")
@login_required('comprador', 'administrador', 'admin')
def comprador_dashboard_view():  
    try:
        valor_uf_actual = obtener_valor_uf_actual()
        
        # Paginación: Página 1 por defecto
        try: page = int(request.args.get('page', 1))
        except ValueError: page = 1

        # Llamamos al servicio PIDIENDO paginación explícitamente
        resultado = leer_propiedades(filtros=request.args, pagina=page, por_pagina=9)
        
        # Desempaquetamos el diccionario
        propiedades_data = resultado['propiedades']
        paginacion = {
            'total': resultado['total'],
            'paginas': resultado['paginas'],
            'actual': resultado['actual']
        }

        usuarios = leer_usuarios()
        nombres = {u.get('id'): f"{u.get('nombre','').strip()} {u.get('apellido','').strip()}".strip() for u in usuarios}
        
        propiedades_filtradas = []
        for p in propiedades_data:
            if not p.get('activo', True): continue
            
            copia = p.copy()
            prop_id = copia.get('propietario')
            copia['propietario_nombre'] = nombres.get(prop_id) if nombres.get(prop_id) else None
            copia['imagen_portada'] = _imagen_portada(copia)
            
            # URL de detalle para el mapa y botones
            if copia.get('id'):
                copia['detalle_url'] = url_for('comprador_propiedad_detalle', propiedad_id=copia.get('id'))
                
            propiedades_filtradas.append(copia)
        
        # Preparamos los filtros para mantener en la paginación
        filtros_limpios = request.args.copy()
        filtros_limpios.pop('page', None) 
        

        return render_template(
            "comprador_dashboard.html", 
            propiedades=propiedades_filtradas, 
            valor_uf=valor_uf_actual,
            paginacion=paginacion,
            filtros=filtros_limpios
        )
    except TimeoutException:
        print(f"ERROR: Timeout en la ruta {request.path}")
        return render_template("error.html", message="La base de datos tardó demasiado."), 504
    except Exception as e:
        print(f"ERROR: {e}")
        return render_template("error.html", message=f"Error inesperado: {e}"), 500


@app.get("/comprador/propiedades/<int:propiedad_id>")
def comprador_propiedad_detalle(propiedad_id):
    try:
        propiedad = obtener_propiedad_por_id(propiedad_id)
        if not propiedad or not propiedad.get('activo', True):
            return render_template("error.html", message="La propiedad no está disponible o fue inhabilitada."), 404

        usuarios = leer_usuarios()
        propietario = next((u for u in usuarios if u.get('id') == propiedad.get('propietario')), None)
        galeria = _galeria_para_propiedad(propiedad)
        valor_uf_actual = obtener_valor_uf_actual()

        return render_template(
            "propiedad_detalle.html",
            propiedad=propiedad,
            propietario=propietario,
            galeria=galeria,
            valor_uf=valor_uf_actual
        )

    except TimeoutException:
        print(f"ERROR: Timeout en la ruta {request.path}")
        return render_template("error.html", message="La base de datos tardó demasiado en responder (Timeout)."), 504
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
        vendedores = [u for u in usuarios if str(u.get('tipo_usuario')).strip().lower() == 'vendedor']
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
            valor_uf=valor_uf_actual,
            vendedores=vendedores
        )
        
    # Bloque para capturar el Timeout (devuelve HTML)
    except TimeoutException:
        print(f"ERROR: Timeout en la ruta {request.path}")
        return render_template("error.html", message="La base de datos tardó demasiado en responder (Timeout)."), 504
    # Bloque para capturar errores generales
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


# Funcionamiento: Ruta pública para el catálogo de ventas.
# Obtiene el valor UF y prepara filtros (forzando estado='venta').
# Gestiona la paginación (página actual) y llama al servicio para obtener datos recortados.
# Enriquece las propiedades (nombres, imágenes de portada, URLs de detalle).
# Limpia los filtros (quita 'page') para generar correctamente los enlaces de paginación.
@app.get("/ventas")
def ventas_view():
    try:
        valor_uf_actual = obtener_valor_uf_actual()
        
        filtros_publicos = request.args.copy()
        filtros_publicos['estado'] = 'venta' 
        
        try: page = int(request.args.get('page', 1))
        except ValueError: page = 1
            
        # Llamada con paginación
        resultado = leer_propiedades(filtros=filtros_publicos, pagina=page, por_pagina=9)
        
        propiedades_data = resultado['propiedades']
        paginacion = {
            'total': resultado['total'],
            'paginas': resultado['paginas'],
            'actual': resultado['actual']
        }
        
        usuarios = leer_usuarios() 
        nombres = {u.get('id'): f"{u.get('nombre','').strip()} {u.get('apellido','').strip()}".strip() for u in usuarios}
        
        propiedades_venta = []
        for p in propiedades_data:
            if not p.get('activo', True): continue
            
            copia = p.copy()
            prop_id = copia.get('propietario')
            copia['propietario_nombre'] = nombres.get(prop_id) if nombres.get(prop_id) else None
            copia['imagen_portada'] = _imagen_portada(copia)
            if copia.get('id'):
                copia['detalle_url'] = url_for('comprador_propiedad_detalle', propiedad_id=copia.get('id'))
            
            propiedades_venta.append(copia)

        # Preparar filtros limpios para paginación
        filtros_limpios = request.args.copy()
        filtros_limpios.pop('page', None)
        

        return render_template(
            "comprador_dashboard.html", 
            propiedades=propiedades_venta,
            valor_uf=valor_uf_actual,
            paginacion=paginacion,
            filtros=filtros_limpios 
        )
    except TimeoutException:
        print(f"ERROR: Timeout en la ruta {request.path}")
        return render_template("error.html", message="La base de datos tardó demasiado."), 504
    except Exception as e:
        print(f"ERROR: {e}")
        return render_template("error.html", message=f"Error inesperado: {e}"), 500
    
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
