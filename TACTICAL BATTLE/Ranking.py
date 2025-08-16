

def cargar_ranking(archivo, ranking):
    try:
        with open(archivo, 'r') as file:
            for linea in file:
                nombre, puntuacion = linea.strip().split(':')
                ranking.insertar_puntuacion(nombre, int(puntuacion))
    except FileNotFoundError:
        # El archivo no existe, no hay nada que cargar
        pass

    return ranking

def guardar_ranking(archivo, ranking):
    with open(archivo, 'w') as file:
        actual = ranking.cabeza
        while actual is not None:
            nombre, puntuacion = actual.dato["nombre"], actual.dato["puntuacion"]
            file.write(f"{nombre}:{puntuacion}\n")
            actual = actual.next





