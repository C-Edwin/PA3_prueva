import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Configuración de la página
st.set_page_config(
    page_title="Dashboard ChatGPT y Programación",
    page_icon="🤖",
    layout="wide"
)

# -------------------------------------------------------------
# ESTILOS CSS PERSONALIZADOS (Optimizado para máxima legibilidad)
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
/* Caja de Valor Agregado Corregida: Fondo Claro y Letra Negra para máxima lectura */
.value-box {
    background-color: #F1F5F9; 
    color: #0F172A;
    padding: 18px; 
    border-radius: 8px; 
    border-left: 6px solid #FF4B4B;
    margin-top: 15px;
    margin-bottom: 25px;
    font-size: 16px;
    line-height: 1.5;
}
</style>
""", unsafe_allow_html=True)

# Título Principal
st.markdown('<div class="main-title">🤖 ChatGPT & Aprendizaje de Programación</div>', unsafe_allow_html=True)
st.caption("Análisis bibliométrico avanzado • Scopus • Grupo 1")

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
# VISUALIZACIÓN BIBLIOMÉTRICA ORIGINAL
# -------------------------------------------------------------
st.header("📈 Análisis de Tendencias Básicas e Impacto")

tab1, tab2, tab3 = st.tabs(["📊 Producción y Acceso", "🏆 Impacto y Fuentes", "🔑 Autores y Keywords"])

with tab1:
    col_t1_1, col_t1_2 = st.columns(2)
    with col_t1_1:
        articulos_anio = df_filtrado["Year"].value_counts().sort_index().reset_index()
        articulos_anio.columns = ["Año", "Publicaciones"]
        fig_linea = px.line(articulos_anio, x="Año", y="Publicaciones", markers=True, title="Evolución de la Producción Científica por Año")
        fig_linea.update_traces(line_color='#FF4B4B', line_width=3)
        st.plotly_chart(fig_linea, use_container_width=True)
    with col_t1_2:
        open_access = df_filtrado["Open Access"].fillna("No especificado").value_counts().reset_index()
        open_access.columns = ["Estatus", "Total"]
        fig_pie = px.pie(open_access, values="Total", names="Estatus", title="Distribución de Artículos en Acceso Abierto (Open Access)", color_discrete_sequence=px.colors.sequential.RdBu)
        st.plotly_chart(fig_pie, use_container_width=True)

with tab2:
    col_t2_1, col_t2_2 = st.columns(2)
    with col_t2_1:
        st.subheader("🏆 Artículos de Mayor Impacto (Top 10 Citados)")
        top_citados = df_filtrado[["Title", "Cited by"]].sort_values(by="Cited by", ascending=False).head(10)
        st.dataframe(top_citados, use_container_width=True)
    with col_t2_2:
        fuentes = df_filtrado["Source title"].value_counts().head(10).reset_index()
        fuentes.columns = ["Revista / Conferencia", "Artículos"]
        fig_fuentes = px.bar(fuentes, x="Artículos", y="Revista / Conferencia", orientation='h', title="Top 10 Canales de Publicación más Frecuentes")
        fig_fuentes.update_yaxes(autorange="reversed")
        st.plotly_chart(fig_fuentes, use_container_width=True)

with tab3:
    autores = df_filtrado["Authors"].dropna().str.split(";").explode().str.strip().value_counts().head(10).reset_index()
    autores.columns = ["Autor", "Publicaciones"]
    fig_autores = px.bar(autores, x="Publicaciones", y="Autor", orientation='h', title="Top 10 Autores más Productivos del Corpus")
    fig_autores.update_yaxes(autorange="reversed")
    st.plotly_chart(fig_autores, use_container_width=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    keywords = df_filtrado["Author Keywords"].dropna().str.split(";").explode().str.strip().value_counts().head(12).reset_index()
    keywords.columns = ["Palabra Clave", "Frecuencia"]
    fig_keys = px.bar(keywords, x="Frecuencia", y="Palabra Clave", orientation='h', title="Top 12 Palabras Clave más Frecuentes", color="Frecuencia", color_continuous_scale="Viridis")
    fig_keys.update_yaxes(autorange="reversed")
    st.plotly_chart(fig_keys, use_container_width=True)

st.markdown("---")
# -------------------------------------------------------------
# 5 VISUALIZACIONES CON VALOR AGREGADO (LETRA CLARA Y LEGUIBLE)
# -------------------------------------------------------------
st.header("💎 Análisis Avanzado de Valor Agregado")
st.write("Explora métricas avanzadas cruzando múltiples dimensiones del corpus académico.")

v_tab1, v_tab2, v_tab3, v_tab4, v_tab5 = st.tabs([
    "🎯 1. Antigüedad vs Impacto", 
    "🔓 2. Acceso por Documento", 
    "📈 3. Impacto de Acceso Abierto", 
    "⏳ 4. Evolución del Impacto", 
    "🔀 5. Intersección de Keywords"
])

with v_tab1:
    df_scatter = df_filtrado.dropna(subset=['Year', 'Cited by']).copy()
    fig_scatter = px.scatter(
        df_scatter, x="Year", y="Cited by", color="Document Type",
        hover_name="Title", size="Cited by", size_max=40,
        title="Relación de Impacto (Citaciones) según el Año de Publicación"
    )
    st.plotly_chart(fig_scatter, use_container_width=True)
    
    st.markdown("""
    <div class="value-box">
        <b>💡 VALOR AGREGADO:</b> Identifica de forma inmediata los artículos 'estrella' (outliers). 
        Permite comprobar visualmente si el impacto académico se concentra en investigaciones tempranas pioneras o si existen publicaciones recientes con un crecimiento de citaciones sumamente acelerado.
    </div>
    """, unsafe_allow_html=True)

with v_tab2:
    df_group = df_filtrado.copy()
    df_group["Open Access"] = df_group["Open Access"].fillna("Cerrado / No especificado")
    fig_group = px.histogram(
        df_group, x="Document Type", color="Open Access", barmode="group",
        title="Disponibilidad de Acceso Abierto por Tipo de Documento"
    )
    st.plotly_chart(fig_group, use_container_width=True)
    
    st.markdown("""
    <div class="value-box">
        <b>💡 VALOR AGREGADO:</b> Muestra la democratización del conocimiento científico. 
        Permite evaluar si la literatura enfocada en ChatGPT es de libre lectura o está restringida por barreras de pago, mapeando la predisposición al Open Access entre artículos de revistas frente a conferencias.
    </div>
    """, unsafe_allow_html=True)

with v_tab3:
    df_oa_impact = df_filtrado.copy()
    df_oa_impact["Open Access"] = df_oa_impact["Open Access"].fillna("Cerrado / No especificado")
    df_oa_grouped = df_oa_impact.groupby("Open Access")["Cited by"].mean().reset_index()
    df_oa_grouped.columns = ["Estatus de Acceso", "Promedio de Citaciones"]
    
    fig_oa_bar = px.bar(
        df_oa_grouped, x="Estatus de Acceso", y="Promedio de Citaciones",
        color="Estatus de Acceso", color_discrete_sequence=px.colors.qualitative.Set2,
        title="Promedio de Citas Recibidas: Artículos Abiertos vs. Cerrados"
    )
    st.plotly_chart(fig_oa_bar, use_container_width=True)
    
    st.markdown("""
    <div class="value-box">
        <b>💡 VALOR AGREGADO:</b> Analiza la ventaja de citación del conocimiento abierto. 
        Demuestra numéricamente si publicar en formato Open Access le otorga mayor visibilidad y tasa de citación a las investigaciones sobre ChatGPT frente a los canales tradicionales de pago.
    </div>
    """, unsafe_allow_html=True)

with v_tab4:
    df_year_citations = df_filtrado.groupby("Year")["Cited by"].sum().reset_index()
    df_year_citations.columns = ["Año", "Total Citaciones Acumuladas"]
    
    fig_area_citations = px.area(
        df_year_citations, x="Año", y="Total Citaciones Acumuladas",
        title="Evolución Histórica de Citaciones Totales por Año",
        markers=True
    )
    fig_area_citations.update_traces(line_color='#FF4B4B')
    st.plotly_chart(fig_area_citations, use_container_width=True)
    
    st.markdown("""
    <div class="value-box">
        <b>💡 VALOR AGREGADO:</b> Muestra la velocidad de absorción del conocimiento en la comunidad científica. 
        Permite identificar el año exacto en que las investigaciones sobre ChatGPT se convirtieron en un pilar de referencia masivo para otros académicos del mundo de la programación.
    </div>
    """, unsafe_allow_html=True)

with v_tab5:
    top_keys = df_filtrado["Author Keywords"].dropna().str.split(";").explode().str.strip().value_counts().head(8).index.tolist()
    df_exploded = df_filtrado.dropna(subset=["Author Keywords"]).copy()
    df_exploded["Keyword"] = df_exploded["Author Keywords"].str.split(";")
    df_exploded = df_exploded.explode("Keyword")
    df_exploded["Keyword"] = df_exploded["Keyword"].str.strip()
    df_exploded = df_exploded[df_exploded["Keyword"].isin(top_keys)]
    
    fig_cross = px.histogram(
        df_exploded, x="Keyword", color="Document Type", barmode="stack",
        title="Intersección y Enfoque Temático según el Tipo de Documento"
    )
    st.plotly_chart(fig_cross, use_container_width=True)
    
    st.markdown("""
    <div class="value-box">
        <b>💡 VALOR AGREGADO:</b> Descubre el enfoque de las metodologías científicas. 
        Permite correlacionar si ciertos conceptos clave (como 'Academic Performance') se discuten más en artículos conceptuales de revista o en experimentos prácticos publicados en actas de congresos.
    </div>
    """, unsafe_allow_html=True)

# Explorador General de la Tabla Completa
st.subheader("📋 Vista Global e Interactiva del Dataset completo")
st.dataframe(df_filtrado, use_container_width=True)

st.markdown("---")

# -------------------------------------------------------------
# HALLAZGOS Y CONCLUSIONES
# -------------------------------------------------------------
st.subheader("📌 Principales Hallazgos Académicos")
st.markdown("""
<div style="background-color: #0F172A; padding: 20px; border-radius: 8px; border-left: 5px solid #FF4B4B;">
    <ul style="color: #E2E8F0; font-size: 16px; line-height: 1.6;">
        <li>🚀 <b>Crecimiento Exponencial:</b> La producción científica enfocada en ChatGPT y educación en ingeniería de software ha estallado verticalmente en el periodo analizado.</li>
        <li>💡 <b>Foco Pedagógico:</b> Las palabras clave y agrupamientos revelan que el debate científico no solo se centra en el plagio, sino en cómo usar LLMs como tutores personalizados de programación 24/7.</li>
        <li>🎓 <b>Transformación de Roles:</b> Se evidencia un marcado interés por medir la competencia de resolución de problemas en estudiantes de primeros ciclos (CS1) asistidos por IA.</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# Pie de página del Proyecto
st.markdown("<br>", unsafe_allow_html=True)
col_pie1, col_pie2 = st.columns(2)
with col_pie1:
    st.markdown("**Desarrollado por:** Grupo 1")
with col_pie2:
    st.markdown("<div style='text-align: right;'><i>Entregable Académico - Fundamentos de Machine Learning</i></div>", unsafe_allow_html=True)

