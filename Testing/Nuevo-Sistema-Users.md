# Explicación de como funciona el nuevo sistema de Login/Register de usuarios.

**Registro** 
- En el nuevo apartado de Registro de usuarios, integré 2 campos básicos, los cuales se conforman por 1 campo para el `EMAIL` y  `CONTRASEÑA`.
- Los cuales cuentan con validaciones sobre el contenido de estos, en el tema del correo, cuenta con validaciones para seguir un formato estandar de correos, el cual es "xx@xxx.xx". El minimo de 2 caracteres antes del `@`, contenido a elección despues de este y lo mismo despues del `.`, como por ejemplo: `.com`, `.cl`, etc.
- Las validaciones en el termino de `CONTRASEÑA` son, un minimo de 8 caracteres y 1 digito.

**Login** 
- En el nuevo sistema de Login integré los mismos 2 campos básicos `EMAIL` y  `CONTRASEÑA`.
- Los cuales cuentan con sus validaciones de Usuario y/o contraseña incorrectos.

**Hash de contraseñas en Argos2**
- El hash se decidio por ser el mejor hash de la Password Hashing Competition en el año 2015, es resistente a ataques de `Fuerza bruta` y esta optimizado para Hardware moderno.
- Tambien crea Hashes en mi parecer largos y Únicos, que es uno de sus puntos Fuertes. 

**DiCloud**
-- `COORDENADAS`.