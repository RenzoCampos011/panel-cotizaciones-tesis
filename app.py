import streamlit as st
from supabase import create_client, Client
import pandas as pd

# 1. Configuración de la página
st.set_page_config(page_title="Panel de Cotizaciones", page_icon="📊", layout="wide")
st.title("📊 Panel de Gerencia: Cotizaciones Procesadas")
st.markdown("Este panel muestra los datos extraídos automáticamente por IA desde los PDFs.")

# 2. Conexión a Supabase (Leyendo desde la bóveda secreta)
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

# 3. Función para traer los datos
@st.cache_data(ttl=10) # Refresca los datos cada 10 segundos
def cargar_datos():
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        respuesta = supabase.table("cotizaciones_prueba").select("*").execute()
        
        if respuesta.data:
            df = pd.DataFrame(respuesta.data)
            return df
        else:
            return pd.DataFrame() 
    except Exception as e:
        st.error(f"Error al conectar con la base de datos: {e}")
        return None

# 4. Mostrar los datos
df_cotizaciones = cargar_datos()

if df_cotizaciones is not None and not df_cotizaciones.empty:
    st.subheader("Resumen General")
    col1, col2 = st.columns(2)
    col1.metric("Total de Cotizaciones", len(df_cotizaciones))
    
    if 'precio_total' in df_cotizaciones.columns:
        total_dinero = df_cotizaciones['precio_total'].sum()
        col2.metric("Monto Total Acumulado", f"S/ {total_dinero:,.2f}")
    
    st.subheader("Base de Datos")
    st.dataframe(df_cotizaciones, use_container_width=True)
else:

    st.info("No hay cotizaciones procesadas todavía o la tabla está vacía.")
