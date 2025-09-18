AFRAME.registerComponent("globo", {
    schema: {
        color: {type: "color", default: "white"},
        lado: {type: "number", default: 1}
    },
    init: function(){
        let self = this
        let data = this.data
        let element = this.el 

        element.setAttribute("geometry", {
                                primitive: "box", 
                                width: data.lado, 
                                height: data.lado, 
                                depth: data.lado},)
        element.setAttribute("material", {color: data.color})

        this.el.addEventListener('obbcollisionstarted', function (event) {
            const target = event.detail.withEl
            target.parentNode.removeChild(target);
        })
    },
});

AFRAME.registerComponent("movedor", {
  schema: {
    velocidad: {type: "number", default: 1},     // unidades por segundo
    intervalo: {type: "number", default: 3000}   // cada cuánto cambia de dirección (ms)
  },

  init: function () {
    this.direccion = this.generarDireccion();  
    this.ultimoCambio = Date.now();            
    this.tAnterior = Date.now();               
  },

  tick: function () {
    const ahora = Date.now();
    const deltaT = (ahora - this.tAnterior) / 1000;
    this.tAnterior = ahora;

    // Cambiar dirección cada cierto intervalo
    if (ahora - this.ultimoCambio >= this.data.intervalo) {
      this.direccion = this.generarDireccion();
      this.ultimoCambio = ahora;
    }

    // Mover la entidad en la dirección actual a velocidad constante
    const desplazamiento = this.direccion.clone().multiplyScalar(this.data.velocidad * deltaT);
    this.el.object3D.position.add(desplazamiento);
  },

  generarDireccion: function () {
    // Genera una dirección aleatoria y la normaliza
    const dx = Math.random() * 2 - 1;
    const dy = Math.random() * 2 - 1;
    const dz = Math.random() * 2 - 1;
    return new THREE.Vector3(dx, dy, dz).normalize();
  }
});


AFRAME.registerComponent("destructor", {
    schema: {
        objetivo: {type: "string", default: ".objetivo"},
        direccion: {type: "vec3", default: {x: 0, y: 0, z: 1}},
        lejos: {type: "number", default: "10"},
        cerca: {type: "number", default: "3"},
        color: {type: "color", default: "#083521"}
    },
    init: function (){
        let data = this.data
        let element = this.el 

        // asignar al componente el atributo del trazador
        element.setAttribute("raycaster", {showLine: true, direction: data.direccion, lineColor: data.color, far: data.lejos, near: data.cerca, objects: data.objetivo})
        element.addEventListener("raycaster-intersection", function(event){
            for (const intersected_el of event.detail.els) {
                if (intersected_el.hasAttribute("globo")) {
                    element.emit("destruido");
                }
                intersected_el.parentNode.removeChild(intersected_el);
            }

        })
    }
})

AFRAME.registerComponent('comedor', {

schema: {

    color: {type: 'color', default: 'green'},
    radio: {type: 'number', default: 1},
    velocidad: {type: 'number', default: 1}

},

init: function()    {

    let self = this;
    let element = this.el
    self.tAnterior = Date.now();
    console.log(this.el.object3D);


    element.setAttribute('geometry', {primitive: 'sphere', radio: self.data.radio});
    element.setAttribute('material', {color: self.data.color});
    element.setAttribute('obb-collider', {show: true});

    element.setAttribute("sound", {
        autoplay: true,
        loop: true,
        src: "#sonido_comedor",
        maxDistance: 100,
        distanceModel: "linear",
        volume: 0.2
    })
    

    element.addEventListener('obbcollisionstarted', (evt) => {
       let target = evt.detail.withEl;
       if (target === self.objetivo) {
        target.parentEl.remove();
    }

    });
},

tick: function () {

  this.objetivo = document.querySelector('[jugador]');
  if (!this.objetivo) return;

  // cuanto tiempo ha pasado desde el ultimo refresco de frame 
  const tActual = Date.now();
  const deltaT = (tActual - this.tAnterior) / 1000; // para pasarlo a segundos
  this.tAnterior = tActual;

  const posComedor = this.el.object3D.position;
  const posJugador = this.objetivo.object3D.position;

  // Crear el vector de dirección que es jugador - comedor
  const direccion = new THREE.Vector3().subVectors(posJugador, posComedor).normalize();

  // Mover el comedor en esa dirección a velocidad constante
  const desplazamiento = direccion.multiplyScalar(this.data.velocidad * deltaT);
  posComedor.add(desplazamiento);
}
});

