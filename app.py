import streamlit as st
import pandas as pd
import glob
import os

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Control de Avance", layout="wide")

st.title("📊 Dashboard de Avance de Proyectos")
st.subheader("Información consolidada de múltiples fuentes de Excel")

# 2. FUNCIÓN PARA CARGAR, LIMPIAR Y CONSOLIDAR LOS EXCEL
@st.cache_data
def cargar_datos():
    archivos_excel = glob.glob("*.xlsx") 
    
    if not archivos_excel:
        return None

    lista_df = []
    for archivo in archivos_excel:
        df = pd.read_excel(archivo)
        
        # Limpieza de columnas para evitar duplicados
        df.columns = df.columns.str.strip().str.capitalize()
        
        df['Origen'] = os.path.basename(archivo)
        lista_df.append(df)
    
    df_final = pd.concat(lista_df, ignore_index=True)
    
    # Corrección automática si Excel guardó los porcentajes como decimales (0.5 en vez de 50)
    if df_final['Porcentaje'].mean() <= 1.0:
        df_final['Porcentaje'] = df_final['Porcentaje'] * 100
        
    return df_final

df = cargar_datos()

# 3. CONSTRUCCIÓN DE LA INTERFAZ
if df is not None:
    
    # -----------------------------------------------------------------
    # >>> NUEVA LÓGICA: AVANCE REAL POR CHECKLIST DE TAREAS <<<
    # -----------------------------------------------------------------
    total_tareas_proyecto = len(df)
    
    # Contamos cuántas filas tienen el progreso al 100%
    tareas_completadas = len(df[df['Porcentaje'] >= 100])
    
    # Calculamos el porcentaje real del proyecto
    if total_tareas_proyecto > 0:
        avance_real_proyecto = (tareas_completadas / total_tareas_proyecto) * 100
    else:
        avance_real_proyecto = 0.0
    
    # Mostramos las tarjetas con la nueva lógica intuitiva
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            label="Progreso Real del Proyecto", 
            value=f"{avance_real_proyecto:.2f}%",
            help="Porcentaje de tareas totales que ya están al 100%"
        )
    with col2:
        st.metric(
            label="Tareas Listas", 
            value=f"{tareas_completadas} / {total_tareas_proyecto}"
        )
    with col3:
        st.metric(
            label="Total de Integrantes", 
            value=df['Responsable'].nunique()
        )

    st.markdown("---")

    # 4. FILTROS EN LA BARRA LATERAL
    st.sidebar.header("Filtros")
    usuarios = st.sidebar.multiselect(
        "Selecciona los integrantes para filtrar los gráficos y la tabla:",
        options=df['Responsable'].unique(),
        default=df['Responsable'].unique()
    )
    
    df_filtrado = df[df['Responsable'].isin(usuarios)]

    # 5. GRÁFICO DE BARRAS (Muestra el promedio de avance que lleva cada uno)
    st.write("### 👥 Avance Promedio por Integrante")
    avance_grafico = df_filtrado.groupby('Responsable')['Porcentaje'].mean().reset_index()
    st.bar_chart(data=avance_grafico, x='Responsable', y='Porcentaje')

    # 6. TABLA DE DATOS DETALLADA
    st.write("### 📄 Detalle de las Tareas")
    st.dataframe(df_filtrado, use_container_width=True)

else:
    st.warning("⚠️ No se encontraron archivos de Excel (.xlsx) en el repositorio. Sube tus archivos para activar el Dashboard.")
    
