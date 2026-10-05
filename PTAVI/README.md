▶️ **[Ver Vídeo Explicativo en YouTube](https://youtu.be/1OTfBErCV1w?si=Ee_4QCYiKQE-ueFk)**

---

# WebRTC Video Streaming System

Sistema distribuido de transmisión de audio y vídeo en tiempo real basado en **WebRTC**, **Python (`aiortc`, `asyncio`, `aiohttp`)** y un servidor de señalización sobre **UDP**.

---

## 🏗️ Arquitectura del Sistema

El sistema consta de tres componentes principales desacoplados:

```
┌─────────────────┐       UDP        ┌───────────────────────┐
│ Streamer Node   │ ────────────────>│  Signaling Server     │
│ (aiortc)        │ <─────────────── │  (signalling.py)      │
└────────┬────────┘   SDP Offer/Ans  └───────────▲───────────┘
         │                                       │ SDP Offer/Ans
         │ WebRTC                                │ (UDP)
         │ Media Stream                          │
┌────────▼────────┐       HTTP       ┌───────────┴───────────┐
│ Browser Client  │ <──────────────> │ Front-end Web Server  │
│ (client.js)     │     /offer       │ (front.py / aiohttp)  │
└─────────────────┘                  └───────────────────────┘
```

1. **Servidor de Señalización (`signalling.py`)**: Intermediario UDP que registra los streamers conectados, mantiene el catálogo dinámico de vídeos y conmuta los mensajes de oferta/respuesta SDP.
2. **Nodo Streamer (`streamer.py`)**: Emisor multimedia basado en `aiortc`. Registra el vídeo en el servidor de señalización, atiende ofertas SDP y transmite los tracks de audio/vídeo.
3. **Servidor Web Front-end (`front.py`)**: Servidor HTTP creado con `aiohttp` que renderiza la interfaz Jinja2 (`index.html`) y gestiona las solicitudes de streaming entre el navegador (`client.js`) y la red de señalización.

---

## 📋 Requisitos Previos

- **Python 3.8+**
- Instalar dependencias necesarias:

```bash
pip install aiortc aiohttp jinja2
```

---

## 🚀 Guía de Ejecución

Sigue el orden numérico abriendo terminales independientes para cada componente:

### 1. Iniciar Servidor de Señalización
```bash
python signalling.py <puerto_udp>
# Ejemplo:
python signalling.py 9999
```

### 2. Iniciar uno o más Streamers
```bash
python streamer.py <archivo_video> <ip_signal> <puerto_signal>
# Ejemplo:
python streamer.py video_1.mp4 127.0.0.1 9999
```

### 3. Iniciar Servidor Web Front-end
```bash
python front.py <puerto_http> <ip_signal> <puerto_signal>
# Ejemplo:
python front.py 8080 127.0.0.1 9999
```

### 4. Abrir la Interfaz Web
Accede desde tu navegador a:
```text
http://localhost:8080
```

---

## 📁 Estructura del Proyecto

```text
.
├── signalling.py      # Servidor de señalización UDP
├── streamer.py        # Nodo de emisión multimedia WebRTC (aiortc)
├── front.py           # Servidor web HTTP (aiohttp + Jinja2)
├── client.js          # Lógica WebRTC en el cliente navegador
├── index.html         # Plantilla de la interfaz de usuario
├── formatoMensaje.py  # Formateador de logs con marcas de tiempo
└── *.mp4              # Archivos de vídeo de prueba
```
