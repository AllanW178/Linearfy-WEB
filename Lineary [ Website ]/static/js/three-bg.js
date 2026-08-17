document.addEventListener("DOMContentLoaded", () => {
    const canvas = document.querySelector('#webgl-canvas');
    if (!canvas) return;

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 100);
    camera.position.z = 8;

    const renderer = new THREE.WebGLRenderer({ canvas: canvas, alpha: true, antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

    const geometry = new THREE.IcosahedronGeometry(2.5, 2); 
    
    // Pure black wireframe material, drawing sharp schematic lines
    const material = new THREE.MeshBasicMaterial({
        color: 0x000000,
        wireframe: true,
        transparent: true,
        opacity: 0.1
    });

    const mesh = new THREE.Mesh(geometry, material);
    scene.add(mesh);

    // Mouse Tracking Data
    let mouseX = 0;
    let mouseY = 0;
    const windowHalfX = window.innerWidth / 2;
    const windowHalfY = window.innerHeight / 2;

    document.addEventListener('mousemove', (event) => {
        mouseX = (event.clientX - windowHalfX);
        mouseY = (event.clientY - windowHalfY);
    });

    window.addEventListener('resize', () => {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
    });

    const clock = new THREE.Clock();

    const tick = () => {
        const elapsedTime = clock.getElapsedTime();

        // Technical, precise rotation
        mesh.rotation.y = elapsedTime * 0.1 + (mouseX * 0.0005);
        mesh.rotation.x = elapsedTime * 0.05 + (mouseY * 0.0005);
        
        // Locked position, slightly offset to right
        mesh.position.x = 2;
        
        renderer.render(scene, camera);
        window.requestAnimationFrame(tick);
    };

    tick();
});
