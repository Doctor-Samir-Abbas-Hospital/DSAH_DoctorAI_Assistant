# character_component.py

character_3d_component = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    
    <!-- Imporant meta information to make the page as rigid as possible on mobiles, to avoid unintentional zooming on the page itself  -->
    <meta name="viewport" content="width=device-width, height=device-height, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">

    <meta http-equiv="X-UA-Compatible" content="ie=edge">
    <title>Character Tutorial</title>
    
</head>
<body>
  
  <!-- The loading element overlays all else until the model is loaded, at which point we remove this element from the DOM -->  
<div class="loading" id="js-loader"><div class="loader"></div></div>
  
<div class="wrapper">
    <!-- The canvas element is used to draw the 3D scene -->
<canvas id="c"></canvas>
 <div class="footer-container">
  <p>Revolusionizing Health Care with AI </p>
</div>
</div>
</body>
</html>
<style>
/* Ensure canvas takes full screen width */
/* Style for the footer container below the canvas */
.footer-container {
  text-align: center;
  padding: 10px;
  background-color: #660022; /* Match the background color if desired */
}

.footer-container p {
  color: white;
  font-family: Arial, sans-serif;
  font-size: 13px;
  margin: 0;
}

</style>
<!-- The main Three.js file -->
<script src='https://cdnjs.cloudflare.com/ajax/libs/three.js/108/three.min.js'></script>

<!-- This brings in the ability to load custom 3D objects in the .gltf file format. Blender allows the ability to export to this format out the box -->
<script src='https://cdn.jsdelivr.net/gh/mrdoob/Three.js@r92/examples/js/loaders/GLTFLoader.js'></script>


<!-- Our HTML consists of a loading animation (currently commented out until we need it), a wrapper div and our all-important canvas element. The canvas is what Three.js uses to render our scene, and the CSS sets this at 100% viewport size. We also load in two dependencies at the bottom of our HTML file: Three.js, and GLTFLoader (GLTF is the format that our 3D model is imported as). Both of these dependencies are available as npm modules.

