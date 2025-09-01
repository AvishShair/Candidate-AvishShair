// Three.js Background Animation
let scene, camera, renderer, particles;

function initThreeJS() {
    scene = new THREE.Scene();
    camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    renderer = new THREE.WebGLRenderer({ alpha: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    document.getElementById('three-container').appendChild(renderer.domElement);

    // Create floating particles
    const geometry = new THREE.BufferGeometry();
    const particleCount = 150;
    const positions = new Float32Array(particleCount * 3);
    
    for (let i = 0; i < particleCount * 3; i++) {
        positions[i] = (Math.random() - 0.5) * 30;
    }
    
    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    
    const material = new THREE.PointsMaterial({
        color: 0x4F46E5,
        size: 0.03,
        transparent: true,
        opacity: 0.4
    });
    
    particles = new THREE.Points(geometry, material);
    scene.add(particles);
    
    camera.position.z = 8;
    
    animate();
}

function animate() {
    requestAnimationFrame(animate);
    
    if (particles) {
        particles.rotation.x += 0.0005;
        particles.rotation.y += 0.001;
    }
    
    renderer.render(scene, camera);
}

// Resize handler
window.addEventListener('resize', () => {
    if (camera && renderer) {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
    }
});

// GSAP Animation Functions
function initAnimations() {
    const tl = gsap.timeline();
    
    tl.to('.hero-section', {
        duration: 1,
        opacity: 1,
        y: 0,
        ease: "power3.out"
    })
    .to('.upload-section', {
        duration: 0.8,
        opacity: 1,
        x: 0,
        ease: "power3.out"
    }, "-=0.5")
    .to('.url-section', {
        duration: 0.8,
        opacity: 1,
        x: 0,
        ease: "power3.out"
    }, "-=0.6");
}

function animateButton(button, isLoading = false) {
    if (isLoading) {
        gsap.to(button, {
            duration: 0.3,
            scale: 0.95,
            ease: "power2.out"
        });
        button.classList.add('pulse-glow');
    } else {
        gsap.to(button, {
            duration: 0.3,
            scale: 1,
            ease: "power2.out"
        });
        button.classList.remove('pulse-glow');
    }
}

// Export functions for global use
window.initThreeJS = initThreeJS;
window.initAnimations = initAnimations;
window.animateButton = animateButton;
