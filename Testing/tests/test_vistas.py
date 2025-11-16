
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
    
    # Verificamos que el código sea 400 (Bad Request)
    assert response.status_code == 400
    
    # Verificamos que la respuesta sea JSON
    assert response.is_json
    
    # Verificamos que el JSON de error contenga el mensaje correcto
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


# Prueba 5: CREATE (POST) falla si los datos son malos (400)
def test_create_propiedad_fails_with_bad_data(client):   
    # Prueba que POST /api/propiedades devuelva 400 si faltan campos obligatorios.

    # Simular inicio de sesión como 'vendedor'
    with client.session_transaction() as sess:
        sess['user_id'] = 97
        sess['user_role'] = 'vendedor'
    
    # Enviar datos inválidos (un JSON vacío)
    response = client.post('/api/propiedades', json={})
    
    # Verificar que el código sea 400 (Bad Request)
    assert response.status_code == 400
    
    # Verificar que el error sea sobre un campo obligatorio
    json_data = response.get_json()
    assert "error" in json_data
    # El validador debe quejarse de 'nombre', 'localizacion' o 'tipo'
    assert "obligatorio" in json_data["error"]

# Prueba 6: DELETE (DELETE) falla si el ID no existe (404)
def test_delete_propiedad_fails_for_nonexistent_id(client):
    # Prueba que DELETE /api/propiedades/<id> devuelva 404 si el ID no existe.
    
    # Simular inicio de sesión como 'admin' (para tener permisos)
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['user_role'] = 'admin'
        
    # Intentar borrar un ID que es imposible que exista
    response = client.delete('/api/propiedades/999999')
    
    # Verificar que el código sea 404 (Not Found)
    assert response.status_code == 404
    
    # Verificar el mensaje de error
    json_data = response.get_json()
    assert "no encontrada" in json_data.get("error", "")

# Prueba 7: READ (GET) falla si no eres admin (403)
def test_get_usuarios_fails_if_not_admin(client):
    # Prueba que GET /api/usuarios devuelva 403 si el rol no es admin
    
    # Simular inicio de sesión como 'comprador'
    with client.session_transaction() as sess:
        sess['user_id'] = 99
        sess['user_role'] = 'comprador'
    
    # Hacemos GET a la ruta de admin
    response = client.get('/api/usuarios', headers={"Accept": "application/json"})
    
    
    # Verificar que el código sea 403 (Forbidden)
    assert response.status_code == 403
    
    # Verificar que se muestre el error de permisos
    json_data = response.get_json()
    assert "Permisos insuficientes" in json_data.get("error", "")


# Prueba 8: UPDATE (PUT) falla si no eres admin (403)
def test_update_usuario_fails_if_not_admin(client):
    # Prueba que PUT /api/usuarios/<id> devuelva 403 si el rol no es admin
    
    # Simular inicio de sesión como 'vendedor'
    with client.session_transaction() as sess:
        sess['user_id'] = 98
        sess['user_role'] = 'vendedor'
        
    # Intentar actualizar al usuario con ID 1 (cualquier ID)
    response = client.put('/api/usuarios/1', json={"ciudad": "Test"}, headers={"Accept": "application/json"})
    
    
    # Verificar que el código sea 403 (Forbidden)
    assert response.status_code == 403
    
    # Verificar el mensaje de error
    json_data = response.get_json()
    assert "Permisos insuficientes" in json_data.get("error", "")