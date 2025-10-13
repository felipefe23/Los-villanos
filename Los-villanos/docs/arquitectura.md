# Arquitectura (base) — Página web de venta y alquileres de casas
## Este documento describe el diagrama por capas y el rol de cada módulo del backend. Es una base mínima para empezar y dividir el trabajo del equipo.

```
[ Cliente / Frontend ]
          │  HTTP (REST/JSON)
          ▼
     ┌─────────────┐
     │   Rutas     │  ← Define endpoints
     └─────┬───────┘
           │ 
           ▼
     ┌─────────────┐
     │ Controlador │  ← Valida solicitud
     └─────┬───────┘
           │ 
           ▼
     ┌─────────────┐
     │  Servicios  │  ← Lógica de negocio
     └─────┬───────┘
           │ 
           ▼
     ┌─────────────┐
     │    Datos    │  ← Almacenamiento de información
     └─────────────┘
```
## Explicación del diagrama por capas

El sistema se organiza en cuatro capas principales que definen cómo fluye la información en el backend:

1. **Rutas**  
   - Encargadas de definir los endpoints de la aplicación.  
   - Ejemplo: `/casas`, `/alquiler`.

2. **Controlador**  
   - Recibe la petición desde las rutas.  
   - Valida los datos básicos y redirige la solicitud hacia los servicios.

3. **Servicios**  
   - Contienen la lógica principal del negocio.  
   - Procesan la información antes de enviarla a la capa de datos.

4. **Datos**  
   - Se encargan del almacenamiento y consulta de la información (por ejemplo, en una base de datos).

---

-> El flujo es lineal: **Rutas → Controlador → Servicios → Datos → Respuesta**.  
De esta manera cada capa tiene una función clara y el sistema se mantiene ordenado.
