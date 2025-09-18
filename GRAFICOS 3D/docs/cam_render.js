// Code for a component implementing texture coming from a camera
//
// Based on code from:
//   https://wirewhiz.com/how-to-use-a-cameras-output-as-a-texture-in-aframe/
//
AFRAME.registerComponent('camrender',{
    schema: {
       // Id of the canvas element used for rendering the camera
       cid: { type: 'string', default: 'camRenderer' },
       // Height of the renderer element
       height: { type: 'number', default: 300 },
       // Width of the renderer element
       width: { type: 'number', default: 400 }
    },
    update: function(oldData) {
        let data = this.data
        if (oldData.cid !== data.cid) {
            // Find canvas element to be used for rendering
            let canvas_el = document.getElementById(this.data.cid);
            // Create renderer
            this.renderer = new THREE.WebGLRenderer({
                antialias: true,
                canvas: canvas_el
            });
        };
        if (oldData.width !== data.width || oldData.height !== data.height) {
            // Set size of canvas renderer
            this.renderer.setSize(data.width, data.height);
            this.renderer.domElement.height = data.height;
            this.renderer.domElement.width = data.width;
        };
    },
    tick: function(time, timeDelta) {
        this.renderer.render( this.el.sceneEl.object3D ,
            this.el.getObject3D('camera'));
    }
});

AFRAME.registerComponent('canvas-updater', {
    dependencies: ['geometry', 'material'],

    tick: function () {
	    let material = this.el.getObject3D('mesh').material;
	    if (material.map) {
            material.map.needsUpdate = true;
        };
    }
});