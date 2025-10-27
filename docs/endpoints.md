# Endpoints ViviendaDigital

Base URL de desarrollo: `http://localhost:5000`

## Variables de entorno relevantes

| Clave | Uso |
| --- | --- |
| `SECRET_KEY` | Firma las cookies de sesión de Flask. |
| `SUPABASE_URL` | URL del proyecto Supabase utilizado como backend de datos. |
| `SUPABASE_SERVICE_KEY` | Clave de servicio para operaciones CRUD. |
| `SUPABASE_USERS_TABLE` | Nombre de la tabla de usuarios (por defecto `users`). |
| `SUPABASE_PROPIEDADES_TABLE` | Nombre de la tabla de propiedades (por defecto `propiedades`). |

## Autenticación

Los endpoints protegidos utilizan sesiones de Flask. Realiza `POST /api/login` primero; las credenciales válidas guardan `session` y devuelven una cookie. Para cerrar sesión usa `POST /logout`. Los perfiles admitidos son `admin`, `administrador`, `vendedor` y `comprador` (según el rol almacenado en Supabase).

---

## POST /api/register

Crea un usuario final (vendedor o comprador). No requiere autenticación previa.

```bash
curl -X POST http://localhost:5000/api/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "nuevo@correo.com",
    "password": "Clave1234",
    "nombre": "María",
    "apellido": "Pérez",
    "telefono": "+56 9 1111 2222",
    "rut": "12345678-9",
    "direccion": "Av. Principal 123",
    "ciudad": "Santiago",
    "tipo_usuario": "vendedor"
  }'
```

Respuesta exitosa (`200 OK`):

```json
{
  "message": "Usuario registrado con éxito.",
  "user": {
    "apellido": "Pérez",
    "ciudad": "Santiago",
    "direccion": "Av. Principal 123",
    "email": "nuevo@correo.com",
    "fecha_registro": "2024-10-27T18:32:11.214598Z",
    "id": 42,
    "nombre": "María",
    "rut": "12345678-9",
    "telefono": "+56 9 1111 2222",
    "tipo_usuario": "vendedor"
  }
}
```

Errores comunes: `400` si el correo ya existe o alguna validación de campos falla.

---

## POST /api/login

Valida credenciales, inicializa la sesión y retorna la URL de destino según el rol.

```bash
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -c cookies.txt \
  -d '{
    "email": "admin@correo.com",
    "password": "Clave1234",
    "tipo_usuario": "admin"
  }'
```

Respuesta exitosa (`200 OK`):

```json
{
  "message": "Login exitoso.",
  "redirect": "/admin",
  "user": {
    "apellido": "Admin",
    "ciudad": "Santiago",
    "direccion": "Calle 1",
    "email": "admin@correo.com",
    "fecha_registro": "2023-09-12T13:44:20Z",
    "id": 1,
    "nombre": "Super",
    "rut": "11.111.111-1",
    "telefono": "+56 9 0000 0000",
    "tipo_usuario": "admin"
  }
}
```

Errores comunes: `400` si el correo no existe, la contraseña es incorrecta o el tipo de usuario no coincide.

---

## GET /api/propiedades

Entrega el catálogo completo de propiedades, incluyendo el nombre legible del propietario (si existe). No requiere autenticación.

```bash
curl http://localhost:5000/api/propiedades
```

Respuesta (`200 OK`):

```json
[
  {
    "activo": true,
    "area": 85,
    "descripcion": "Departamento céntrico.",
    "estado": "venta",
    "id": 7,
    "img": null,
    "localizacion": "Santiago, Chile",
    "nombre": "Depto Centro",
    "precio": 125000000,
    "propietario": 12,
    "propietario_nombre": "Ana Rojas",
    "tipo": "Departamento"
  }
]
```

---

## POST /api/propiedades

Crea una propiedad asociada al usuario autenticado. Requiere rol `vendedor`, `administrador` o `admin` y cookie de sesión.

