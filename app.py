import streamlit as st
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import plotly.express as px

# Configuración de la página
st.set_page_config(
    page_title="Dashboard ChatGPT y Programación",
    page_icon="🤖",
    layout="wide"
)

# -------------------------------------------------------------
# ESTILOS CSS PERSONALIZADOS (Punto 2: Alto contraste y legibilidad)
# -------------------------------------------------------------
st.markdown("""
<style>
.main-title {
    color: #FF4B4B;
    font-size: 38px;
    font-weight: bold;
    margin-bottom: 5px;
}
.research-box {
    padding: 25px;
    border: 2px solid #FF4B4B;
    border-radius: 12px;
    background-color: #1E293B;
    text-align: center;
    margin-bottom: 20px;
}
.research-title {
    color: #FF4B4B;
    font-size: 18px;
    font-weight: bold;
    margin-bottom: 10px;
    text-transform: uppercase;
    letter-spacing: 1px;
}
.research-text {
    color: #F8FAFC;
    font-size: 22px;
    font-weight: 500;
    line-height: 1.4;
}
.keyword-badge {
    background-color: #065F46;
    color: #A7F3D0;
    padding: 6px 14px;
    border-radius: 20px;
    font-weight: bold;
    font-size: 14px;
    display: inline-block;
    margin: 4px;
    border: 1px solid #047857;
}
</style>
""", unsafe_allow_html=True)

# Título Principal
st.markdown('<div class="main-title">🤖 ChatGPT & Aprendizaje de Programación</div>', unsafe_allow_html=True)
st.caption("Análisis bibliométrico y Machine Learning • Scopus • Grupo 1")

# Pregunta de Investigación con Alto Contraste
st.markdown("""
<div class="research-box">
    <div class="research-title">📌 Pregunta de Investigación</div>
    <div class="research-text">
        ¿Cómo influye el uso de ChatGPT en el aprendizaje de programación y el rendimiento académico de estudiantes universitarios?
    </div>
</div>
""", unsafe_allow_html=True)

# Keywords Utilizadas (Badges Limpios)
with st.expander("🔑 Palabras clave de búsqueda en Scopus", expanded=False):
    st.markdown("""
    <div style="margin-bottom: 10px;">
        <span class="keyword-badge">ChatGPT</span>
        <span class="keyword-badge">Academic Performance</span>
        <span class="keyword-badge">Programming Education</span>
        <span class="keyword-badge">Students</span>
    </div>
    """, unsafe_allow_html=True)
    st.info("El análisis procesa literatura científica indexada en Scopus mapeando el impacto de la IA generativa en la educación informática.")

# Carga de Datos
archivo = st.file_uploader("Cargar otro archivo CSV de Scopus (opcional)", type=["csv"])

@st.cache_data
def cargar_datos(source):
    try:
        if source is not None:
            return pd.read_csv(source)
        return pd.read_csv("dataset_grupo1.csv")
    except Exception as e:
        st.error(f"Error al cargar el archivo: {e}")
        return pd.DataFrame()

df = cargar_datos(archivo)

if df.empty:
    st.warning("Por favor, asegúrate de que 'dataset_grupo1.csv' esté en tu repositorio de GitHub o sube un archivo válido.")
    st.stop()

# -------------------------------------------------------------
# FILTROS EN LA BARRA LATERAL
# -------------------------------------------------------------
st.sidebar.header("🔍 Filtros del Corpus")
df["Year"] = pd.to_numeric(df["Year"], errors='coerce').fillna(2026).astype(int)
años = sorted(df["Year"].unique())
años_seleccionados = st.sidebar.multiselect("Selecciona los años de publicación", años, default=años)

# Filtrado por tipo de documento
todos_tipos = df["Document Type"].dropna().unique().tolist()
tipos_seleccionados = st.sidebar.multiselect("Tipo de Documento", todos_tipos, default=todos_tipos)

# Aplicar filtros
df_filtrado = df[(df["Year"].isin(años_seleccionados)) & (df["Document Type"].isin(tipos_seleccionados))]

# KPIs Principales
col1, col2, col3, col4 = st.columns(4)
col1.metric("Artículos Filtrados", df_filtrado.shape[0])
col2.metric("Total Citaciones", int(df_filtrado["Cited by"].fillna(0).sum()))
col3.metric("Año más Reciente", int(df_filtrado["Year"].max()) if not df_filtrado.empty else 2026)
col4.metric("Tipos de Fuente", df_filtrado["Source title"].nunique())

st.markdown("---")

# -------------------------------------------------------------
# SECCIÓN DE MACHINE LEARNING (¡Esencial para tu entrega!)
# -------------------------------------------------------------
st.header("🧠 Módulo de Machine Learning: Agrupamiento Temático (Clustering)")
st.write("Aplicamos un modelo no supervisado **K-Means** sobre los resúmenes (`Abstract`) para descubrir los frentes de investigación ocultos.")

# Limpieza rápida de nulos en Abstract
df_ml = df_filtrado.dropna(subset=['Abstract', 'Title']).copy()

