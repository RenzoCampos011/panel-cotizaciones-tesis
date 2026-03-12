import streamlit as st
from supabase import create_client, Client
import pandas as pd
import plotly.express as px
import re # Para limpiar textos y convertirlos a números

# =========================================================================
# 1. CONFIGURACIÓN DE LA PÁGINA
# =========================================================================
st.set_page_config(page_title="Comité Virtual: Licitaciones B2B", page_icon="👔", layout="wide")

# =========================================================================
# 2. CONEXIÓN A SUPABASE (Nivel Producción)
# =========================================================================
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

@st.cache_resource
def init_connection():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase: Client = init_connection()

@st.cache_data(ttl=60) # Refresca los datos cada minuto
def load_data():
    response = supabase.table("cotizaciones_prueba").select("*").execute()
    df = pd.DataFrame(response.data)
    
    # Limpieza preventiva preventiva: si hay datos antiguos sin proyecto
    if 'proyecto' not in df.columns:
        df['proyecto'] = "General"
    else:
        df['proyecto'] = df['proyecto'].fillna("General")
        
    return df

# =========================================================================
# 3. INTERFAZ: EL COMITÉ VIRTUAL
# =========================================================================
st.title("👔 Comité de Compras Virtual: Multi-Agente IA")
st.markdown("Análisis competitivo y recomendación gerencial impulsada por agentes autónomos.")
st.divider()

