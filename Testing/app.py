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
    direccion = data.get('direccion')
    precio = data.get('precio')

    try:
        precio = int(precio)
    except (ValueError, TypeError):
        return jsonify({"error": "El precio debe ser un número."}), 400

    propiedades = leer_propiedades()
    nueva = {
        "id": len(propiedades) + 1,
        "direccion": direccion,
        "precio": precio
    }
    propiedades.append(nueva)
    guardar_propiedades(propiedades)
    return jsonify({"message": "Propiedad ingresada con éxito.", "propiedades": propiedades})

if __name__ == '__main__':
    app.run(debug=True)