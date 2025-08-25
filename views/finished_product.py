"""
Vista de Evaluaciones de Producto Terminado para PT_CALIDAD
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from utils.get_api import listar_archivos_en_carpeta_compartida, get_download_url_by_name
from utils.get_token import get_access_token, get_access_token_alza
from utils.pdf_generator import generate_fcl_pdf_report
import base64
import zipfile
import io
import json


@st.cache_data(show_spinner="Cargando datos...", ttl=3600)
def get_data():
    """Cargar datos principales con cache optimizado"""
    access_token = get_access_token()
    DATAS = listar_archivos_en_carpeta_compartida(access_token, "b!k0xKW2h1VkGnxasDN0z40PeA8yi0BwBKgEf_EOEPStmAWVEVjX8MQIydW1yMzk1b", "01SPKVU4I6RWNBBAVFIJF3GHBOYOFMUKZS")
    data_ = get_download_url_by_name(DATAS, "BD EVALUACION DE CALIDAD DE PRODUCTO TERMINADO.xlsx")
    df = pd.read_excel(data_, sheet_name="CALIDAD PRODUCTO TERMINADO")
    return df


@st.cache_data(show_spinner="Cargando images...",ttl=3600)
def get_images():
    """Cargar solo metadatos de imágenes para optimizar rendimiento"""
    access_token = get_access_token_alza()
    DATAS = listar_archivos_en_carpeta_compartida(access_token, "b!M5ucw3aa_UqBAcqv3a6affR7vTZM2a5ApFygaKCcATxyLdOhkHDiRKl9EvzaYbuR", "01XOBWFSBLVGULAQNEKNG2WR7CPRACEN7Q")
    data_ = get_download_url_by_name(DATAS, "base64_images_pt.parquet")
    
    df = pd.read_parquet(data_)
    
    df["folder_name"] = df["folder_name"].str.strip()
    df = df.groupby(["folder_name"]).agg({
        "cantidad_images": "sum",
        "base64_complete": lambda x: x.tolist(),
    }).reset_index()
    
    
    return df



def clean_data():
    """Procesar y limpiar datos con cache optimizado"""
    df = get_data()
    
    # Convertir fechas una sola vez
    df["FECHA DE MP"] = pd.to_datetime(df["FECHA DE MP"])
    df["FECHA DE PROCESO"] = pd.to_datetime(df["FECHA DE PROCESO"])

    # Fill NaN values with 0 for all float columns
    float_columns = df.select_dtypes(include=['float64']).columns
    df[float_columns] = df[float_columns].fillna(0)

    # Limpiar datos de manera más eficiente
    replacements = {
        "MODULO ": {"`1": 1},
        "TURNO ": {"Dia": 2, 111: 11},
        "N° FCL": ['None', 'nan', 'NaN', 'NULL', 'null', ''],
        "TRAZABILIDAD": ['None', 'nan', 'NaN', 'NULL', 'null', ''],
        "OBSERVACIONES": ['None', 'nan', 'NaN', 'NULL', 'null', '']
    }
    
    # Aplicar reemplazos de manera vectorizada
    for col, values in replacements.items():
        if col in df.columns:
            if isinstance(values, dict):
                df[col] = df[col].replace(values)
            else:
                df[col] = df[col].replace(values, "-")
    
    # Fill NaN values
    df["TURNO "] = df["TURNO "].fillna(0)
    df["VARIEDAD"] = df["VARIEDAD"].fillna("NO ESPECIFICADO")
    df["PRESENTACION "] = df["PRESENTACION "].fillna("NO ESPECIFICADO")
    df["DESTINO"] = df["DESTINO"].fillna("NO ESPECIFICADO")
    df["TIPO DE CAJA"] = df["TIPO DE CAJA"].fillna("-")
    df["TRAZABILIDAD"] = df["TRAZABILIDAD"].fillna("-")
    
    # Strip strings de manera vectorizada
    string_columns = ["VARIEDAD", "PRESENTACION ", "DESTINO", "TIPO DE CAJA", "TRAZABILIDAD", "N° FCL"]
    for col in string_columns:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
            
    # Mapeo de empresas
    empresa_mapping = {
        'GMH BERRIES S.A.C': 'AGRICOLA BLUE GOLD S.A.C.',
        'BIG BERRIES S.A.C': 'AGRICOLA BLUE GOLD S.A.C.',
        'CANYON BERRIES S.A.C': 'AGRICOLA BLUE GOLD S.A.C.',
        'AGRICOLA BLUE GOLD S.A.C': 'AGRICOLA BLUE GOLD S.A.C.',
        'EXCELLENCE FRUIT S.A.C': "SAN LUCAR S.A.",
        'GAP BERRIES S.A.C': "SAN LUCAR S.A.",
        'SAN EFISIO S.A.C': "SAN LUCAR S.A."
    }
    df["EMPRESA"] = df["PRODUCTOR"].replace(empresa_mapping)
    
    # Filtrar y limpiar - mejorar el filtrado para eliminar NaN
    df = df[df["N° FCL"] != "-"]
    df = df[df["N° FCL"] != "nan"]
    df = df[df["N° FCL"] != "NaN"]
    df = df[df["N° FCL"] != "None"]
    df = df[df["N° FCL"].notna()]  # Eliminar valores NaN de pandas
    df.columns = df.columns.str.strip()
    
    # Fill NaN en columnas numéricas
    numeric_columns = df.select_dtypes(include=['float64', 'int64']).columns
    df[numeric_columns] = df[numeric_columns].fillna(0)
    
    # Agregar información de imágenes (solo metadatos)
    #img_df = get_images()

    #df = df.merge(img_df, left_on="N° FCL", right_on="folder_name", how="left")
    
    
    return df


@st.cache_data(show_spinner="Cargando imágenes específicas...", ttl=300)
def get_fcl_images(fcl_number, df_with_images=None):
    """Cargar imágenes base64 solo para un FCL específico cuando sea necesario"""
    try:
        # Validar que el FCL number no sea NaN o vacío
        if pd.isna(fcl_number) or fcl_number == "" or fcl_number == "nan":
            return []
        
        # Si tenemos el dataframe con imágenes, usarlo directamente
        if df_with_images is not None and 'base64_complete' in df_with_images.columns:
            fcl_data = df_with_images[df_with_images['N° FCL'] == fcl_number]
            if not fcl_data.empty:
                base64_list = fcl_data.iloc[0].get('base64_complete', [])
                if isinstance(base64_list, list):
                    return base64_list
            return []
            
        # Si no tenemos el dataframe, cargar desde la API (fallback)
        access_token = get_access_token_alza()
        DATAS = listar_archivos_en_carpeta_compartida(access_token, "b!M5ucw3aa_UqBAcqv3a6affR7vTZM2a5ApFygaKCcATxyLdOhkHDiRKl9EvzaYbuR", "01XOBWFSBLVGULAQNEKNG2WR7CPRACEN7Q")
        data_ = get_download_url_by_name(DATAS, "base64_images_pt.json")
        df = pd.read_json(data_)
        
        # Filtrar solo el FCL específico
        df["folder_name"] = df["folder_name"].astype(str).fillna("")
        fcl_images = df[df["folder_name"].str.strip() == str(fcl_number)]
        
        if not fcl_images.empty:
            # Obtener todas las imágenes base64 para este FCL
            all_images = []
            for _, row in fcl_images.iterrows():
                base64_list = row.get('base64_complete', [])
                if isinstance(base64_list, list) and len(base64_list) > 0:
                    all_images.extend(base64_list)
            return all_images
        return []
    except Exception as e:
        st.error(f"Error al cargar imágenes para FCL {fcl_number}: {str(e)}")
        return []


def show_finished_product():
    """Mostrar la página de evaluaciones de producto terminado"""
    
    # Verificar si hay una vista específica seleccionada
    if hasattr(st.session_state, 'current_view') and st.session_state.current_view == "fcl_detail":
        show_fcl_detail_view()
        return
    
    df = clean_data()
    
    
    
    st.markdown('<h1 class="main-header">🫐 Evaluación de Producto Terminado</h1>', unsafe_allow_html=True)
    #st.markdown('<h4 style="text-align: center; color: #666;">Datos de calidad de arándanos por contenedor</h4>', unsafe_allow_html=True)
    
    # Preparar datos agrupados de manera optimizada
   
    df = df.sort_values(by="FECHA DE PROCESO", ascending=False)
    # Barra de búsqueda y filtros
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    
    with col1:
        search_term = st.text_input("Buscar por FCL...", placeholder="Ej: EXC080")
    
    
    
    #with col2:
    #    empresa_filter = st.selectbox("Productor", ["Todos"] + list(df["EMPRESA"].unique()))
    
    with col4:
        st.metric("Total FCL", f"{len(df)}")
    
    
    
    # Filtrar datos
    filtered_df = df.copy()
    
    if search_term:
        filtered_df = filtered_df[filtered_df["N° FCL"].str.contains(search_term.upper(), na=False)]
    
   
    
    #if empresa_filter != "Todos":
    #    filtered_df = filtered_df[filtered_df["EMPRESA"] == empresa_filter]
    
    # Paginación
    items_per_page = 10
    total_items = len(filtered_df)
    total_pages = (total_items + items_per_page - 1) // items_per_page
    
    # Selector de página
    
    with col2:
        current_page = st.selectbox(
            f"Página (1-{total_pages})", 
            range(1, total_pages + 1), 
            index=0,
            key="page_selector"
        )
    
    # Calcular índices para la página actual
    start_idx = (current_page - 1) * items_per_page
    end_idx = min(start_idx + items_per_page, total_items)
    
    # Mostrar información de paginación
    st.markdown(f"**Mostrando {start_idx + 1}-{end_idx} de {total_items} FCL**")
    
    
    # Mostrar tarjetas de evaluación para la página actual
    page_df = filtered_df.iloc[start_idx:end_idx]
    
    # Usar st.container para optimizar el renderizado
    with st.container():
        for i, row in page_df.iterrows():
            # Determinar estado basado en BRIX
            
            # Crear tarjeta clickeable con modal
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"""
                <div class="clickable-card" onclick="openModal_{i}()" style="cursor: pointer;">
                    <div class="card-main-info">
                        <h3 style="margin: 0; color: var(--text-color, #333);">📦 {row['N° FCL']}</h3>
                        <p style="margin: 5px 0; color: var(--text-color, #666); font-size: 13px; opacity: 0.8;">
                            📅 {row['FECHA DE PROCESO'].strftime('%d %b %Y')} | 🗓️ Semana {row['SEMANA']}
                        </p>
                        <p style="margin: 2px 0; font-size: 13px; color: var(--text-color, #666); opacity: 0.9;"><strong>Variedad:</strong> {row['VARIEDAD']}</p>
                        <p style="margin: 2px 0; font-size: 13px; color: var(--text-color, #666); opacity: 0.9;"><strong>Productor:</strong> {row['PRODUCTOR']}</p>
                        <p style="margin: 2px 0; font-size: 13px; color: var(--text-color, #666); opacity: 0.9;"><strong>Presentación:</strong> {row['PRESENTACION']}</p>
                        <p style="margin: 2px 0; font-size: 13px; color: var(--text-color, #666); opacity: 0.9;"><strong>BRIX:</strong> {row['BRIX']:.2f}</p>
                        <p style="margin: 2px 0; font-size: 13px; color: var(--text-color, #666); opacity: 0.9;"><strong>Acidez:</strong> {row['ACIDEZ']:.2f}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                if st.button("👁️ Ver Detalles", key=f"detail_{i}", help="Ver detalles completos",use_container_width=True):
                    # Guardar el FCL seleccionado en session_state para la nueva vista
                    st.session_state.selected_fcl = row['N° FCL']
                    st.session_state.selected_fcl_data = row
                    st.session_state.current_view = "fcl_detail"
                    st.rerun()
                #if st.button("📥 PDF", key=f"pdf_{i}", help="Generar reporte PDF",use_container_width=True):
                    # Get detailed records for this FCL
                #    fcl_details = df[df['N° FCL'] == row['N° FCL']]
                #    generate_and_download_pdf(row['N° FCL'], row, fcl_details)
            
            # Modal HTML (se mantiene oculto hasta que se haga clic en la tarjeta)
            st.markdown(f"""
            <!-- Modal para esta tarjeta -->
            <div id="modal_{i}" class="modal-overlay" style="display: none;">
                <div class="modal-content">
                    <div class="modal-header">
                        <h2>📋 Detalle de Evaluación - {row['N° FCL']}</h2>
                        <button class="modal-close" onclick="closeModal_{i}()">×</button>
                    </div>
                    
                    <div class="modal-body">
                        <div class="modal-grid">
                            <div class="modal-section">
                                <h4>📊 Información General</h4>
                                <div class="info-list">
                                    <div><strong>N° FCL:</strong> {row['N° FCL']}</div>
                                    <div><strong>Fecha Proceso:</strong> {row['FECHA DE PROCESO'].strftime('%d/%m/%Y %H:%M')}</div>
                                    <div><strong>Semana:</strong> {row['SEMANA']}</div>
                                    <div><strong>BRIX:</strong> {row['BRIX']:.2f}</div>
                                    <div><strong>Acidez:</strong> {row['ACIDEZ']:.2f}</div>
                                </div>
                            </div>
                            
                            <div class="modal-section">
                                <h4>🍇 Información del Producto</h4>
                                <div class="info-list">
                                    <div><strong>Variedad:</strong> {row['VARIEDAD']}</div>
                                    <div><strong>Productor:</strong> {row['PRODUCTOR']}</div>
                                    <div><strong>Tipo:</strong> {row['TIPO DE PRODUCTO']}</div>
                                    <div><strong>Fundo:</strong> {row['FUNDO']}</div>
                                    <div><strong>Presentación:</strong> {row['PRESENTACION']}</div>
                                    <div><strong>Destino:</strong> {row['DESTINO']}</div>
                                    <div><strong>📸 Imágenes:</strong> {'✅ Disponibles' if row.get('images', False) else '❌ No disponibles'}</div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="modal-actions">
                            <button class="action-btn export-btn" onclick="generatePDF_{i}()">📥 Exportar PDF</button>
                            <button class="action-btn email-btn">📧 Enviar Reporte</button>
                            <button class="action-btn reevaluate-btn">🔄 Re-evaluar</button>
                            <button class="action-btn close-btn" onclick="closeModal_{i}()">❌ Cerrar</button>
                        </div>
                    </div>
                </div>
            </div>
            
            <script>
            function openModal_{i}() {{
                document.getElementById('modal_{i}').style.display = 'flex';
            }}
            
            function closeModal_{i}() {{
                document.getElementById('modal_{i}').style.display = 'none';
            }}
            
            function generatePDF_{i}() {{
                // Set session state for PDF generation
                window.parent.postMessage({{
                    type: 'generatePDF',
                    fcl: '{row['N° FCL']}',
                    data: {row.to_dict()}
                }}, '*');
                closeModal_{i}();
            }}
            
            // Cerrar modal al hacer clic fuera de él
            document.getElementById('modal_{i}').addEventListener('click', function(e) {{
                if (e.target === this) {{
                    closeModal_{i}();
                }}
            }});
            </script>
            """, unsafe_allow_html=True)

        
        
        
    



