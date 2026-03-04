import streamlit as st
import pandas as pd
import numpy as np
import io
import base64
from PIL import Image
import plotly.graph_objects as go
from typing import Optional

# =============================
# CONFIGURACIÓN BÁSICA / ESTILO
# =============================
st.set_page_config(page_title="Dashboard de burbujas (tiempo real)", page_icon="🫧", layout="wide")

# === Marca / assets ===
logo_path_top = "logo-grupo-epm (1).png"
logo_path_bottom = "logo-julius.png"
background_path = "fondo-julius-epm.png"

def img_to_b64(path: str) -> Optional[str]:
    try:
        img = Image.open(path)
        buf = io.BytesIO()
        fmt = "PNG" if path.lower().endswith("png") else "JPEG"
        img.save(buf, format=fmt)
        return base64.b64encode(buf.getvalue()).decode()
    except Exception:
        return None

b64_logo_top = img_to_b64(logo_path_top)
b64_logo_bottom = img_to_b64(logo_path_bottom)
b64_background = img_to_b64(background_path)

# Encabezado con logo centrado
if b64_logo_top:
    st.markdown(
        f"""
        <div style='position: absolute; top: 20px; left: 50%; transform: translateX(-50%); z-index: 9999;'>
            <img src="data:image/png;base64,{b64_logo_top}" width="233px"/>
        </div>
        <div style='margin-top: 220px;'></div>
        """,
        unsafe_allow_html=True,
    )