```bash
curl -X POST http://localhost:5000/api/propiedades \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "nombre": "Casa Las Palmas",
    "precio": 235000000,
    "localizacion": "Valparaíso, Chile",
    "tipo": "Casa",
    "estado": "venta",
    "dormitorios": 4,
    "baños": 3,
    "area": 180,
    "descripcion": "Casa familiar con patio.",
    "coordenadas": "-33.0472,-71.6127",
    "activo": true,
    "img": null
  }'
```

Respuesta exitosa (`201 Created`):

```json
{
  "message": "Propiedad ingresada con éxito.",
  "propiedad": {
    "activo": true,
    "area": 180,
    "coordenadas": "-33.0472,-71.6127",
    "descripcion": "Casa familiar con patio.",
    "dormitorios": 4,
    "estado": "venta",
    "id": 18,
    "img": null,
    "localizacion": "Valparaíso, Chile",
    "nombre": "Casa Las Palmas",
    "precio": 235000000,
    "propietario": 12,
    "tipo": "Casa"
  }
}
```

Errores comunes: `400` para validaciones de dominios (campos faltantes, duplicados), `401` si no hay sesión activa.

---

## DELETE /api/propiedades/<id>

Elimina una propiedad del usuario autenticado. Los administradores pueden borrar cualquier registro.

```bash
curl -X DELETE http://localhost:5000/api/propiedades/18 \
  -b cookies.txt
```

Respuesta (`200 OK`):

```json
{
  "message": "Propiedad eliminada con éxito."
}
```

Errores comunes: `403` cuando un vendedor intenta eliminar una propiedad que no le pertenece; `404` si el ID no existe.

---

## GET /api/usuarios

Lista los usuarios registrados. Restringido a roles `admin` o `administrador`.

```bash
curl http://localhost:5000/api/usuarios \
  -b cookies.txt
```

Respuesta (`200 OK`):

```json
[
  {
    "apellido": "Rojas",
    "ciudad": "Concepción",
    "direccion": "Los Cipreses 45",
    "email": "vendedora@correo.com",
    "id": 12,
    "nombre": "Ana",
    "rol_legible": "Vendedor",
    "rut": "19.876.543-2",
    "telefono": "+56 9 2222 3333",
    "tipo_usuario": "vendedor"
  }
]
```

Errores comunes: `401/403` si la sesión no pertenece a un administrador.

---

## PUT /api/usuarios/<id>

Actualiza datos de un usuario específico (solo administradores). Permite cambios parciales y valida cada campo.

```bash
curl -X PUT http://localhost:5000/api/usuarios/12 \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "telefono": "+56 9 4444 5555",
    "ciudad": "Viña del Mar",
    "tipo_usuario": "vendedor"
  }'
```

Respuesta (`200 OK`):

```json
{
  "message": "Usuario actualizado correctamente.",
  "user": {
    "apellido": "Rojas",
    "ciudad": "Viña del Mar",
    "direccion": "Los Cipreses 45",
    "email": "vendedora@correo.com",
    "id": 12,
    "nombre": "Ana",
    "rol_legible": "Vendedor",
    "rut": "19.876.543-2",
    "telefono": "+56 9 4444 5555",
    "tipo_usuario": "vendedor"
  }
}
```

Errores comunes: `400` si un campo no cumple validaciones, `404` cuando el usuario no existe.

---

## POST /logout

Cierra la sesión actual y limpia las cookies.

```bash
curl -X POST http://localhost:5000/logout \
  -b cookies.txt
```

Respuesta (`200 OK`):

```json
{
  "message": "Sesión cerrada."
}
```

---

### Notas

- Todos los ejemplos suponen que el servidor corre en local (`flask run` o `python Testing/app.py`). Ajusta el host/puerto según tu despliegue.
- Las respuestas reales pueden incluir campos adicionales provenientes de Supabase (por ejemplo `fecha_registro`).
- Mantén tu archivo `.env` fuera de control de versiones para proteger las llaves de servicio.
