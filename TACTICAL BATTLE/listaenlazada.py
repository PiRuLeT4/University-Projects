class Nodo:
    def __init__(self, dato, next=None, anterior=None):
        self.dato = dato
        self.next = next
        self.anterior = anterior


class ListaSimple:
    def __init__(self):
        self.cabeza = None
        self.size = 0


    def insertar_puntuacion(self, nombre, puntuacion):
        nuevo = Nodo({"nombre": nombre, "puntuacion": puntuacion})
        nuevo.next = self.cabeza
        if self.cabeza:
            self.cabeza.anterior = nuevo
        self.cabeza = nuevo
        self.size += 1

    def obtener_ranking_string(self):
        ranking_str = ""
        actual = self.cabeza

        while actual is not None:
            ranking_str += f"{actual.dato['nombre']}:{actual.dato['puntuacion']}\n"
            actual = actual.next

        return ranking_str


    def eliminar_valor(self, dato):
        # Uso actual para ir moviéndome entre nodos
        actual = self.cabeza
        # Uso anterior para gaurdar el nodo previo y actualizar el .next
        anterior = None
        posicion = 0  # Para saber en que elemento estoy posicionado

        # Recorro hasta el final o hasta que encuentro el dato
        while actual is not None and actual.dato != dato:
            anterior = actual  # En la siguiente iter, anterior será el nodo actual
            actual = actual.next  # En la siguiente iter, actual es el siguiente
            posicion += 1  # Actualizo posicion

        if actual is None:  # Lista vacia o no encontrado
            return False
        elif posicion == 0:  # Encontrado en la posicion 0
            self.cabeza = self.cabeza.next
        else:  # Encontrado en cualquier otra posicion
            anterior.next = actual.next

        self.size -= 1  # Disminuyo el tamaño
        return True


        return actual.dato


# Si no ponemos esto, lo que va debajo (el main) se ejecutaría también al importar la clase ListaSimple desde otro archivo
if __name__ == '__main__':
    pass