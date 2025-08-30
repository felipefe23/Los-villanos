# Arquitectura (base) — Página web de venta y alquileres de casas
## Este documento describe el diagrama por capas y el rol de cada módulo del backend. Es una base mínima para empezar y dividir el trabajo del equipo.

```plaintext
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
