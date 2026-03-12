import streamlit as st
from supabase import create_client, Client
import pandas as pd
import plotly.express as px

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Comité de Compras IA", page_icon="👔", layout="wide")

# 2. CONEXIÓN A SUPABASE
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

@st.cache_resource
def init_connection():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase: Client = init_connection()

@st.cache_data(ttl=60)
def load_data():
    response = supabase.table("cotizaciones_prueba").select("*").execute()
    df = pd.DataFrame(response.data)
    if 'proyecto' not in df.columns:
        df['proyecto'] = "General"
    else:
        df['proyecto'] = df['proyecto'].fillna("General")
    return df

# 3. INTERFAZ: EL COMITÉ VIRTUAL
st.title("👔 Comité de Compras Virtual: Multi-Agente IA")
st.markdown("Análisis competitivo y recomendación gerencial impulsada por agentes autónomos.")
st.divider()

try:
    df_completo = load_data()
    
    if df_completo.empty:
        st.warning("⚠️ No hay datos en la base de datos.")
        st.stop()

    # --- BARRA LATERAL: PROYECTO ---
    st.sidebar.header("📂 Gestión de Proyectos")
    lista_proyectos = df_completo['proyecto'].unique()
    proyecto_elegido = st.sidebar.selectbox("Seleccione la Licitación:", lista_proyectos)
    
    df = df_completo[df_completo['proyecto'] == proyecto_elegido].copy()
    
    # Limpieza de datos numéricos para los gráficos
    df['precio_total'] = pd.to_numeric(df['precio_total'], errors='coerce')
    df['puntaje_ia'] = pd.to_numeric(df['puntaje_ia'], errors='coerce')

    # =========================================================================
    # FASE 1: VISIÓN GERENCIAL (GRÁFICOS DE IMPACTO)
    # =========================================================================
    st.subheader("📊 Resumen Competitivo del Proyecto")
    
    col_graf1, col_graf2 = st.columns(2)
    
    with col_graf1:
        # Gráfico 1: Comparativa de Precios (El dolor de bolsillo)
        fig_precio = px.bar(
            df, x='proveedor', y='precio_total', 
            text='precio_total',
            title="Comparativa de Oferta Económica (Menor es mejor)",
            color='precio_total', color_continuous_scale='Blues'
        )
        fig_precio.update_traces(texttemplate='%{text:.2s}', textposition='outside')
        st.plotly_chart(fig_precio, use_container_width=True)

    with col_graf2:
        # Gráfico 2: Score de la IA vs Riesgo
        fig_score = px.scatter(
            df, x='proveedor', y='puntaje_ia', 
            size='puntaje_ia', color='nivel_riesgo',
            title="Score de Confiabilidad B2B vs Nivel de Riesgo",
            color_discrete_map={"Bajo": "#00CC96", "Medio": "#FFA15A", "Alto": "#EF553B"},
            size_max=40
        )
        st.plotly_chart(fig_score, use_container_width=True)

    st.divider()

    # =========================================================================
    # FASE 2: EL ANÁLISIS DE LOS AGENTES (LOS PROFESIONALES)
    # =========================================================================
    st.subheader("🕵️‍♂️ Revisión del Comité (Detalle por Proveedor)")
    
    lista_proveedores = df['proveedor'].dropna().unique()
    proveedor_elegido = st.selectbox("Seleccione el Proveedor para ver el desglose:", lista_proveedores)
    datos_prov = df[df['proveedor'] == proveedor_elegido].iloc[0]

    # Usamos Pestañas para simular los roles de la empresa
    tab1, tab2, tab3 = st.tabs(["💰 Agente 1: Analista Financiero", "🤝 Agente 2: Gerente Comercial", "⚖️ Agente 3: Asesor Legal"])
    
    with tab1:
        st.info("**Misión del Agente:** Extraer y validar la información fiscal y los montos ofertados.")
        col_f1, col_f2 = st.columns(2)
        col_f1.metric("Empresa / Proveedor", str(datos_prov.get('proveedor', 'N/A')))
        col_f1.metric("RUC Validado", str(datos_prov.get('ruc', 'N/A')))
        col_f2.metric("Monto Total", f"{datos_prov.get('moneda', '')} {datos_prov.get('precio_total', 0)}")
        col_f2.metric("Fecha de Emisión", str(datos_prov.get('fecha', 'N/A')))

    with tab2:
        st.info("**Misión del Agente:** Analizar las condiciones logísticas y el trato comercial.")
        st.markdown(f"**💳 Condición de Pago exigida:** {datos_prov.get('condicion_pago', 'N/A')}")
        st.markdown(f"**⏱️ Tiempo de Entrega prometido:** {datos_prov.get('tiempo_entrega', 'N/A')}")
        st.markdown(f"**🛡️ Garantía cubierta:** {datos_prov.get('garantia', 'N/A')}")

    with tab3:
        st.info("**Misión del Agente:** Proteger a la empresa evaluando la vigencia y penalidades.")
        st.markdown(f"**📅 Validez de la Oferta:** {datos_prov.get('validez_oferta', 'N/A')}")
        st.markdown(f"**⚖️ Cláusula de Penalidades por Retraso:** {datos_prov.get('penalidades_retraso', 'N/A')}")

    st.markdown("<br>", unsafe_allow_html=True) # Espacio en blanco

    # =========================================================================
    # FASE 3: LA RECOMENDACIÓN FINAL DEL AUDITOR IA
    # =========================================================================
    st.subheader("🧠 Veredicto Final: Agente Auditor (IA)")
    
    # Un contenedor con borde destacado para la recomendación final
    with st.container(border=True):
        col_a1, col_a2 = st.columns([1, 3]) # Columna 2 es más ancha
        
        with col_a1:
            score = datos_prov.get('puntaje_ia', 0)
            st.metric(label="Score Final", value=f"{score} / 100")
            
            riesgo = str(datos_prov.get('nivel_riesgo', 'Desconocido'))
            if riesgo.lower() == "bajo": st.success(f"Riesgo: 🟢 {riesgo}")
            elif riesgo.lower() == "medio": st.warning(f"Riesgo: 🟡 {riesgo}")
            else: st.error(f"Riesgo: 🔴 {riesgo}")
            
        with col_a2:
            st.markdown("### Recomendación Directa al Gerente:")
            st.write(datos_prov.get('resumen_ia', 'El Agente 4 no generó un resumen para esta cotización.'))

except Exception as e:
    st.error(f"Error en la visualización: {e}")