The CSS also consists of a small amount of centering styling and the rest is just the loading animation; really nothing more to it than that. You can now collapse your HTML and CSS panels, we will delve into that very little for the rest of the tutorial. -->
    <script src='https://cdnjs.cloudflare.com/ajax/libs/three.js/108/three.min.js'></script>
    <script src='https://cdn.jsdelivr.net/gh/mrdoob/Three.js@r92/examples/js/loaders/GLTFLoader.js'></script>
    <script>
     (function() {
  // Set our main variables
  let scene,  
    renderer,
    camera,
    model,                              // Our character
    neck,                               // Reference to the neck bone in the skeleton
    waist,                              // Reference to the waist bone in the skeleton
    possibleAnims,                      // Animations found in our file
    mixer,                              // THREE.js animations mixer
    idle,                               // Idle, the default state our character returns to
    clock = new THREE.Clock(),          // Used for anims, which run to a clock instead of frame rate 
    currentlyAnimating = false,         // Used to check whether characters neck is being used in another anim
    raycaster = new THREE.Raycaster(),  // Used to detect the click on our character
    loaderAnim = document.getElementById('js-loader');
    
  init();

  function init() {
    const MODEL_PATH = 'https://s3-us-west-2.amazonaws.com/s.cdpn.io/1376484/stacy_lightweight.glb';
    
    const canvas = document.querySelector('#c');
    
    // Init the scene
    scene = new THREE.Scene();

    // Set the single dark color as background
    const backgroundColor = 0x660022; // Darker shade of #990033
    scene.background = new THREE.Color(backgroundColor);

    // Init the renderer
    renderer = new THREE.WebGLRenderer({canvas, antialias: true});
    renderer.shadowMap.enabled = true;
    renderer.setPixelRatio(window.devicePixelRatio);
    document.body.appendChild(renderer.domElement);

    // Add a camera
    camera = new THREE.PerspectiveCamera(
      50,
      window.innerWidth / window.innerHeight,
      0.1,
      1000
    );
    camera.position.z = 30;
    camera.position.x = 0;
    camera.position.y = -3;

    let stacy_txt = new THREE.TextureLoader().load('https://s3-us-west-2.amazonaws.com/s.cdpn.io/1376484/stacy.jpg');
    stacy_txt.flipY = false;
    
    const stacy_mtl = new THREE.MeshPhongMaterial({
      map: stacy_txt,
      color: 0xffffff,
      skinning: true
    });

    var loader = new THREE.GLTFLoader();

    loader.load(
      MODEL_PATH,
      function(gltf) {
        model = gltf.scene;
        let fileAnimations = gltf.animations;
        
        model.traverse(o => {
          if(o.isMesh) {
            o.castShadow = true;
            o.receiveShadow = true;
            o.material = stacy_mtl;
          }
          if (o.isBone && o.name === 'mixamorigNeck') {
            neck = o;
          }
          if (o.isBone && o.name === 'mixamorigSpine') {
            waist = o;
          }
        });

        model.scale.set(7, 7, 7);
        model.position.y = -11;
        scene.add(model);
        
        loaderAnim.remove();
        
        mixer = new THREE.AnimationMixer(model);
        
        let clips = fileAnimations.filter(val => val.name !== 'idle');
        possibleAnims = clips.map(val => {
          let clip = THREE.AnimationClip.findByName(clips, val.name);
          clip.tracks.splice(3, 3);
          clip.tracks.splice(9, 3);
          clip = mixer.clipAction(clip);
          return clip;
        });
        
        let idleAnim = THREE.AnimationClip.findByName(fileAnimations, 'idle');
        idleAnim.tracks.splice(3, 3);
        idleAnim.tracks.splice(9, 3);
        idle = mixer.clipAction(idleAnim);
        idle.play();
      },
      undefined,
      function(error) {
        console.error(error);
      }
    );
    
    let hemiLight = new THREE.HemisphereLight(0xffffff, 0xffffff, 0.61);
    hemiLight.position.set(0, 50, 0);
    scene.add(hemiLight);

    let d = 8.25;
    let dirLight = new THREE.DirectionalLight(0xffffff, 0.54);
    dirLight.position.set(-8, 12, 8);
    dirLight.castShadow = true;
    dirLight.shadow.mapSize = new THREE.Vector2(1024, 1024);
    dirLight.shadow.camera.near = 0.1;
    dirLight.shadow.camera.far = 1500;
    dirLight.shadow.camera.left = d * -1;
    dirLight.shadow.camera.right = d;
    dirLight.shadow.camera.top = d;
    dirLight.shadow.camera.bottom = d * -1;
    scene.add(dirLight);

    let floorGeometry = new THREE.PlaneGeometry(5000, 5000, 1, 1);
    let floorMaterial = new THREE.MeshPhongMaterial({
      color: 0xeeeeee,
      shininess: 0
    });
    
    let floor = new THREE.Mesh(floorGeometry, floorMaterial);
    floor.rotation.x = -0.5 * Math.PI;
    floor.receiveShadow = true;
    floor.position.y = -11;
    scene.add(floor);

    let geometry = new THREE.SphereGeometry(8, 32, 32);
    let material = new THREE.MeshBasicMaterial({ color: 0x9bffaf });
    let sphere = new THREE.Mesh(geometry, material);
    sphere.position.z = -15;
    sphere.position.y = -2.5;
    sphere.position.x = -0.25;
    scene.add(sphere);
  }

  function update() {
    if (mixer) {
      mixer.update(clock.getDelta());
    }
    
    if (resizeRendererToDisplaySize(renderer)) {
      const canvas = renderer.domElement;
      camera.aspect = canvas.clientWidth / canvas.clientHeight;
      camera.updateProjectionMatrix();
    }
    renderer.render(scene, camera);
    requestAnimationFrame(update);
  }
  update();

  function resizeRendererToDisplaySize(renderer) {
    const canvas = renderer.domElement;
    let width = window.innerWidth;
    let height = window.innerHeight;
    let canvasPixelWidth = canvas.width / window.devicePixelRatio;
    let canvasPixelHeight = canvas.height / window.devicePixelRatio;
    
    const needResize = 
          canvasPixelWidth !== width || canvasPixelHeight !== height;
    if (needResize) {
      renderer.setSize(width, height, false)
    }
    return needResize;
  }
     
  window.addEventListener('click', e => raycast(e));
  window.addEventListener('touchend', e => raycast(e, true));

  function raycast(e, touch = false) {
    var mouse = {};
    if (touch) {
      mouse.x = 2 * (e.changedTouches[0].clientX / window.innerWidth) - 1;
      mouse.y = 1 - 2 * (e.changedTouches[0].clientY / window.innerHeight);
    } else {
      mouse.x = 2 * (e.clientX / window.innerWidth) - 1;
      mouse.y = 1 - 2 * (e.clientY / window.innerHeight);
    }
    raycaster.setFromCamera(mouse, camera);
    var intersects = raycaster.intersectObjects(scene.children, true);
    if (intersects[0]) {
      var object = intersects[0].object;
      if (object.name === 'stacy') {
        if (!currentlyAnimating) {
          currentlyAnimating = true;
          playOnClick();
        }
      }
    }
  }

  function playOnClick() {
    let anim = Math.floor(Math.random() * possibleAnims.length);
    playModifierAnimation(idle, 0.25, possibleAnims[anim], 0.25);
  }

  function playModifierAnimation(from, fSpeed, to, tSpeed) {
    to.setLoop(THREE.LoopOnce);
    to.reset();
    to.play();
    from.crossFadeTo(to, fSpeed, true);
    setTimeout(function() {
      from.enabled = true;
      to.crossFadeTo(from, tSpeed, true);
      currentlyAnimating = false;
    }, to._clip.duration * 1000 -((tSpeed + fSpeed) * 1000));
  }

  document.addEventListener('mousemove', function(e) {
    var mousecoords = getMousePos(e);
    if(neck && waist) {
      moveJoint(mousecoords, neck, 50);
      moveJoint(mousecoords, waist, 30);
    }
  });

  function getMousePos(e) {
    return { x: e.clientX, y: e.clientY};
  }

  function moveJoint(mouse, joint, degreeLimit) {
    let degrees = getMouseDegrees(mouse.x, mouse.y, degreeLimit);
    joint.rotation.y = THREE.Math.degToRad(degrees.x);
    joint.rotation.x = THREE.Math.degToRad(degrees.y); 
  }

  function getMouseDegrees(x, y, degreeLimit) {
    let dx = 0, dy = 0, xdiff, xPercentage, ydiff, yPercentage;
    let w = { x: window.innerWidth, y: window.innerHeight };

    if (x <= w.x / 2) {
      xdiff = w.x / 2 - x;  
      xPercentage = (xdiff / (w.x / 2)) * 100;
      dx = ((degreeLimit * xPercentage) / 100) * -1;
    }
    if (x >= w.x / 2) {
      xdiff = x - w.x / 2;
      xPercentage = (xdiff / (w.x / 2)) * 100;
      dx = (degreeLimit * xPercentage) / 100;
    }
    if (y <= w.y / 2) {
      ydiff = w.y / 2 - y;
      yPercentage = (ydiff / (w.y / 2)) * 100;
      dy = (((degreeLimit * 0.5) * yPercentage) / 100) * -1;
    }
    if (y >= w.y / 2) {
      ydiff = y - w.y / 2;
      yPercentage = (ydiff / (w.y / 2)) * 100;
      dy = (degreeLimit * yPercentage) / 100;
    }
    return { x: dx, y: dy };
  }
})();
    </script>
</body>
</html>
"""
