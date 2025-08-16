from utils import *

class Personaje:
    def __init__(self, equipo):
        self.nombre = ""
        self.vida_maxima = 99
        self.vida_actual = 0
        self.danyo = 0
        self.posicion = ""
        self.enfriamiento = 1
        self.enfriamiento_restante = 0
        self.equipo = equipo

    def mover(self):
        celda_valida = False
        while not celda_valida:
            celda = input('Indica la celda a la que mover al {} (Posición actual: {})\n'.format(self.nombre, self.posicion))
            celda = celda.upper()
            celda_valida = validar_celda(celda, 'D', '4')
            if not celda_valida:
                print('Ups... valor de celda incorrecto. ')
            else:
                disponible = comprobar_celda_disponible(celda, self.equipo)
                if disponible:
                    es_contigua = validar_celda_contigua(celda, self.posicion)
                    if not es_contigua:
                        celda_valida = False
                        print('Ups... la celda {} no es contigua a la posicion actual {}'.format(celda, self.posicion))
                        continue
                    self.posicion = celda
                else:
                    celda_valida = False
                    print('Ups... la celda ya está ocupada!')
                    continue
        return None

    def habilidad(self):
        raise NotImplemented("habilidad() no implementada")

    def habilidad_disponible(self):
        return self.enfriamiento_restante == 0

    def desc_habilidad(self):
        raise NotImplemented("desc_habilidad() no implementada")


class Medico(Personaje):
    def __init__(self, equipo):
        super().__init__(equipo)
        self.nombre = "Medico"
        self.vida_maxima = 1
        self.vida_actual = 1
        self.danyo = 0

    def get_personajes_curables(self):
        personajes_curables = dict()
        contador_acciones = 1

        for per in self.equipo:
            if per.vida_actual < per.vida_maxima:
                personajes_curables[str(contador_acciones)] = per
                contador_acciones += 1
        return personajes_curables

    def habilidad_disponible(self):
        return self.enfriamiento_restante == 0 and len(self.get_personajes_curables())>0

    def habilidad(self):
        personajes_curables = self.get_personajes_curables()
        for num, per in personajes_curables.items():
            print("{}: {} [{}/{}]".format(num, per.nombre, per.vida_actual, per.vida_maxima))

        while True:
            # Elegir personaje
            personaje = input('Selecciona el personaje a curar: ')
            if personaje not in personajes_curables:
                print('ERROR: selección inválida. ')
                continue

            personajes_curables[personaje].vida_actual = personajes_curables[personaje].vida_maxima

            for per in self.equipo:
                per.enfriamiento_restante = 0
            self.enfriamiento_restante = self.enfriamiento
            return None  # Devolvemos el código de acción

    def desc_habilidad(self):
        return 'Curar a un compañero'


class Artillero(Personaje):
    def __init__(self, equipo):
        super().__init__(equipo)
        self.nombre = "Artillero"
        self.vida_maxima = 2
        self.vida_actual = 2
        self.danyo = 1

    def habilidad(self):
        while True:
            celda = input('Indica las coordenadas de la esquina superior izquierda en la que disparar (área 2x2): ')
            celda = celda.upper()
            celda_valida = validar_celda(celda, 'D', '4')
            if not celda_valida:
                print('Ups... valor de celda incorrecto. ')
                continue

            for per in self.equipo:
                per.enfriamiento_restante = 0
            self.enfriamiento_restante = self.enfriamiento
            return 'A'+ celda

    def desc_habilidad(self):
        return 'Disparar en área (2x2). Daño 1.'


class Francotirador(Personaje):
    def __init__(self, equipo):
        super().__init__(equipo)
        self.nombre = "Francotirador"
        self.vida_maxima = 3
        self.vida_actual = 3
        self.danyo = 3

    def habilidad(self):
        while True:
            celda = input('Indica las coordenadas de la celda a la que disparar: ')
            celda = celda.upper()
            celda_valida = validar_celda(celda, 'D', '4')
            if not celda_valida:
                print('Ups... valor de celda incorrecto. ')
                continue

            for per in self.equipo:
                per.enfriamiento_restante = 0
            self.enfriamiento_restante = self.enfriamiento
            return 'F'+ celda

    def desc_habilidad(self):
        return 'Disparar a una celda. Daño 3.'


class Inteligencia(Personaje):
    def __init__(self, equipo):
        super().__init__(equipo)
        self.nombre = "Inteligencia"
        self.vida_maxima = 2
        self.vida_actual = 2
        self.danyo = 0

    def habilidad(self):
        while True:
            celda = input('Indica las coordenadas de la esquina superior izquierda de la zona de observación (área 2x2): ')
            celda = celda.upper()
            celda_valida = validar_celda(celda, 'D', '4')
            if not celda_valida:
                print('Ups... valor de celda incorrecto. ')
                continue

            for per in self.equipo:
                per.enfriamiento_restante = 0
            self.enfriamiento_restante = self.enfriamiento
            return 'I'+ celda

    def desc_habilidad(self):
        return 'Reverlar a los enemigos en un área 2x2.'
