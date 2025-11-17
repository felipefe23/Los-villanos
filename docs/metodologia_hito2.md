# Metodología Aplicada hasta el Hito N°2

La metodología utilizada en las primeras fases del proyecto se distinguió por ser colaborativa, iterativa y enfocada en la organización modular del código. Para garantizar un desarrollo organizado y escalable, se fusionaron prácticas vinculadas a los modelos ágiles con una arquitectura basada en capas y un sistema de trabajo que posibilitó la incorporación gradual de funcionalidades. A continuación, se presenta una descripción detallada de las prácticas metodológicas implementadas.

---

## 1. Organización del Trabajo en Equipo

Desde el comienzo del proyecto se estableció una estructura de trabajo colaborativa que permitió distribuir responsabilidades y mantener un avance constante. Para ello, se realizó:

- **Asignación de roles:** cada integrante asumió un rol concreto (backend, frontend, documentación, QA, líder de integración), lo que facilitó la especialización y la coordinación.
- **Uso de Trello como tablero Kanban:** la planificación y el seguimiento de tareas se realizaron mediante listas de “To do”, “In progress” y “Done”. Esto permitió visualizar el estado del proyecto, registrar avances y mantener una comunicación clara.
- **División del proyecto en hitos:** el desarrollo fue organizado por etapas, permitiendo establecer prioridades y objetivos específicos para cada una. 

### 2.1. Arquitectura en Capas
Con el fin de mantener un proyecto escalable, legible y fácil de mantener, se siguió una arquitectura organizada en distintas capas:

- **Rutas:** ubicadas en `app.py`, actúan como puntos de entrada para procesar las solicitudes HTTP.
- **Controladores:** módulos encargados de dirigir las operaciones relacionadas a cada entidad (usuarios, propiedades, autenticación, vistas).
- **Servicios:** capa donde reside la lógica de negocio, aislando las reglas internas de la aplicación.
- **Capa de persistencia:** encargada de interactuar exclusivamente con Supabase, permitiendo la separación entre la lógica del sistema y el acceso a la base de datos.

Este enfoque permitió una mayor claridad y facilitó la identificación de errores y el trabajo simultáneo entre integrantes.

### 2.2. Enfoque Iterativo
El desarrollo se realizó en ciclos cortos y sucesivos en los que se desarrollaba, probaba y ajustaba cada funcionalidad. Durante el Hito 2, se priorizó:

- La construcción del **CRUD de usuarios**.
- La integración inicial con la base de datos **Supabase**.
- La carga y lectura preliminar de propiedades desde la base.
- Las validaciones mínimas ofrecidas por Supabase, dejando pendiente la implementación de validaciones internas en el código.

Este enfoque permitió avanzar de forma progresiva, identificando rápidamente errores y oportunidades de mejora.

---

## 3. Pruebas y Validación

Durante el Hito 2 se realizaron pruebas manuales y verificaciones básicas sobre cada funcionalidad implementada:

- **Pruebas en Postman y navegador** para validar rutas, autenticación y operaciones del CRUD.
- **Revisión de bases de datos en Supabase** para verificar registros, inserciones y consultas.
- **Detección de errores recurrentes**, entre los que destacaron:
  - Validaciones insuficientes en el backend.
  - Incompletitud del CRUD de administrador.
  - Falta de manejo de errores en algunos endpoints.

Estas observaciones fueron incorporadas como tareas prioritarias para el siguiente hito.

---

## 4. Documentación y Registro del Proceso

El equipo mantuvo una documentación continua del proceso a través de:

- **Trello**, donde se registraron avances, fechas, requisitos y tareas pendientes.
- **Comentarios en el código**, explicando funciones clave y decisiones técnicas.
- **Bitácoras de tareas**, utilizadas para justificar el avance en la entrega del Hito 2.

Esta documentación permitió comprender la evolución del proyecto y dejó un registro claro del trabajo realizado.

---

# Conclusión General

Hasta el Hito N°2, la metodología aplicada combinó organización colaborativa, desarrollo estructurado en capas, integración progresiva de funcionalidades y pruebas continuas. Este enfoque permitió construir una base sólida sobre la cual se desarrollarán las validaciones internas, optimizaciones de rendimiento, mejoras de seguridad y el avance del CRUD de propiedades y demás módulos en el hito siguiente.
