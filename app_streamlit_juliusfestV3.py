import json
import random
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Streamlit + Three.js Bubble Demo",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown(
    """
    <style>
    .stApp {
        background:
            radial-gradient(circle at 20% 20%, rgba(0,242,255,0.12), transparent 25%),
            radial-gradient(circle at 80% 15%, rgba(112,0,255,0.12), transparent 25%),
            radial-gradient(circle at 50% 85%, rgba(191,255,0,0.10), transparent 25%),
            linear-gradient(180deg, #030303 0%, #080808 100%);
    }
    .block-container {
        padding-top: 1rem;
        max-width: 100%;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Burbujas 3D · Streamlit + Three.js")
st.caption("Plantilla mínima funcional con animación fluida en frontend")

max_bubbles = st.slider("Número de burbujas", 5, 20, 12)
bubble_scale = st.slider("Escala de burbujas", 0.3, 2.0, 1.0, 0.1)
speed = st.slider("Velocidad", 0.1, 2.0, 0.8, 0.1)

palette = ["#00f2ff", "#7000ff", "#bfff00"]

bubbles = []
for i in range(max_bubbles):
    bubbles.append(
        {
            "name": f"Bubble_{i+1}",
            "x": random.uniform(-6, 6),
            "y": random.uniform(-3, 3),
            "z": random.uniform(-4, 4),
            "r": random.uniform(0.35, 0.9) * bubble_scale,
            "color": random.choice(palette),
            "phase": random.uniform(0, 6.28),
        }
    )

bubbles_json = json.dumps(bubbles)

html_code = f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8" />
  <style>
    html, body {{
      margin: 0;
      padding: 0;
      overflow: hidden;
      background: transparent;
      width: 100%;
      height: 100%;
    }}
    #scene-container {{
      width: 100vw;
      height: 78vh;
      position: relative;
      overflow: hidden;
      background:
        radial-gradient(circle at 20% 20%, rgba(0,242,255,0.08), transparent 25%),
        radial-gradient(circle at 80% 15%, rgba(112,0,255,0.08), transparent 25%),
        radial-gradient(circle at 50% 85%, rgba(191,255,0,0.06), transparent 25%),
        rgba(0,0,0,0.15);
      border-radius: 20px;
    }}
    #label {{
      position: absolute;
      left: 20px;
      bottom: 16px;
      color: rgba(255,255,255,0.7);
      font-family: Arial, sans-serif;
      font-size: 14px;
      letter-spacing: 0.5px;
      z-index: 10;
      pointer-events: none;
    }}
  </style>
</head>
<body>
  <div id="scene-container">
    <div id="label">Drag para rotar · Scroll para zoom</div>
  </div>

  <script type="module">
    import * as THREE from "https://unpkg.com/three@0.160.0/build/three.module.js";
    import {{ OrbitControls }} from "https://unpkg.com/three@0.160.0/examples/jsm/controls/OrbitControls.js";

    const container = document.getElementById("scene-container");
    const bubbles = {bubbles_json};
    const SPEED = {speed};

    const scene = new THREE.Scene();
    scene.fog = new THREE.FogExp2(0x050505, 0.045);

    const camera = new THREE.PerspectiveCamera(
      55,
      container.clientWidth / container.clientHeight,
      0.1,
      100
    );
    camera.position.set(0, 1.5, 14);

    const renderer = new THREE.WebGLRenderer({{
      antialias: true,
      alpha: true
    }});
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setSize(container.clientWidth, container.clientHeight);
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    container.appendChild(renderer.domElement);

    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.autoRotate = true;
    controls.autoRotateSpeed = 0.4;
    controls.minDistance = 7;
    controls.maxDistance = 24;

    // Luces
    const ambient = new THREE.AmbientLight(0xffffff, 0.7);
    scene.add(ambient);

    const point1 = new THREE.PointLight(0x00f2ff, 18, 40);
    point1.position.set(-8, 6, 8);
    scene.add(point1);

    const point2 = new THREE.PointLight(0x7000ff, 16, 40);
    point2.position.set(8, 4, 6);
    scene.add(point2);

    const point3 = new THREE.PointLight(0xbfff00, 10, 30);
    point3.position.set(0, -4, 8);
    scene.add(point3);

    // Partículas de fondo
    const starGeometry = new THREE.BufferGeometry();
    const starCount = 250;
    const starPositions = new Float32Array(starCount * 3);

    for (let i = 0; i < starCount; i++) {{
      starPositions[i * 3] = (Math.random() - 0.5) * 40;
      starPositions[i * 3 + 1] = (Math.random() - 0.5) * 24;
      starPositions[i * 3 + 2] = (Math.random() - 0.5) * 30;
    }}

    starGeometry.setAttribute("position", new THREE.BufferAttribute(starPositions, 3));

    const starMaterial = new THREE.PointsMaterial({{
      size: 0.05,
      transparent: true,
      opacity: 0.7
    }});

    const stars = new THREE.Points(starGeometry, starMaterial);
    scene.add(stars);

    // Grupo principal
    const bubbleGroup = new THREE.Group();
    scene.add(bubbleGroup);

    const bubbleMeshes = [];

    bubbles.forEach((b) => {{
      const group = new THREE.Group();

      // Halo
      const glowGeometry = new THREE.SphereGeometry(b.r * 1.45, 32, 32);
      const glowMaterial = new THREE.MeshBasicMaterial({{
        color: b.color,
        transparent: true,
        opacity: 0.12
      }});
      const glow = new THREE.Mesh(glowGeometry, glowMaterial);
      group.add(glow);

      // Burbuja principal
      const sphereGeometry = new THREE.SphereGeometry(b.r, 48, 48);
      const sphereMaterial = new THREE.MeshPhysicalMaterial({{
        color: b.color,
        transparent: true,
        opacity: 0.92,
        roughness: 0.15,
        metalness: 0.05,
        transmission: 0.18,
        clearcoat: 0.9,
        clearcoatRoughness: 0.15
      }});
      const sphere = new THREE.Mesh(sphereGeometry, sphereMaterial);
      group.add(sphere);

      group.position.set(b.x, b.y, b.z);
      bubbleGroup.add(group);

      bubbleMeshes.push({{
        group,
        baseX: b.x,
        baseY: b.y,
        baseZ: b.z,
        radius: b.r,
        phase: b.phase
      }});
    }});

    const clock = new THREE.Clock();

    function animate() {{
      const t = clock.getElapsedTime() * SPEED;

      bubbleMeshes.forEach((b, i) => {{
        b.group.position.x = b.baseX + Math.sin(t * 0.7 + b.phase + i * 0.17) * 0.35;
        b.group.position.y = b.baseY + Math.cos(t * 0.9 + b.phase + i * 0.11) * 0.28;
        b.group.position.z = b.baseZ + Math.sin(t * 0.5 + b.phase + i * 0.23) * 0.45;

        b.group.rotation.y += 0.003;
        b.group.rotation.x += 0.0015;

        const pulse = 1 + Math.sin(t * 1.4 + b.phase) * 0.035;
        b.group.scale.set(pulse, pulse, pulse);
      }});

      stars.rotation.y += 0.0008;
      controls.update();
      renderer.render(scene, camera);
      requestAnimationFrame(animate);
    }}

    animate();

    function onResize() {{
      camera.aspect = container.clientWidth / container.clientHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(container.clientWidth, container.clientHeight);
    }}

    window.addEventListener("resize", onResize);
  </script>
</body>
</html>
"""

components.html(html_code, height=650, scrolling=False)
