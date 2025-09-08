from flask import Flask, render_template, request, jsonify
from persistencia.manejoArchivo import leer_propiedades, guardar_propiedades, coordenadas_repetidas, siguiente_id

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/propiedades', methods=['GET'])
def get_propiedades():
    propiedades = leer_propiedades()
    return jsonify(propiedades)

@app.route('/api/propiedades', methods=['POST'])
def add_propiedad():
    data = request.json
    nombre = data.get('nombre')
    descripcion = data.get('descripcion')
    precio = data.get('precio')
    propietario = data.get('propietario')
    localizacion = data.get('localizacion')
    dormitorios = data.get('dormitorios')
    baños = data.get('baños')
    area = data.get('area')
    tipo = data.get('tipo')
    estado = data.get('estado')
    activo = data.get('activo', True)
    img = data.get('img')
    coordenadas = data.get('coordenadas')



 ## VALIDACIONES !!!!!!!
 
    try:
        precio = int(precio)
    except (ValueError, TypeError):
        return jsonify({"error": "El precio debe ser un número."}), 400
    
    try:
        dormitorios = int(dormitorios)
    except (ValueError, TypeError):
        return jsonify({"error": "Los dormitorios deben ser un número."}), 400
    
    try:
        baños = int(baños)
    except (ValueError, TypeError):
        return jsonify({"error": "Los baños deben ser un número."}), 400

    try:
        area = int(area)
    except (ValueError, TypeError):
        return jsonify({"error": "El área debe ser un número."}), 400 
    
    
    estado= estado.lower()
    if estado != "venta" and estado != "arriendo":
        return jsonify({"error": "El estado debe ser 'venta' o 'arriendo'."}), 400
    

    if coordenadas_repetidas(leer_propiedades(), coordenadas):
        return jsonify({"error": "Las coordenadas ya existen en otra propiedad."}), 400
    

    if precio is None or precio <= 0:
        return jsonify({"error": "El precio debe ser un número entero positivo o mayor a 0."}), 400
    
    if dormitorios is None or dormitorios <= 0:
        return jsonify({"error": "El número de dormitorios debe ser un entero no negativo."}), 400
    
    if baños is None or baños <= 0:
        return jsonify({"error": "El número de baños debe ser un entero no negativo."}), 400

    if area is None or area <= 0:
        return jsonify({"error": "El área debe ser un entero no negativo ni 0."}), 400

    if descripcion.strip() == "":
        descripcion = "Sin descripción"


    
    propiedades = leer_propiedades()
    nueva = {
        "id": siguiente_id(propiedades),
        "nombre": nombre,
        "descripcion": descripcion,
        "precio": precio,
        "propietario": propietario,
        "localizacion": localizacion,
        "dormitorios": dormitorios,
        "baños": baños,
        "area": area,
        "tipo": tipo,
        "estado": estado,
        "activo": activo,
        "img": img,
        "coordenadas": coordenadas
    }
    propiedades.append(nueva)
    guardar_propiedades(propiedades)
    return jsonify({"message": "Propiedad ingresada con éxito.", "propiedades": propiedades})

if __name__ == '__main__':

    app.run(debug=True)

