"""
Vista de Reportes para PT_CALIDAD
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def show_reports():
    """Mostrar la página de reportes"""
    
    st.markdown('<h1 class="main-header">📈 Reportes de Calidad</h1>', unsafe_allow_html=True)
    
    # Pestañas para diferentes tipos de reportes
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Dashboard", "📋 Reporte Diario", "📈 Reporte Semanal", "📅 Reporte Mensual", "📊 Pruebas"])
    
    with tab1:
        show_dashboard()
    
    with tab2:
        show_daily_report()
    
    with tab3:
        show_weekly_report()
    
    with tab4:
        show_monthly_report()
    
    with tab5:
        show_test_data()

def show_dashboard():
    """Mostrar dashboard principal"""
    
    st.markdown('<h3 class="sub-header">📊 Dashboard de Calidad</h3>', unsafe_allow_html=True)
    
    # Filtros de fecha
    col1, col2, col3 = st.columns(3)
    
    with col1:
        period = st.selectbox("Período", ["Hoy", "Última Semana", "Último Mes", "Último Trimestre"])
    
    with col2:
        line_filter = st.selectbox("Línea de Producción", ["Todas", "Línea A", "Línea B", "Línea C"])
    
    with col3:
        evaluator_filter = st.selectbox("Evaluador", ["Todos", "Ana García", "Carlos López", "María Rodríguez"])
    
    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Evaluaciones", "156", "↑ 12%")
    
    with col2:
        st.metric("Tasa de Aceptación", "98.5%", "↑ 2.1%")
    
    with col3:
        st.metric("Puntuación Promedio", "8.7/10", "↑ 0.3")
    
    with col4:
        st.metric("Defectos Detectados", "12", "↓ 3")
    
    # Gráficos principales
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Evolución de Calidad**")
        
        # Datos de ejemplo
        dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
        quality_scores = [8.0 + np.random.normal(0, 0.3) for _ in range(len(dates))]
        
        df_quality = pd.DataFrame({
            'Fecha': dates,
            'Puntuación': quality_scores
        })
        
        fig_quality = px.line(df_quality, x='Fecha', y='Puntuación',
                             title='Evolución de Puntuación de Calidad')
        fig_quality.add_hline(y=8.0, line_dash="dash", line_color="red", 
                             annotation_text="Límite Mínimo")
        st.plotly_chart(fig_quality, use_container_width=True)
    
    with col2:
        st.markdown("**Distribución de Defectos por Tipo**")
        
        defect_types = ['Dimensión', 'Color', 'Peso', 'Embalaje', 'Otros']
        defect_counts = [5, 3, 2, 1, 1]
        
        fig_defects = px.bar(x=defect_types, y=defect_counts,
                            title='Defectos por Tipo',
                            color=defect_counts,
                            color_continuous_scale='Reds')
        st.plotly_chart(fig_defects, use_container_width=True)
    
    # Análisis por línea de producción
    st.markdown("### Análisis por Línea de Producción")
    
    line_data = {
        'Línea': ['Línea A', 'Línea B', 'Línea C'],
        'Evaluaciones': [45, 38, 42],
        'Puntuación Promedio': [8.7, 8.2, 8.9],
        'Tasa de Aceptación (%)': [96.2, 94.1, 97.8],
        'Defectos': [3, 5, 2]
    }
    
    df_lines = pd.DataFrame(line_data)
    
    # Gráfico de líneas
    fig_lines = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Puntuación Promedio por Línea', 'Tasa de Aceptación por Línea'),
        specs=[[{"type": "bar"}, {"type": "bar"}]]
    )
    
    fig_lines.add_trace(
        go.Bar(x=df_lines['Línea'], y=df_lines['Puntuación Promedio'], name='Puntuación'),
        row=1, col=1
    )
    
    fig_lines.add_trace(
        go.Bar(x=df_lines['Línea'], y=df_lines['Tasa de Aceptación (%)'], name='Aceptación'),
        row=1, col=2
    )
    
    fig_lines.update_layout(height=400, showlegend=False)
    st.plotly_chart(fig_lines, use_container_width=True)
    
    # Tabla de resumen
    st.dataframe(df_lines, use_container_width=True)

def show_daily_report():
    """Mostrar reporte diario"""
    
    st.markdown('<h3 class="sub-header">📋 Reporte Diario</h3>', unsafe_allow_html=True)
    
    # Selección de fecha
    report_date = st.date_input("Fecha del Reporte", value=datetime.now())
    
    # Generar reporte
    if st.button("📊 Generar Reporte Diario"):
        
        # Datos de ejemplo para el día seleccionado
        daily_data = {
            'Hora': ['08:00', '10:00', '12:00', '14:00', '16:00', '18:00'],
            'Producto': ['PROD-001', 'PROD-002', 'PROD-003', 'PROD-004', 'PROD-005', 'PROD-006'],
            'Línea': ['A', 'B', 'C', 'A', 'B', 'C'],
            'Evaluador': ['Ana García', 'Carlos López', 'María Rodríguez', 'Ana García', 'Carlos López', 'María Rodríguez'],
            'Puntuación': [8.5, 7.8, 9.2, 8.9, 8.1, 9.0],
            'Defectos': [0, 1, 0, 0, 2, 0],
            'Resultado': ['✅ Aprobado', '⚠️ Con Obs.', '✅ Aprobado', '✅ Aprobado', '⚠️ Con Obs.', '✅ Aprobado']
        }
        
        df_daily = pd.DataFrame(daily_data)
        
        # Resumen del día
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Evaluaciones Realizadas", len(df_daily))
        
        with col2:
            approved = len(df_daily[df_daily['Resultado'].str.contains('Aprobado')])
            st.metric("Productos Aprobados", approved)
        
        with col3:
            avg_score = df_daily['Puntuación'].mean()
            st.metric("Puntuación Promedio", f"{avg_score:.1f}/10")
        
        with col4:
            total_defects = df_daily['Defectos'].sum()
            st.metric("Total Defectos", total_defects)
        
        # Gráfico de tendencia del día
        fig_daily = px.line(df_daily, x='Hora', y='Puntuación',
                           title=f'Puntuación de Calidad - {report_date.strftime("%d/%m/%Y")}')
        fig_daily.add_hline(y=8.0, line_dash="dash", line_color="red", 
                           annotation_text="Límite Mínimo")
        st.plotly_chart(fig_daily, use_container_width=True)
        
        # Tabla detallada
        st.markdown("### Detalle de Evaluaciones")
        st.dataframe(df_daily, use_container_width=True)
        
        # Exportar reporte
        csv = df_daily.to_csv(index=False)
        st.download_button(
            label="📥 Descargar Reporte CSV",
            data=csv,
            file_name=f"reporte_diario_{report_date.strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

def show_weekly_report():
    """Mostrar reporte semanal"""
    
    st.markdown('<h3 class="sub-header">📈 Reporte Semanal</h3>', unsafe_allow_html=True)
    
    # Selección de semana
    week_start = st.date_input("Inicio de Semana", value=datetime.now().replace(day=1))
    
    if st.button("📊 Generar Reporte Semanal"):
        
        # Datos de ejemplo para la semana
        week_data = {
            'Día': ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'],
            'Evaluaciones': [25, 28, 22, 30, 26, 15, 10],
            'Puntuación Promedio': [8.4, 8.7, 8.2, 8.9, 8.6, 8.3, 8.5],
            'Defectos': [2, 1, 3, 0, 2, 1, 0],
            'Tasa Aceptación (%)': [96.0, 97.1, 94.5, 100.0, 95.8, 96.7, 100.0]
        }
        
        df_week = pd.DataFrame(week_data)
        
        # Resumen de la semana
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Evaluaciones", df_week['Evaluaciones'].sum())
        
        with col2:
            st.metric("Puntuación Promedio", f"{df_week['Puntuación Promedio'].mean():.1f}/10")
        
        with col3:
            st.metric("Total Defectos", df_week['Defectos'].sum())
        
        with col4:
            st.metric("Tasa Aceptación Promedio", f"{df_week['Tasa Aceptación (%)'].mean():.1f}%")
        
        # Gráficos semanales
        col1, col2 = st.columns(2)
        
        with col1:
            fig_evaluations = px.bar(df_week, x='Día', y='Evaluaciones',
                                   title='Evaluaciones por Día')
            st.plotly_chart(fig_evaluations, use_container_width=True)
        
        with col2:
            fig_scores = px.line(df_week, x='Día', y='Puntuación Promedio',
                               title='Puntuación Promedio por Día')
            fig_scores.add_hline(y=8.0, line_dash="dash", line_color="red")
            st.plotly_chart(fig_scores, use_container_width=True)
        
        # Tabla de resumen semanal
        st.dataframe(df_week, use_container_width=True)

def show_monthly_report():
    """Mostrar reporte mensual"""
    
    st.markdown('<h3 class="sub-header">📅 Reporte Mensual</h3>', unsafe_allow_html=True)
    
    # Selección de mes
    month_year = st.date_input("Mes y Año", value=datetime.now())
    
    if st.button("📊 Generar Reporte Mensual"):
        
        # Datos de ejemplo para el mes
        month_data = {
            'Semana': ['Semana 1', 'Semana 2', 'Semana 3', 'Semana 4'],
            'Evaluaciones': [120, 135, 128, 142],
            'Puntuación Promedio': [8.3, 8.6, 8.4, 8.8],
            'Defectos': [8, 5, 7, 3],
            'Tasa Aceptación (%)': [95.8, 97.2, 96.5, 98.1]
        }
        
        df_month = pd.DataFrame(month_data)
        
        # Resumen del mes
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Evaluaciones", df_month['Evaluaciones'].sum())
        
        with col2:
            st.metric("Puntuación Promedio", f"{df_month['Puntuación Promedio'].mean():.1f}/10")
        
        with col3:
            st.metric("Total Defectos", df_month['Defectos'].sum())
        
        with col4:
            st.metric("Tasa Aceptación Promedio", f"{df_month['Tasa Aceptación (%)'].mean():.1f}%")
        
        # Gráfico de tendencia mensual
        fig_month = px.line(df_month, x='Semana', y=['Puntuación Promedio', 'Tasa Aceptación (%)'],
                           title='Tendencia Mensual de Calidad',
                           labels={'value': 'Valor', 'variable': 'Métrica'})
        st.plotly_chart(fig_month, use_container_width=True)
        
        # Análisis por línea de producción (mensual)
        st.markdown("### Análisis por Línea de Producción - Mes")
        
        line_monthly_data = {
            'Línea': ['Línea A', 'Línea B', 'Línea C'],
            'Evaluaciones': [180, 165, 175],
            'Puntuación Promedio': [8.6, 8.3, 8.7],
            'Tasa de Aceptación (%)': [96.8, 95.2, 97.1],
            'Defectos': [6, 8, 5]
        }
        
        df_line_monthly = pd.DataFrame(line_monthly_data)
        st.dataframe(df_line_monthly, use_container_width=True)
        
        # Gráfico de líneas mensual
        fig_lines_monthly = px.bar(df_line_monthly, x='Línea', y=['Evaluaciones', 'Defectos'],
                                 title='Evaluaciones y Defectos por Línea - Mes',
                                 barmode='group')
        st.plotly_chart(fig_lines_monthly, use_container_width=True)




