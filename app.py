import streamlit as st
from supabase import create_client, Client
import pandas as pd

# -----------------------------------------------------------------------------
# 1. CONFIGURACIÓN DE LA PÁGINA 
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Dashboard Gerencial B2B | Evaluación IA", 
    page_icon="🏢", 
    layout="wide"
)

# -----------------------------------------------------------------------------
# 2. CONEXIÓN A SUPABASE (Bóveda Secreta - Nivel Producción)
# -----------------------------------------------------------------------------
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

@st.cache_resource
def init_connection():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase: Client = init_connection()

@st.cache_data(ttl=60) # Refresca los datos cada minuto
def load_data():
    response = supabase.table("cotizaciones_prueba").select("*").execute()
    return pd.DataFrame(response.data)

# -----------------------------------------------------------------------------
# 3. INTERFAZ VISUAL: EL DASHBOARD B2B
# -----------------------------------------------------------------------------
st.title("📊 Sistema Orquestador B2B: Evaluación de Proveedores")
st.markdown("Plataforma de apoyo a la decisión con análisis Multi-Agente IA.")
st.divider()

try:
    df = load_data()
    
    if df.empty:
        st.warning("⚠️ No hay datos en la base de datos. Ejecuta tu flujo en n8n primero.")
    else:
        # --- SECCIÓN A: COMPARATIVA GLOBAL ---
        st.subheader("📈 Visión Global: Comparativa de Precios")
        
        # Limpiamos los datos para el gráfico (asegurar que el precio sea número)
        df['precio_total'] = pd.to_numeric(df['precio_total'], errors='coerce')
        
        # Gráfico de barras
        st.bar_chart(data=df, x='proveedor', y='precio_total', use_container_width=True)
        st.divider()

        # --- SECCIÓN B: ANÁLISIS A PROFUNDIDAD ---
        st.subheader("🔍 Análisis Detallado por Proveedor")
        st.markdown("Seleccione un proveedor para ver el contraste entre los datos extraídos y la evaluación de la IA.")
        
        # Selector de proveedor
        lista_proveedores = df['proveedor'].dropna().unique()
        proveedor_elegido = st.selectbox("Seleccione el Proveedor a evaluar:", lista_proveedores)
        
        # Filtramos la fila del proveedor seleccionado
        datos_prov = df[df['proveedor'] == proveedor_elegido].iloc[0]
        
        # ¡LA MAGIA DE LA DIVISIÓN DE PANTALLA!
        col1, col2 = st.columns(2)
        
        # ---------------------------------------------------------
        # COLUMNA 1: LOS DATOS OBJETIVOS (La Realidad)
        # ---------------------------------------------------------
        with col1:
            st.markdown("### 📄 Datos Objetivos (Realidad)")
            st.info("Información factual extraída del documento original por los Agentes 1, 2 y 3.")
            
            with st.container(border=True):
                st.markdown(f"**🏢 Empresa:** {datos_prov.get('proveedor', 'N/A')}")
                st.markdown(f"**🆔 RUC:** {datos_prov.get('ruc', 'N/A')}")
                st.markdown(f"**💰 Monto Ofertado:** {datos_prov.get('moneda', '')} {datos_prov.get('precio_total', 'N/A')}")
                st.markdown(f"**💳 Condición de Pago:** {datos_prov.get('condicion_pago', 'N/A')}")
                st.markdown(f"**⏱️ Tiempo de Entrega:** {datos_prov.get('tiempo_entrega', 'N/A')}")
                st.markdown(f"**🛡️ Garantía:** {datos_prov.get('garantia', 'N/A')}")
                st.markdown(f"**⚖️ Penalidades:** {datos_prov.get('penalidades_retraso', 'N/A')}")
                st.markdown(f"**📅 Validez de Oferta:** {datos_prov.get('validez_oferta', 'N/A')}")

        # ---------------------------------------------------------
        # COLUMNA 2: LA RECOMENDACIÓN IA (El Copiloto)
        # ---------------------------------------------------------
        with col2:
            st.markdown("### 🤖 Evaluación Multi-Agente IA")
            st.warning("Análisis de riesgo y scoring generado por el Motor B2B y el Agente Auditor.")
            
            with st.container(border=True):
                # 1. El Puntaje Gigante
                score = datos_prov.get('puntaje_ia', 0)
                st.metric(label="Score de Confiabilidad B2B", value=f"{score} / 100")
                
                # 2. El Semáforo de Riesgo
                riesgo = datos_prov.get('nivel_riesgo', 'Desconocido')
                if riesgo == "Bajo":
                    st.success(f"**Nivel de Riesgo:** 🟢 {riesgo}")
                elif riesgo == "Medio":
                    st.warning(f"**Nivel de Riesgo:** 🟡 {riesgo}")
                else:
                    st.error(f"**Nivel de Riesgo:** 🔴 {riesgo}")
                
                st.markdown("---")
                
                # 3. El Veredicto del Agente 4
                st.markdown("**Resumen Gerencial del Auditor IA:**")
                st.write(datos_prov.get('resumen_ia', 'El Agente 4 no generó un resumen para esta cotización.'))

        # --- SECCIÓN C: AUDITORÍA ---
        st.divider()
        with st.expander("Ver Base de Datos Completa (Modo Auditoría)"):
            st.dataframe(df, use_container_width=True)

except Exception as e:
    st.error(f"Error crítico al conectar con la base de datos: {e}")
    st.stop()
