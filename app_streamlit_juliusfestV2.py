import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import time

# =========================
# CONFIG
# =========================
st.set_page_config(
    page_title="Live Booth Analytics WOW",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =========================
# ESTILO GLOBAL WOW
# =========================
st.markdown("""
<style>
html, body, [class*="css"] {
    font-family: "Inter", "Segoe UI", sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at 15% 20%, rgba(0,242,255,0.16), transparent 26%),
        radial-gradient(circle at 85% 18%, rgba(112,0,255,0.15), transparent 28%),
        radial-gradient(circle at 50% 88%, rgba(191,255,0,0.10), transparent 24%),
        linear-gradient(180deg, #030303 0%, #050505 45%, #090909 100%);
    color: white;
}

header, footer {
    visibility: hidden;
}

.block-container {
    padding-top: 1.2rem;
    padding-bottom: 0.5rem;
    max-width: 100%;
}

.wow-title {
    text-align: center;
    font-size: 52px;
    font-weight: 800;
    letter-spacing: 1px;
    color: white;
    margin-bottom: 0.1rem;
    text-shadow:
        0 0 14px rgba(255,255,255,0.10),
        0 0 26px rgba(0,242,255,0.10);
}

.wow-subtitle {
    text-align: center;
    font-size: 18px;
    color: rgba(255,255,255,0.72);
    letter-spacing: 0.2px;
    margin-bottom: 1.2rem;
}

[data-testid="stMetricValue"] {
    font-size: 88px !important;
    color: #00f2ff !important;
    text-align: center;
    text-shadow:
        0 0 10px rgba(0,242,255,0.40),
        0 0 22px rgba(0,242,255,0.28),
        0 0 34px rgba(0,242,255,0.18);
}

[data-testid="stMetricLabel"] {
    font-size: 22px !important;
    color: rgba(255,255,255,0.92) !important;
    text-align: center;
    letter-spacing: 1.4px;
}

[data-testid="stHorizontalBlock"] {
    align-items: center;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="wow-title">LIVE BOOTH INTELLIGENCE</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="wow-subtitle">Dinámica de participantes en tiempo real · Visual premium para pantalla de evento</div>',
    unsafe_allow_html=True
)

# =========================
# ESTADO
# =========================
MAX_BUBBLES = 20

CATEGORY_COLORS = {
    '🚀 LÍDERES': '#00f2ff',
    '💎 PREMIUM': '#7000ff',
    '🌀 ESTRATEGAS': '#bfff00'
}

def get_cluster_name(row):
    if row['Innovacion'] > 3.85:
        return '🚀 LÍDERES'
    elif row['Presupuesto'] > 3.85:
        return '💎 PREMIUM'
    return '🌀 ESTRATEGAS'

if 'db' not in st.session_state:
    n_inicial = 7
    base_df = pd.DataFrame({
        'Nombre': [f'User_{i+1}' for i in range(n_inicial)],
        'Innovacion': np.random.uniform(1.2, 4.8, n_inicial),
        'Presupuesto': np.random.uniform(1.2, 4.8, n_inicial),
        'Sostenibilidad': np.random.uniform(2.0, 4.9, n_inicial),
    })
    base_df['spawn_time'] = time.time() - np.random.uniform(1.0, 4.0, n_inicial)
    st.session_state.db = base_df

# =========================
# LAYOUT
# =========================
top_left, top_center, top_right = st.columns([1, 2.2, 1])

with top_center:
    metric_placeholder = st.empty()

chart_placeholder = st.empty()

# =========================
# LOOP PRINCIPAL
# =========================
while True:
    now = time.time()
    df = st.session_state.db.copy()

    # -------------------------
    # Movimiento orgánico premium
    # -------------------------
    idx = np.arange(len(df))

    df['Innovacion_anim'] = (
        df['Innovacion']
        + np.sin(now * 0.42 + idx * 0.95) * 0.035
        + np.sin(now * 0.14 + idx * 1.77) * 0.012
    )

    df['Presupuesto_anim'] = (
        df['Presupuesto']
        + np.cos(now * 0.42 + idx * 0.95) * 0.035
        + np.cos(now * 0.14 + idx * 1.77) * 0.012
    )

    df['Innovacion_anim'] = df['Innovacion_anim'].clip(0.9, 5.1)
    df['Presupuesto_anim'] = df['Presupuesto_anim'].clip(0.9, 5.1)

    # -------------------------
    # Categorías
    # -------------------------
    df['Categoria'] = df.apply(get_cluster_name, axis=1)

    # -------------------------
    # Entrada lenta de burbujas
    # -------------------------
    if len(st.session_state.db) < MAX_BUBBLES and np.random.random() > 0.994:
        new_row = pd.DataFrame({
            'Nombre': [f'Guest_{len(st.session_state.db) + 1}'],
            'Innovacion': [np.random.uniform(1.15, 4.85)],
            'Presupuesto': [np.random.uniform(1.15, 4.85)],
            'Sostenibilidad': [np.random.uniform(2.2, 5.0)],
            'spawn_time': [now]
        })
        st.session_state.db = pd.concat([st.session_state.db, new_row], ignore_index=True)
        df = st.session_state.db.copy()
        idx = np.arange(len(df))

        df['Innovacion_anim'] = (
            df['Innovacion']
            + np.sin(now * 0.42 + idx * 0.95) * 0.035
            + np.sin(now * 0.14 + idx * 1.77) * 0.012
        )
        df['Presupuesto_anim'] = (
            df['Presupuesto']
            + np.cos(now * 0.42 + idx * 0.95) * 0.035
            + np.cos(now * 0.14 + idx * 1.77) * 0.012
        )
        df['Innovacion_anim'] = df['Innovacion_anim'].clip(0.9, 5.1)
        df['Presupuesto_anim'] = df['Presupuesto_anim'].clip(0.9, 5.1)
        df['Categoria'] = df.apply(get_cluster_name, axis=1)

    # -------------------------
    # Animación de aparición (grow-in)
    # -------------------------
    age = now - df['spawn_time']
    growth = np.clip(age / 2.2, 0.18, 1.0)
    bubble_size = (df['Sostenibilidad'] * 20) * growth + 8

    # -------------------------
    # Etiquetas: solo algunas grandes
    # -------------------------
    labels = []
    threshold = df['Sostenibilidad'].quantile(0.62) if len(df) > 3 else 0
    for _, row in df.iterrows():
        labels.append(row['Nombre'] if row['Sostenibilidad'] >= threshold else "")

    # -------------------------
    # Contador
    # -------------------------
    metric_placeholder.metric(
        label="PARTICIPANTES EN VIVO",
        value=len(df)
    )

    # =========================
    # FIGURA WOW
    # =========================
    fig = go.Figure()

    # Capa glow grande
    for cat, color in CATEGORY_COLORS.items():
        subset = df[df['Categoria'] == cat]
        if len(subset) == 0:
            continue

        glow_sizes = ((subset['Sostenibilidad'] * 20) * np.clip((now - subset['spawn_time']) / 2.2, 0.18, 1.0) + 8) * 1.8

        fig.add_trace(go.Scatter(
            x=subset['Innovacion_anim'],
            y=subset['Presupuesto_anim'],
            mode='markers',
            hoverinfo='skip',
            showlegend=False,
            marker=dict(
                size=glow_sizes,
                color=color,
                opacity=0.10,
                line=dict(width=0)
            )
        ))

    # Capa glow media
    for cat, color in CATEGORY_COLORS.items():
        subset = df[df['Categoria'] == cat]
        if len(subset) == 0:
            continue

        glow_sizes = ((subset['Sostenibilidad'] * 20) * np.clip((now - subset['spawn_time']) / 2.2, 0.18, 1.0) + 8) * 1.35

        fig.add_trace(go.Scatter(
            x=subset['Innovacion_anim'],
            y=subset['Presupuesto_anim'],
            mode='markers',
            hoverinfo='skip',
            showlegend=False,
            marker=dict(
                size=glow_sizes,
                color=color,
                opacity=0.16,
                line=dict(width=0)
            )
        ))

    # Capa principal por categoría
    for cat, color in CATEGORY_COLORS.items():
        subset = df[df['Categoria'] == cat].copy()
        if len(subset) == 0:
            continue

        sub_labels = [labels[i] for i in subset.index]

        fig.add_trace(go.Scatter(
            x=subset['Innovacion_anim'],
            y=subset['Presupuesto_anim'],
            mode='markers+text',
            name=cat,
            text=sub_labels,
            textposition='top center',
            textfont=dict(
                size=14,
                color='rgba(255,255,255,0.92)'
            ),
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "Innovación: %{customdata[1]:.2f}<br>"
                "Presupuesto: %{customdata[2]:.2f}<br>"
                "Sostenibilidad: %{customdata[3]:.2f}<br>"
                "Categoría: %{customdata[4]}<extra></extra>"
            ),
            customdata=np.stack([
                subset['Nombre'],
                subset['Innovacion'],
                subset['Presupuesto'],
                subset['Sostenibilidad'],
                subset['Categoria']
            ], axis=-1),
            marker=dict(
                size=bubble_size.loc[subset.index],
                color=color,
                opacity=0.90,
                line=dict(
                    width=2,
                    color='rgba(255,255,255,0.95)'
                )
            )
        ))

    # -------------------------
    # Layout visual
    # -------------------------
    fig.update_layout(
        height=780,
        margin=dict(l=10, r=10, t=20, b=10),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=0.01,
            xanchor="center",
            x=0.5,
            font=dict(size=20, color="white"),
            bgcolor='rgba(0,0,0,0)'
        ),
        xaxis=dict(
            range=[0.5, 5.5],
            showgrid=False,
            zeroline=False,
            visible=False
        ),
        yaxis=dict(
            range=[0.5, 5.5],
            showgrid=False,
            zeroline=False,
            visible=False
        ),
        transition=dict(
            duration=950,
            easing='cubic-in-out'
        ),
        hoverlabel=dict(
            bgcolor="rgba(20,20,20,0.95)",
            font_size=15,
            font_color="white"
        )
    )

    chart_placeholder.plotly_chart(
        fig,
        use_container_width=True,
        config={'displayModeBar': False}
    )

    # Suave y estable
    time.sleep(0.09)
