import random
import socket
import pickle
import sys
import threading
from cola import Cola
import time
from listaenlazada import ListaSimple
from Ranking import cargar_ranking, guardar_ranking



puerto = int(sys.argv[1])
num_partidas = int(sys.argv[2])
fichero = sys.argv[3]

lock_lobby = threading.Lock()
lock_partidas = threading.Lock()
lock_cola = threading.Lock()
usuarios_lobby = []
partidas = []

cola_espera = Cola()

ranking = ListaSimple() #va a ser la lista doblemente enlazada

cargar_ranking(fichero, ranking)


class Partida:
    def __init__(self, j1, j2):
        self.j1 = j1
        self.j2 = j2


class Cliente:
    def __init__(self, nombre, skt):
        self.nombre = nombre
        self.socket = skt
        self.posicion_cola = None


def bienvenida_usuario(clt_socket):
    global lock_partidas
    global lock_cola
    # Elegir nombre de usuario
    nombre = clt_socket.recv(1024)
    if not nombre:
        clt_socket.close()
        print("El cliente ha cancelado la conexión antes de elegir nombre")
        return
    nombre_decoded = nombre.decode()
    cliente = Cliente(nombre_decoded, clt_socket)

    lock_cola.acquire()
    if len(partidas) < num_partidas:

        if cola_espera.size != 0:
            j1 = cola_espera.desencolar()
            j2 = cliente
            lock_cola.release()

            lock_partidas.acquire()
            juego = Partida(j1, j2)
            partidas.append(juego)
            print(len(partidas))
            lock_partidas.release()

            threading.Thread(target=jugar_partida, args=(juego,)).start()

        else:
            cola_espera.encolar(cliente)
            cliente.posicion_cola = cola_espera.size
            lock_cola.release()

    else:


        cola_espera.encolar(cliente)

        lock_cola.release()

        while True:
            lock_cola.acquire()

            # Comprobar si hay al menos dos jugadores en la cola de espera y hay partidas disponibles
            if cola_espera.size >= 2 and len(partidas) < num_partidas:
                # Desencolar dos jugadores para formar una partida
                j1 = cola_espera.desencolar()
                j2 = cola_espera.desencolar()

                lock_cola.release()

                lock_partidas.acquire()
                juego = Partida(j1, j2)
                partidas.append(juego)
                lock_partidas.release()

                threading.Thread(target=jugar_partida, args=(juego,)).start()

                break  # Salir del bucle de espera en el lobby

            lock_cola.release()

            # Duermo para evitar un bucle continuo intensivo en recursos
            time.sleep(1)




def jugar_partida(partida):
    print(f"Partida comenzada entre {partida.j1.nombre} y {partida.j2.nombre}")

    jugadores = [partida.j1, partida.j2]  # Facilitar turnos de jugadores

    # Les damos a conocer
    jugadores[0].socket.sendall(jugadores[1].nombre.encode())
    jugadores[1].socket.sendall(jugadores[0].nombre.encode())

    # Tirar moneda para ver quien empieza
    jugador_activo = random.randint(0, 1)
    empieza_j1 = jugador_activo == 0

    # Les indico quien empieza
    jugadores[0].socket.sendall(pickle.dumps(empieza_j1))
    jugadores[1].socket.sendall(pickle.dumps(not empieza_j1))

    # Espero a que tengan los tableros preparados. TODO Comprobar mensaje?
    jugadores[0].socket.recv(1024)
    jugadores[1].socket.recv(1024)

    # Bucle de turnos
    turno = 1
    while True:
        print("Ronda", turno, ". Ataca:", jugadores[jugador_activo].nombre, "Defiende:", jugadores[jugador_activo-1].nombre)
        # Recibir acción del jugador activo
        codigo = jugadores[jugador_activo].socket.recv(1024)

        # Enviar acción al jugador que espera
        print("Contactando con el oponente para recibir resultado")
        jugadores[jugador_activo-1].socket.sendall(codigo)

        # Recibir resultado del jugador atacado
        resultado = jugadores[jugador_activo-1].socket.recv(1024)
        resultado_decodificado = pickle.loads(resultado)
        print("Resultado recibido:", resultado_decodificado)

        # Enviar resultado de la acción al jugador que atacó
        print("Enviando resultado al atacante")
        jugadores[jugador_activo].socket.sendall(resultado)

        if resultado_decodificado is not None and resultado_decodificado["victoria"]:
            print("Partida terminada. Ha ganado:", jugadores[jugador_activo].nombre)

            estado_equipo = jugadores[jugador_activo].socket.recv(1024) #Recibo estado del equipo ganador
            estado_equipo_enemigo = jugadores[jugador_activo-1].socket.recv(1024) #Recibo estado del equipo perdedor
            estado_equipo_decodificado = pickle.loads(estado_equipo)
            estado_equipo_enemigo_decodificado = pickle.loads(estado_equipo_enemigo)

            num_turnos = turno // 2
            punt_turnos_ganador = max(0, (20 - num_turnos)) * 20
            punt_turnos_perdedor = 0 if num_turnos < 10 else (num_turnos - 10) * 20

            punt_equipo_ganador = sum(100 for per in estado_equipo_decodificado)
            punt_equipo_perdedor = sum(100 for per in estado_equipo_enemigo_decodificado)

            if num_turnos > 25:
                punt_ganador = 1000
                punt_perdedor = 900

            elif num_turnos <= 25:
                punt_ganador = 1000 + punt_turnos_ganador + punt_equipo_ganador
                punt_perdedor = punt_turnos_perdedor + punt_equipo_perdedor

            ranking.insertar_puntuacion(jugadores[jugador_activo].nombre, punt_ganador)
            ranking.insertar_puntuacion(jugadores[jugador_activo-1].nombre, punt_perdedor)


            guardar_ranking(fichero, ranking)

            ranking_str = ranking.obtener_ranking_string()

            jugadores[jugador_activo].socket.sendall(ranking_str.encode())
            jugadores[jugador_activo-1].socket.sendall(ranking_str.encode())



            lock_partidas.acquire()

            try:
                partidas.remove(partida)
            except ValueError:
                pass
            lock_partidas.release()


            break

        # Actualizar el índice del jugador activo
        jugador_activo = (jugador_activo+1) % 2

        turno += 1


print("Arrancando servidor...")
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((socket.gethostname(), puerto))
server_socket.listen()

# Imprimir IP del servidor
nombre_server = socket.gethostname()
print(socket.gethostbyname(nombre_server))

try:
    while True:
        client_socket, addr = server_socket.accept()
        if client_socket:
            print("Cliente conectado: ", addr)
            threading.Thread(target=bienvenida_usuario, args=(client_socket,)).start()
except KeyboardInterrupt:
    print("Apagado solicitado")

server_socket.close()
print("Apagando servidor...")