import requests
from math import radians, sin, cos, sqrt, atan2

# API de OpenStreetMap (Nominatim) para obtener información de ubicación
CURICO_LAT = -34.982   # Latitud central de Curicó
CURICO_LON = -71.239   # Longitud central de Curicó
RADIO_MAX_KM = 10      # Radio máximo permitido (km)

def distancia_km(lat1, lon1, lat2, lon2):
    #Calcula la distancia entre dos puntos (fórmula de Haversine).
    R = 6371.0  # Radio de la Tierra en km
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

def obtener_informacion_mapa(lat, lon):
    #Consulta la API externa y maneja validaciones y errores.
    try:
        lat = float(lat)
        lon = float(lon)
    except ValueError:
        return {"ok": False, "error": "Coordenadas inválidas: deben ser numéricas."}

    # Validar que esté dentro del radio permitido
    distancia = distancia_km(lat, lon, CURICO_LAT, CURICO_LON)
    if distancia > RADIO_MAX_KM:
        return {
            "ok": False,
            "error": f"Coordenadas fuera del radio permitido ({distancia:.2f} km de Curicó)."
        }

    try:
        url = "https://nominatim.openstreetmap.org/reverse"
        params = {"format": "json", "lat": lat, "lon": lon, "zoom": 12, "addressdetails": 1}
        headers = {"User-Agent": "ViviendaDigital"}

        # Petición a la API con control de tiempo de respuesta
        response = requests.get(url, params=params, headers=headers, timeout=5)
        response.raise_for_status()
        data = response.json()
        return {"ok": True, "data": data}

    # Manejo de errores específicos
    except requests.Timeout:
        return {"ok": False, "error": "Timeout: la API externa tardó demasiado en responder."}
    except requests.ConnectionError:
        return {"ok": False, "error": "Error de conexión al contactar a la API."}
    except requests.RequestException as e:
        return {"ok": False, "error": f"Error inesperado en la API: {str(e)}"}
