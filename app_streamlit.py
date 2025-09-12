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

from views.despacho import show_despacho
from views.pruebas import show_pruebas
from utils.config import load_config

from styles import load_css

# Función de autenticación
def authenticate_user(username, password):
    """Autentica al usuario con credenciales específicas"""
    return username == "admin_apg" and password == "2025apg"

def login_form():
    """Muestra el formulario de login con diseño mejorado"""
    
    # Estilos CSS mejorados para el login
    st.markdown("""
    <style>
    .container {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100vh;
        flex-direction: column;
    }
    .form-container {
        width: 300px;
        padding: 20px;
        box-shadow: 0 0 15px rgba(0, 0, 0, 0.2);
        border-radius: 10px;
    }
    .logo {
        text-align: center;
        margin-bottom: 0px;
    }
    .logo img {
        max-width: 100px;
    }
    .title {
        text-align: center;
        font-size: 45px;
        font-weight: bold;
        margin-bottom: 20px;
        margin-top: 1px;
    }
    [data-testid="stForm"]{
        width : 380px;
        align-self : center;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # HTML Structure
    
    
    # Logo centrado
    st.markdown('<div class="logo"><img src="http://34.136.15.241:3000/logo.png" alt="Logo" style="width: 70px; height: auto;"></div>', unsafe_allow_html=True)
    st.markdown('<div class="title" style="letter-spacing: -.015em;"><b class="colorT1" style="color:#1f2937;">Bien</b><b class="colorT2" style="color:#1f2937;">venido</b></div>', unsafe_allow_html=True)
    # Título de bienvenida
    
    
    # Formulario de login
    with st.form("login", clear_on_submit=False):
        username = st.text_input("Usuario", placeholder="Ingresa tu usuario", key="login_user", label_visibility="visible")
        password = st.text_input("Contraseña", type="password", placeholder="Ingresa tu contraseña", key="login_pass", label_visibility="visible")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            submitted = st.form_submit_button("Iniciar Sesión", use_container_width=True)
        
        if submitted:
            if authenticate_user(username, password):
                st.session_state.authenticated = True
                st.session_state.username = username
                st.success("✅ ¡Bienvenido! Accediendo al sistema...")
                st.rerun()
            else:
                st.error("❌ Usuario o contraseña incorrectos")
    
    # Cerrar HTML structure
    
def logout():
    """Cierra la sesión del usuario"""
    st.session_state.authenticated = False
    st.session_state.username = None
    st.rerun()

def main():
    """Función principal de la aplicación"""
    
    # Configurar página
    st.set_page_config(
        page_title="APG PACKING",
        page_icon="🔍",
        layout="wide",
        initial_sidebar_state="auto"
    )
    st.logo("./assets/logo.jpg")  
    
    # Cargar estilos CSS
    load_css()
    
    # Cargar configuración
    config = load_config()
    
    # Verificar autenticación
    #if 'authenticated' not in st.session_state:
    #    st.session_state.authenticated = False
    
    #if not st.session_state.authenticated:
    #    login_form()
    #    return
    
    # Sidebar con navegación
    with st.sidebar:
        st.title("🔍 PACKING")
        
        
        
        
        # Menú de navegación
        selected = option_menu(
                    menu_title=None,
                    options=["🏠 Inicio", "🫐 Producto Terminado", "🚚 Despacho"],
                    icons=["house", "check-circle", "truck", "search"],
                    menu_icon="cast",
                    default_index=0,
                                styles={
                        "container": {"padding": "0!important", "background-color": "#f0f4ff"},
                        "icon": {"color": "white", "font-size": "18px"},
                        "nav-link": {
                            "font-size": "16px",
                            "text-align": "left",
                            "margin": "0px",
                            "--hover-color": "#dbeafe",
                            "color": "#333"
                        },
                        "nav-link-selected": {"background-color": "#1f2937","color": "#fff"},
                        "nav-link-active": {"background-color": "#1f2937","color": "#fff"},
                    },
                )
                # Mostrar información del usuario y botón de logout
        #st.markdown("---")
        #col1, col2 = st.columns([3, 1])
        #with col1:
        #    st.markdown(f"👤 **{st.session_state.username}**")
        #with col2:
        #    if st.button("🚪", help="Cerrar sesión", key="logout_btn"):
        #            logout()
            # Contenido principal
    if selected == "🏠 Inicio":
            show_home()
    elif selected == "🫐 Producto Terminado":
            show_finished_product()
    elif selected == "🚚 Despacho":
            show_despacho()
    elif selected == "🔍 Pruebas":
            show_pruebas()

    #elif selected == "📊 Control de Calidad":
    #    show_quality_control()
    #elif selected == "📈 Reportes":
    #    show_reports()
    #elif selected == "⚙️ Configuración":
    #    show_settings()

if __name__ == "__main__":
    main()
