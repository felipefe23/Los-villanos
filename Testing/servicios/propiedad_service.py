from persistencia.base_datos import obtener_propiedades
import math

# Funcionamiento: Lee propiedades con filtrado y paginación opcional.
# Si se pasa 'pagina' y 'por_pagina': Retorna un DICT con datos de paginación.
# Si NO se pasan: Retorna una LISTA simple (para compatibilidad con el resto del sistema).
def leer_propiedades(filtros=None, pagina=None, por_pagina=None):
    propiedades = obtener_propiedades()
    
    # Filtrado 
    filtradas = []
    
    # Si no hay filtros y no hay paginación, retorno rápido
    if not filtros and not pagina:
        return propiedades

    q = (filtros.get('q') or '').strip().lower() if filtros else ''
    tipo = (filtros.get('tipo') or '').strip().lower() if filtros else ''
    estado = (filtros.get('estado') or '').strip().lower() if filtros else ''
    
    min_precio = 0
    max_precio = 0
    if filtros:
        try: min_precio = int(filtros.get('min_precio') or 0)
        except ValueError: min_precio = 0
        try: max_precio = int(filtros.get('max_precio') or 0)
        except ValueError: max_precio = 0

    for p in propiedades:
        # Filtro Texto
        if q:
            texto = f"{p.get('nombre','')} {p.get('localizacion','')} {p.get('descripcion','')}".lower()
            if q not in texto: continue
        # Filtro Tipo
        if tipo and str(p.get('tipo', '')).lower() != tipo: continue
        # Filtro Estado
        if estado and str(p.get('estado', '')).lower() != estado: continue
        # Filtro Precio
        precio = int(p.get('precio') or 0)
        if min_precio > 0 and precio < min_precio: continue
        if max_precio > 0 and precio > max_precio: continue
        
        filtradas.append(p)

    # Paginación (Solo si se solicita explícitamente)
    if pagina is not None and por_pagina is not None:
        total_propiedades = len(filtradas)
        total_paginas = math.ceil(total_propiedades / por_pagina)
        
        if pagina < 1: pagina = 1
        if pagina > total_paginas and total_paginas > 0: pagina = total_paginas
        
        inicio = (pagina - 1) * por_pagina
        fin = inicio + por_pagina
        
        return {
            "propiedades": filtradas[inicio:fin],
            "total": total_propiedades,
            "paginas": total_paginas,
            "actual": pagina
        }
    
    # Retorno Clásico (Para Admin y Validaciones)
    return filtradas

# Funcionamiento: Función interna de ayuda (helper).
# Verifica si un rol de usuario (ej. 'admin') es considerado administrador, manejando mayúsculas o valores nulos (None).
def _es_admin(role):
    return (role or '').lower() in {'admin', 'administrador'}


# Funcionamiento: Función interna de ayuda (helper).
# Convierte un valor (string, bool) a un booleano estricto.
# Acepta "si", "true", "1" (para True) y "no", "false", "0" (para False). Falla (ValueError) si no es reconocible.
def _normalizar_bool(valor, campo):
    if isinstance(valor, bool):
        return valor
    if isinstance(valor, str):
        valor_normalizado = valor.strip().lower()
        if valor_normalizado in {'true', '1', 'si', 'sí', 'on'}:
            return True
        if valor_normalizado in {'false', '0', 'no', 'off'}:
            return False
    raise ValueError(f"El campo '{campo}' debe ser booleano.")


