from flask import Blueprint, jsonify, request
from servicios.map_service import obtener_informacion_mapa  # Función que consulta la API externa

# Blueprint que agrupa las rutas relacionadas con el mapa
map_bp = Blueprint("map_bp", __name__)
#Ruta que recibe coordenadas y devuelve información desde la API de mapas.
@map_bp.route("/api/mapdata", methods=["GET"])
def get_map_data():
    # Si no se envían coordenadas, usa por defecto las de Curicó
    lat = request.args.get("lat", "-34.982")
    lon = request.args.get("lon", "-71.239")

    # Llama al servicio que obtiene los datos desde OpenStreetMap
    resultado = obtener_informacion_mapa(lat, lon)

    # Devuelve la respuesta en formato JSON al cliente
    return jsonify(resultado)
