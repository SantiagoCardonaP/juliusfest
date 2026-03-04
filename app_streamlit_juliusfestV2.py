import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np
import time

# Configuración de pantalla completa para el stand
st.set_page_config(page_title="Live Data Arena", layout="wide", initial_sidebar_state="collapsed")

# CSS para ocultar todo el ruido de Streamlit y que parezca una app nativa
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .reportview-container .main {color: white; background-color: #050505;}
    </style>
    """, unsafe_allow_html=True)

# 1. INICIALIZACIÓN DE LA BASE DE DATOS EN SESIÓN
if 'db' not in st.session_state:
    # Creamos 15 puntos iniciales
    st.session_state.db = pd.DataFrame({
        'Nombre': [f"User_{i}" for i in range(15)],
        'Innovacion': np.random.uniform(1, 5, 15),
        'Presupuesto': np.random.uniform(1, 5, 15),
        'Sostenibilidad': np.random.uniform(1, 5, 15)
    })

def get_cluster_name(row):
    if row['Innovacion'] > 3.5: return '🚀 INNOVADORES'
    if row['Presupuesto'] > 3.5: return '💰 ESTRATÉGICOS'
    return '🌱 EXPLORADORES'

# 2. BUCLE DE ANIMACIÓN CONTINUA
placeholder = st.empty()

while True:
    df = st.session_state.db.copy()
    
    # --- EFECTO "VIVO" (Jitter) ---
    # Añadimos un pequeño movimiento aleatorio a cada burbuja para que parezca que flotan
    df['Innovacion'] += np.random.uniform(-0.05, 0.05, len(df))
    df['Presupuesto'] += np.random.uniform(-0.05, 0.05, len(df))
    
    # Asignar categorías y colores
    df['Categoria'] = df.apply(get_cluster_name, axis=1)

    # --- LÓGICA DE NUEVO INGRESO ---
    # Simulamos que cada 3 ciclos entra alguien nuevo (Sustituir por lectura de Sheets)
    if np.random.random() > 0.7:
        new_row = pd.DataFrame({
            'Nombre': [f"User_{len(df)}"],
            'Innovacion': [np.random.uniform(1, 5)],
            'Presupuesto': [np.random.uniform(1, 5)],
            'Sostenibilidad': [np.random.uniform(1, 5)]
        })
        st.session_state.db = pd.concat([st.session_state.db, new_row], ignore_index=True)

    # 3. CREACIÓN DEL GRÁFICO (Sin animation_frame para que sea fluido)
    fig = px.scatter(
        df,
        x="Innovacion",
        y="Presupuesto",
        size="Sostenibilidad",
        color="Categoria",
        hover_name="Nombre",
        text="Nombre",
        range_x=[0, 6],
        range_y=[0, 6],
        size_max=45,
        color_discrete_map={
            '🚀 INNOVADORES': '#00f2ff', 
            '💰 ESTRATÉGICOS': '#7000ff',
            '🌱 EXPLORADORES': '#bfff00'
        },
        template="plotly_dark"
    )

    # Ajustes de estilo para máxima visibilidad en monitor
    fig.update_layout(
        height=850,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom", y=1.02,
            xanchor="center", x=0.5,
            font=dict(size=20, color="white")
        ),
        margin=dict(l=0, r=0, t=50, b=0),
        # Quitamos las líneas de cuadrícula para un look más limpio
        xaxis=dict(showgrid=False, zeroline=False, visible=False),
        yaxis=dict(showgrid=False, zeroline=False, visible=False),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    fig.update_traces(
        textposition='top center',
        marker=dict(line=dict(width=2, color='white')), # Borde blanco para resaltar
        selector=dict(mode='markers+text')
    )

    # Renderizado
    with placeholder.container():
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    # Control de velocidad: 0.1 para que el movimiento sea vibrante y constante
    time.sleep(0.1)