# CSS y fondo dinámico
background_css = (f"background-image: url('data:image/jpeg;base64,{b64_background}');" if b64_background else "")
custom_css = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600;700&display=swap');
html, body, [class*="css"] {{ font-family: 'Montserrat', sans-serif !important; }}
.stApp {{
    {background_css}
    background-repeat: no-repeat; background-position: top center; background-size: auto; background-attachment: scroll;
}}
.stApp .main .block-container {{
    background-image: linear-gradient(to bottom, transparent 330px, #240531 330px) !important;
    background-repeat: no-repeat !important; background-size: 100% 100% !important;
    border-radius: 20px !important; padding: 40px !important; max-width: 1400px !important; margin: 2rem auto !important;
}}
label, .stSelectbox label, .stMultiSelect label, .stTextInput label {{ color: white !important; font-size: 1.05em; }}
:root {{ --brand: #ff5722; }}
div.stButton > button {{
    background-color: var(--brand);
    color: #ffffff !important;
    font-weight: 700;
    font-size: 16px;
    padding: 12px 24px;
    border-radius: 50px;
    border: none;
    width: 100%;
    margin-top: 10px;
}}
div.stButton > button:hover {{ background-color: #e64a19; color:#4B006E !important; }}
.block {{ background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 16px; padding: 18px; margin-bottom: 14px; }}
.hint {{ color:#ddd; font-size: 12px; margin-top: -6px; }}
.small {{ color:#ddd; font-size: 12px; }}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

st.markdown("""
<div style='position: relative; z-index: 1; padding-top: 20px; text-align:center;'>
  <h1>Dashboard de burbujas en tiempo real</h1>
  <div class="small">Las respuestas del formulario se reflejan al instante en el gráfico (sin necesidad de “Guardar”).</div>
</div>
""", unsafe_allow_html=True)

# =============================
# STATE
# =============================
defaults = {
    "empresa": "",
    "habeas_aceptado": False,
    "nombre_persona": "",
    "celular": "",
    "ventas_mes": "",
    "df_form": None,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# =============================
# FORMULARIO XLSX
# =============================
@st.cache_data(show_spinner=False)
def load_form(path: str = "Formulario.xlsx") -> pd.DataFrame:
    df = pd.read_excel(path, sheet_name="Formulario")
    categoria_col = next((c for c in df.columns if str(c).strip().lower().startswith("categor")), None)
    pregunta_col  = next((c for c in df.columns if str(c).strip().lower().startswith("pregun")), None)
    calif_col     = next((c for c in df.columns if str(c).strip().lower().startswith("calif")), None)
    if not (categoria_col and pregunta_col):
        raise ValueError("La hoja 'Formulario' debe tener columnas 'Categoría' y 'Pregunta'.")
    if not calif_col:
        df["Calificación"] = np.nan
        calif_col = "Calificación"
    df = df.rename(columns={categoria_col: "Categoría", pregunta_col: "Pregunta", calif_col: "Calificación"})
    return df[["Categoría", "Pregunta", "Calificación"]]

if st.session_state.df_form is None:
    try:
        st.session_state.df_form = load_form("Formulario.xlsx")
    except Exception as e:
        st.error(f"No se pudo cargar 'Formulario.xlsx'. Detalle: {e}")
        st.stop()

df_form = st.session_state.df_form.copy()

# Inicializa sliders si no existen (default=2)
initial_scores = list(df_form["Calificación"].fillna(2).clip(1, 3).astype(int))
for i, v in enumerate(initial_scores):
    st.session_state.setdefault(f"slider_{i}", int(v))

# =============================
# LAYOUT: FORM (izq) + DASHBOARD (der)
# =============================
left, right = st.columns([1.15, 1], gap="large")

with left:
    st.markdown("## 1) Datos generales")
    c1, c2 = st.columns([1, 1])
    with c1:
        st.session_state.nombre_persona = st.text_input("Nombre", value=st.session_state.nombre_persona, placeholder="Ej. Juan Pérez")
        st.session_state.celular = st.text_input("Celular", value=st.session_state.celular, placeholder="Ej. 3001234567")
    with c2:
        st.session_state.empresa = st.text_input("Nombre de la empresa", value=st.session_state.empresa, placeholder="Ej. ACME S.A.S.")
        st.session_state.ventas_mes = st.text_input("Promedio de ventas ($) al mes", value=str(st.session_state.ventas_mes), placeholder="Ej. 1.000.000")

    st.session_state.habeas_aceptado = st.checkbox(
        "Autorizo el tratamiento de mis datos (Habeas Data).",
        value=st.session_state.habeas_aceptado,
        help="Acepto que la información suministrada sea usada para análisis y recomendaciones."
    )

    st.markdown("## 2) Formulario")
    st.caption("**1 = No · 2 = Parcialmente · 3 = Sí** (se actualiza en el dashboard a la derecha).")

    if not st.session_state.habeas_aceptado:
        st.info("Para diligenciar el formulario, primero acepta Habeas Data.")
    else:
        # Agrupar por categoría y mostrar en expanders
        for cat, df_cat in df_form.groupby("Categoría", dropna=False):
            with st.expander(str(cat), expanded=False):
                for idx in df_cat.index:
                    q = df_form.loc[idx, "Pregunta"]
                    st.markdown(f"**{q}**")
                    st.slider(
                        " ",
                        min_value=1, max_value=3, step=1,
                        value=int(st.session_state.get(f"slider_{idx}", 2)),
                        key=f"slider_{idx}",
                        disabled=not st.session_state.habeas_aceptado,
                    )
                    st.markdown("<div class='hint'>1=No · 2=Parcialmente · 3=Sí</div>", unsafe_allow_html=True)

        # Botones utilitarios (opcionales)
        b1, b2, b3 = st.columns([1, 1, 1])
        with b1:
            if st.button("Poner todo en 2", use_container_width=True):
                for i in range(len(df_form)):
                    st.session_state[f"slider_{i}"] = 2
                st.rerun()
        with b2:
            if st.button("Poner todo en 1", use_container_width=True):
                for i in range(len(df_form)):
                    st.session_state[f"slider_{i}"] = 1
                st.rerun()
        with b3:
            if st.button("Poner todo en 3", use_container_width=True):
                for i in range(len(df_form)):
                    st.session_state[f"slider_{i}"] = 3
                st.rerun()

# =============================
# DF ACTUAL (siempre desde session_state)
# =============================
df_calc = df_form.copy()
for i in range(len(df_calc)):
    df_calc.at[df_calc.index[i], "Calificación"] = float(st.session_state.get(f"slider_{i}", 2))
df_calc["Calificación"] = df_calc["Calificación"].astype(float)

# =============================
# DASHBOARD DE BURBUJAS (TIEMPO REAL)
# =============================
with right:
    st.markdown("## Dashboard (burbujas)")

    if not st.session_state.habeas_aceptado:
        st.warning("El dashboard se activará cuando aceptes Habeas Data.")
    else:
        # Controles del dashboard
        mode = st.radio(
            "Vista",
            options=["Por pregunta (todas las respuestas)", "Por categoría (promedios)"],
            horizontal=True,
            index=0,
        )

        if mode == "Por categoría (promedios)":
            radar_df = (
                df_calc.groupby("Categoría", dropna=False)["Calificación"]
                .agg(n="count", promedio="mean")
                .reset_index()
            )
            radar_df["promedio"] = radar_df["promedio"].round(2)

            fig = go.Figure()
            fig.add_trace(
                go.Scatter(
                    x=radar_df["Categoría"].astype(str),
                    y=radar_df["promedio"],
                    mode="markers+text",
                    text=radar_df["promedio"].astype(str),
                    textposition="top center",
                    marker=dict(
                        size=(radar_df["n"] * 6).clip(14, 60),
                        sizemode="diameter",
                        color=radar_df["promedio"],
                        colorscale="Viridis",
                        showscale=True,
                        line=dict(width=1, color="rgba(255,255,255,0.35)"),
                        opacity=0.9,
                    ),
                    hovertemplate="<b>%{x}</b><br>Promedio: %{y:.2f}<br>Preguntas: %{marker.size}<extra></extra>",
                )
            )
            fig.update_layout(
                height=520,
                margin=dict(t=30, b=30, l=20, r=20),
                xaxis=dict(title="Categoría"),
                yaxis=dict(title="Promedio (1–3)", range=[0.8, 3.2], dtick=0.5),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(size=14, color="white"),
            )
            st.plotly_chart(fig, use_container_width=True, theme=None)

            # Tabla resumen compacta
            st.markdown("### Resumen por categoría")
            st.dataframe(
                radar_df.rename(columns={"n": "Preguntas", "promedio": "Promedio"}),
                use_container_width=True,
                hide_index=True,
            )

        else:
            # --- Por pregunta: burbujas con jitter horizontal por categoría ---
            cats = df_calc["Categoría"].astype(str).fillna("Sin categoría")
            unique_cats = list(dict.fromkeys(cats.tolist()))
            cat_to_x = {c: i for i, c in enumerate(unique_cats)}

            # posición X = índice de categoría + offset dentro de la categoría
            df_plot = df_calc.copy()
            df_plot["_cat"] = df_plot["Categoría"].astype(str).fillna("Sin categoría")
            df_plot["_x_base"] = df_plot["_cat"].map(cat_to_x).astype(float)

            # offset determinístico por orden dentro de cada categoría (evita que se apilen)
            df_plot["_ord"] = df_plot.groupby("_cat").cumcount()
            df_plot["_cnt"] = df_plot.groupby("_cat")["_ord"].transform("max").replace(0, 1)
            df_plot["_offset"] = (df_plot["_ord"] / df_plot["_cnt"] - 0.5) * 0.7  # [-0.35, +0.35]
            df_plot["_x"] = df_plot["_x_base"] + df_plot["_offset"]

            # tamaño según calificación (más alto => burbuja más grande)
            df_plot["_size"] = (12 + df_plot["Calificación"] * 10).clip(16, 48)

            fig = go.Figure()
            fig.add_trace(
                go.Scatter(
                    x=df_plot["_x"],
                    y=df_plot["Calificación"],
                    mode="markers",
                    marker=dict(
                        size=df_plot["_size"],
                        color=df_plot["Calificación"],
                        colorscale="Viridis",
                        showscale=True,
                        line=dict(width=1, color="rgba(255,255,255,0.35)"),
                        opacity=0.9,
                    ),
                    customdata=np.stack([df_plot["_cat"], df_plot["Pregunta"]], axis=-1),
                    hovertemplate="<b>%{customdata[0]}</b><br>%{customdata[1]}<br>Calificación: %{y:.0f}<extra></extra>",
                )
            )

            fig.update_layout(
                height=560,
                margin=dict(t=30, b=40, l=20, r=20),
                xaxis=dict(
                    title="Categoría",
                    tickmode="array",
                    tickvals=list(cat_to_x.values()),
                    ticktext=unique_cats,
                    range=[-0.8, max(cat_to_x.values()) + 0.8 if unique_cats else 1],
                ),
                yaxis=dict(title="Calificación (1–3)", range=[0.8, 3.2], dtick=1),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(size=14, color="white"),
            )
            st.plotly_chart(fig, use_container_width=True, theme=None)

            st.markdown("### Respuestas (tabla)")
            st.dataframe(
                df_calc[["Categoría", "Pregunta", "Calificación"]],
                use_container_width=True,
                hide_index=True,
            )

# === Footer brand ===
if b64_logo_bottom:
    st.markdown(
        f"""
        <div style='display: flex; justify-content: center; align-items: center; margin-top: 40px; margin-bottom: 10px;'>
            <img src="data:image/png;base64,{b64_logo_bottom}" width="96" height="69"/>
        </div>
        """,
        unsafe_allow_html=True,
    )
