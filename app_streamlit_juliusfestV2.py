import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np
import time

# Configuración general
st.set_page_config(
    page_title="Live Booth Analytics",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estética general tipo evento / feria tecnológica
st.markdown("""
    <style>
    html, body, [class*="css"] {
        font-family: 'Arial', sans-serif;
    }

    .main {
        background:
            radial-gradient(circle at top left, rgba(0,242,255,0.10), transparent 30%),
            radial-gradient(circle at top right, rgba(112,0,255,0.10), transparent 30%),
            radial-gradient(circle at bottom center, rgba(191,255,0,0.08), transparent 30%),
            #050505;
    }

    header, footer {
        visibility: hidden;
    }

    [data-testid="stMetricValue"] {
        font-size: 92px !important;
        color: #00f2ff !important;
        text-align: center;
        text-shadow: 0 0 15px rgba(0, 242, 255, 0.7);
    }

    [data-testid="stMetricLabel"] {
        font-size: 26px !important;
        color: #ffffff !important;
        text-align: center;
        letter-spacing: 1px;
    }

    [data-testid="stHorizontalBlock"] {
        align-items: center;
    }
    </style>
""", unsafe_allow_html=True)

# -------- Estado inicial --------
if 'db' not in st.session_state:
    n_inicial = 8
    st.session_state.db = pd.DataFrame({
        'Nombre': [f"User_{i+1}" for i in range(n_inicial)],
        'Innovacion': np.random.uniform(1.2, 4.8, n_inicial),
        'Presupuesto': np.random.uniform(1.2, 4.8, n_inicial),
        'Sostenibilidad': np.random.uniform(1.8, 4.8, n_inicial)
    })

def get_cluster_name(row):
    if row['Innovacion'] > 3.8:
        return '🚀 LÍDERES'
    elif row['Presupuesto'] > 3.8:
        return '💎 PREMIUM'
    return '🌀 ESTRATEGAS'

# Contenedores visuales
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    metric_placeholder = st.empty()

chart_placeholder = st.empty()

# -------- Loop principal --------
while True:
    df = st.session_state.db.copy()
    t = time.time()

    # Movimiento orgánico, suave y atractivo
    df['Innovacion'] += np.sin(t * 0.55 + df.index * 0.90) * 0.025
    df['Presupuesto'] += np.cos(t * 0.55 + df.index * 0.90) * 0.025

    # Micro-oscilación secundaria para dar sensación más viva
    df['Innovacion'] += np.sin(t * 0.18 + df.index * 1.70) * 0.010
    df['Presupuesto'] += np.cos(t * 0.18 + df.index * 1.70) * 0.010

    # Limitar a rango visual
    df['Innovacion'] = df['Innovacion'].clip(0.8, 5.2)
    df['Presupuesto'] = df['Presupuesto'].clip(0.8, 5.2)

    df['Categoria'] = df.apply(get_cluster_name, axis=1)

    # Aparición lenta de nuevas burbujas, limitada a 20
    if len(st.session_state.db) < 20 and np.random.random() > 0.992:
        new_row = pd.DataFrame({
            'Nombre': [f"Guest_{len(st.session_state.db) + 1}"],
            'Innovacion': [np.random.uniform(1.1, 4.9)],
            'Presupuesto': [np.random.uniform(1.1, 4.9)],
            'Sostenibilidad': [np.random.uniform(2.0, 5.0)]
        })
        st.session_state.db = pd.concat([st.session_state.db, new_row], ignore_index=True)

    metric_placeholder.metric(
        label="PARTICIPANTES EN VIVO",
        value=len(df)
    )

    # Capa principal
    fig = px.scatter(
        df,
        x="Innovacion",
        y="Presupuesto",
        size="Sostenibilidad",
        color="Categoria",
        hover_name="Nombre",
        text="Nombre",
        range_x=[0.5, 5.5],
        range_y=[0.5, 5.5],
        size_max=85,
        color_discrete_map={
            '🚀 LÍDERES': '#00f2ff',
            '💎 PREMIUM': '#7000ff',
            '🌀 ESTRATEGAS': '#bfff00'
        },
        template="plotly_dark"
    )

    # Glow visual simulando profundidad
    fig.update_traces(
        textposition='top center',
        textfont=dict(size=14, color='white'),
        marker=dict(
            line=dict(width=2, color='rgba(255,255,255,0.95)'),
            opacity=0.88
        )
    )

    fig.update_layout(
        height=760,
        margin=dict(l=0, r=0, t=10, b=0),
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
            showgrid=False,
            zeroline=False,
            visible=False
        ),
        yaxis=dict(
            showgrid=False,
            zeroline=False,
            visible=False
        ),
        transition=dict(
            duration=900,
            easing='cubic-in-out'
        )
    )

    chart_placeholder.plotly_chart(
        fig,
        use_container_width=True,
        config={'displayModeBar': False}
    )

    # Refresco un poco más lento para que se sienta más premium
    time.sleep(0.08)
