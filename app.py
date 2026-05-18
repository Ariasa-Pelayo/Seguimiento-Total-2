import streamlit as st
import pandas as pd
import glob
import os

st.set_page_config(page_title="Control de Avance", layout="wide")
st.title("📊 Dashboard de Avance de Proyectos")
st.subheader("Información consolidada de múltiples fuentes de Excel")

# --- FUNCIÓN CORREGIDA PARA CONFIGURAR Y CARGAR DATOS ---
@st.cache_data
def cargar_datos():
    archivos_excel = glob.glob("*.xlsx") 
    
    if not archivos_excel:
        return None

    lista_df = []
    for archivo in archivos_excel:
        df = pd.read_excel(archivo)
        
        # SOLUCIÓN ERROR 2: Limpiamos los nombres de las columnas
        # Quita espacios al principio/final y convierte la primera letra en mayúscula
        df.columns = df.columns.str.strip().str.capitalize()
        
        # Añadimos el origen
        df['Origen'] = os.path.basename(archivo)
        lista_df.append(df)
    
    df_final = pd.concat(lista_df, ignore_index=True)
    
    # SOLUCIÓN ERROR 1: Aseguramos que el porcentaje esté en base 100
    # Si el promedio general da menos de 1.0, significa que Excel lo guardó como decimal (0.5 en vez de 50)
    if df_final['Porcentaje'].mean() <= 1.0:
        df_final['Porcentaje'] = df_final['Porcentaje'] * 100
        
    return df_final

df = cargar_datos()

if df is not None:
    # Asegurar que las columnas clave se llamen exactamente como esperamos tras el .capitalize()
    # 'Responsable', 'Tarea', 'Porcentaje', 'Fecha'
    
    # MÈTRICAS GENERALES
    avance_general = df['Porcentaje'].mean() # Ya viene corregido en base 100
    
    col1, col2 = st.columns(2)
    with col1:
        # Mostramos el porcentaje correcto
        st.metric(label="Progreso Total del Proyecto", value=f"{avance_general:.2f}%")
    with col2:
        st.metric(label="Total de Integrantes", value=df['Responsable'].nunique())

    st.markdown("---")

    # FILTROS
    st.sidebar.header("Filtros")
    usuarios = st.sidebar.multiselect(
        "Selecciona los integrantes:",
        options=df['Responsable'].unique(),
        default=df['Responsable'].unique()
    )
    
    df_filtrado = df[df['Responsable'].isin(usuarios)]

    # VISUALIZACIÓN
    st.write("### 👥 Avance por Integrante")
    avance_por_persona = df_filtrado.groupby('Responsable')['Porcentaje'].mean().reset_index()
    st.bar_chart(data=avance_por_persona, x='Responsable', y='Porcentaje')

    # TABLA DETALLADA (Ahora mostrará una sola columna Tarea limpia)
    st.write("### 📄 Detalle de las Tareas")
    st.dataframe(df_filtrado, use_container_width=True)

else:
    st.warning("⚠️ No se encontraron archivos de Excel (.xlsx) en el repositorio.")
