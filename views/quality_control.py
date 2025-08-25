"""
Vista de Control de Calidad para PT_CALIDAD
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

def show_quality_control():
    """Mostrar la página de control de calidad"""
    
    st.markdown('<h1 class="main-header">📊 Control de Calidad</h1>', unsafe_allow_html=True)
    
    # Pestañas para diferentes funcionalidades
    tab1, tab2, tab3, tab4 = st.tabs(["🔍 Nueva Evaluación", "📋 Historial", "📊 Análisis", "⚙️ Criterios"])
    
    with tab1:
        show_new_evaluation()
    
    with tab2:
        show_evaluation_history()
    
    with tab3:
        show_quality_analysis()
    
    with tab4:
        show_quality_criteria()

def show_new_evaluation():
    """Mostrar formulario de nueva evaluación"""
    
    st.markdown('<h3 class="sub-header">🔍 Nueva Evaluación de Calidad</h3>', unsafe_allow_html=True)
    
    # Formulario de evaluación
    with st.form("quality_evaluation_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Información del Producto")
            product_code = st.text_input("Código del Producto", placeholder="Ej: PROD-001")
            product_name = st.text_input("Nombre del Producto", placeholder="Ej: Producto XYZ")
            batch_number = st.text_input("Número de Lote", placeholder="Ej: LOTE-2024-001")
            quantity = st.number_input("Cantidad Evaluada", min_value=1, value=100)
        
        with col2:
            st.subheader("Información de Evaluación")
            evaluator = st.text_input("Evaluador", placeholder="Nombre del evaluador")
            evaluation_date = st.date_input("Fecha de Evaluación", value=datetime.now())
            shift = st.selectbox("Turno", ["Mañana", "Tarde", "Noche"])
            line = st.selectbox("Línea de Producción", ["Línea A", "Línea B", "Línea C"])
        
        st.markdown("---")
        
        # Criterios de evaluación
        st.subheader("Criterios de Evaluación")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**Aspecto Visual**")
            visual_score = st.slider("Puntuación Visual (1-10)", 1, 10, 8)
            visual_notes = st.text_area("Notas Visuales", placeholder="Observaciones sobre aspecto visual...")
        
        with col2:
            st.markdown("**Dimensiones**")
            dimension_score = st.slider("Puntuación Dimensiones (1-10)", 1, 10, 9)
            dimension_notes = st.text_area("Notas Dimensiones", placeholder="Observaciones sobre dimensiones...")
        
        with col3:
            st.markdown("**Funcionalidad**")
            functionality_score = st.slider("Puntuación Funcionalidad (1-10)", 1, 10, 9)
            functionality_notes = st.text_area("Notas Funcionalidad", placeholder="Observaciones sobre funcionalidad...")
        
        # Defectos encontrados
        st.subheader("Defectos Detectados")
        
        col1, col2 = st.columns(2)
        
        with col1:
            defect_types = st.multiselect(
                "Tipos de Defectos",
                ["Dimensión incorrecta", "Color irregular", "Peso fuera de rango", 
                 "Embalaje defectuoso", "Rayones", "Manchas", "Otros"],
                default=[]
            )
            
            defect_quantity = st.number_input("Cantidad de Defectos", min_value=0, value=0)
        
        with col2:
            defect_severity = st.selectbox("Severidad de Defectos", ["Baja", "Media", "Alta", "Crítica"])
            defect_notes = st.text_area("Descripción de Defectos", placeholder="Descripción detallada de los defectos...")
        
        # Botón de envío
        submitted = st.form_submit_button("📝 Guardar Evaluación")
        
        if submitted:
            # Calcular puntuación total
            total_score = (visual_score + dimension_score + functionality_score) / 3
            
            # Determinar resultado
            if total_score >= 8 and defect_quantity == 0:
                result = "✅ APROBADO"
                st.success("Evaluación guardada exitosamente!")
            elif total_score >= 6 and defect_quantity <= 2:
                result = "⚠️ APROBADO CON OBSERVACIONES"
                st.warning("Evaluación guardada con observaciones.")
            else:
                result = "❌ RECHAZADO"
                st.error("Producto rechazado por no cumplir estándares de calidad.")
            
            # Mostrar resumen
            st.markdown("### Resumen de Evaluación")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Puntuación Total", f"{total_score:.1f}/10")
            
            with col2:
                st.metric("Defectos", defect_quantity)
            
            with col3:
                st.metric("Resultado", result)

def show_evaluation_history():
    """Mostrar historial de evaluaciones"""
    
    st.markdown('<h3 class="sub-header">📋 Historial de Evaluaciones</h3>', unsafe_allow_html=True)
    
    # Filtros
    col1, col2, col3 = st.columns(3)
    
    with col1:
        date_from = st.date_input("Desde", value=datetime.now().replace(day=1))
    
    with col2:
        date_to = st.date_input("Hasta", value=datetime.now())
    
    with col3:
        result_filter = st.selectbox("Resultado", ["Todos", "Aprobado", "Rechazado", "Con Observaciones"])
    
    # Datos de ejemplo
    history_data = {
        'Fecha': ['2024-12-20', '2024-12-19', '2024-12-18', '2024-12-17', '2024-12-16'],
        'Producto': ['PROD-001', 'PROD-002', 'PROD-003', 'PROD-004', 'PROD-005'],
        'Lote': ['LOTE-2024-001', 'LOTE-2024-002', 'LOTE-2024-003', 'LOTE-2024-004', 'LOTE-2024-005'],
        'Evaluador': ['Ana García', 'Carlos López', 'María Rodríguez', 'Juan Pérez', 'Ana García'],
        'Puntuación': [8.5, 7.2, 9.1, 6.8, 8.9],
        'Defectos': [0, 2, 0, 3, 1],
        'Resultado': ['✅ Aprobado', '⚠️ Con Obs.', '✅ Aprobado', '❌ Rechazado', '✅ Aprobado']
    }
    
    df_history = pd.DataFrame(history_data)
    st.dataframe(df_history, use_container_width=True)
    
    # Estadísticas del período
    st.markdown("### Estadísticas del Período")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Evaluaciones", len(df_history))
    
    with col2:
        approved = len(df_history[df_history['Resultado'].str.contains('Aprobado')])
        st.metric("Aprobadas", approved)
    
    with col3:
        rejected = len(df_history[df_history['Resultado'].str.contains('Rechazado')])
        st.metric("Rechazadas", rejected)
    
    with col4:
        avg_score = df_history['Puntuación'].mean()
        st.metric("Puntuación Promedio", f"{avg_score:.1f}")

def show_quality_analysis():
    """Mostrar análisis de calidad"""
    
    st.markdown('<h3 class="sub-header">📊 Análisis de Calidad</h3>', unsafe_allow_html=True)
    
    # Gráficos de análisis
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Tendencia de Puntuaciones**")
        
        # Datos de ejemplo
        dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='W')
        scores = [8.2 + np.random.normal(0, 0.5) for _ in range(len(dates))]
        
        df_trend = pd.DataFrame({'Fecha': dates, 'Puntuación': scores})
        
        fig_trend = px.line(df_trend, x='Fecha', y='Puntuación', 
                           title='Evolución Semanal de Calidad')
        st.plotly_chart(fig_trend, use_container_width=True)
    
    with col2:
        st.markdown("**Distribución de Resultados**")
        
        results = ['Aprobado', 'Con Observaciones', 'Rechazado']
        counts = [75, 15, 10]
        
        fig_pie = px.pie(values=counts, names=results, title='Distribución de Resultados')
        st.plotly_chart(fig_pie, use_container_width=True)
    
    # Análisis por línea de producción
    st.markdown("### Análisis por Línea de Producción")
    
    line_data = {
        'Línea': ['Línea A', 'Línea B', 'Línea C'],
        'Evaluaciones': [45, 38, 42],
        'Puntuación Promedio': [8.7, 8.2, 8.9],
        'Tasa de Aceptación': [96.2, 94.1, 97.8]
    }
    
    df_lines = pd.DataFrame(line_data)
    st.dataframe(df_lines, use_container_width=True)

def show_quality_criteria():
    """Mostrar criterios de calidad"""
    
    st.markdown('<h3 class="sub-header">⚙️ Criterios de Calidad</h3>', unsafe_allow_html=True)
    
    # Criterios actuales
    st.subheader("Criterios Actuales")
    
    criteria_data = {
        'Criterio': ['Aspecto Visual', 'Dimensiones', 'Funcionalidad', 'Embalaje'],
        'Peso (%)': [25, 30, 35, 10],
        'Puntuación Mínima': [7, 8, 8, 6],
        'Descripción': [
            'Evaluación del aspecto visual del producto',
            'Verificación de dimensiones según especificaciones',
            'Pruebas de funcionalidad básica',
            'Estado del embalaje y etiquetado'
        ]
    }
    
    df_criteria = pd.DataFrame(criteria_data)
    st.dataframe(df_criteria, use_container_width=True)
    
    # Configuración de criterios
    st.subheader("Configurar Criterios")
    
    with st.form("criteria_config_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.number_input("Puntuación Mínima para Aprobación", 1, 10, 8)
            st.number_input("Máximo Defectos Permitidos", 0, 10, 2)
        
        with col2:
            st.selectbox("Severidad Mínima para Rechazo", ["Baja", "Media", "Alta", "Crítica"])
            st.checkbox("Requerir fotos de defectos")
        
        st.form_submit_button("💾 Guardar Configuración")
