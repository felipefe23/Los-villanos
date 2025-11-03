# Funcionamiento: El punto de entrada para servidores WSGI (producción).
# Cuando subes tu app a un hosting (como Vercel o Heroku), el servidor busca este archivo para encontrar la 'app' de Flask.
# El 'if __name__ == "__main__":' se usa solo si ejecutas este archivo directamente (ej. 'python wsgi.py'), iniciando el servidor en modo debug.

from app import app

if __name__ == "__main__":
    app.run(debug=False) # "debug=True" permite que cualquier cambio en el codigo, el servidor se reinicie solo para aplicar los cambios