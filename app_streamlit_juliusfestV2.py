import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np
import time

# Configuración de la página para que se vea bien en el monitor del stand
st.set_page_config(page_title="Data Arena - Stand Interactiva", layout="wide")

st.title("🚀 Visualización de Clientes en Tiempo Real")
st.write("Escanea el QR y mira cómo aparece tu burbuja en el cluster correspondiente.")

# 1. FUNCIÓN PARA SIMULAR DATOS (Sustituir luego por tu Google Sheets/API)
def get_data():
    # Creamos 20 clientes iniciales con escalas 1-5
    n_clientes = 20
    data = {
        'ID': range(n_clientes),
        'Nombre': [f"Cliente {i}" for i in range(n_clientes)],
        'Innovacion': np.random.randint(1, 6, n_clientes),
        'Presupuesto': np.random.randint(1, 6, n_clientes),
        'Sostenibilidad': np.random.randint(1, 6, n_clientes),
    }
    df = pd.DataFrame(data)
    
    # Lógica de Clusterización Simple
    # Categoría A: Innovadores (Innovacion > 3)
    # Categoría B: Conservadores (Innovacion <= 3 y Presupuesto > 3)
    # Categoría C: Eficientes (Resto)
    def clusterize(row):
        if row['Innovacion'] > 3: return 'Cluster Innovación'
        if row['Presupuesto'] > 3: return 'Cluster Estabilidad'
        return 'Cluster Eficiencia'
    
    df['Categoria'] = df.apply(clusterize, axis=1)
    return df

# 2. INTERFAZ DE STREAMLIT
df = get_data()

# Contenedor para el gráfico (para que se refresque sin parpadear)
placeholder = st.empty()

# Bucle de "Tiempo Real" simulado
while True:
    # Añadimos un "nuevo cliente" aleatorio cada ciclo para ver la animación
    nuevo_cliente = pd.DataFrame({
        'ID': [len(df)],
        'Nombre': [f"Nuevo {len(df)}"],
        'Innovacion': [np.random.randint(1, 6)],
        'Presupuesto': [np.random.randint(1, 6)],
        'Sostenibilidad': [np.random.randint(1, 6)],
    })
    
    # Recalculamos categoría para el nuevo
    def quick_cluster(row):
        if row['Innovacion'] > 3: return 'Cluster Innovación'
        if row['Presupuesto'] > 3: return 'Cluster Estabilidad'
        return 'Cluster Eficiencia'
    
    nuevo_cliente['Categoria'] = nuevo_cliente.apply(quick_cluster, axis=1)
    df = pd.concat([df, nuevo_cliente], ignore_index=True)

    # 3. CREACIÓN DEL GRÁFICO DE BURBUJAS CON PLOTLY
    fig = px.scatter(
        df,
        x="Innovacion",
        y="Presupuesto",
        size="Sostenibilidad", # El tamaño depende del tercer campo
        color="Categoria",
        hover_name="Nombre",
        text="Nombre",
        size_max=40,
        range_x=[0.5, 5.5], # Escala 1-5 fija
        range_y=[0.5, 5.5],
        color_discrete_map={
            "Cluster Innovación": "#00FFCC", # Colores neón para el stand
            "Cluster Estabilidad": "#FF007F",
            "Cluster Eficiencia": "#FFFF00"
        },
        template="plotly_dark" # Fondo oscuro para que resalte en el monitor
    )

    # Ajustes estéticos para que se vea "limpio" en pantalla grande
    fig.update_layout(
        height=700,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    fig.update_traces(textposition='top center')

    # Renderizar en el placeholder
    with placeholder.container():
        st.plotly_chart(fig, use_container_width=True)
    
    # Espera de 3 segundos antes de buscar nuevos datos
    time.sleep(3)