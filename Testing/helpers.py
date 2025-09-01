# test base de persistencia

from persistencia.manejoArchivo import leer_propiedades, guardar_propiedades

def mostrar_propiedades():
    propiedades = leer_propiedades()
    if not propiedades:
        print("No hay propiedades registradas.")
    else:
        print("\nListado de propiedades:")
        for p in propiedades:
            print(f"ID: {p['id']} | Dirección: {p['direccion']} | Precio: ${p['precio']}")

def agregar_propiedad():
    direccion = input("Ingrese la dirección en coordenada de la propiedad (Ejemplo: -34.96241,-71.22117): ")
    precio = input("Ingrese el precio: ")

    try:
        precio = int(precio)
    except ValueError:
        print("El precio debe ser un número.")
        return

    propiedades = leer_propiedades()
    nueva = {
        "id": len(propiedades) + 1,
        "direccion": direccion,
        "precio": precio
    }
    propiedades.append(nueva)
    guardar_propiedades(propiedades)
    print("Propiedad agregada con éxito.")

def menu():
    while True:
        print("\n--- Menú de prueba de persistencia ---")
        print("1. Mostrar propiedades")
        print("2. Agregar nueva propiedad")
        print("3. Salir")
        opcion = input("Seleccione una opción: ")

        if opcion == '1':
            mostrar_propiedades()
        elif opcion == '2':
            agregar_propiedad()
        elif opcion == '3':
            print("Cerrando prueba.")
            break
        else:
            print("Opción inválida. Intente nuevamente.")

if __name__ == '__main__':
    menu()