def show_fcl_detail_view():
    """Mostrar la vista detallada de un FCL específico"""
    
    # Verificar que tenemos los datos necesarios
    if not hasattr(st.session_state, 'selected_fcl') or not hasattr(st.session_state, 'selected_fcl_data'):
        st.error("No se encontraron datos del FCL seleccionado")
        st.button("← Volver a la lista", on_click=go_back_to_list)
        return
    
    fcl_number = st.session_state.selected_fcl
    row = st.session_state.selected_fcl_data
    
    # Cargar datos completos
    df = clean_data()
   
    # Header con botón de regreso
    col1, col2 = st.columns([4, 1])
    
    with col1:
        st.markdown(f'<h1 class="main-header">📋 Detalle del FCL: {fcl_number}</h1>', unsafe_allow_html=True)
    
    with col2:
        if st.button("← Volver a la lista", key="back_button"):
            go_back_to_list()
    
    
    # Métricas principales
    
    
    # Información detallada
    st.markdown("### 📋 Información del Producto")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🫐 Información Básica**")
        st.write(f"**Variedad:** {row['VARIEDAD']}")
        st.write(f"**Productor:** {row['PRODUCTOR']}")
        st.write(f"**Tipo:** {row['TIPO DE PRODUCTO']}")
        st.write(f"**Fundo:** {row['FUNDO']}")
        st.write(f"**Presentación:** {row['PRESENTACION']}")
        st.write(f"**Destino:** {row['DESTINO']}")
    
    with col2:
        st.markdown("**📅 Información de Proceso**")
        st.write(f"**N° FCL:** {row['N° FCL']}")
        st.write(f"**Fecha Proceso:** {row['FECHA DE PROCESO'].strftime('%d/%m/%Y')}")
        st.write(f"**Semana:** {row['SEMANA']}")
        st.write(f"**BRIX:** {row['BRIX']:.2f}")
        st.write(f"**Acidez:** {row['ACIDEZ']:.2f}")
    
    # Obtener datos detallados del FCL específico
    fcl_details = df[df['N° FCL'] == fcl_number]
    #fcl_details = fcl_details.reset_index()
    img_df = get_images()
    img_df = img_df[img_df["folder_name"] == fcl_number]
    img_df = sum(img_df["base64_complete"], [])
    img_df = list(set(img_df))
    #fcl_details = fcl_details.merge(img_df, left_on="N° FCL", right_on="folder_name", how="left")
    
    # Sección de datos de calidad detallados
    
    
    # Tabla de datos completos
    st.markdown("### 📋 Registros Detallados del FCL")
    st.dataframe(fcl_details, use_container_width=True,hide_index=True)
    
    # Sección de imágenes
    st.markdown("### 📸 Imágenes")
    
    # Obtener las imágenes del FCL actual usando la función optimizada
    
    
    if len(img_df) > 0:
        col_img = st.columns(3)
        for i, img in enumerate(img_df):
            with col_img[i % 3]:
                st.image(img)
        
    else:
        st.info("📷 No hay imágenes disponibles para este FCL")
    
    
    
    # Botones de acción
    st.markdown("### ⚡ Acciones")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        
        generate_and_download_pdf(fcl_number, row, fcl_details,img_df)
    
    
    
    with col4:
        if st.button("❌ Cerrar", key=f"close_{fcl_number}"):
            go_back_to_list()


