"""
Vista de inicio para PT_CALIDAD
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

def show_home():
    """Mostrar la página de inicio"""
    
    st.markdown('<h1 class="main-header">🏠 Panel de Control - APG PACKING</h1>', unsafe_allow_html=True)
    
    # Métricas principales
    
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<h4>ℹ️ Información del Sistema</h4>', unsafe_allow_html=True)
        st.info("""
        - **Versión:** 1.0.0
        - **Última actualización:** 2025-08-22
        - **Estado:** Operativo
       
        """)
    
    with col2:
        st.markdown('<h4>🚀 Acciones Rápidas</h4>', unsafe_allow_html=True)
        
        if st.button("📊 Generar Reporte Diario",use_container_width=True,disabled=True):
            st.success("Reporte generado exitosamente!")
        
        if st.button("🔍",use_container_width=True,disabled=True):
            st.info("Redirigiendo a Control de Calidad...")
        
        

# Importar numpy para los datos de ejemplo
import numpy as np
