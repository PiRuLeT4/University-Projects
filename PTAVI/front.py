import argparse
import asyncio
import json
import logging
import os
import jinja2
import formatoMensaje
from aiohttp import web
from aiortc import RTCSessionDescription

ROOT = os.path.dirname(__file__)

relay = None
webcam = None
lista_recibido = []
answer_recibido = ""
cliente = None
remote_addr = ""
titulos = []
descripciones = []
navegador_id = 0  # Counter to keep track of browser requests


async def index(request):
    global navegador_id
    loop = asyncio.get_running_loop()
    on_con_lost = loop.create_future()
    message = "LISTA"
    global cliente
    cliente = EchoClientProtocol(message, on_con_lost)
    await loop.create_datagram_endpoint(lambda: cliente, remote_addr=remote_addr)
    await wait_lista_recibido()

    # Assign a unique ID to each browser request to differentiate video selection
    navegador_id += 1
    if navegador_id == 1:  # If it's the first browser (the only one), send the entire list
        assigned_videos = lista_recibido
        assigned_titulos = titulos
        assigned_descripciones = descripciones
    else:  # For subsequent browsers, distribute videos in a round-robin manner
        assigned_videos = [lista_recibido[(navegador_id - 1) % len(lista_recibido)]]
        assigned_titulos = [titulos[lista_recibido.index(assigned_videos[0])]]
        assigned_descripciones = [descripciones[lista_recibido.index(assigned_videos[0])]]

    template = jinja2.Template(open(os.path.join(ROOT, "index.html")).read())
    context = {'videos': assigned_videos, 'titulos': assigned_titulos, 'descripciones': assigned_descripciones}
    return web.Response(text=template.render(context), content_type='text/html')


async def javascript(request):
    content = open(os.path.join(ROOT, "client.js"), "r").read()
    return web.Response(content_type="application/javascript", text=content)


async def offer(request):
    formatoMensaje.log_message('Mensaje de oferta SDP del navegador recibido')
    params = await request.json()
    formatoMensaje.log_message('Mensaje de oferta SDP del navegador enviado a (127.0.0.1, 9999)')

    offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])
    print(offer.sdp)
    video_elegido = "Name:" + params["video"]

    print("Send:", video_elegido)
    cliente.transport.sendto(video_elegido.encode())

    print("Send:", json.dumps(offer.__dict__))
    cliente.transport.sendto(json.dumps(offer.__dict__).encode())

    await wait_answer_recibido()
    global answer_recibido

    answer = json.loads(answer_recibido)
    sdp = answer["sdp"]
    print(sdp)

    formatoMensaje.log_message('Mensaje de respuesta SDP al navegador enviado')
    answer_recibido = ""

    return web.Response(
        content_type="application/json",
        text=json.dumps(
            {"sdp": sdp, "type": "answer"}
        ),
    )


pcs = set()


async def on_shutdown():
    coros = [pc.close() for pc in pcs]
    await asyncio.gather(*coros)
    pcs.clear()


class EchoClientProtocol:
    def __init__(self, message, on_con_lost):
        self.message = message
        self.on_con_lost = on_con_lost
        self.transport = None

    def connection_made(self, transport):
        self.transport = transport
        formatoMensaje.log_message('Mensaje de peticion del listado de videos enviado a (127.0.0.1, 9999)')
        self.transport.sendto(self.message.encode())

    def datagram_received(self, data, addr):

        if data.decode().split('"')[len(data.decode().split('"')) - 2] == "answer":
            formatoMensaje.log_message('Mensaje de respuesta SDP al navegador recibido de ' + str(addr))
            global answer_recibido
            print("Received:", data.decode())
            answer_recibido = data.decode()
            return

        if json.loads(data.decode())[0].split('"')[1].split("_")[0] == "video":
            formatoMensaje.log_message('Mensaje de listado de videos recibido de ' + str(addr))
            global lista_recibido, titulos, descripciones
            print("Received:", json.loads(data.decode()))
            n = 0
            for video in json.loads(data.decode()):
                lista_recibido.append(str(json.loads(video).keys()).split("'")[1])
                titulos.append(json.loads(video)[lista_recibido[n]]["Titulo"])
                descripciones.append(json.loads(video)[lista_recibido[n]]["Descripcion"])
                n += 1

    def error_received(self, exc):
        print('Error received:', exc)

    def connection_lost(self):
        print("Connection closed")
        self.on_con_lost.set_result(True)


async def wait_lista_recibido():
    while lista_recibido == "":
        await asyncio.sleep(1)
    await asyncio.sleep(1)


async def wait_answer_recibido():
    while answer_recibido == "":
        await asyncio.sleep(1)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("http_port", type=int, help="TCP port for HTTP requests")
    parser.add_argument("signal_ip", help="Signaling server IP address")
    parser.add_argument("signal_port", type=int, help="Signaling server port")

    args = parser.parse_args()
    global remote_addr
    remote_addr = (args.signal_ip, args.signal_port)
    logging.basicConfig(level=logging.INFO)
    ssl_context = None
    formatoMensaje.log_message("Comienzo")
    app = web.Application()
    app.on_shutdown.append(on_shutdown)
    app.router.add_get("/", index)
    app.router.add_get("/client.js", javascript)
    app.router.add_post("/offer", offer)
    web.run_app(app, host="0.0.0.0", port=args.http_port, ssl_context=ssl_context)


if __name__ == "__main__":
    main()
