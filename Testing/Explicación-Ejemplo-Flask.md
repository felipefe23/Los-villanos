# Breve Explicación de Flask para Interactuar con HTML y JSON

**Flask** es un microframework de Python para desarrollar aplicaciones web de forma sencilla y flexible. Permite crear interfaces web dinámicas al integrar backend (Python) con frontend (HTML, JavaScript) y manejar datos en formato JSON.

## ¿Cómo usa Flask HTML y JSON?
- **Renderizado de HTML**: Flask utiliza la carpeta `templates` para almacenar archivos HTML. Con la función `render_template`, se pueden servir páginas web dinámicas al frontend.
- **Manejo de JSON**: Flask permite enviar y recibir datos JSON mediante rutas. Usando `jsonify`, el backend puede enviar datos JSON al frontend, y con `request.get_json()`, puede procesar datos JSON enviados desde el frontend.
- **Interacción dinámica**: A través de rutas (por ejemplo, `/get_data` para GET o `/post_data` para POST), Flask conecta el HTML (usando JavaScript para solicitudes `fetch`) con el backend, permitiendo mostrar o enviar datos JSON en la interfaz web.

## Ejemplo Básico
- Un archivo HTML en `templates/index.html` se renderiza con una ruta (`@app.route('/')`).
- JavaScript en el HTML hace solicitudes a rutas como `/get_data` para obtener datos JSON o `/post_data` para enviarlos.
- Los datos JSON pueden provenir de un archivo (`data.json`) o generarse dinámicamente en el backend.