if len(df_ml) >= 5:
    num_clusters = st.slider("Selecciona el número de clusters (temas a descubrir)", min_value=2, max_value=5, value=3)
    
    # Pipeline de Machine Learning
    vectorizer = TfidfVectorizer(stop_words='english', max_features=500)
    X = vectorizer.fit_transform(df_ml['Abstract'])
    
    kmeans = KMeans(n_clusters=num_clusters, random_state=42, n_init=10)
    df_ml['Cluster'] = kmeans.fit_predict(X)
    
    # Mapear nombres entendibles a los clusters basados en sus palabras más comunes
    df_ml['Cluster Name'] = df_ml['Cluster'].apply(lambda x: f"Eje de Investigación #{x+1}")
    
    # Gráfico del resultado del modelo
    cluster_counts = df_ml['Cluster Name'].value_counts().reset_index()
    cluster_counts.columns = ['Eje Temático', 'Cantidad de Artículos']
    
    fig_cluster = px.bar(
        cluster_counts, 
        x='Cantidad de Artículos', 
        y='Eje Temático', 
        orientation='h',
        title="Distribución de Artículos por Ejes Temáticos de ML",
        color='Eje Temático',
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    st.plotly_chart(fig_cluster, use_container_width=True)
    
    # Explorador de los clusters
    with st.expander("🔍 Explorar artículos clasificados por la Inteligencia Artificial"):
        cluster_ver = st.selectbox("Selecciona un eje temático para inspeccionar:", sorted(df_ml['Cluster Name'].unique()))
        articulos_en_cluster = df_ml[df_ml['Cluster Name'] == cluster_ver][['Title', 'Source title', 'Year', 'Cited by']].head(8)
        st.dataframe(articulos_en_cluster, use_container_width=True)
else:
    st.info("Se requieren al menos 5 artículos con la columna 'Abstract' completa para ejecutar el agrupamiento de Machine Learning.")

st.markdown("---")

# -------------------------------------------------------------
# VISUALIZACIÓN BIBLIOMÉTRICA OPTIMIZADA (Punto 1: No redundante)
# -------------------------------------------------------------
st.header("📈 Análisis de Tendencias e Impacto")

tab1, tab2, tab3 = st.tabs(["📊 Producción y Acceso", "🏆 Impacto y Fuentes", "🔑 Autores y Keywords"])

with tab1:
    col_t1_1, col_t1_2 = st.columns(2)
    
    with col_t1_1:
        # Tendencia temporal (Línea interactiva en lugar de barras)
        articulos_anio = df_filtrado["Year"].value_counts().sort_index().reset_index()
        articulos_anio.columns = ["Año", "Publicaciones"]
        fig_linea = px.line(articulos_anio, x="Año", y="Publicaciones", markers=True, title="Evolución de la Producción Científica por Año")
        fig_linea.update_traces(line_color='#FF4B4B', line_width=3)
        st.plotly_chart(fig_linea, use_container_width=True)
        
    with col_t1_2:
        # Distribución de Open Access (Gráfico de Pastel)
        open_access = df_filtrado["Open Access"].fillna("No especificado").value_counts().reset_index()
        open_access.columns = ["Estatus", "Total"]
        fig_pie = px.pie(open_access, values="Total", names="Estatus", title="Distribución de Artículos en Acceso Abierto (Open Access)", color_discrete_sequence=px.colors.sequential.RdBu)
        st.plotly_chart(fig_pie, use_container_width=True)

with tab2:
    col_t2_1, col_t2_2 = st.columns(2)
    
    with col_t2_1:
        # Top 10 más citados (Tabla limpia y estilizada)
        st.subheader("🏆 Artículos de Mayor Impacto (Top 10 Citados)")
        top_citados = df_filtrado[["Title", "Cited by"]].sort_values(by="Cited by", ascending=False).head(10)
        st.dataframe(top_citados, use_container_width=True)
        
    with col_t2_2:
        # Revistas/Conferencias Top (Barras Horizontales para evitar colisión de texto)
        fuentes = df_filtrado["Source title"].value_counts().head(10).reset_index()
        fuentes.columns = ["Revista / Conferencia", "Artículos"]
        fig_fuentes = px.bar(fuentes, x="Artículos", y="Revista / Conferencia", orientation='h', title="Top 10 Canales de Publicación más Frecuentes")
        fig_fuentes.update_yaxes(autorange="reversed")
        st.plotly_chart(fig_fuentes, use_container_width=True)

with tab3:
    col_t3_1, col_t3_2 = st.columns(2)
    
    with col_t3_1:
        # Autores productivos
        autores = df_filtrado["Authors"].dropna().str.split(";").explode().str.strip().value_counts().head(10).reset_index()
        autores.columns = ["Autor", "Publicaciones"]
        fig_autores = px.bar(autores, x="Publicaciones", y="Autor", orientation='h', title="Top 10 Autores más Productivos del Corpus")
        fig_autores.update_yaxes(autorange="reversed")
        st.plotly_chart(fig_autores, use_container_width=True)
        
    with col_t3_2:
        # Palabras clave más frecuentes
        keywords = df_filtrado["Author Keywords"].dropna().str.split(";").explode().str.strip().value_counts().head(12).reset_index()
        keywords.columns = ["Palabra Clave", "Frecuencia"]
        fig_keys = px.bar(keywords, x="Frecuencia", y="Palabra Clave", orientation='h', title="Top 12 Palabras Clave más Frecuentes", color="Frecuencia", color_continuous_scale="Viridis")
        fig_keys.update_yaxes(autorange="reversed")
        st.plotly_chart(fig_keys, use_container_width=True)

# Explorador General de la Tabla Completa
