import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np
import time

# Configuración de pantalla de alta visibilidad
st.set_page_config(page_title="Live Booth Analytics", layout="wide", initial_sidebar_state="collapsed")

# CSS para el contador y estética de pantalla de feria
st.markdown("""
    <style>
    [data-testid="stMetricValue"] {
        font-size: 80px !important;
        color: #00f2ff !important;
        text-align: center;
    }
    [data-testid="stMetricLabel"] {
        font-size: 25px !important;
        color: #ffffff !important;
        text-align: center;
    }
    .main { background-color: #050505; }
    header, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# 1. ESTADO DE DATOS
if 'db' not in st.session_state:
    st.session_state.db = pd.DataFrame({
        'Nombre': [f"User_{i}" for i in range(10)],
        'Innovacion': np.random.uniform(1, 5, 10),
        'Presupuesto': np.random.uniform(1, 5, 10),
        'Sostenibilidad': np.random.uniform(1, 5, 10)
    })

def get_cluster_name(row):
    if row['Innovacion'] > 3.5: return '🚀 LÍDERES'
    if row['Presupuesto'] > 3.5: return '💎 PREMIUM'
    return '🌀 ESTRATEGAS'

# 2. INTERFAZ SUPERIOR (Contador)
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    metric_placeholder = st.empty()

# 3. CONTENEDOR DEL GRÁFICO
chart_placeholder = st.empty()

# BUCLE DE ANIMACIÓN
while True:
    df = st.session_state.db.copy()
    
    # EFECTO DE MOVIMIENTO FLUIDO (Ondulación senoidal)
    # En lugar de azar puro, usamos una función de tiempo para un balanceo suave
    t = time.time()
    df['Innovacion'] += np.sin(t + df.index) * 0.04
    df['Presupuesto'] += np.cos(t + df.index) * 0.04
    
    df['Categoria'] = df.apply(get_cluster_name, axis=1)

    # SIMULACIÓN DE ENTRADA (Sustituir por consulta a Google Sheets)
    if np.random.random() > 0.95:
        new_row = pd.DataFrame({
            'Nombre': [f"Guest_{len(df)+1}"],
            'Innovacion': [np.random.uniform(1, 5)],
            'Presupuesto': [np.random.uniform(1, 5)],
            'Sostenibilidad': [np.random.uniform(1, 5)]
        })
        st.session_state.db = pd.concat([st.session_state.db, new_row], ignore_index=True)

    # ACTUALIZAR CONTADOR
    metric_placeholder.metric(label="PARTICIPANTES EN VIVO", value=len(df))

    # 4. GRÁFICO CON TRANSICIONES SUAVIZADAS
    fig = px.scatter(
        df, x="Innovacion", y="Presupuesto", size="Sostenibilidad",
        color="Categoria", hover_name="Nombre", text="Nombre",
        range_x=[0.5, 5.5], range_y=[0.5, 5.5],
        size_max=50,
        color_discrete_map={'🚀 LÍDERES': '#00f2ff', '💎 PREMIUM': '#7000ff', '🌀 ESTRATEGAS': '#bfff00'},
        template="plotly_dark"
    )

    # Deshabilitar animaciones de Plotly para evitar el "salto" de redibujado
    # y manejar la fluidez mediante el tiempo de refresco del bucle
    fig.update_layout(
        height=750,
        margin=dict(l=0, r=0, t=0, b=0),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=0.01, xanchor="center", x=0.5, font=dict(size=20)),
        xaxis=dict(showgrid=False, zeroline=False, visible=False),
        yaxis=dict(showgrid=False, zeroline=False, visible=False),
        transition_duration=300 # Suaviza el movimiento de las burbujas entre frames
    )
    
    fig.update_traces(textposition='top center', marker=dict(line=dict(width=1, color='white')))

    chart_placeholder.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    # Pequeña pausa para controlar la carga del CPU (ajustar según potencia del PC del stand)
    time.sleep(0.05)
