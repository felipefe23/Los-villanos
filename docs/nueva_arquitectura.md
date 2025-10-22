# Acutalización Arquitectura en Capas - *Los Villanos*

## 📌 Contexto
El proyecto original tenía toda la lógica (rutas, validaciones, acceso a base de datos, etc.) concentrada dentro de `app.py`.  
Esto dificultaba el mantenimiento, las pruebas unitarias y la legibilidad.  
Por eso se aplicó una **arquitectura en capas** separando responsabilidades por módulo.

---

## 🗂️ Nueva Estructura de Carpetas

```
LOS-VILLANOS/
│
├── controladores/
│   ├── auth_controller.py
│   ├── usuario_controller.py
│   ├── propiedad_controller.py
│   ├── vista_controller.py
│   └── __init__.py
│
├── servicios/
│   ├── auth_service.py
│   ├── usuario_service.py
│   ├── propiedad_service.py
│   └── __init__.py
│
├── persistencia/
│   ├── base_datos.py
│   ├── manejoArchivo.py
│   └── __init__.py
│
├── utils/
│   ├── decoradores.py
│   ├── helpers.py
│   └── __init__.py
│
├── templates/
│   ├── landing.html
│   ├── vendedor.html
│   ├── comprador_dashboard.html
│   └── ...
│
├── app.py
├── wsgi.py
└── README.md
```

---

## ⚙️ Cambios Realizados y Motivos

### 1. Separación de Capas
| Capa | Archivos | Responsabilidad |
|------|-----------|------------------|
| **Controladores** | `controladores/*.py` | Manejan las rutas Flask y reciben las peticiones HTTP. |
| **Servicios** | `servicios/*.py` | Contienen la lógica de negocio (validaciones, procesamiento, etc.). |
| **Persistencia** | `persistencia/*.py` | Acceden a la base de datos (Supabase en este caso). |
| **Utils** | `utils/*.py` | Contienen decoradores, helpers y funciones reutilizables. |

**Motivo:**  
Permitir que cada módulo tenga una única responsabilidad, siguiendo el principio *Single Responsibility Principle (SRP)*.

---

### 2. Limpieza de `app.py`
El archivo pasó de tener más de 1.000 líneas a un rol mínimo:

```python
from flask import Flask
from persistencia.base_datos import init_db
from controladores import auth_controller, usuario_controller, propiedad_controller, vista_controller

app = Flask(__name__)
app.secret_key = ...
init_db()

@app.after_request
def harden_cache_headers(response):
    ...

if __name__ == "__main__":
    app.run(debug=True)
```

**Motivo:**  
`app.py` ahora **solo inicializa** la aplicación y registra controladores.  
Toda la lógica fue distribuida a las capas correspondientes.

---

### 3. Creación de `wsgi.py`
Archivo nuevo:
```python
from app import app

if __name__ == "__main__":
    app.run(debug=True)
```

**Motivo:**  
Evitar el bug de las **dos instancias de Flask (`__main__` y `app`)**.  
Cuando se ejecutaba `python app.py`, Flask creaba dos copias del objeto `app`,  
provocando que las rutas se registraran en una instancia y el servidor corriera otra.  
Ejecutar `python wsgi.py` garantiza que ambas apunten al mismo objeto Flask.

---

### 4. División por Controladores

| Controlador | Rutas principales | Función |
|--------------|-------------------|---------|
| `auth_controller.py` | `/api/register`, `/api/login`, `/logout` | Registro y autenticación |
| `usuario_controller.py` | `/api/usuarios`, `/api/usuarios/<id>` | CRUD de usuarios |
| `propiedad_controller.py` | `/api/propiedades`, `/api/propiedades/<id>` | CRUD de propiedades |
| `vista_controller.py` | `/`, `/login`, `/admin`, `/vendedor`, `/comprador` | Renderizado de vistas HTML |

**Motivo:**  
Permitir escalar y mantener las rutas de forma modular y ordenada.

---

### 5. Servicios creados

| Archivo | Funciones principales | Propósito |
|----------|-----------------------|-----------|
| `auth_service.py` | `ph = PasswordHasher()` | Manejo de hashing Argon2 |
| `usuario_service.py` | `validar_email`, `validar_password`, `leer_usuarios`, `rol_legible` | Validaciones y lógica de usuario |
| `propiedad_service.py` | `leer_propiedades`, `_es_admin`, `_validar_y_normalizar_propiedad` | Lógica de propiedades y validaciones |

**Motivo:**  
Evitar repetir lógica en controladores y centralizar reglas de negocio.

---

### 6. Utils creados

| Archivo | Contenido | Descripción |
|----------|------------|-------------|
| `decoradores.py` | `login_required`, `harden_cache_headers` | Control de acceso y cache |
| `helpers.py` | `_prefers_json`, `convertir_a_base64` | Funciones de ayuda reutilizables |

**Motivo:**  
Reutilización de funciones comunes y separación de lógica auxiliar.

---

## 🧠 Beneficios Técnicos
- **Mantenibilidad:** cada capa es independiente y testeable.
- **Escalabilidad:** se pueden agregar nuevas funcionalidades sin tocar `app.py`.
- **Legibilidad:** estructura clara, fácil de seguir para nuevos desarrolladores.
- **Reutilización:** lógica de validaciones centralizada en servicios y helpers.
---

## 🚀 Ejecución
```bash
# Activar entorno
python -m venv venv
venv\Scripts\activate  # (Windows)

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar servidor
python wsgi.py
```

---
