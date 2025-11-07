import pytest
from app import app as flask_app

# Funcionamiento: Configura la app para modo "Testing"
# Esto desactiva cosas como los manejadores de error que interfieren con las pruebas, ya que pytest no se detendra por errores, solo los reportara.
@pytest.fixture
def app():
    flask_app.config.update({
        "TESTING": True,
        "SECRET_KEY": "test-secret-key" # Clave de prueba
    })
    yield flask_app

@pytest.fixture
def client(app):
    # Cliente de prueba simulado
    return app.test_client()