# Funcionamiento: El motor de validación para propiedades.
# Recibe datos (data) y un flag 'parcial' (para PATCH/PUT).
# 1. Valida campos obligatorios (texto y numéricos).
# 2. Normaliza valores (ej. '  Nombre ' -> 'Nombre').
# 3. Valida reglas de negocio (ej. 'precio' > 0).
# 4. Asegura que 'coordenadas' sean únicas en la BD.
# 5. Falla (ValueError) si algún campo es inválido.
# 6. Retorna un diccionario 'resultado' con datos limpios.
# 7. el "parcial=True" permite a la funcion determinar solo los campos que consideras en el diccionario.
def _validar_y_normalizar_propiedad(data, parcial, propiedades_existentes, propiedad_actual=None):
    if not isinstance(data, dict):
        raise ValueError("Formato de datos inválido para la propiedad.")

    resultado = {}
    campos_texto_obligatorios = ['nombre', 'localizacion', 'tipo']
    campos_numericos = ['precio', 'dormitorios', 'baños', 'area']
    campos_permitidos = {
        'nombre', 'descripcion', 'precio', 'localizacion', 'dormitorios', 'baños',
        'area', 'tipo', 'estado', 'activo', 'img', 'coordenadas', 'propietario'
    }

    for campo in campos_texto_obligatorios:
        if campo not in data:
            if parcial:
                continue
            raise ValueError(f"El campo '{campo}' es obligatorio.")
        valor = data.get(campo)
        if valor is None:
            raise ValueError(f"El campo '{campo}' no puede estar vacío.")
        valor = str(valor).strip()
        if not valor:
            raise ValueError(f"El campo '{campo}' no puede estar vacío.")
        resultado[campo] = valor

    for campo in campos_numericos:
        if campo not in data:
            if parcial:
                continue
            raise ValueError(f"El campo '{campo}' es obligatorio.")
        valor = data.get(campo)
        if isinstance(valor, str):
            valor = valor.strip()
        if valor in (None, ''):
            raise ValueError({
                'precio': "El precio debe ser un número.",
                'dormitorios': "Los dormitorios deben ser un número.",
                'baños': "Los baños deben ser un número.",
                'area': "El área debe ser un número."
            }[campo])
        try:
            valor_entero = int(valor)
        except (TypeError, ValueError):
            raise ValueError({
                'precio': "El precio debe ser un número.",
                'dormitorios': "Los dormitorios deben ser un número.",
                'baños': "Los baños deben ser un número.",
                'area': "El área debe ser un número."
            }[campo])
        if valor_entero <= 0:
            raise ValueError({
                'precio': "El precio debe ser un número entero positivo o mayor a 0.",
                'dormitorios': "El número de dormitorios debe ser un entero no negativo.",
                'baños': "El número de baños debe ser un entero no negativo.",
                'area': "El área debe ser un entero no negativo ni 0."
            }[campo])
        resultado[campo] = valor_entero

    if 'descripcion' in data:
        descripcion = data.get('descripcion')
        if descripcion is None or (isinstance(descripcion, str) and not descripcion.strip()):
            resultado['descripcion'] = "Sin descripción"
        else:
            resultado['descripcion'] = str(descripcion).strip()
    elif not parcial:
        resultado['descripcion'] = "Sin descripción"

    if 'estado' in data:
        estado = data.get('estado')
        if estado is None:
            raise ValueError("El estado debe ser 'venta' o 'arriendo'.")
        estado_normalizado = str(estado).strip().lower()
        if estado_normalizado not in {'venta', 'arriendo'}:
            raise ValueError("El estado debe ser 'venta' o 'arriendo'.")
        resultado['estado'] = estado_normalizado
    elif not parcial:
        raise ValueError("El campo 'estado' es obligatorio.")

    if 'coordenadas' in data:
        coordenadas = data.get('coordenadas')
        if coordenadas is None:
            raise ValueError("Las coordenadas no pueden estar vacías.")
        coordenadas_normalizadas = str(coordenadas).strip()
        if not coordenadas_normalizadas:
            raise ValueError("Las coordenadas no pueden estar vacías.")
        propiedad_id_actual = propiedad_actual.get('id') if propiedad_actual else None
        for propiedad in propiedades_existentes:
            if propiedad.get('coordenadas') == coordenadas_normalizadas and propiedad.get('id') != propiedad_id_actual:
                raise ValueError("Las coordenadas ya existen en otra propiedad.")
        resultado['coordenadas'] = coordenadas_normalizadas
    elif not parcial:
        raise ValueError("El campo 'coordenadas' es obligatorio.")

    if 'activo' in data:
        resultado['activo'] = _normalizar_bool(data.get('activo'), 'activo')
    elif not parcial:
        resultado['activo'] = True

    if 'img' in data:
        img = data.get('img')
        if img is None:
            resultado['img'] = None
        else:
            resultado['img'] = str(img)
    elif not parcial:
        resultado['img'] = None

    campos_extra = set(data.keys()) - campos_permitidos - {'id', 'propietario'}
    if campos_extra:
        raise ValueError(f"Campos no permitidos: {', '.join(sorted(campos_extra))}.")

    return resultado