# Página Web de Venta de Casas

Este proyecto tiene como objetivo crear una plataforma web donde los usuarios puedan explorar y comprar casas. La aplicación incluirá una interfaz fácil de usar, con un catálogo de propiedades disponibles. Además, se integrará la API de Google Maps para mostrar la ubicación de cada propiedad en un mapa interactivo, además, contara con diversas herramientas para facilitar la entrega de detalles sobre la propiedad.

## Integrantes de proyecto

- Luis Felipe Guzman. GitHub: felipefe23  Trello: @lguzman241
- Diego Ignacio Rojas. GitHub: DiCloudd  Trello: @diegoignaciorojasacevedo1
- Francisco Javier Reyes. GitHub: frryesss  Trello: @fcooreyes44
- Joaquin Emilio Contreras. GitHub: Jo4King09  Trello: @jocontreras24

## Características clave:
- *Búsqueda de propiedades:* Los usuarios pueden buscar casas según su ubicación, precio, y características.
- *Mapa interactivo:* La API de leaflet se utilizará para mostrar la ubicación exacta de cada propiedad.
- *Interfaz fácil de usar:* La página contará con un diseño limpio y sencillo, permitiendo una navegación fluida.

### BITACIORA DE AVANCES:

# Detalles de avance - Semana 1:
Como grupo decidimos conocernos y ver que intereses en común teníamos para llegar a una idea en concreto para el proyecto, sumado a una definición del
tablero Kanban en el trello, asignación de roles, acta de equipo y la creación de este archivo readme que funcionara como "bitácora" de los avances en las semanas.

# Detalles de avance - Semana 2:
Se definió como grupo de trabajo completo aquellos requisitos funcionales y no funcionales para el proyecto. Posteriormente
Mediante la búsqueda de una buena API que reemplazara la idea de Google Maps, decidimos implementar "Leaflet" para el proyecto.

Los datos y el enlace de la API están en su documento correspondiente.

# Detalles de avance - Semana 3:
Se concreto la búsqueda de información para el uso de la API en el proyecto imaginado. A su vez, nos correspondió definir
nuestro diagrama de capas a utilizar, el cual nos basamos esencialmente en el presentado por el profesor, manteniendo la sencillez inicial
y pensando en lo que usaríamos en un comienzo, ya una mayor complejidad vendría dependiendo de las necesidades que vayan surgiendo.

# Detalles de avance - Semana 4:
Para esta semana ya se comenzó a desarrollar trabajo de manera independiente para cada uno, es decir con los roles asignados previamente.
En este caso fue el backend de ese sprint (Francisco Reyes) y el frontend (Diego Rojas) quien implemento una capa de datos básica y un manejo de errores simple para ir iniciando. En cuanto a la Documentación (Joaquín Contreras) y el Lider (Luis Guzman) priorizaron la presentación y el readme de esta semana. También avanzamos de manera "extra"
ya que logramos implementar el mapa interactivo de la API, logrando agregar puntos de interés en este mismo, el cual serian las casas que están en venta. En esta misma agregamos varias validaciones que ya teníamos de base del manejo de errores creado anteriormente y lo reforzamos, adjunto imagen:

<img width="1899" height="947" alt="image" src="https://github.com/user-attachments/assets/e832aff5-90e0-44d5-8267-fc7d8b9336d7" />

# Detalles de avance - Semana 5 (de regreso de la semana sin entrega):
Esta semana trabajamos en nuestros nuevos roles con el cambio de Sprint, el cual fue Francisco Reyes: Lider; Diego Rojas: Backend; Joaquin Contreras: Frontend; y por ultimo Luis Guzman: Documentacion.

Principalmente definimos un metodo de trabajo en donde el backend y el frontend trabajan juntos para implementar lo solicitado, y el lider y la documentacion a su vez se encargan de revisar y detallar los avances correspondientes.

En este avance implementamos un html con un puerto local y un login con un manejo de errores sencillo pero funcional, vinculando el login de "vendedor" que una vez inicia sesion se redirige a el mapa interactivo de la API presentado en la semana 4, adjunto imagenes:

