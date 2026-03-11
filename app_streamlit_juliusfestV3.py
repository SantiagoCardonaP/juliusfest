import json
import random
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Burbujas 3D · Streamlit + Three.js",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
.stApp {
    background:
        radial-gradient(circle at 20% 20%, rgba(0,242,255,0.10), transparent 25%),
        radial-gradient(circle at 80% 15%, rgba(112,0,255,0.10), transparent 25%),
        radial-gradient(circle at 50% 85%, rgba(191,255,0,0.08), transparent 25%),
        linear-gradient(180deg, #030303 0%, #080808 100%);
}
.block-container {
    padding-top: 1rem;
    max-width: 100%;
}
</style>
""", unsafe_allow_html=True)

st.title("Burbujas 3D · Streamlit + Three.js")
st.caption("Plantilla mínima funcional con animación fluida en frontend")

n_bubbles = st.slider("Número de burbujas", 5, 20, 10)
bubble_scale = st.slider("Escala de burbujas", 0.3, 2.0, 0.9, 0.1)
speed = st.slider("Velocidad", 0.1, 2.0, 1.0, 0.1)

palette = ["#00f2ff", "#7000ff", "#bfff00"]

bubbles = []
for i in range(n_bubbles):
    bubbles.append({
        "name": f"Bubble_{i+1}",
        "x": random.uniform(-6, 6),
        "y": random.uniform(-3, 3),
        "z": random.uniform(-4, 4),
        "r": random.uniform(0.35, 0.9) * bubble_scale,
        "color": random.choice(palette),
        "phase": random.uniform(0, 6.28),
    })

bubbles_json = json.dumps(bubbles)

html_code = f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8"/>
  <style>
    html, body {{
      margin: 0;
      padding: 0;
      width: 100%;
      height: 100%;
      overflow: hidden;
      background: transparent;
    }}

    #scene-container {{
      width: 100%;
      height: 650px;
      position: relative;
      overflow: hidden;
      border-radius: 22px;
      background:
        radial-gradient(circle at 20% 20%, rgba(0,242,255,0.08), transparent 25%),
        radial-gradient(circle at 80% 15%, rgba(112,0,255,0.08), transparent 25%),
        radial-gradient(circle at 50% 85%, rgba(191,255,0,0.06), transparent 25%),
        rgba(0,0,0,0.10);
    }}

    #hint {{
      position: absolute;
      left: 18px;
      bottom: 14px;
      z-index: 10;
      color: rgba(255,255,255,0.75);
      font-family: Arial, sans-serif;
      font-size: 14px;
      pointer-events: none;
    }}

    #debug {{
      position: absolute;
      right: 18px;
      top: 14px;
      z-index: 10;
      color: rgba(255,255,255,0.75);
      font-family: Arial, sans-serif;
      font-size: 13px;
      background: rgba(0,0,0,0.35);
      padding: 6px 10px;
      border-radius: 10px;
    }}
  </style>
</head>
<body>
  <div id="scene-container">
    <div id="hint">Drag para rotar · Scroll para zoom</div>
    <div id="debug">Cargando escena…</div>
  </div>

  <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>

  <script>
    const debugBox = document.getElementById("debug");

    try {{
      const bubbles = {bubbles_json};
      const SPEED = {speed};

      const container = document.getElementById("scene-container");

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
      container.appendChild(renderer.domElement);

      const controls = new THREE.OrbitControls(camera, renderer.domElement);
      controls.enableDamping = true;
      controls.dampingFactor = 0.05;
      controls.autoRotate = true;
      controls.autoRotateSpeed = 0.5;
      controls.minDistance = 7;
      controls.maxDistance = 24;

      const ambient = new THREE.AmbientLight(0xffffff, 0.75);
      scene.add(ambient);

      const point1 = new THREE.PointLight(0x00f2ff, 1.7, 40);
      point1.position.set(-8, 6, 8);
      scene.add(point1);

      const point2 = new THREE.PointLight(0x7000ff, 1.5, 40);
      point2.position.set(8, 4, 6);
      scene.add(point2);

      const point3 = new THREE.PointLight(0xbfff00, 1.0, 30);
      point3.position.set(0, -4, 8);
      scene.add(point3);

      // Fondo de partículas
      const starGeometry = new THREE.BufferGeometry();
      const starCount = 250;
      const starPositions = new Float32Array(starCount * 3);

      for (let i = 0; i < starCount; i++) {{
        starPositions[i * 3] = (Math.random() - 0.5) * 40;
        starPositions[i * 3 + 1] = (Math.random() - 0.5) * 24;
        starPositions[i * 3 + 2] = (Math.random() - 0.5) * 30;
      }}

      starGeometry.setAttribute(
        "position",
        new THREE.BufferAttribute(starPositions, 3)
      );

      const starMaterial = new THREE.PointsMaterial({{
        size: 0.06,
        transparent: true,
        opacity: 0.75,
        color: 0xffffff
      }});

      const stars = new THREE.Points(starGeometry, starMaterial);
      scene.add(stars);

      const bubbleGroup = new THREE.Group();
      scene.add(bubbleGroup);

      const bubbleMeshes = [];

      bubbles.forEach((b) => {{
        const group = new THREE.Group();

        // Halo
        const glowGeometry = new THREE.SphereGeometry(b.r * 1.55, 32, 32);
        const glowMaterial = new THREE.MeshBasicMaterial({{
          color: b.color,
          transparent: true,
          opacity: 0.14
        }});
        const glow = new THREE.Mesh(glowGeometry, glowMaterial);
        group.add(glow);

        // Burbuja principal
        const sphereGeometry = new THREE.SphereGeometry(b.r, 40, 40);
        const sphereMaterial = new THREE.MeshPhongMaterial({{
          color: b.color,
          transparent: true,
          opacity: 0.92,
          shininess: 110,
          specular: 0xffffff
        }});
        const sphere = new THREE.Mesh(sphereGeometry, sphereMaterial);
        group.add(sphere);

        group.position.set(b.x, b.y, b.z);
        bubbleGroup.add(group);

        bubbleMeshes.push({{
          group: group,
          baseX: b.x,
          baseY: b.y,
          baseZ: b.z,
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

      function onResize() {{
        const w = container.clientWidth;
        const h = container.clientHeight;
        camera.aspect = w / h;
        camera.updateProjectionMatrix();
        renderer.setSize(w, h);
      }}

      window.addEventListener("resize", onResize);

      debugBox.textContent = "Escena 3D activa";
      animate();

    }} catch (err) {{
      debugBox.textContent = "Error cargando Three.js";
      console.error(err);
    }}
  </script>
</body>
</html>
"""

components.html(html_code, height=680, scrolling=False)
