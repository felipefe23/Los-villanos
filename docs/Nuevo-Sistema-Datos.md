# Breve explicacón de los cambios en el .json

**NUEVO SISTEMA DE DATOS** En este nuevo sistema de datos implementamos un formato más completo, anteriormente contabamos con un formato básico que consistia en `ID`, `DIRECCIÓN` y `PRECIO`. El cual era my básico para la información que necesitamos dar, en esta nueva adaptación agregamos y actualizamos los datos, quedando de la siguiente manera.
`ID` -- `NOMBRE` -- `PRECIO` -- `LOCALIZACIÓN` -- `DORMITORIOS` -- `BAÑOS` -- `AREA` -- `TIPO` -- `ESTADO` -- `IMG` -- `COORDENADAS`.
Dandonos asi una vista más especifica de los datos relacionados a las casas que proponemos promocionar en nuestra página.

## Cambios en el INDEX.HTML
- **Integración de campos de TEXT Y NUMBER** Al tener más datos que registrar, es obvio que necesita más campos para poder que el usuario pueda ingresar la información requerida.
- **Actualización de datos** Al tener nuevos datos que registrar por casas, nos vimos en la obligación de eliminar la base de datos antigua para dar paso a la nueva con datos más actuales y con mayor información, los cuales estaban integrados en el `index.html` desde cuando creamos el primer TEST de la Aplicación web.
- **Actualización de TODAS las funciones** Al tener los siguientes cambios tuvimos que actualizar TODAS las funciones del programa.
 
## Corrección de ERRORES de versiones pasadas
- **Error: No se encuentra el doc. `propiedades.json`** El error se debia a que la ruta del archivo en algunos ordenadores la encontraba sin importar la especificación de la ruta del mismo, en esta corrección "Forzamos" al programa a buscarlo dentro de la ruta específica.
Detección del error: Implementamos una linea de codigo que si no encontraba el doc. lo creara, al momento de que el programa creó el doc. nos dimos cuenta de que lo estaba creando fuera de la ruta establecida para los `DATOS` asi nos dimos cuenta de que claro, no la encontraba por que en la ruta en la que lo estaba buscando, nunca existió.

## Validaciones hasta el momento.
- **Todos los campos rellenados** Valida que todos los campos requeridos para la creación de la propiedad estes completos al momento de realizar la solicitud.
- **Realizados en semana 4** VALIDACIÓN DE PRECIO <= 0, VALIDACIÓN DE COORDENADAS IGUALES A OTRAS, VALIDACIÓN DE TIPO DENTRO DE PARAMETROS (CASA/DEPARTAMENTO/CASA DE VERANO/CASA DE ESTUDIANTES/HABITACIÓN DE ESTUDIANTES/RECREACIONAL, ETC), VALIDACIÓN DE ESTADO DENTRO DE LOS PARAMETROS (ACTIVA = True / False) Solo para la vista de los usuarios Admins.
 
**DiCloud**
