# Requisitos del Proyecto

## Requisitos Funcionales

- Realizar un login de usuario, para una experiencia personalizada
- Filtro de resultados (venta, arriendo, precios, ubicación, etc.)
- Implementación API de mapa para una experiencia más inmersiva
- Diversos perfiles y roles (Vendedor, Cliente y administrador)
- Publicación de producto inmobiliario (Subir casas, departamentos)
- Catálogo de propiedades
- Visualización de puntos de interés cercanos de las propiedades
- Rutas de desplazamiento (Los usuarios deben poder planificar rutas y calcular tiempos de desplazamiento a la propiedad a través del mapa)
- Visualización tipo mosaico para ofrecer un filtro de búsqueda distinto
- Área de soporte y políticas de uso

## Requisitos No Funcionales

### PC o Laptop
- Procesador: Intel Core i3 o superior
- Memoria: 8 GB de RAM (16 GB recomendado)
- Almacenamiento: 256 GB SSD o más (recomendado)
- Conexión a Internet para descargar herramientas y acceder a APIs

### Compatibilidad Multiplataforma
- La plataforma debe ser accesible desde diferentes dispositivos (PC, tabletas, teléfonos móviles) y navegadores web comunes (Chrome, Firefox, Safari)

### Mantenimiento
- El sistema debe ser fácil de mantener, con un código bien estructurado y comentarios adecuados para que los desarrolladores puedan agregar nuevas funciones y corregir errores con facilidad

### Servidor
- El servidor debe contar con al menos 4 GB de memoria RAM, etc.

# Requisitos de instalacion paso a paso

## 1) tener instalado python 3.9 o superior.

## 2) crear un entorno virtual con el siguiente comando en la terminal; python -m venv venv

## 3) activar el entorno virtual mediante la terminal con; .\venv\Scripts\activate ; si la activación fue exitosa veras algo asi:
<img width="835" height="70" alt="image" src="https://github.com/user-attachments/assets/9102c8e3-fca2-4846-a7ac-4a829663aca2" />

## 4) se debe escoger el entorno virtual creado, para lo cual presionaremos "ctrl+shift+p" y colocaremos “Python: Select Interpreter” esto arrojará opciones y debemos escoger la siguiente: .\venv\Scripts\python.exe

## 5) ahora, en caso de no poseer pip, instalar extension pip con ; python -m ensurepip --default-pip ;

(necesaria para los siguientes pasos)

## 6) en la terminal ejecutar ; pip install -r requirements.txt ; lo cual instalara todas las dependencias necesarias para la ejecucion correcta.

## 7) Ya como uno de los ultimos paso, es crear el .env manualmente con los valores que estan en el .env.example

## 8) verificar donde se creó el archivo ; .env ; el cual debe estar acá, dentro de la carpeta "Testing":

<img width="300" height="502" alt="image" src="https://github.com/user-attachments/assets/c6637046-5d63-40c0-9234-6189e7e3f91d" />

## 9) Finalmente ejecutar y abrir el puerto local que tiene la aplicación.










