import streamlit as st
import pandas as pd
import glob
import os

# Configuración de la página
st.set_page_config(page_title="Control de Avance", layout="wide")
st.title("📊 Dashboard de Avance de Proyectos")
st.subheader("Información consolidada de múltiples fuentes de Excel")

# 1. FUNCIÓN PARA CARGAR Y CONSOLIDAR DATOS
@st.cache_data # Esto optimiza la app para que no lea los Excel en cada clic
def cargar_datos():
    # Busca todos los archivos .xlsx en la carpeta actual
    archivos_excel = glob.glob("*.xlsx") 
    
    if not archivos_excel:
        return None

    lista_df = []
    for archivo in archivos_excel:
        # Leemos el excel
        df = pd.read_excel(archivo)
        # Añadimos una columna para saber de qué archivo viene (opcional)
        df['Origen'] = os.path.basename(archivo)
        lista_df.append(df)
    
    # Consolidamos todos los Excel en un solo DataFrame
    df_final = pd.concat(lista_df, ignore_index=True)
    return df_final

df = cargar_datos()

if df is not None:
    # --- PROCESAMIENTO DE DATOS ---
    # (Asumiendo que tienes las columnas 'Responsable' y 'Porcentaje')
    # Ajusta los nombres de las columnas según tus archivos reales
    
    # 2. MÉTRICAS GENERALES
    avance_general = df['Porcentaje'].mean() # Promedio de avance total
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Progreso Total del Proyecto", value=f"{avance_general:.2f}%")
    with col2:
        st.metric(label="Total de Integrantes", value=df['Responsable'].nunique())

    st.markdown("---")

    # 3. FILTROS EN LA BARRA LATERAL
    st.sidebar.header("Filtros")
    usuarios = st.sidebar.multiselect(
        "Selecciona los integrantes:",
        options=df['Responsable'].unique(),
        default=df['Responsable'].unique()
    )
    
    # Filtrar el dataframe
    df_filtrado = df[df['Responsable'].isin(usuarios)]

    # 4. VISUALIZACIÓN DE RESULTADOS
    st.write("### 👥 Avance por Integrante")
    
    # Agrupamos para ver el avance promedio de cada persona
    avance_por_persona = df_filtrado.groupby('Responsable')['Porcentaje'].mean().reset_index()
    
    # Mostramos un gráfico de barras
    st.bar_chart(data=avance_por_persona, x='Responsable', y='Porcentaje')

    # 5. TABLA DE DATOS DETALLADA
    st.write("### 📄 Detalle de las Tareas")
    st.dataframe(df_filtrado, use_container_width=True)

else:
    st.warning("⚠️ No se encontraron archivos de Excel (.xlsx) en el repositorio. Sube algunos para empezar.")
