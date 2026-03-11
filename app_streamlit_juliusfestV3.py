import json
import math
import random
import urllib.parse

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

try:
    from streamlit_autorefresh import st_autorefresh
except ImportError:
    st_autorefresh = None

st.set_page_config(
    page_title="Burbujas 3D · Google Sheets + Three.js",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =========================================================
# CONFIG
# =========================================================
SHEET_ID = "1v2_7wlNnPA0jxg0ZBRcSLlMbtfxAh04RcvdmyVyvi8s"
SHEET_NAME = "Hoja 1"
MAX_BUBBLES = 20

COMPANY_COL = "¿Cuál es el nombre de tu empresa?"
SUM_COL = "Suma"

CACHE_TTL_SECONDS = 5
AUTOREFRESH_MS = 5000

# =========================================================
# AUTOREFRESH
# =========================================================
if st_autorefresh is not None:
    st_autorefresh(interval=AUTOREFRESH_MS, key="bubble_refresh")
else:
    st.warning(
        "No está instalado streamlit-autorefresh. Instálalo con: "
        "`pip install streamlit-autorefresh`"
    )

# =========================================================
# ESTILO STREAMLIT
# =========================================================
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

h1, h2, h3, p, div, label {
    color: white;
}
</style>
""", unsafe_allow_html=True)

st.title("Burbujas 3D · Empresas en tiempo real")
st.caption("Google Sheets + Streamlit + Three.js · Auto refresh + nombres legibles")

# =========================================================
# GOOGLE SHEETS
# =========================================================
@st.cache_data(ttl=CACHE_TTL_SECONDS)
def load_sheet(sheet_id: str, sheet_name: str) -> pd.DataFrame:
    encoded_name = urllib.parse.quote(sheet_name)

    urls = [
        f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={encoded_name}",
        f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&sheet={encoded_name}",
    ]

    last_error = None
    for url in urls:
        try:
            return pd.read_csv(url)
        except Exception as e:
            last_error = e

    raise last_error

def safe_text(value) -> str:
    if pd.isna(value):
        return ""
    return str(value).strip()

def color_from_suma(value: float, vmin: float, vmax: float) -> str:
    if math.isclose(vmin, vmax):
        return "#00f2ff"

    norm = (value - vmin) / (vmax - vmin)

    if norm >= 0.66:
        return "#00f2ff"   # alto
    if norm >= 0.33:
        return "#7000ff"   # medio
    return "#bfff00"       # bajo

def size_from_suma(value: float, vmin: float, vmax: float) -> float:
    if math.isclose(vmin, vmax):
        return 0.95
    norm = (value - vmin) / (vmax - vmin)
    return 0.60 + norm * 0.95

# =========================================================
# CARGA Y LIMPIEZA
# =========================================================
try:
    df = load_sheet(SHEET_ID, SHEET_NAME)
except Exception as e:
    st.error(f"No pude leer Google Sheets: {e}")
    st.stop()

required_cols = [COMPANY_COL, SUM_COL]
missing = [c for c in required_cols if c not in df.columns]

if missing:
    st.error(f"Faltan columnas requeridas: {missing}")
    st.write("Columnas encontradas:", list(df.columns))
    st.stop()

df = df.copy()
df[COMPANY_COL] = df[COMPANY_COL].apply(safe_text)
df[SUM_COL] = pd.to_numeric(df[SUM_COL], errors="coerce")

df = df.dropna(subset=[SUM_COL])
df = df[df[COMPANY_COL] != ""]
df = df.tail(MAX_BUBBLES).reset_index(drop=True)

if df.empty:
    st.warning("No hay filas válidas para mostrar.")
    st.stop()

# =========================================================
# CONTROLES
# =========================================================
col1, col2, col3, col4 = st.columns(4)

with col1:
    speed = st.slider("Velocidad", 0.2, 2.0, 0.9, 0.1)

with col2:
    spread = st.slider("Separación", 6, 18, 10)

with col3:
    auto_rotate = st.toggle("Auto rotación", value=True)

with col4:
    show_debug = st.toggle("Mostrar debug", value=False)

st.metric("Empresas visibles", len(df))

# =========================================================
# MAPEO DE DATOS A BURBUJAS
# =========================================================
vmin = float(df[SUM_COL].min())
vmax = float(df[SUM_COL].max())

bubbles = []
n = len(df)

for i, row in df.iterrows():
    angle = (i / max(n, 1)) * math.pi * 2.0
    layer = i % 4
    radius_ring = 3.0 + layer * (spread / 10.0)

    x = math.cos(angle) * radius_ring
    y = math.sin(angle * 1.35) * 2.4
    z = math.sin(angle) * radius_ring * 0.85

    company = safe_text(row[COMPANY_COL])
    suma = float(row[SUM_COL])

    bubbles.append({
        "name": company,
        "suma": round(suma, 2),
        "x": round(x, 3),
        "y": round(y, 3),
        "z": round(z, 3),
        "r": round(size_from_suma(suma, vmin, vmax), 3),
        "color": color_from_suma(suma, vmin, vmax),
        "phase": round(random.uniform(0, 6.28), 3)
    })

bubbles_json = json.dumps(bubbles, ensure_ascii=False)
auto_rotate_js = "true" if auto_rotate else "false"
debug_display = "block" if show_debug else "none"

# =========================================================
# HTML + THREE.JS
# =========================================================
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
      font-family: Arial, sans-serif;
    }}

    #scene-container {{
      width: 100%;
      height: 740px;
      position: relative;
      overflow: hidden;
      border-radius: 24px;
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
      color: rgba(255,255,255,0.78);
      font-size: 14px;
      pointer-events: none;
    }}

    #debug {{
      position: absolute;
      right: 18px;
      top: 14px;
      z-index: 20;
      color: rgba(255,255,255,0.78);
      font-size: 13px;
      background: rgba(0,0,0,0.35);
      padding: 6px 10px;
      border-radius: 10px;
      display: {debug_display};
    }}

    #tooltip {{
      position: absolute;
      z-index: 30;
      display: none;
      padding: 8px 10px;
      border-radius: 10px;
      background: rgba(10,10,10,0.92);
      color: white;
      font-size: 13px;
      line-height: 1.35;
      pointer-events: none;
      border: 1px solid rgba(255,255,255,0.12);
      white-space: nowrap;
    }}

    #labels-layer {{
      position: absolute;
      inset: 0;
      pointer-events: none;
      z-index: 25;
    }}

    .bubble-label {{
      position: absolute;
      transform: translate(-50%, -50%);
      color: rgba(255,255,255,0.97);
      font-size: 13px;
      font-weight: 700;
      text-align: center;
      line-height: 1.1;
      white-space: normal;
      max-width: 130px;
      text-shadow:
        0 0 6px rgba(0,0,0,0.70),
        0 0 12px rgba(0,0,0,0.55),
        0 0 18px rgba(0,0,0,0.40);
      opacity: 1;
      will-change: transform, left, top;
    }}
  </style>
</head>
<body>
  <div id="scene-container">
    <div id="hint">Drag para rotar · Scroll para zoom</div>
    <div id="debug">Cargando escena…</div>
    <div id="tooltip"></div>
    <div id="labels-layer"></div>
  </div>

  <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>

  <script>
    const debugBox = document.getElementById("debug");
    const tooltip = document.getElementById("tooltip");
    const labelsLayer = document.getElementById("labels-layer");

    try {{
      const bubbles = {bubbles_json};
      const SPEED = {speed};
      const AUTO_ROTATE = {auto_rotate_js};

      const container = document.getElementById("scene-container");

      const scene = new THREE.Scene();
      scene.fog = new THREE.FogExp2(0x050505, 0.04);

      const camera = new THREE.PerspectiveCamera(
        55,
        container.clientWidth / container.clientHeight,
        0.1,
        100
      );
      camera.position.set(0, 1.8, 15);

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
      controls.autoRotate = AUTO_ROTATE;
      controls.autoRotateSpeed = 0.45;
      controls.minDistance = 7;
      controls.maxDistance = 28;

      const ambient = new THREE.AmbientLight(0xffffff, 0.90);
      scene.add(ambient);

      const point1 = new THREE.PointLight(0x00f2ff, 1.8, 40);
      point1.position.set(-8, 7, 8);
      scene.add(point1);

      const point2 = new THREE.PointLight(0x7000ff, 1.5, 40);
      point2.position.set(9, 4, 6);
      scene.add(point2);

      const point3 = new THREE.PointLight(0xbfff00, 1.1, 30);
      point3.position.set(0, -5, 8);
      scene.add(point3);

      // Partículas
      const starGeometry = new THREE.BufferGeometry();
      const starCount = 240;
      const starPositions = new Float32Array(starCount * 3);

      for (let i = 0; i < starCount; i++) {{
        starPositions[i * 3] = (Math.random() - 0.5) * 42;
        starPositions[i * 3 + 1] = (Math.random() - 0.5) * 26;
        starPositions[i * 3 + 2] = (Math.random() - 0.5) * 30;
      }}

      starGeometry.setAttribute("position", new THREE.BufferAttribute(starPositions, 3));

      const starMaterial = new THREE.PointsMaterial({{
        size: 0.06,
        transparent: true,
        opacity: 0.72,
        color: 0xffffff
      }});

      const stars = new THREE.Points(starGeometry, starMaterial);
      scene.add(stars);

      const bubbleGroup = new THREE.Group();
      scene.add(bubbleGroup);

      const raycaster = new THREE.Raycaster();
      const mouse = new THREE.Vector2();

      const bubbleMeshes = [];
      const hoverTargets = [];

      function wrapLabelText(text, maxLength) {{
        const words = String(text).split(" ");
        const lines = [];
        let current = "";

        for (const word of words) {{
          const candidate = current ? current + " " + word : word;
          if (candidate.length > maxLength && current) {{
            lines.push(current);
            current = word;
          }} else {{
            current = candidate;
          }}
        }}

        if (current) lines.push(current);

        const limited = lines.slice(0, 3);
        if (lines.length > 3) {{
          limited[2] = limited[2].slice(0, Math.max(0, maxLength - 3)) + "...";
        }}

        return limited.join("<br>");
      }}

      bubbles.forEach((b) => {{
        const group = new THREE.Group();

        const glowGeometry = new THREE.SphereGeometry(b.r * 1.55, 36, 36);
        const glowMaterial = new THREE.MeshBasicMaterial({{
          color: b.color,
          transparent: true,
          opacity: 0.14
        }});
        const glow = new THREE.Mesh(glowGeometry, glowMaterial);
        group.add(glow);

        const sphereGeometry = new THREE.SphereGeometry(b.r, 48, 48);
        const sphereMaterial = new THREE.MeshPhongMaterial({{
          color: b.color,
          transparent: true,
          opacity: 0.90,
          shininess: 120,
          specular: 0xffffff
        }});
        const sphere = new THREE.Mesh(sphereGeometry, sphereMaterial);
        group.add(sphere);

        group.position.set(b.x, b.y, b.z);
        bubbleGroup.add(group);

        const htmlLabel = document.createElement("div");
        htmlLabel.className = "bubble-label";
        htmlLabel.innerHTML = wrapLabelText(b.name, 16);
        labelsLayer.appendChild(htmlLabel);

        bubbleMeshes.push({{
          group: group,
          baseX: b.x,
          baseY: b.y,
          baseZ: b.z,
          phase: b.phase,
          meta: b,
          sphere: sphere,
          htmlLabel: htmlLabel
        }});

        hoverTargets.push(sphere);
      }});

      const clock = new THREE.Clock();

      function updateTooltip(event) {{
        const rect = renderer.domElement.getBoundingClientRect();
        mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
        mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

        raycaster.setFromCamera(mouse, camera);
        const intersects = raycaster.intersectObjects(hoverTargets);

        if (intersects.length > 0) {{
          const mesh = intersects[0].object;
          const found = bubbleMeshes.find(item => item.sphere === mesh);

          if (found) {{
            tooltip.style.display = "block";
            tooltip.style.left = (event.clientX - rect.left + 14) + "px";
            tooltip.style.top = (event.clientY - rect.top + 14) + "px";
            tooltip.innerHTML = "<b>" + found.meta.name + "</b><br>Suma: " + found.meta.suma;
          }}
        }} else {{
          tooltip.style.display = "none";
        }}
      }}

      renderer.domElement.addEventListener("mousemove", updateTooltip);
      renderer.domElement.addEventListener("mouseleave", () => {{
        tooltip.style.display = "none";
      }});

      function updateLabels() {{
        const width = container.clientWidth;
        const height = container.clientHeight;

        bubbleMeshes.forEach((b) => {{
          const projected = b.group.position.clone();
          projected.project(camera);

          const x = (projected.x * 0.5 + 0.5) * width;
          const y = (-projected.y * 0.5 + 0.5) * height;

          const inFront = projected.z < 1;
          const inBounds = x >= -60 && x <= width + 60 && y >= -60 && y <= height + 60;
          const visible = inFront && inBounds;

          if (!visible) {{
            b.htmlLabel.style.display = "none";
            return;
          }}

          const depthOpacity = Math.max(0.45, Math.min(1.0, 1.15 - projected.z * 0.35));
          const scale = Math.max(0.75, Math.min(1.15, 1.15 - projected.z * 0.12));

          b.htmlLabel.style.display = "block";
          b.htmlLabel.style.left = x + "px";
          b.htmlLabel.style.top = y + "px";
          b.htmlLabel.style.opacity = depthOpacity.toFixed(2);
          b.htmlLabel.style.transform = "translate(-50%, -50%) scale(" + scale.toFixed(2) + ")";
        }});
      }}

      function animate() {{
        const t = clock.getElapsedTime() * SPEED;

        bubbleMeshes.forEach((b, i) => {{
          b.group.position.x = b.baseX + Math.sin(t * 0.7 + b.phase + i * 0.17) * 0.35;
          b.group.position.y = b.baseY + Math.cos(t * 0.9 + b.phase + i * 0.11) * 0.26;
          b.group.position.z = b.baseZ + Math.sin(t * 0.5 + b.phase + i * 0.23) * 0.45;

          b.group.rotation.y += 0.0022;

          const pulse = 1 + Math.sin(t * 1.35 + b.phase) * 0.03;
          b.group.scale.set(pulse, pulse, pulse);
        }});

        stars.rotation.y += 0.0007;

        controls.update();
        updateLabels();
        renderer.render(scene, camera);
        requestAnimationFrame(animate);
      }}

      function onResize() {{
        const w = container.clientWidth;
        const h = container.clientHeight;
        camera.aspect = w / h;
        camera.updateProjectionMatrix();
        renderer.setSize(w, h);
        updateLabels();
      }}

      window.addEventListener("resize", onResize);

      debugBox.textContent = "Escena 3D activa · " + bubbles.length + " empresas";
      updateLabels();
      animate();

    }} catch (err) {{
      debugBox.textContent = "Error cargando escena";
      console.error(err);
    }}
  </script>
</body>
</html>
"""

components.html(html_code, height=760, scrolling=False)
