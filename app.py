import streamlit as st
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="ChatGPT & Programación", page_icon="🤖", layout="wide")

st.title("🤖 ChatGPT & Aprendizaje de Programación")
st.write("Análisis de datos científicos de Scopus - Grupo 1")

# Intentar cargar la base de datos automáticamente
try:
    df = pd.read_csv("dataset_grupo1.csv")
    st.success("¡Base de datos 'dataset_grupo1.csv' cargada con éxito desde GitHub!")
    
    # Mostrar métricas básicas
    st.header("📊 Resumen de los Datos")
    col1, col2 = st.columns(2)
    col1.metric("Total de Artículos", len(df))
    col2.metric("Columnas Detectadas", len(df.columns))
    
    # Mostrar la tabla con los datos
    st.header("📋 Explorador de Datos")
    st.dataframe(df.head(10)) # Muestra las primeras 10 filas
    
except FileNotFoundError:
    st.error("Aviso: El archivo 'dataset_grupo1.csv' aún no está en tu repositorio. Por favor, súbelo.")