try:
    df_completo = load_data()
    
    if df_completo.empty:
        st.warning("⚠️ No hay datos en la base de datos.")
        st.stop()

    # --- BARRA LATERAL: GESTIÓN DE PROYECTO ---
    st.sidebar.header("📂 Gestión de Proyectos")
    lista_proyectos = df_completo['proyecto'].unique()
    proyecto_elegido = st.sidebar.selectbox("Seleccione la licitación/proyecto:", lista_proyectos)
    
    # FILTRAMOS LOS DATOS: Solo usamos los datos del proyecto elegido
    df = df_completo[df_completo['proyecto'] == proyecto_elegido].copy()
    
    # ---------------------------------------------------------
    # PROCESAMIENTO DE DATOS PARA LOS GRÁFICOS (Crítico)
    # ---------------------------------------------------------
    # 1. Aseguramos que los precios sean numéricos
    df['precio_total'] = pd.to_numeric(df['precio_total'], errors='coerce')
    
    # 2. Aseguramos que el puntaje sea numérico
    df['puntaje_ia'] = pd.to_numeric(df['puntaje_ia'], errors='coerce')
    
    # 3. Convertimos "15 días calendario" en el número 15 (Para el gráfico)
    def extraer_dias(texto):
        if not texto: return 0
        numeros = re.findall(r'(\d+)', str(texto))
        return int(numeros[0]) if numeros else 0
        
    df['tiempo_entrega_num'] = df['tiempo_entrega'].apply(extraer_dias)

    # =========================================================================
    # FASE 1: VISIÓN DE CONJUNTO (GRÁFICOS DE IMPACTO - SECCIÓN A)
    # =========================================================================
    st.header("📈 Visión de Conjunto (Comparativa Directa)")
    st.divider()

    # ---------------------------------------------------------
    # GRÁFICO 1: EL REY (FULL WIDTH) - PRECIO TOTAL
    # ---------------------------------------------------------
    st.subheader("1️⃣ Oferta Económica Final")
    st.markdown("Muestra la diferencia de precio puro entre los proveedores.")
    
    fig_precio = px.bar(
        df, 
        x='proveedor', 
        y='precio_total', 
        title=f"Monto Ofertado por Proveedor: {proyecto_elegido}",
        labels={'precio_total': 'Monto Total', 'proveedor': 'Empresa Ofertante'},
        text='precio_total',
        color='precio_total', # Efecto de color gradiente
        color_continuous_scale='Blues'
    )
    fig_precio.update_traces(texttemplate='%{text:.2s}', textposition='outside')
    fig_precio.update_layout(height=400) # Altura fija para el gráfico principal
    st.plotly_chart(fig_precio, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True) # Espacio en blanco

    # ---------------------------------------------------------
    # GRÁFICOS 2 Y 3: ANÁLISIS TÉCNICO CROSS-COMPARATIVO (EN COLUMNAS)
    # ---------------------------------------------------------
    st.subheader("🔍 Análisis Técnico y de Riesgo")
    st.markdown("Contraste de los factores de confianza y tiempos frente al costo.")
    col_scatters1, col_scatters2 = st.columns(2)
    
    # Mapa de colores unificado para el riesgo
    color_map = {"Bajo": "#00CC96", "Medio": "#FFA15A", "Alto": "#EF553B"}
    
    # GRÁFICO 2: SCORE VS RIESGO (En columna izquierda)
    with col_scatters1:
        st.markdown("**2️⃣ Confiabilidad B2B vs Nivel de Riesgo**")
        st.markdown("Ayuda a ver quién es el más confiable y quién representa una alerta.")
        fig_score = px.scatter(
            df, 
            x='proveedor', 
            y='puntaje_ia', 
            size='puntaje_ia', # El tamaño depende de la confianza
            color='nivel_riesgo', # El color depende del semáforo
            title="Score de Confiabilidad y Semáforo de Riesgo",
            labels={'puntaje_ia': 'Score IA', 'proveedor': 'Empresa', 'nivel_riesgo': 'Alerta de Riesgo'},
            color_discrete_map=color_map,
            size_max=40,
            hover_data=['proveedor', 'puntaje_ia', 'resumen_ia']
        )
        # Hacemos que la leyenda del riesgo sea más profesional
        fig_score.update_layout(legend_title_text='Nivel de Riesgo (Alerta)')
        st.plotly_chart(fig_score, use_container_width=True)

    # GRÁFICO 3: TIEMPO VS COSTO (En columna derecha)
    with col_scatters2:
        st.markdown("**3️⃣ Equilibrio de Compra: Tiempo vs Costo**")
        st.markdown("Permite ver quién es el proveedor más rápido y barato en un solo vistazo.")
        fig_speed = px.scatter(
            df, 
            x='tiempo_entrega_num', # El número de días que extrajimos
            y='precio_total', 
            size='puntaje_ia', # El tamaño también depende de la confianza
            color='nivel_riesgo',
            title="Costo vs Tiempo de Entrega vs Confiabilidad",
            labels={'precio_total': 'Monto Total', 'tiempo_entrega_num': 'Días de Entrega', 'nivel_riesgo': 'Nivel de Riesgo'},
            color_discrete_map=color_map,
            size_max=35,
            hover_data=['proveedor', 'tiempo_entrega', 'precio_total', 'puntaje_ia'] # Mostramos el texto original en el hover
        )
        # Hacemos que la leyenda sea profesional
        fig_speed.update_layout(legend_title_text='Nivel de Riesgo (Alerta)')
        st.plotly_chart(fig_speed, use_container_width=True)

    st.divider()

    # =========================================================================
    # FASE 2: EL ANÁLISIS DE LOS AGENTES (LOS PROFESIONALES)
    # =========================================================================
    st.header("🕵️‍♂️ Revisión del Comité (Detalle Individual)")
    st.markdown("Seleccione un proveedor para ver el desglose por área profesional.")
    
    lista_proveedores = df['proveedor'].dropna().unique()
    proveedor_elegido = st.selectbox("Seleccione el Proveedor para ver el desglose:", lista_proveedores)
    
    # Filtramos la fila del proveedor seleccionado
    datos_prov = df[df['proveedor'] == proveedor_elegido].iloc[0]

    # Usamos Pestañas para simular los roles de la empresa
    tab1, tab2, tab3 = st.tabs(["💰 Agente 1: Analista Financiero", "🤝 Agente 2: Gerente Comercial", "⚖️ Agente 3: Asesor Legal"])
    
    # ---------------------------------------------------------
    # PESTAÑA 1: ANALISTA FINANCIERO
    # ---------------------------------------------------------
    with tab1:
        st.info("**Misión del Agente:** Extraer y validar la información fiscal y los montos ofertados.")
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            st.metric("Empresa / Proveedor", str(datos_prov.get('proveedor', 'N/A')))
            st.metric("RUC Validado", str(datos_prov.get('ruc', 'N/A')))
        with col_f2:
            st.metric("Monto Total Ofertado", f"{datos_prov.get('moneda', '')} {datos_prov.get('precio_total', 0)}")
            st.metric("Fecha de Emisión", str(datos_prov.get('fecha', 'N/A')))

    # ---------------------------------------------------------
    # PESTAÑA 2: GERENTE COMERCIAL
    # ---------------------------------------------------------
    with tab2:
        st.info("**Misión del Agente:** Analizar las condiciones logísticas y el trato comercial.")
        with st.container(border=True):
            st.markdown(f"**💳 Condición de Pago exigida:** {datos_prov.get('condicion_pago', 'N/A')}")
            st.markdown(f"**⏱️ Tiempo de Entrega prometido:** {datos_prov.get('tiempo_entrega', 'N/A')}")
            st.markdown(f"**🛡️ Garantía cubierta:** {datos_prov.get('garantia', 'N/A')}")

    # ---------------------------------------------------------
    # PESTAÑA 3: ASESOR LEGAL
    # ---------------------------------------------------------
    with tab3:
        st.info("**Misión del Agente:** Proteger a la empresa evaluando la vigencia y penalidades legales.")
        with st.container(border=True):
            st.markdown(f"**📅 Validez de la Oferta:** {datos_prov.get('validez_oferta', 'N/A')}")
            st.markdown(f"**⚖️ Cláusula de Penalidades por Retraso:** {datos_prov.get('penalidades_retraso', 'N/A')}")

    st.markdown("<br>", unsafe_allow_html=True) # Espacio en blanco

    # =========================================================================
    # FASE 3: LA RECOMENDACIÓN FINAL DEL AUDITOR IA
    # =========================================================================
    st.subheader("🧠 Veredicto Final: Agente Auditor (IA)")
    st.markdown("Recomendación sintetizada para la toma de decisión del gerente.")
    
    # Un contenedor con borde destacado para la recomendación final
    with st.container(border=True):
        col_a1, col_a2 = st.columns([1, 3]) # Columna 2 es más ancha
        
        with col_a1:
            score = datos_prov.get('puntaje_ia', 0)
            st.metric(label="Score Final de Confiabilidad", value=f"{score} / 100")
            
            # Semáforo de Riesgo
            riesgo = str(datos_prov.get('nivel_riesgo', 'Desconocido'))
            if riesgo.lower() == "bajo":
                st.success(f"Nivel de Riesgo: 🟢 {riesgo}")
            elif riesgo.lower() == "medio":
                st.warning(f"Nivel de Riesgo: 🟡 {riesgo}")
            else:
                st.error(f"Nivel de Riesgo: 🔴 {riesgo}")
            
        with col_a2:
            st.markdown("### Recomendación Directa al Gerente:")
            # Justificación redactada por el Agente 4
            st.write(datos_prov.get('resumen_ia', 'El Agente 4 no generó un resumen para esta cotización.'))

    # --- SECCIÓN C: AUDITORÍA ---
    st.divider()
    with st.expander("Ver Base de Datos del Proyecto (Modo Auditoría)"):
        # Mostramos la tabla solo del proyecto actual
        st.dataframe(df, use_container_width=True)

except Exception as e:
    st.error(f"Error crítico en la visualización: {e}")
