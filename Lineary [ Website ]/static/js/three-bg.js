document.addEventListener("DOMContentLoaded", () => {
    const canvas = document.querySelector('#webgl-canvas');
    if (!canvas) return;

    // 1. Scene Setup
    const scene = new THREE.Scene();
    
    // 2. Camera Setup
    const camera = new THREE.PerspectiveCamera(40, window.innerWidth / window.innerHeight, 0.1, 100);
    camera.position.z = 7;

    // 3. Renderer Setup
    const renderer = new THREE.WebGLRenderer({ canvas: canvas, alpha: true, antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

    // 4. Create a Low-Poly Torus (Sleek Modern Ring Shape)
    // Parameters: radius, tube, radialSegments, tubularSegments
    const geometry = new THREE.TorusGeometry(1.8, 0.6, 6, 16); 
    
    const material = new THREE.MeshStandardMaterial({
        color: 0x111111,
        roughness: 0.3,
        metalNess: 0.8,
        flatShading: true, // Gives it that clean low-poly faceted look
        transparent: true,
        opacity: 0.15 // Low opacity so it stays safely in the background behind text
    });

    const mesh = new THREE.Mesh(geometry, material);
    scene.add(mesh);

    // 5. Lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 1);
    scene.add(ambientLight);

    const pointLight = new THREE.PointLight(0xffffff, 2);
    pointLight.position.set(5, 5, 5);
    scene.add(pointLight);

    // 6. Interaction Variables (Scroll & Mouse)
    let scrollY = window.scrollY;
    let currentScroll = 0;
    
    let mouseX = 0;
    let mouseY = 0;
    let targetX = 0;
    let targetY = 0;

    const windowHalfX = window.innerWidth / 2;
    const windowHalfY = window.innerHeight / 2;

    window.addEventListener('scroll', () => {
        scrollY = window.scrollY;
    });

    document.addEventListener('mousemove', (event) => {
        mouseX = (event.clientX - windowHalfX);
        mouseY = (event.clientY - windowHalfY);
    });

    window.addEventListener('resize', () => {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
    });

    // 7. Animation Loop with Slideshow Parallax Effect
    const clock = new THREE.Clock();

    const tick = () => {
        const elapsedTime = clock.getElapsedTime();

        currentScroll += (scrollY - currentScroll) * 0.05;

        targetX = mouseX * 0.0008;
        targetY = mouseY * 0.0008;

        // Smooth rotation & shifting to the right side of the screen so it frames text nicely
        mesh.rotation.y = elapsedTime * 0.2 + targetX;
        mesh.rotation.x = elapsedTime * 0.15 + targetY;
        
        // Push the object slightly to the right side and let scroll move it vertically
        mesh.position.x = 1.5;
        mesh.position.y = (currentScroll * 0.001) + Math.sin(elapsedTime * 0.4) * 0.2;

        renderer.render(scene, camera);
        window.requestAnimationFrame(tick);
    };

    tick();
});
