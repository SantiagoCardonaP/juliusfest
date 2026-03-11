import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Burbujas 3D · Google Sheets + Three.js",
    layout="wide",
    initial_sidebar_state="collapsed"
)

SHEET_ID = "1v2_7wlNnPA0jxg0ZBRcSLlMbtfxAh04RcvdmyVyvi8s"
SHEET_NAME = "Hoja 1"
MAX_BUBBLES = 20
POLL_MS = 5000

COMPANY_COL = "¿Cuál es el nombre de tu empresa?"
SUM_COL = "Suma"

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
st.caption("Three.js consulta Google Sheets cada 5 segundos sin reiniciar la escena")

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
      height: 760px;
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
      color: rgba(255,255,255,0.82);
      font-size: 13px;
      background: rgba(0,0,0,0.35);
      padding: 6px 10px;
      border-radius: 10px;
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
    <div id="debug">Inicializando escena…</div>
    <div id="tooltip"></div>
    <div id="labels-layer"></div>
  </div>

  <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>

  <script>
    const SHEET_ID = "{SHEET_ID}";
    const SHEET_NAME = "{SHEET_NAME}";
    const MAX_BUBBLES = {MAX_BUBBLES};
    const POLL_MS = {POLL_MS};
    const COMPANY_COL = "{COMPANY_COL}";
    const SUM_COL = "{SUM_COL}";

    const container = document.getElementById("scene-container");
    const debugBox = document.getElementById("debug");
    const tooltip = document.getElementById("tooltip");
    const labelsLayer = document.getElementById("labels-layer");

    const state = {{
      bubbleMap: new Map(),
      hovered: null,
      lastLoadedAt: null
    }};

    function wrapLabelText(text, maxLength) {{
      const words = String(text || "").split(" ");
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

    function csvToRows(text) {{
      const rows = [];
      let row = [];
      let cell = "";
      let inQuotes = false;

      for (let i = 0; i < text.length; i++) {{
        const ch = text[i];
        const next = text[i + 1];

        if (ch === '"') {{
          if (inQuotes && next === '"') {{
            cell += '"';
            i++;
          }} else {{
            inQuotes = !inQuotes;
          }}
        }} else if (ch === ',' && !inQuotes) {{
          row.push(cell);
          cell = "";
        }} else if ((ch === '\\n' || ch === '\\r') && !inQuotes) {{
          if (ch === '\\r' && next === '\\n') i++;
          row.push(cell);
          rows.push(row);
          row = [];
          cell = "";
        }} else {{
          cell += ch;
        }}
      }}

      if (cell.length > 0 || row.length > 0) {{
        row.push(cell);
        rows.push(row);
      }}
      return rows;
    }}

    function rowsToObjects(rows) {{
      if (!rows || rows.length < 2) return [];
      const headers = rows[0].map(h => String(h || "").trim());
      return rows.slice(1).map(r => {{
        const obj = {{}};
        headers.forEach((h, idx) => {{
          obj[h] = r[idx] ?? "";
        }});
        return obj;
      }});
    }}

    function safeText(value) {{
      if (value === null || value === undefined) return "";
      return String(value).trim();
    }}

    function colorFromSuma(value, vmin, vmax) {{
      if (!isFinite(value)) return "#bfff00";
      if (vmin === vmax) return "#00f2ff";
      const norm = (value - vmin) / (vmax - vmin);
      if (norm >= 0.66) return "#00f2ff";
      if (norm >= 0.33) return "#7000ff";
      return "#bfff00";
    }}

    function sizeFromSuma(value, vmin, vmax) {{
      if (!isFinite(value)) return 0.8;
      if (vmin === vmax) return 0.95;
      const norm = (value - vmin) / (vmax - vmin);
      return 0.60 + norm * 0.95;
    }}

    function computeTargetPositions(items) {{
      const n = items.length;
      return items.map((item, i) => {{
        const angle = (i / Math.max(n, 1)) * Math.PI * 2.0;
        const layer = i % 4;
        const radiusRing = 3.0 + layer * 1.0;
        const x = Math.cos(angle) * radiusRing;
        const y = Math.sin(angle * 1.35) * 2.4;
        const z = Math.sin(angle) * radiusRing * 0.85;
        return {{
          ...item,
          tx: x,
          ty: y,
          tz: z
        }};
      }});
    }}

    function makeBubbleObject(item) {{
      const group = new THREE.Group();

      const glowGeometry = new THREE.SphereGeometry(item.r * 1.55, 36, 36);
      const glowMaterial = new THREE.MeshBasicMaterial({{
        color: item.color,
        transparent: true,
        opacity: 0.14
      }});
      const glow = new THREE.Mesh(glowGeometry, glowMaterial);
      group.add(glow);

      const sphereGeometry = new THREE.SphereGeometry(item.r, 48, 48);
      const sphereMaterial = new THREE.MeshPhongMaterial({{
        color: item.color,
        transparent: true,
        opacity: 0.90,
        shininess: 120,
        specular: 0xffffff
      }});
      const sphere = new THREE.Mesh(sphereGeometry, sphereMaterial);
      group.add(sphere);

      group.position.set(item.tx, item.ty, item.tz);
      group.scale.set(0.01, 0.01, 0.01);

      const htmlLabel = document.createElement("div");
      htmlLabel.className = "bubble-label";
      htmlLabel.innerHTML = wrapLabelText(item.name, 16);
      labelsLayer.appendChild(htmlLabel);

      scene.add(group);

      const obj = {{
        key: item.key,
        name: item.name,
        suma: item.suma,
        color: item.color,
        radius: item.r,
        phase: Math.random() * Math.PI * 2,
        group,
        glow,
        sphere,
        htmlLabel,
        x: item.tx,
        y: item.ty,
        z: item.tz,
        tx: item.tx,
        ty: item.ty,
        tz: item.tz,
        scale: 0.01,
        targetScale: 1.0,
        remove: false
      }};

      sphere.userData.key = item.key;
      return obj;
    }}

    function updateBubbleVisual(obj) {{
      obj.glow.material.color.set(obj.color);
      obj.sphere.material.color.set(obj.color);

      const newSphereGeometry = new THREE.SphereGeometry(obj.radius, 48, 48);
      obj.sphere.geometry.dispose();
      obj.sphere.geometry = newSphereGeometry;

      const newGlowGeometry = new THREE.SphereGeometry(obj.radius * 1.55, 36, 36);
      obj.glow.geometry.dispose();
      obj.glow.geometry = newGlowGeometry;

      obj.htmlLabel.innerHTML = wrapLabelText(obj.name, 16);
    }}

    function removeBubbleObject(obj) {{
      if (obj.htmlLabel && obj.htmlLabel.parentNode) {{
        obj.htmlLabel.parentNode.removeChild(obj.htmlLabel);
      }}
      if (obj.sphere.geometry) obj.sphere.geometry.dispose();
      if (obj.glow.geometry) obj.glow.geometry.dispose();
      if (obj.sphere.material) obj.sphere.material.dispose();
      if (obj.glow.material) obj.glow.material.dispose();
      scene.remove(obj.group);
    }}

    async function fetchSheetData() {{
      const encodedName = encodeURIComponent(SHEET_NAME);
      const url = `https://docs.google.com/spreadsheets/d/${{SHEET_ID}}/gviz/tq?tqx=out:csv&sheet=${{encodedName}}&_=${{Date.now()}}`;

      const res = await fetch(url, {{ cache: "no-store" }});
      if (!res.ok) {{
        throw new Error(`HTTP ${{res.status}}`);
      }}
      const csvText = await res.text();
      const rows = csvToRows(csvText);
      const records = rowsToObjects(rows);

      const cleaned = records
        .map(r => {{
          const name = safeText(r[COMPANY_COL]);
          const suma = Number(String(r[SUM_COL] ?? "").replace(",", "."));
          return {{ name, suma }};
        }})
        .filter(r => r.name !== "" && Number.isFinite(r.suma))
        .slice(-MAX_BUBBLES);

      const values = cleaned.map(r => r.suma);
      const vmin = values.length ? Math.min(...values) : 0;
      const vmax = values.length ? Math.max(...values) : 1;

      const mapped = cleaned.map((r, idx) => ({{
        key: r.name,
        name: r.name,
        suma: Number(r.suma.toFixed(2)),
        color: colorFromSuma(r.suma, vmin, vmax),
        r: sizeFromSuma(r.suma, vmin, vmax)
      }}));

      return computeTargetPositions(mapped);
    }}

    async function syncData() {{
      try {{
        const items = await fetchSheetData();
        const incomingKeys = new Set(items.map(x => x.key));

        for (const obj of state.bubbleMap.values()) {{
          if (!incomingKeys.has(obj.key)) {{
            obj.remove = true;
            obj.targetScale = 0.01;
          }}
        }}

        items.forEach(item => {{
          if (state.bubbleMap.has(item.key)) {{
            const obj = state.bubbleMap.get(item.key);
            obj.name = item.name;
            obj.suma = item.suma;
            obj.color = item.color;
            obj.radius = item.r;
            obj.tx = item.tx;
            obj.ty = item.ty;
            obj.tz = item.tz;
            obj.targetScale = 1.0;
            obj.remove = false;
            updateBubbleVisual(obj);
          }} else {{
            const obj = makeBubbleObject(item);
            state.bubbleMap.set(item.key, obj);
          }}
        }});

        state.lastLoadedAt = new Date();
        debugBox.textContent = `Escena activa · ${{state.bubbleMap.size}} empresas · actualizado ${{state.lastLoadedAt.toLocaleTimeString()}}`;
      }} catch (err) {{
        debugBox.textContent = "Error leyendo Google Sheets";
        console.error(err);
      }}
    }}

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
    controls.autoRotate = true;
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

    const raycaster = new THREE.Raycaster();
    const mouse = new THREE.Vector2();

    function updateTooltip(event) {{
      const rect = renderer.domElement.getBoundingClientRect();
      mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
      mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

      raycaster.setFromCamera(mouse, camera);
      const targets = Array.from(state.bubbleMap.values()).map(o => o.sphere);
      const intersects = raycaster.intersectObjects(targets);

      if (intersects.length > 0) {{
        const key = intersects[0].object.userData.key;
        const obj = state.bubbleMap.get(key);
        if (obj) {{
          tooltip.style.display = "block";
          tooltip.style.left = (event.clientX - rect.left + 14) + "px";
          tooltip.style.top = (event.clientY - rect.top + 14) + "px";
          tooltip.innerHTML = "<b>" + obj.name + "</b><br>Suma: " + obj.suma;
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

      state.bubbleMap.forEach(obj => {{
        const projected = obj.group.position.clone();
        projected.project(camera);

        const x = (projected.x * 0.5 + 0.5) * width;
        const y = (-projected.y * 0.5 + 0.5) * height;

        const inFront = projected.z < 1;
        const inBounds = x >= -60 && x <= width + 60 && y >= -60 && y <= height + 60;
        const visible = inFront && inBounds && obj.scale > 0.15;

        if (!visible) {{
          obj.htmlLabel.style.display = "none";
          return;
        }}

        const depthOpacity = Math.max(0.45, Math.min(1.0, 1.15 - projected.z * 0.35));
        const scale = Math.max(0.75, Math.min(1.15, 1.15 - projected.z * 0.12));

        obj.htmlLabel.style.display = "block";
        obj.htmlLabel.style.left = x + "px";
        obj.htmlLabel.style.top = y + "px";
        obj.htmlLabel.style.opacity = depthOpacity.toFixed(2);
        obj.htmlLabel.style.transform = "translate(-50%, -50%) scale(" + scale.toFixed(2) + ")";
      }});
    }}

    const clock = new THREE.Clock();

    function animate() {{
      const t = clock.getElapsedTime();

      state.bubbleMap.forEach((obj, index) => {{
        obj.x += (obj.tx - obj.x) * 0.035;
        obj.y += (obj.ty - obj.y) * 0.035;
        obj.z += (obj.tz - obj.z) * 0.035;
        obj.scale += (obj.targetScale - obj.scale) * 0.055;

        const driftX = Math.sin(t * 0.7 + obj.phase + index * 0.17) * 0.18;
        const driftY = Math.cos(t * 0.9 + obj.phase + index * 0.11) * 0.16;
        const driftZ = Math.sin(t * 0.5 + obj.phase + index * 0.23) * 0.24;

        obj.group.position.set(obj.x + driftX, obj.y + driftY, obj.z + driftZ);

        const pulse = 1 + Math.sin(t * 1.35 + obj.phase) * 0.03;
        const s = Math.max(0.001, obj.scale * pulse);
        obj.group.scale.set(s, s, s);

        obj.group.rotation.y += 0.0022;

        if (obj.remove && obj.scale < 0.03) {{
          removeBubbleObject(obj);
          state.bubbleMap.delete(obj.key);
        }}
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

    syncData();
    setInterval(syncData, POLL_MS);
    animate();
  </script>
</body>
</html>
"""

components.html(html_code, height=780, scrolling=False)
