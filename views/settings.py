"""
Vista de Configuración para PT_CALIDAD
"""

import streamlit as st
import json
import os
from datetime import datetime

def show_settings():
    """Mostrar la página de configuración"""
    
    st.markdown('<h1 class="main-header">⚙️ Configuración del Sistema</h1>', unsafe_allow_html=True)
    
    # Pestañas de configuración
    tab1, tab2, tab3, tab4 = st.tabs(["🔧 General", "👥 Usuarios", "📊 Criterios", "💾 Base de Datos"])
    
    with tab1:
        show_general_settings()
    
    with tab2:
        show_user_settings()
    
    with tab3:
        show_criteria_settings()
    
    with tab4:
        show_database_settings()

def show_general_settings():
    """Mostrar configuración general"""
    
    st.markdown('<h3 class="sub-header">🔧 Configuración General</h3>', unsafe_allow_html=True)
    
    with st.form("general_settings_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Información de la Empresa")
            company_name = st.text_input("Nombre de la Empresa", value="Mi Empresa S.A.")
            company_address = st.text_area("Dirección", value="Calle Principal 123, Ciudad")
            company_phone = st.text_input("Teléfono", value="+1 234 567 8900")
            company_email = st.text_input("Email", value="contacto@miempresa.com")
        
        with col2:
            st.subheader("Configuración del Sistema")
            app_title = st.text_input("Título de la Aplicación", value="PT_CALIDAD")
            app_version = st.text_input("Versión", value="1.0.0")
            timezone = st.selectbox("Zona Horaria", ["UTC", "America/Mexico_City", "Europe/Madrid", "America/New_York"])
            language = st.selectbox("Idioma", ["Español", "English", "Français"])
        
        st.markdown("---")
        
        st.subheader("Configuración de Notificaciones")
        
        col1, col2 = st.columns(2)
        
        with col1:
            email_notifications = st.checkbox("Notificaciones por Email", value=True)
            sms_notifications = st.checkbox("Notificaciones por SMS", value=False)
            daily_reports = st.checkbox("Reportes Diarios Automáticos", value=True)
        
        with col2:
            weekly_reports = st.checkbox("Reportes Semanales Automáticos", value=True)
            monthly_reports = st.checkbox("Reportes Mensuales Automáticos", value=True)
            alert_threshold = st.number_input("Umbral de Alerta (%)", 1, 100, 85)
        
        # Botón de guardar
        submitted = st.form_submit_button("💾 Guardar Configuración General")
        
        if submitted:
            st.success("Configuración general guardada exitosamente!")

