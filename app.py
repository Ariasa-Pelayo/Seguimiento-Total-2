import streamlit as st
import pandas as pd
import glob
import os

# 1. CONFIGURACIÓN DE LA PÁGINA (Debe ser la primera instrucción de Streamlit)
st.set_page_config(page_title="Control de Avance", layout="wide")

st.title("📊 Dashboard de Avance de Proyectos")
st.subheader("Información consolidada de múltiples fuentes de Excel")

# 2. FUNCIÓN PARA CARGAR, LIMPIAR Y CONSOLIDAR LOS EXCEL
@st.cache_data # Optimiza la app para que no lea los Excel en cada clic
def cargar_datos():
    # Busca todos los archivos .xlsx en la carpeta actual del repositorio
    archivos_excel = glob.glob("*.xlsx") 
    
    if not archivos_excel:
        return None

    lista_df = []
    for archivo in archivos_excel:
        # Leer el archivo Excel actual
        df = pd.read_excel(archivo)
        
        # CORRECCIÓN DE COLUMNAS DUPLICADAS:
        # Borra espacios fantasmas a los lados y pone la primera letra en mayúscula.
        # Esto unifica 'tarea', 'Tarea ' y 'TAREA' en una sola columna 'Tarea'.
        df.columns = df.columns.str.strip().str.capitalize()
        
        # Guardamos el nombre del archivo de origen para saber de quién viene
        df['Origen'] = os.path.basename(archivo)
        lista_df.append(df)
    
    # Consolidamos todos los archivos Excel en un único DataFrame de Pandas
    df_final = pd.concat(lista_df, ignore_index=True)
    
    # CORRECCIÓN DE PORCENTAJE BAJO:
    # Si el promedio es menor o igual a 1.0, Excel guardó los datos como decimales (ej: 0.50 en vez de 50).
    # Multiplicamos toda la columna por 100 para estandarizar a base 100.
    if df_final['Porcentaje'].mean() <= 1.0:
        df_final['Porcentaje'] = df_final['Porcentaje'] * 100
        
    return df_final

# Ejecutamos la función de carga de datos
df = cargar_datos()

# 3. CONSTRUCCIÓN DE LA INTERFAZ SI EXISTEN DATOS
if df is not None:
    
    # --- MÉTRICAS GENERALES (CORREGIDO CON LA OPCIÓN A) ---
    # Paso 1: Calculamos el progreso promedio real de cada trabajador de forma individual
    progreso_por_persona = df['Porcentaje'].groupby(df['Responsable']).mean()
    
    # Paso 2: Promediamos los totales de cada uno para obtener el avance equitativo del proyecto
    avance_general = progreso_por_persona.mean()
    
    # Mostramos las tarjetas con los resultados correctos en la pantalla
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Progreso Total del Proyecto (Promedio Equipo)", value=f"{avance_general:.2f}%")
    with col2:
        st.metric(label="Total de Integrantes", value=df['Responsable'].nunique())

    st.markdown("---")

    # 4. FILTROS EN LA BARRA LATERAL
    st.sidebar.header("Filtros")
    usuarios = st.sidebar.multiselect(
        "Selecciona los integrantes para filtrar los gráficos y la tabla:",
        options=df['Responsable'].unique(),
        default=df['Responsable'].unique()
    )
    
    # Filtrar el dataframe según la selección del usuario
    df_filtrado = df[df['Responsable'].isin(usuarios)]

    # 5. GRÁFICO DE BARRAS
    st.write("### 👥 Avance por Integrante")
    
    # Agrupamos los datos filtrados para mostrar el avance individual de cada persona seleccionada
    avance_grafico = df_filtrado.groupby('Responsable')['Porcentaje'].mean().reset_index()
    
    # Dibujar gráfico de barras nativo de Streamlit
    st.bar_chart(data=avance_grafico, x='Responsable', y='Porcentaje')

    # 6. TABLA DE DATOS DETALLADA (Limpia y sin columnas duplicadas)
    st.write("### 📄 Detalle de las Tareas")
    st.dataframe(df_filtrado, use_container_width=True)

else:
    # Mensaje de aviso en caso de que no haya archivos en el repositorio de GitHub
    st.warning("⚠️ No se encontraron archivos de Excel (.xlsx) en el repositorio. Sube tus archivos para activar el Dashboard.")