# Ventana inicial de Inicio de Sesion:
<img width="1914" height="940" alt="image" src="https://github.com/user-attachments/assets/96491d4d-1c49-4f54-99bf-b1e3d3bad801" />

# Login de Comprador:
<img width="1901" height="933" alt="image" src="https://github.com/user-attachments/assets/1a931db4-94ce-4afe-afdd-4fb357bf9c18" />

# Login de Vendedor:
<img width="1899" height="944" alt="image" src="https://github.com/user-attachments/assets/74be5401-052e-48ef-8664-05cfc8eb737e" />
Si se ingresa un usuario y contraseña existente se redijira hacia el mapa de la semana 4, permitiendo asi agregar casas con los puntos de interes y sus coordenadas.

# Login de Administrador:
<img width="1900" height="942" alt="image" src="https://github.com/user-attachments/assets/a066bec2-b0b5-4911-934d-aa711a6cb0e9" />


# Detalles de avance - Semana 6:
Bien, directamente esta semana realizamos cambios y avances muy fuertes a comparación de lo que llevábamos realizado. Primeramente hubieron cambios en el inicio de sesión y la manera de administrar los usuarios, ahora estos tienen un valor que indica si son administradores, compradores y vendedores, las cuales el backend decidio implementarlo con hasheo de Argon 2, para así tener mas seguridad y agregar dificultad para un intento de robo de datos. He aquí una foto del nuevo inicio de sesión y de la estructura de usuario:
<img width="1915" height="936" alt="image" src="https://github.com/user-attachments/assets/4f3279f0-6e34-4ee0-8214-bc306059d744" />

<img width="985" height="515" alt="image" src="https://github.com/user-attachments/assets/d28233f3-9e99-4ddd-9ea0-d819c0fc68ef" />

Mantuvimos 2 registros distintos para comprador y vendedor, el registro de administrador lo agregamos solo para cuando se necesita crear una cuenta admin, como ya hay varias listas para nuestro uso no hemos necesitado implementarlo mas.

# Administrador
Este es el panel de administrador, se ofrece botones que responden y envían a distintas secciones para poder administrarlas, de momento esta agregado el panel de vendedor que permite agregar casa al igual que una cuenta de ese tipo, y un botón que redirige a las propiedades publicadas desde un punto de vista como comprador. Adjunto imágenes:

<img width="1910" height="935" alt="image" src="https://github.com/user-attachments/assets/42c48a8f-75af-4660-aac4-4c22c91b732a" />

Y en cuanto al apartado de registro comprador/vendedor, es similar al anterior, contiene sus respectivas validaciones, como la de no repetir un correo que este vinculado a un usuario, largo de contraseña, validación de rut, etc. Adjunto imagen:

<img width="1900" height="944" alt="image" src="https://github.com/user-attachments/assets/94b3efd5-5b9a-4ea3-a0cb-1f36e39a911d" />

# Comprador
En cuanto al apartado de comprador, se muestran las casas tanto en modo mosaico, como en modo mapa. Esta vez se agregaron las imagenes, las cuales son convertidas en base64 y de momento solo se admiten archivos jpg. Adjunto imagen:
# Modo Mosaico:
<img width="1902" height="941" alt="image" src="https://github.com/user-attachments/assets/dd1bd654-2cd5-4127-97a6-0a8001298206" />

# Modo Mapa:
<img width="1897" height="944" alt="image" src="https://github.com/user-attachments/assets/ddeaea0c-e3ac-452f-8fdf-28106d3d9276" />


# Vendedor
Ahora el apartado de vendedor, este contiene funciones nuevas bien interesantes, como un boton de actualizar lista, que enseña tus propiedades publicadas, el cual a su vez contiene las funciones de editar y eliminar la propiedad que desee, esto seria el Crud implementado para mostrar el flujo de datos con las propiedades. Tambien ya no es necesario agregar coordenadas manualmente, si no que el usuario mismo puede poner un punto en el mapa para escoger la ubicacion de la propiedad. He aqui una imagen:

<img width="1915" height="945" alt="image" src="https://github.com/user-attachments/assets/0fc631c5-f3d1-4560-96a6-27419c0e37ba" />


Si presionamos el boton de agregar propiedad, se desplegara una ventana pequeña al costado donde se podran rellenar los datos, el cual de las coordenadas se va actualizando dependiendo donde coloques el punto en el mapa. Adjunto imagen:

<img width="1916" height="945" alt="image" src="https://github.com/user-attachments/assets/5b96d6b8-59f6-4b9e-8c11-fa0a1207fd1f" />

# Pantalla de error 404
Y por ultimo pero no menos importante, tenemos nuestra ventana de error 404 ya implementada
<img width="1910" height="947" alt="image" src="https://github.com/user-attachments/assets/7e801d65-0387-4d9e-8fe6-27fee69e9b87" />

Estos fueron los avances registrados esta semana, decidimos conectar todo de manera efectiva y sin errores, como por ejemplo al volver atras y que se pudiera iniciar sesion igualmente, agregar la pantalla de error 404, tambien el no poder acceder a rutas desde la url, etc. Estamos satisfechos con este avance, ya que ahora tenemos una base muy firme para poder ir concretando los detalles que faltan por implementar y mejorar.

# Detalles de avance - Semana 7:
Esta semana nos centramos principalmente en concretar bien los avances para la entrega del hito 1, los cuales fueron centrados en la zona del panel de administrador y una mejora en el CRUD, permitiendo que este no solo sea en cuanto a las propiedades, si no que tambien pueda administrar los usuarios registrados hasta el momento. Adjunto imagenes de como luce actualmente:

<img width="1344" height="643" alt="image" src="https://github.com/user-attachments/assets/a7f20c7b-ed82-4675-b7cb-37447987aa65" />

Para ambas secciones aparece un boton de editar y eliminar, claramente el de eliminar borra al usuario del archivo JSON, y el de editar despliega la siguiente ventana permitiendo los siguientes cambios:

<img width="1348" height="641" alt="image" src="https://github.com/user-attachments/assets/74e7ef59-7efa-4a4b-ba42-147a1abf34a4" />

Como se puede apreciar, inlcuso se permite una modificacion al tipo de usuario vinculado.

Ahora el enfoque para la siguiente semana sera migrar a una base de datos funcional, la cual esta en desarrollo hasta el momento.


# Detalles de avance - Semana 8:
Durante esta semana nos correspondio realizar una migracion a base de datos, la cual fue exitosa en nuestro caso. El avance debia ser un crud funcional de lo que ya teniamos perp en la base de datos seleccionada
la cual para nuestro proyecto es supabase, aunque de manera poco probable podia ocurrir un cambio. A continuacion mostrare imagenes de como luce la base de datos y como esta fue conectada al proyecto.

FUNCIONES UTILIZADAS EN CODIGO PARA LA MIGRACION:


Y asi es como luce una tabla de datos, en este caso propiedades:

<img width="1855" height="404" alt="image" src="https://github.com/user-attachments/assets/30192360-e1f7-41e1-9053-5af8300a8b9d" />

Cabe mencionar que todos los valores que llevabamos registrados en los JSON fueron correctamente migrados. Estas tablas contienen validaciones extras, las cuales estamos tratando de entender bien su funcionamiento y aporte
ya que la base de datos es en base a la conexion a internet y puede relentizarse.

<img width="650" height="874" alt="image" src="https://github.com/user-attachments/assets/3781f5fc-9cb8-48bb-a5b5-8363db123dcc" />

Este es el menu de edicion de cada tabla, si presionamos el engranaje de un valor, nos arrojara a la ventana de validaciones extra:

<img width="641" height="486" alt="image" src="https://github.com/user-attachments/assets/4b9efe62-9fc5-4a68-b27c-3abfefa61119" />

Para ir finalizando, el crud esta completamente funcional para el panel de administracion, crear publicaciones de casas y usuarios nuevos, por lo cual la migracion no presento drama alguno mas alla de tiempos de carga sobre el promedio.