def generate_and_download_pdf(fcl_number, fcl_data, detailed_records,img_df):
    """Generate and provide download link for FCL PDF report"""
    
    
    # Prepare FCL data dictionary
    fcl_info = {
            'N° FCL': fcl_data['N° FCL'],
            'VARIEDAD': fcl_data['VARIEDAD'],
            'PRODUCTOR': fcl_data['PRODUCTOR'],
            'TIPO DE PRODUCTO': fcl_data['TIPO DE PRODUCTO'],
            'FUNDO': fcl_data['FUNDO'],
            'PRESENTACION': fcl_data['PRESENTACION'],
            'DESTINO': fcl_data['DESTINO'],
            'FECHA DE PROCESO': fcl_data['FECHA DE PROCESO'],
            'SEMANA': fcl_data['SEMANA'],
            'BRIX': fcl_data['BRIX'],
            'ACIDEZ': fcl_data['ACIDEZ']
        }
        
        # Cargar imágenes solo si es necesario
        
        
        # Generate PDF
    pdf_buffer = generate_fcl_pdf_report(fcl_info, detailed_records, images_list=img_df)
        
        # Create download button
    filename = f"Quality_Control_Report_{fcl_number}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
    st.download_button(
            label="📥 Descargar Reporte PDF",
            data=pdf_buffer.getvalue(),
            file_name=filename,
            mime="application/pdf",
            key=f"download_pdf_{fcl_number}",
            help="Descargar reporte de control de calidad en formato PDF"
        )
        
    
        



def go_back_to_list():
    """Función para volver a la lista principal"""
    if hasattr(st.session_state, 'current_view'):
        del st.session_state.current_view
    if hasattr(st.session_state, 'selected_fcl'):
        del st.session_state.selected_fcl
    if hasattr(st.session_state, 'selected_fcl_data'):
        del st.session_state.selected_fcl_data
    st.rerun()
