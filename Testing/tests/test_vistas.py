
# Prueba 1: Que la página de inicio cargue (Código 200)
# Prueba que la ruta principal '/' cargue correctamente.
def test_landing_page(client):
    response = client.get('/')
    
    # Verificamos que el código de estado sea 200 (OK)
    assert response.status_code == 200
    
    # (Opcional) Verificamos que contenga el HTML del login
    # 'response.data' es el contenido HTML en bytes (por eso la 'b')
    assert b"login" in response.data.lower()


# Prueba 2: Que una ruta inexistente devuelva 404
# Prueba que una ruta que no existe devuelva un 404.
def test_404_not_found(client):
    response = client.get('/esta-ruta-no-existe-999')
    
    assert response.status_code == 404
    # Verificamos que el manejador de error personalizado funcione
    assert b"La p\xc3\xa1gina que buscas no existe" in response.data


# Prueba 3: Que la API de login devuelva 400 (Bad Request) si no enviamos datos
# Prueba que POST a /api/login sin JSON devuelva un error 400.
# Esta es una prueba de "camino triste" (sad path).
def test_api_login_sin_datos(client):
    
    # Hacemos un POST a la API, pero sin enviar un body/json
    response = client.post('/api/login', json={})
    
    # 1. Verificamos que el código sea 400 (Bad Request)
    assert response.status_code == 400
    
    # 2. Verificamos que la respuesta sea JSON
    assert response.is_json
    
    # 3. Verificamos que el JSON de error contenga el mensaje correcto
    json_data = response.get_json()
    assert 'error' in json_data
    assert json_data['error'] == 'Correo no encontrado.'


# Prueba 4: Que la ruta de admin devuelva 403 (Prohibido) para un rol incorrecto
def test_admin_route_forbidden_for_comprador(client):
    # Simula una sesion de usuario con rol 'comprador'
    # Usamos session_transaction para modificar la sesion antes de la solicitud
    with client.session_transaction() as sess:
        sess['user_id'] = 99 # ID de prueba, no importa el valor
        sess['user_role'] = 'comprador'
    
    # Ahora hacemos la solicitud GET a /admin (estando logueados como 'comprador')
    response = client.get('/admin')
    
    # Verificar que el codigo de estado sea 403 (Forbidden)
    assert response.status_code == 403
    
    assert b"No tienes permiso para acceder" in response.data