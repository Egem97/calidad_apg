"""
Aplicación principal de PT_CALIDAD
Basado en la estructura del proyecto alzaqr
"""

import streamlit as st
from streamlit_option_menu import option_menu
import sys
import os

# Agregar el directorio raíz al path para importar módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from views.home import show_home
from views.quality_control import show_quality_control
from views.reports import show_reports
from views.settings import show_settings
from views.finished_product import show_finished_product
from utils.config import load_config
from styles import load_css

def main():
    """Función principal de la aplicación"""
    
    # Configurar página
    st.set_page_config(
        page_title="APG PACKING",
        page_icon="🔍",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    st.logo("./assets/logo.jpg")  
    
    # Cargar estilos CSS
    load_css()
    
    # Cargar configuración
    config = load_config()
    
    # Sidebar con navegación
    with st.sidebar:
        st.title("🔍 PACKING")
        
        
        # Menú de navegación
        selected = option_menu(
            menu_title=None,
            options=["🏠 Inicio", "🫐 Producto Terminado"],
            icons=["house", "check-circle"],
            menu_icon="cast",
            default_index=0,
                         styles={
                 "container": {"padding": "0!important", "background-color": "#f0f4ff"},
                 "icon": {"color": "#1e3a8a", "font-size": "18px"},
                 "nav-link": {
                     "font-size": "16px",
                     "text-align": "left",
                     "margin": "0px",
                     "--hover-color": "#dbeafe",
                     "color": "#333"
                 },
                 "nav-link-selected": {"background-color": "#1e3a8a","color": "#fff"},
                 "nav-link-active": {"background-color": "#1e3a8a","color": "#fff"},
             },
        )
    
    # Contenido principal
    if selected == "🏠 Inicio":
        show_home()
    elif selected == "🫐 Producto Terminado":
        show_finished_product()
    #elif selected == "📊 Control de Calidad":
    #    show_quality_control()
    #elif selected == "📈 Reportes":
    #    show_reports()
    #elif selected == "⚙️ Configuración":
    #    show_settings()

if __name__ == "__main__":
    main()
