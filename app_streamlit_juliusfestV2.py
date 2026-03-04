import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np
import time

st.set_page_config(page_title="Stand Interactivo", layout="wide")

# Estilo para ocultar menús de Streamlit y centrar el foco en el gráfico
st.markdown("""<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;}</style>""", unsafe_allow_html=True)

# 1. ESTADO DE LA SESIÓN (Simula nuestra base de datos real)
if 'db' not in st.session_state:
    # Datos iniciales: 5 puntos de referencia
    st.session_state.db = pd.DataFrame({
        'ID': range(5),
        'Nombre': [f"Ref {i}" for i in range(5)],
        'Innovacion': np.random.uniform(1, 5, 5),
        'Presupuesto': np.random.uniform(1, 5, 5),
        'Sostenibilidad': np.random.uniform(1, 5, 5),
        'Frame': [0]*5  # El frame inicial
    })

def get_cluster(row):
    if row['Innovacion'] > 3.5: return 'Estratégico (A)'
    if row['Presupuesto'] > 3.5: return 'Operativo (B)'
    return 'Exploratorio (C)'

# 2. BUCLE DE ACTUALIZACIÓN EN VIVO
placeholder = st.empty()

while True:
    # SIMULACIÓN: Llega un nuevo cliente cada ciclo
    new_id = len(st.session_state.db)
    new_row = {
        'ID': new_id,
        'Nombre': f"Invitado_{new_id}",
        'Innovacion': np.random.uniform(1, 5),
        'Presupuesto': np.random.uniform(1, 5),
        'Sostenibilidad': np.random.uniform(1, 5),
        'Frame': new_id  # Cada nuevo ID es un nuevo paso en la animación
    }
    
    # Añadimos el nuevo registro a la base de datos local
    st.session_state.db = pd.concat([st.session_state.db, pd.DataFrame([new_row])], ignore_index=True)
    st.session_state.db['Categoria'] = st.session_state.db.apply(get_cluster, axis=1)

    # 3. CREACIÓN DEL GRÁFICO ANIMADO
    # 'animation_frame' hace que los puntos se muevan entre estados
    fig = px.scatter(
        st.session_state.db,
        x="Innovacion",
        y="Presupuesto",
        size="Sostenibilidad",
        color="Categoria",
        animation_frame="Frame", # LA CLAVE: Crea la secuencia de movimiento
        hover_name="Nombre",
        range_x=[0, 6], 
        range_y=[0, 6],
        size_max=50,
        color_discrete_map={
            "Estratégico (A)": "#00d4ff", 
            "Operativo (B)": "#ff0070",
            "Exploratorio (C)": "#ccff00"
        },
        template="plotly_dark"
    )

    # Configuración de la velocidad de la animación
    fig.layout.updatemenus[0].buttons[0].args[1]['frame']['duration'] = 800
    fig.layout.updatemenus[0].buttons[0].args[1]['transition']['duration'] = 600
    
    # Estética del Stand
    fig.update_layout(
        height=800,
        margin=dict(l=20, r=20, t=20, b=20),
        showlegend=True,
        legend=dict(font=dict(size=18), yanchor="top", y=0.99, xanchor="left", x=0.01)
    )

    with placeholder.container():
        st.plotly_chart(fig, use_container_width=True)
        st.write(f"✨ Total de registros: {len(st.session_state.db)}")

    time.sleep(4) # Tiempo de espera para que la gente vea su burbuja
