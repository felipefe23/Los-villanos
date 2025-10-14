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

## 1) tener instalado python 3.9 o superior

## 2) crear un entorno virtual con el siguiente comando en la terminal; python -m venv venv

## 3) activar el entorno virtual mediante la terminal con; .\venv\Scripts\activate ; si la activación fue exitosa veras algo asi:
<img width="835" height="70" alt="image" src="https://github.com/user-attachments/assets/9102c8e3-fca2-4846-a7ac-4a829663aca2" />

## 4) ahora, en caso de no poseer pip, instalar extension pip con ; python -m ensurepip --default-pip ;

(necesaria para los siguientes pasos)

## 5) en la terminal ejecutar ; pip install flask ; el cual si se ejecuto bien arrojará algo así hasta finalizar la descarga, adjunto imagen:
<img width="835" height="156" alt="image" src="https://github.com/user-attachments/assets/67702c65-0343-4fcb-9308-9fe5c732abb9" />

## 6) a continuación instalaremos el Argon2, el cual necesita del siguiente comando en terminal; pip install argon2-cffi ; y de manera al flask muy similar arroja lo siguiente:
<img width="837" height="148" alt="image" src="https://github.com/user-attachments/assets/5e6faaea-6156-482a-a394-40744aad25fb" />

## 7) ahora para continuar, instalaremos supabase para poder ejecutar la base de datos, se utiliza el siguiente comando; pip install supabase ; el cual, al igual que las otras extensiones, arroja esto:
<img width="837" height="137" alt="image" src="https://github.com/user-attachments/assets/3264bd59-95a0-4adc-93d8-4b5ee34ca26b" />

## 8) como requerimiento también instalar dotenv con; pip install dotenv ; arroja esto si funciono bien:
<img width="839" height="197" alt="image" src="https://github.com/user-attachments/assets/91e42840-74b7-4b6a-af08-448ce1803ba0" />

## 9) Ya como uno de los ultimos paso, es crear el .env manualmente con los siguientes valores:

SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_SERVICE_KEY=tu-clave-service-role
SECRET_KEY=clave-secreta-para-flask
FLASK_ENV=development
SUPABASE_USERS_TABLE=users
SUPABASE_PROPIEDADES_TABLE=propiedades

## 10) verificar donde se creó el archivo ; .env ; el cual debe estar acá:
<img width="372" height="242" alt="image" src="https://github.com/user-attachments/assets/8ed918b3-3103-42b8-8c21-5571281d277d" />

Debe estar dentro de la raíz del proyecto, fuera de las subcarpetas.

## 11) Finalmente ejecutar y abrir el puerto local que tiene la aplicación.




