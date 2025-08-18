import argparse
import asyncio
import json
from aiortc import (
    RTCPeerConnection,
    RTCSessionDescription,
)
from aiortc.contrib.media import MediaBlackhole, MediaPlayer
import formatoMensaje


cliente = ""
offer_recibido = ""
answer_enviado = ""
bye_recibido = ""
remote_addr = ""
informacion_ficheros = {
    "video_1.mp4": {"Titulo": "Aguila cazando",
                    "Descripcion": "En el video podras observar un aguila cazando una cabra, lo cual resulta increible "
                                   "el como una ave considerablemente mas pequeña que su presa es capaz de cazarla."
                    },
    "video_2.mp4": {"Titulo": "GO PRO SKY DIVING",
                    "Descripcion": "De los deportes mas arriesgados que existen, veras como unos profesionales "
                                   "se lanzan desde un avion en Dubai y hacen piruetas sin despeinarse."
                    },
    "video_3.mp4": {"Titulo": "Tortuga hambrienta",
                    "Descripcion": "Un biologo marino grabo estas imagenes de una tortuga verde disfrutando "
                                   "de una comida un tanto 'urticante': una medusa."
                    },
    "video_4.mp4": {"Titulo": "Volcan en activo",
                    "Descripcion": "Un volcan en erupcion se ilumina cuando un rayo impacta su columna de ceniza,"
                                   "creando un espectaculo impresionante de fuego y electricidad."
                    },
    "video_5.mp4": {"Titulo": "Meteorito",
                    "Descripcion": "Un meteorito surco el cielo de Espania, dejando una estela brillante"
                                   "por varias regiones. El fenomeno fue un espectaculo celestial."
                    },
}


async def run(pc, player, recorder, role, args):
    formatoMensaje.log_message("Comienzo")

    def add_tracks():
        if player and player.audio:
            pc.addTrack(player.audio)

        if player and player.video:
            pc.addTrack(player.video)
        else:
            print("No video source available.")

    @pc.on("track")  # Se activa cuando hace la conexion, Solo se hace en el servidor.
    def on_track(track):
        print("Receiving %s" % track.kind)
        recorder.addTrack(track)

    global cliente
    if role == "offer":
        # send offer
        add_tracks()
        await pc.setLocalDescription(await pc.createOffer())
        # await signaling.send(pc.localDescription)

    # consume signaling
    if cliente == "":
        loop = asyncio.get_running_loop()

        diccionario_mensaje = {args.video_file: informacion_ficheros[args.video_file]}
        message = "REGISTER STREAMER-" + json.dumps(diccionario_mensaje)
        on_con_lost = loop.create_future()
        cliente = EchoClientProtocol(message, on_con_lost)
        global remote_addr
        remote_addr = (args.signal_ip, args.signal_port)
        await loop.create_datagram_endpoint(lambda: cliente, remote_addr=(remote_addr))

    while True:

        await wait_offer_recibido()
        offer = json.loads(offer_recibido)
        sdp = offer["sdp"]
        obj = RTCSessionDescription(sdp=sdp, type="offer")
        print("oferta recibida")
        print(obj.sdp)

        if isinstance(obj, RTCSessionDescription):
            await pc.setRemoteDescription(obj)
            if obj.type == "offer":
                # send answer
                add_tracks()
                await pc.setLocalDescription(await pc.createAnswer())
                global answer_enviado
                answer_enviado = json.dumps(pc.localDescription.__dict__)
                print(pc.localDescription.sdp)

                formatoMensaje.log_message('Mensaje de respuesta SDP al navegador enviado a' + str(remote_addr))
                print("Send: ", answer_enviado)
                cliente.transport.sendto(answer_enviado.encode())

        formatoMensaje.log_message('Comienzo conexion WebRTC con el navegador')
        await wait_bye_recibido()


class EchoClientProtocol:
    def __init__(self, message, on_con_lost):
        self.message = message
        self.on_con_lost = on_con_lost
        self.transport = None

    def connection_made(self, transport):
        self.transport = transport
        formatoMensaje.log_message('Mensaje REGISTRO enviado a ' + str(remote_addr))
        self.transport.sendto(self.message.encode())

    def datagram_received(self, data, addr):
        if data.decode().split('"')[len(data.decode().split('"')) - 2] == "offer":
            # Accept the offer
            formatoMensaje.log_message('Mensaje de oferta SDP del navegador recibido de ' + str(addr))
            print("Received:", data.decode())
            global offer_recibido
            offer_recibido = data.decode()

    def error_received(self, exc):
        print('Error received:', exc)

    def connection_lost(self):
        print("Connection closed")
        self.on_con_lost.set_result(True)


async def wait_offer_recibido():
    while offer_recibido == "":
        await asyncio.sleep(1)


async def wait_bye_recibido():
    while bye_recibido == "":
        await asyncio.sleep(1)


def reset_variables_globales():
    global offer_recibido
    global answer_enviado
    global bye_recibido
    offer_recibido = ""
    answer_enviado = ""
    bye_recibido = ""


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("video_file", help="Video file to stream")
    parser.add_argument("signal_ip", help="Signaling server IP address")
    parser.add_argument("signal_port", type=int, help="Signaling server port")
    args = parser.parse_args()
    pc = RTCPeerConnection()

    # create media source
    if args.video_file:
        player = MediaPlayer(args.video_file)
    else:
        player = None

    recorder = MediaBlackhole()

    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(
            run(
                pc=pc,
                player=player,
                recorder=recorder,
                role="answer",
                args=args
            )
        )
    except KeyboardInterrupt:
        pass
    finally:
        # cleanup
        loop.run_until_complete(recorder.stop())
        loop.run_until_complete(pc.close())


if __name__ == "__main__":
    main()
