from flask import Flask, render_template, request, jsonify
from persistencia.manejoArchivo import leer_propiedades, guardar_propiedades

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
    precio = data.get('precio')
    localizacion = data.get('localizacion')
    dormitorios = data.get('dormitorios')
    baños = data.get('baños')
    area = data.get('area')
    tipo = data.get('tipo')
    estado = data.get('estado')
    img = data.get('img')
    coordenadas = data.get('coordenadas')


    try:
        precio = int(precio)
    except (ValueError, TypeError):
        return jsonify({"error": "El precio debe ser un número."}), 400

    try:
        precio!=0
    except (ValueError, TypeError):
        return jsonify({"error": "El precio debe ser un número superior a 0."}), 400
    
    propiedades = leer_propiedades()
    nueva = {
        "id": len(propiedades) + 1,
        "nombre": nombre,
        "precio": precio,
        "localizacion": localizacion,
        "dormitorios": dormitorios,
        "baños": baños,
        "area": area,
        "tipo": tipo,
        "estado": estado,
        "img": img,
        "coordenadas": coordenadas
    }
    propiedades.append(nueva)
    guardar_propiedades(propiedades)
    return jsonify({"message": "Propiedad ingresada con éxito.", "propiedades": propiedades})

if __name__ == '__main__':

    app.run(debug=True)