def show_user_settings():
    """Mostrar configuración de usuarios"""
    
    st.markdown('<h3 class="sub-header">👥 Gestión de Usuarios</h3>', unsafe_allow_html=True)
    
    # Pestañas para gestión de usuarios
    user_tab1, user_tab2 = st.tabs(["👤 Usuarios", "🔐 Roles y Permisos"])
    
    with user_tab1:
        st.subheader("Lista de Usuarios")
        
        # Datos de ejemplo de usuarios
        users_data = {
            'Usuario': ['admin', 'ana.garcia', 'carlos.lopez', 'maria.rodriguez'],
            'Nombre': ['Administrador', 'Ana García', 'Carlos López', 'María Rodríguez'],
            'Email': ['admin@empresa.com', 'ana@empresa.com', 'carlos@empresa.com', 'maria@empresa.com'],
            'Rol': ['Administrador', 'Evaluador', 'Supervisor', 'Evaluador'],
            'Estado': ['✅ Activo', '✅ Activo', '✅ Activo', '⏸️ Inactivo'],
            'Último Acceso': ['2024-12-20 14:30', '2024-12-20 13:15', '2024-12-20 12:45', '2024-12-19 16:20']
        }
        
        df_users = pd.DataFrame(users_data)
        st.dataframe(df_users, use_container_width=True)
        
        # Formulario para agregar usuario
        with st.expander("➕ Agregar Nuevo Usuario"):
            with st.form("add_user_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    new_username = st.text_input("Nombre de Usuario")
                    new_name = st.text_input("Nombre Completo")
                    new_email = st.text_input("Email")
                
                with col2:
                    new_role = st.selectbox("Rol", ["Evaluador", "Supervisor", "Administrador"])
                    new_password = st.text_input("Contraseña", type="password")
                    new_status = st.selectbox("Estado", ["Activo", "Inactivo"])
                
                add_user = st.form_submit_button("➕ Agregar Usuario")
                
                if add_user:
                    st.success("Usuario agregado exitosamente!")
    
    with user_tab2:
        st.subheader("Roles y Permisos")
        
        # Definición de roles
        roles_data = {
            'Rol': ['Administrador', 'Supervisor', 'Evaluador'],
            'Evaluaciones': ['✅ Lectura/Escritura', '✅ Lectura/Escritura', '✅ Lectura/Escritura'],
            'Reportes': ['✅ Lectura/Escritura', '✅ Lectura', '❌ Sin Acceso'],
            'Configuración': ['✅ Lectura/Escritura', '❌ Sin Acceso', '❌ Sin Acceso'],
            'Usuarios': ['✅ Lectura/Escritura', '❌ Sin Acceso', '❌ Sin Acceso']
        }
        
        df_roles = pd.DataFrame(roles_data)
        st.dataframe(df_roles, use_container_width=True)
        
        # Configuración de permisos
        with st.expander("🔐 Configurar Permisos"):
            selected_role = st.selectbox("Seleccionar Rol", ["Administrador", "Supervisor", "Evaluador"])
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.checkbox("Evaluaciones - Lectura", value=True)
                st.checkbox("Evaluaciones - Escritura", value=True)
                st.checkbox("Reportes - Lectura", value=True)
                st.checkbox("Reportes - Escritura", value=False)
            
            with col2:
                st.checkbox("Configuración - Lectura", value=False)
                st.checkbox("Configuración - Escritura", value=False)
                st.checkbox("Usuarios - Lectura", value=False)
                st.checkbox("Usuarios - Escritura", value=False)
            
            if st.button("💾 Guardar Permisos"):
                st.success("Permisos guardados exitosamente!")

def show_criteria_settings():
    """Mostrar configuración de criterios"""
    
    st.markdown('<h3 class="sub-header">📊 Configuración de Criterios</h3>', unsafe_allow_html=True)
    
    # Criterios actuales
    st.subheader("Criterios de Evaluación Actuales")
    
    criteria_data = {
        'Criterio': ['Aspecto Visual', 'Dimensiones', 'Funcionalidad', 'Embalaje', 'Peso'],
        'Peso (%)': [25, 30, 35, 5, 5],
        'Puntuación Mínima': [7, 8, 8, 6, 7],
        'Descripción': [
            'Evaluación del aspecto visual del producto',
            'Verificación de dimensiones según especificaciones',
            'Pruebas de funcionalidad básica',
            'Estado del embalaje y etiquetado',
            'Verificación del peso del producto'
        ]
    }
    
    df_criteria = pd.DataFrame(criteria_data)
    st.dataframe(df_criteria, use_container_width=True)
    
    # Configuración de criterios
    with st.form("criteria_settings_form"):
        st.subheader("Configurar Criterios")
        
        col1, col2 = st.columns(2)
        
        with col1:
            min_score_approval = st.number_input("Puntuación Mínima para Aprobación", 1, 10, 8)
            max_defects_allowed = st.number_input("Máximo Defectos Permitidos", 0, 10, 2)
            auto_reject_threshold = st.number_input("Umbral de Rechazo Automático (%)", 1, 100, 70)
        
        with col2:
            min_severity_rejection = st.selectbox("Severidad Mínima para Rechazo", ["Baja", "Media", "Alta", "Crítica"])
            require_photos = st.checkbox("Requerir fotos de defectos", value=True)
            require_notes = st.checkbox("Requerir notas descriptivas", value=True)
        
        st.markdown("---")
        
        st.subheader("Configuración de Defectos")
        
        defect_types = st.multiselect(
            "Tipos de Defectos Disponibles",
            ["Dimensión incorrecta", "Color irregular", "Peso fuera de rango", 
             "Embalaje defectuoso", "Rayones", "Manchas", "Falta de piezas", 
             "Funcionamiento defectuoso", "Etiquetado incorrecto", "Otros"],
            default=["Dimensión incorrecta", "Color irregular", "Peso fuera de rango", 
                    "Embalaje defectuoso", "Rayones", "Manchas", "Otros"]
        )
        
        # Botón de guardar
        submitted = st.form_submit_button("💾 Guardar Configuración de Criterios")
        
        if submitted:
            st.success("Configuración de criterios guardada exitosamente!")

def show_database_settings():
    """Mostrar configuración de base de datos"""
    
    st.markdown('<h3 class="sub-header">💾 Configuración de Base de Datos</h3>', unsafe_allow_html=True)
    
    # Estado de la base de datos
    st.subheader("Estado de la Base de Datos")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Estado", "✅ Conectada")
    
    with col2:
        st.metric("Tipo", "SQLite")
    
    with col3:
        st.metric("Tamaño", "2.3 MB")
    
    with col4:
        st.metric("Registros", "1,247")
    
    # Configuración de conexión
    with st.form("database_settings_form"):
        st.subheader("Configuración de Conexión")
        
        col1, col2 = st.columns(2)
        
        with col1:
            db_type = st.selectbox("Tipo de Base de Datos", ["SQLite", "PostgreSQL", "MySQL", "SQL Server"])
            db_host = st.text_input("Host", value="localhost")
            db_port = st.number_input("Puerto", value=5432)
        
        with col2:
            db_name = st.text_input("Nombre de Base de Datos", value="pt_calidad")
            db_user = st.text_input("Usuario", value="admin")
            db_password = st.text_input("Contraseña", type="password", value="")
        
        # Configuración de respaldo
        st.markdown("---")
        st.subheader("Configuración de Respaldo")
        
        col1, col2 = st.columns(2)
        
        with col1:
            auto_backup = st.checkbox("Respaldo Automático", value=True)
            backup_frequency = st.selectbox("Frecuencia de Respaldo", ["Diario", "Semanal", "Mensual"])
            backup_retention = st.number_input("Días de Retención", 1, 365, 30)
        
        with col2:
            backup_location = st.text_input("Ubicación de Respaldo", value="/backups/")
            compress_backups = st.checkbox("Comprimir Respaldos", value=True)
            encrypt_backups = st.checkbox("Encriptar Respaldos", value=False)
        
        # Botones de acción
        col1, col2, col3 = st.columns(3)
        
        with col1:
            test_connection = st.form_submit_button("🔍 Probar Conexión")
        
        with col2:
            create_backup = st.form_submit_button("💾 Crear Respaldo")
        
        with col3:
            save_config = st.form_submit_button("💾 Guardar Configuración")
        
        if test_connection:
            st.success("Conexión exitosa a la base de datos!")
        
        if create_backup:
            st.success("Respaldo creado exitosamente!")
        
        if save_config:
            st.success("Configuración de base de datos guardada!")

# Importar pandas para los datos de ejemplo
