# University Projects

Colección de proyectos de grado en **Ingeniería de Sistemas Audiovisuales y Multimedia**.

---

## Juego de Realidad Virtual (WebXR)

Videojuego inmersivo 3D en **Realidad Virtual (WebXR)** desarrollado sobre la biblioteca A-Frame y Three.js.

### Mecánica de Juego

- **Objetivo**: Destruir los _globos_ flotantes apuntando directamente con la mirada/puntero (`raycaster`).
- **Enemigos (_Comedores_)**: Esferas enemigas que persiguen activamente al jugador guiadas por **audio posicional 3D**.
- **HUD & Minimapa**: Vista principal con marcador en tiempo real y vista cenital secundaria proyectada en la interfaz mediante canvas dinámico.

### Stack Tecnológico

- **Framework VR/3D**: [A-Frame](https://aframe.io/) (v1.7.0) + [Three.js](https://threejs.org/)
- **Detección de Colisiones**: `aframe-obb-collider-component`
- **Lenguajes**: JavaScript (ES6+), HTML5, Canvas 2D
- **Sonido**: Web Audio API (Audio espacial 3D)

---

## Ejecución del Juego VR

1. Accede a la carpeta `GRAFICOS 3D/docs/`.
2. Abre `juego_completo.html` o `juego_xr.html` en tu navegador o visor VR (Meta Quest, Chrome, Firefox).