AFRAME.registerComponent("jugador", {
    schema: {
        radio: {type: "number", default: 1},
        color: {type: "color", default: "#45fcf2"}
    },
    init: function(){
        let data = this.data
        let element = this.el
        console.log(this.el.object3D);


        element.setAttribute("geometry", {primitive: "sphere", radius: data.radio})
        element.setAttribute("material", {color: data.color})
        element.setAttribute('obb-collider', {show: true})

    }
})

AFRAME.registerComponent("juego", {
    schema: {
        num_globos: {type: "number", default: 3},
        num_comedores: {type: "number", default: 2},
        col_globos: {type: "color", default: "cyan"},
        col_comedores: {type: "color", default: "purple"},
        col_jugador: {type: "color", default: "pink"},
        tam_globos: {type: "number", default: 1},
        tam_comedores: {type: "number", default: 1},
        tam_jugador: {type: "number", default: 1},
        vel_globos: {type: "number", default: 1},
        vel_comedores: {type: "number", default: 1},
        intervalo_globos: {type: "number", default: 3000},
        dir_destructor: {type: "vec3", default: {x: 0, y: 0, z: 1}},
        lejos_destructor: {type: "number", default: 10},
        cerca_destructor: {type: "number", default: 2},
        intervalo_creacion_globos: {type: "number", default: 1500}, // ms
        intervalo_creacion_comedores: {type: "number", default: 2000}
    },
    init: function(){
        self = this
        element = this.el
        data = this.data
        
        // inicializar el componente añadiendo todos los atributos distintos del juego

        // globos
        setInterval(function(){
            const globo = document.createElement("a-entity")

            globo.setAttribute("globo", {
                color: data.col_globos,
                tam_globos: data.tam_globos
            })
            globo.setAttribute("movedor", {
                velocidad: data.vel_globos,
                intervalo: data.intervalo_globos
            })
            globo.setAttribute("position", {
                x: Math.random() * 20 - 10,
                y: Math.random() * 10 - 5,
                z: Math.random() * 10,
            })
            globo.setAttribute("class", "objetivo")

            element.appendChild(globo)
        }, data.intervalo_creacion_globos)
        // comdores
        setInterval(function(){
            const comedor = document.createElement("a-entity")

            comedor.setAttribute("comedor", {
                color: data.col_comedores,
                radio: data.tam_comedores,
                velocidad: data.vel_comedores
            })
            comedor.setAttribute("position", {
                x: Math.random() * 35 - 10,
                y: Math.random() * 35 - 10,
                z: -5,
            })
            comedor.setAttribute("class", "objetivo")

            element.appendChild(comedor)
        }, data.intervalo_creacion_comedores)

        // jugador y destructor a la camara
        const camera = document.querySelector("a-camera")

        if (camera){
            camera.setAttribute("jugador", {
                radio: data.tam_jugador,
                color: data.col_jugador
            })
            camera.setAttribute("destructor", {
                direccion: data.dir_destructor,
                lejos: data.lejos_destructor,
                cerca: data.cerca_destructor,
                color: data.col_jugador
            })
            const puntero = document.createElement("a-entity")
            puntero.setAttribute("geometry", {
                primitive: "ring",
                radiusInner: 0.02,
                radiusOuter: 0.04
            })
            puntero.setAttribute("material", {
                color: data.col_jugador
            })
            puntero.setAttribute("position", "0 0 -0.5")
            camera.appendChild(puntero)
        }
    }
})

AFRAME.registerComponent("marcador", {
    schema: {
        color: {type: "color", default: "white"},
        fondo: {type: "color", default: "black"}
    },
    init: function () {
        this.contador = 0;
        let element = this.el

        // Crear el texto en el plano
        this.texto = document.createElement("a-entity");
        this.texto.setAttribute("text", {
            value: "Globos destruidos: 0",
            align: "center",
            color: this.data.color,
            width: 2
        });
        this.texto.setAttribute("position", "0 0 0.01");

        element.setAttribute("geometry", {
            primitive: "plane",
            height: 0.3,
            width: 2
        });

        element.setAttribute("material", {
            color: this.data.fondo,
            opacity: 0.7
        });

        element.appendChild(this.texto);

        // Escuchar evento "destruido"
        const destructor = document.querySelector("[destructor]");
        if (destructor) {
            destructor.addEventListener("destruido", () => {
                this.contador++;
                this.texto.setAttribute("text", "value", "Globos destruidos: " + this.contador);
            });
        }
    }
});

