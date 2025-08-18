import asyncio
import json
import formatoMensaje
import argparse

clientlist = []
streamers = {}
ficheros = []
mensaje_no_enviado = []
streamer_elegido = ""
video_requests = {}  # Dictionary to keep track of video requests by clients

class EchoServerProtocol:

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        message = data.decode()
        print(f"\nReceived: {message!r} from {addr}")
        print(f"\nClient IP: {addr[0]}, Client Port: {addr[1]}")
        if message.split("-")[0] == "REGISTER STREAMER":
            for streamer in json.loads(message.split("-")[1]).keys():
                streamers[streamer] = addr
            print(streamers)
            ficheros.append(message.split("-")[1])
            formatoMensaje.log_message("\nMensaje REGISTRO STREAMER recibido de " + str(addr))

        if message == "LISTA":
            clientlist.append({"Name": len(clientlist) + 1, "Direccion": addr})
            print(clientlist)
            print(f"Send {ficheros} to {addr}")
            self.transport.sendto(json.dumps(ficheros).encode(), addr)

        if message.split(":")[0] == "Name":
            global streamer_elegido
            # Track the requested video for each client
            video_requests[addr] = message.split(":")[1]
            streamer_elegido = message.split(":")[1]

        if message.split('"')[len(message.split('"')) - 2] == "offer":
            formatoMensaje.log_message("\nMensaje de oferta SDP recibido de" + str(addr))
            try:
                self.transport.sendto(message.encode(), streamers[streamer_elegido])
                formatoMensaje.log_message("\nMensaje de oferta SDP enviado a " + str(streamers[streamer_elegido]))
            except IndexError:
                print(f'\nSend: "No hay servidores disponibles" to {clientlist[-1]["Direccion"]}')
                self.transport.sendto(
                    "No hay servidores disponibles, se enviara el mensaje cuando se abra un servidor".encode(),
                    clientlist[-1]["Direccion"])
                mensaje_no_enviado.append(message)
        if message.split('"')[len(message.split('"')) - 2] == "answer":
            formatoMensaje.log_message("\nMensaje de respuesta SDP recibido de " + str(addr))
            print(f"\nSend {message!r} to {clientlist[-1]['Direccion']}")
            self.transport.sendto(message.encode(), clientlist[-1]["Direccion"])
            formatoMensaje.log_message(
                "\nMensaje de respuesta SDP enviada a" + str(clientlist[-1]["Direccion"]))


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("signal_port", type=int, help="UDP port to listen for signaling messages")
    args = parser.parse_args()
    port = args.signal_port
    formatoMensaje.log_message("Comienzo")

    loop = asyncio.get_running_loop()

    transport, protocol = await loop.create_datagram_endpoint(
        lambda: EchoServerProtocol(),
        local_addr=('127.0.0.1', port))

    print(f"\nServer listening on 127.0.0.1:{port}")

    try:
        await asyncio.sleep(3600)  # Serve for 1 hour.
    finally:
        transport.close()


if __name__ == "__main__":
    asyncio.run(main())
