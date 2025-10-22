# app.py
import os
from flask import Flask
from persistencia.base_datos import init_db

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key')
app.config.setdefault('SESSION_COOKIE_HTTPONLY', True)
app.config.setdefault('SESSION_COOKIE_SAMESITE', 'Lax')

# Cache headers (déjalo aquí tal cual)
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

print(app.url_map)

if __name__ == '__main__':
    app.run(debug=True)
