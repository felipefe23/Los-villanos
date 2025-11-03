# Funcionamiento: El archivo principal de la aplicación.
# 1. Crea la instancia de la aplicación Flask ('app').
# 2. Configura claves secretas y la seguridad de las cookies.
# 3. Establece cabeceras (headers) para evitar la caché.
# 4. Llama a init_db() para conectar (y poblar) la BD.
# 5. Importa todos los controladores (vistas/APIs) para que sus rutas queden registradas en la app.
# 6. Corre el servidor en modo 'debug' si se ejecuta este archivo directamente.

import os
from flask import Flask
from persistencia.base_datos import init_db
from controladores.map_controller import map_bp

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key')
app.config.setdefault('SESSION_COOKIE_HTTPONLY', True)
app.config.setdefault('SESSION_COOKIE_SAMESITE', 'Lax')
app.register_blueprint(map_bp) 

@app.after_request
def harden_cache_headers(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

# Inicializa DB
init_db()
from controladores import (
    auth_controller,
    usuario_controller,
    propiedad_controller,
    vista_controller
)

if __name__ == '__main__':
    app.run(debug=True)
