import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from utils.get_api import listar_archivos_en_carpeta_compartida, get_download_url_by_name, test_json
from utils.get_token import get_access_token, get_access_token_alza
from utils.handler_db import get_img_despacho_data
from utils.pdf_generator import generate_fcl_pdf_report
import base64
import zipfile
import io
import json
import re
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.pdfgen import canvas

def clean_cod_column(cod):
    """
    Limpia un código individual según las reglas:
    - EXCE -> EXC
    - GP -> GAP
    - Agregar 0 a la izquierda si hay menos de 3 dígitos
    - Quitar solo los ceros EXTRA si hay MÁS de 3 dígitos
    - Eliminar todo después del guión
    """
    if pd.isna(cod):
        return cod
    
    cod = str(cod).strip()
    original_cod = cod
    
    # 1. Eliminar todo después del guión
    if '-' in cod:
        cod = cod.split('-')[0]
    
    # 2. EXCE -> EXC
    if cod.startswith('EXCE'):
        cod = 'EXC' + cod[4:]
    
    # 3. GP -> GAP
    if cod.startswith('GP'):
        cod = 'GAP' + cod[2:]
    
    # 4. Buscar la parte numérica
    match = re.match(r'^([A-Z]+)(\d+)$', cod)
    if match:
        prefix = match.group(1)
        numbers = match.group(2)
        
        # Debug
        print(f"Original: {original_cod} -> After processing: {cod}")
        print(f"Prefix: {prefix}, Numbers: {numbers}, Length: {len(numbers)}")
        
        # Manejar los números según la cantidad de dígitos
        if len(numbers) > 3:
            # Si hay más de 3 dígitos, quitar solo los ceros EXTRA
            numbers_clean = numbers[-3:]  # Tomar solo los últimos 3 dígitos
        elif len(numbers) < 3:
            # Si hay menos de 3 dígitos, agregar 0 a la izquierda
            numbers_clean = numbers.zfill(3)
        else:
            # Si tiene exactamente 3 dígitos, mantener como está
            numbers_clean = numbers
        
        result = prefix + numbers_clean
        print(f"Final result: {result}")
        return result
    
    print(f"No match found for: {cod}")
    return cod

@st.cache_data(ttl=300,show_spinner="Cargando datos...")
def get_programacion_despachos():
    access_token = get_access_token_alza()
    DATAS = listar_archivos_en_carpeta_compartida(access_token, "b!VQYmeHVjYEWz0GKghOyC7vEXg4ECVBhNtIUi_0GrC_YtxGLZYwDkTIeZ8M0lJvFk", "01YFYVLBY2AXGEFA43KBCLDKFUHBDMF2OP")
    data_ = get_download_url_by_name(DATAS, "PROGRAMACION.xlsx")
    aereo = pd.read_excel(data_, sheet_name="PROGRAMA ALZA PACKING AEREO", skiprows=1)
    aereo = aereo.drop(["Unnamed: 0"], axis=1)
    aereo["ENVIO"] = "AEREO"
    maritimo = pd.read_excel(data_, sheet_name="PROGRAMA ALZA PACKING MARITIMO", skiprows=1)
    maritimo = maritimo.drop(["Unnamed: 0"], axis=1)
    maritimo["ENVIO"] = "MARITIMO"
    
    despacho_ = pd.concat([aereo, maritimo], ignore_index=True)
    despacho_['CODIGO'] = despacho_['COD']
    despacho_['COD'] = despacho_['COD'].str.replace("EZCE", "EXC")
    despacho_['COD'] = despacho_['COD'].apply(clean_cod_column)
    despacho_ = despacho_.drop(["FCL"], axis=1)
    despacho_ = despacho_.rename(columns={"COD":"FCL","DIA  DESP.":"FECHA DE DESPACHO"})
    return despacho_



def show_despacho():
    """Mostrar la página de despacho"""
    
    # Verificar si hay una vista específica seleccionada
    if hasattr(st.session_state, 'current_view') and st.session_state.current_view == "despacho_detail":
        show_despacho_detail_view()
        return
    
    st.markdown('<h1 class="main-header">🚚 Despacho de PT</h1>', unsafe_allow_html=True)
    
    st.markdown("---")
    def get_data():
        access_token = get_access_token_alza()
        DATAS = listar_archivos_en_carpeta_compartida(access_token, "b!VQYmeHVjYEWz0GKghOyC7vEXg4ECVBhNtIUi_0GrC_YtxGLZYwDkTIeZ8M0lJvFk", "01YFYVLBY2AXGEFA43KBCLDKFUHBDMF2OP")
        data_ = get_download_url_by_name(DATAS, "DESPACHOS_EXCELLENCE FRUIT.xlsx")
        exc_despachos_df = pd.read_excel(data_, sheet_name="camp 2025")
 
        return  exc_despachos_df
    #despacho_img.xlsx
    def get_data_img():
        access_token = get_access_token_alza()
        DATAS = listar_archivos_en_carpeta_compartida(access_token, "b!M5ucw3aa_UqBAcqv3a6affR7vTZM2a5ApFygaKCcATxyLdOhkHDiRKl9EvzaYbuR", "01XOBWFSBLVGULAQNEKNG2WR7CPRACEN7Q")
        data_ = get_download_url_by_name(DATAS, "despacho_img.xlsx")
        print(data_)
        df = pd.read_excel(data_)
        return  df
    
    def get_lista_maestra():
        access_token = get_access_token()
        DATAS = listar_archivos_en_carpeta_compartida(access_token, "b!oArJxyQJjk2YBRLaxF9M6-wEuCX8zKZAl30NL3kNPhUNCKEYLTZmTYa0i4oZ1qxK", "01OAW3XC5MKUBY6XFXQVDLAQAM6OHH5C5Z")
        data_ = get_download_url_by_name(DATAS, "LISTA MAESTRA DE DESPACHOS 2025.xlsx")
        
        exc_despachos_df = pd.read_excel(data_, sheet_name="CONTROL DE DESPACHOS", skiprows=4)
        exc_despachos_df = exc_despachos_df.drop(["Unnamed: 0","Unnamed: 3","Unnamed: 6","Unnamed: 16","Unnamed: 17"], axis=1)
        exc_despachos_df = exc_despachos_df.rename(columns={"Unnamed: 15":"OBSERVACIONES"})
        exc_despachos_df = exc_despachos_df[exc_despachos_df["FECHA DE DESPACHO"].notna()]
        exc_despachos_df['FECHA DE DESPACHO'] = pd.to_datetime(exc_despachos_df['FECHA DE DESPACHO'], format='%d.%m.%y', errors='coerce')
        exc_despachos_df['ETD'] = pd.to_datetime(exc_despachos_df['ETD'], format='%d.%m.%y', errors='coerce')
        exc_despachos_df['ETA'] = pd.to_datetime(exc_despachos_df['ETA'], format='%d.%m.%y', errors='coerce')
        return  exc_despachos_df
    #exc_despachos_df = get_lista_maestra()
    #print(exc_despachos_df.columns)
    #st.dataframe(exc_despachos_df)
    #exc_despachos_img_df = get_data_img()
    #st.dataframe(exc_despachos_img_df)
    #aereo_df, maritimo_df = get_programacion_despachos()
    #st.dataframe(aereo_df)
    #st.dataframe(maritimo_df)
    #df = pd.read_json("http://localhost:5544/phl-pt-all-tabla")
    #df = df[df["cliente"].isin(["SAN EFISIO S.A.C.", "EXCELLENCE FRUIT S.A.C","GAP BERRIES S.A.C" ] )]
    #df["envio"] = df["envio"].str.replace("SAN PEDR", "MARITIMO")
    #df["fecha_cosecha"] = pd.to_datetime(df["fecha_cosecha"]).dt.date
    #df["contenedor"] = df["contenedor"].str.split("-").str[0]
    #df["contenedor"] = df["contenedor"].str.strip()
    #print(df.columns)
    #df = df[[
    #    'envio','fecha_produccion', 'fecha_cosecha', 'cliente',
    #    'contenedor', 'descripcion_producto', 'destino',
    #    'variedad', 'n_cajas',  'peso_caja',
    #    'exportable', 'estado', 
    #]]
    #df = df.groupby(['envio','cliente',
    #    'contenedor', 'descripcion_producto', 'destino',
    #    'variedad',   'peso_caja','estado'])[['exportable','n_cajas',]].sum().reset_index()
    #st.dataframe(df)
    #lista_maestra = get_lista_maestra() 
    #print(lista_maestra.columns)
    #lista_maestra["Nº FCL"] = lista_maestra["Nº FCL"].str.replace("-", "")
    #lista_maestra["Nº FCL"] = lista_maestra["Nº FCL"].str.strip()
    #st.dataframe(lista_maestra)
    
    # Cargar y limpiar datos
    dff = get_programacion_despachos()
    
    
    # Convertir fechas
    if 'FECHA DE DESPACHO' in dff.columns:
        dff['FECHA DE DESPACHO'] = pd.to_datetime(dff['FECHA DE DESPACHO'], errors='coerce')
    if 'ETD' in dff.columns:
        dff['ETD'] = pd.to_datetime(dff['ETD'], errors='coerce')
    if 'ETA' in dff.columns:
        dff['ETA'] = pd.to_datetime(dff['ETA'], errors='coerce')
    
    # Fill NaN values
    dff = dff.fillna("-")
    
    # Limpiar strings
    string_columns = ["FCL", "CLIENTE", "EMPRESA", "DESTINO", "ENVIO", "ESTADO", "PRESENTACION"]
    for col in string_columns:
        if col in dff.columns:
            dff[col] = dff[col].astype(str).str.strip()
    
    # Filtrar datos válidos
    dff = dff[dff["FCL"] != "-"]
    dff = dff[dff["FCL"].notna()]
    
    dff = dff.sort_values(by="FECHA DE DESPACHO", ascending=False)
    
    # Barra de búsqueda y filtros
    col1, col2 = st.columns([5, 2])
    
    with col1:
        search_term = st.multiselect("Buscar FCL", sorted(dff["FCL"].unique()))
        if search_term != [] or len(search_term) > 0:
            dff = dff[dff["FCL"].isin(search_term)]
    
    # Crear resumen para mostrar en tarjetas usando las columnas disponibles
    available_columns = ['FCL', 'FECHA DE DESPACHO', 'CLIENTE', 'EMPRESA', 'ENVIO', 'ESTADO']
    # Filtrar solo las columnas que existen en el dataframe
    summary_columns = [col for col in available_columns if col in dff.columns]
    
    resumen_despacho_df = dff[summary_columns]
    resumen_despacho_df = resumen_despacho_df.groupby([col for col in summary_columns if col != 'FECHA DE DESPACHO']).agg({"FECHA DE DESPACHO": "max"}).reset_index()
    resumen_despacho_df = resumen_despacho_df.drop_duplicates()
    resumen_despacho_df = resumen_despacho_df.reset_index(drop=True)
    
    if search_term == [] or len(search_term) == 0:
        resumen_despacho_df = resumen_despacho_df.sort_values(by="FECHA DE DESPACHO", ascending=False)
        resumen_despacho_df = resumen_despacho_df.head(10)
    
    # Mostrar tarjetas de despacho
    with st.container():
        for i, row in resumen_despacho_df.iterrows():
            # Obtener el primer registro del FCL para mostrar información detallada
            fcl_number = row['FCL']
            fcl_detail_row = dff[dff['FCL'] == fcl_number].iloc[0]
            
            # Crear tarjeta clickeable
            col1, col2 = st.columns([3, 1])
            
            with col1:
                # Construir información de la tarjeta dinámicamente basada en las columnas disponibles
                fecha_info = fcl_detail_row['FECHA DE DESPACHO'].strftime('%d %b %Y') if pd.notna(fcl_detail_row['FECHA DE DESPACHO']) else 'Sin fecha'
                envio_info = row.get('ENVIO', 'N/A')
                cliente_info = row.get('CLIENTE', 'N/A')
                empresa_info = row.get('EMPRESA', 'N/A')
                estado_info = row.get('ESTADO', 'N/A')
                
                st.markdown(f"""
                <div class="clickable-card" onclick="openModal_{i}()" style="cursor: pointer;">
                    <div class="card-main-info">
                        <h3 style="margin: 0; color: var(--text-color, #333);">🚚 {row['FCL']}</h3>
                        <p style="margin: 5px 0; color: var(--text-color, #666); font-size: 13px; opacity: 0.8;">
                            📅 {fecha_info} |  {envio_info}
                        </p>
                        <p style="margin: 2px 0; font-size: 13px; color: var(--text-color, #666); opacity: 0.9;"><strong>Cliente:</strong> {cliente_info}</p>
                        <p style="margin: 2px 0; font-size: 13px; color: var(--text-color, #666); opacity: 0.9;"><strong>Empresa:</strong> {empresa_info}</p>
                        <p style="margin: 2px 0; font-size: 13px; color: var(--text-color, #666); opacity: 0.9;"><strong>Estado:</strong> {estado_info}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                if st.button("👁️ Ver Detalles", key=f"detail_{i}", help="Ver detalles completos", use_container_width=True):
                    # Guardar el FCL seleccionado en session_state para la nueva vista
                    st.session_state.selected_fcl = fcl_number
                    st.session_state.selected_fcl_data = fcl_detail_row
                    st.session_state.current_view = "despacho_detail"
                    st.rerun()
            
            # Modal HTML (se mantiene oculto hasta que se haga clic en la tarjeta)
            st.markdown(f"""
            <!-- Modal para esta tarjeta -->
            <div id="modal_{i}" class="modal-overlay" style="display: none;">
                <div class="modal-content">
                    <div class="modal-header">
                        <h2>🚚 Detalle de Despacho - {fcl_number}</h2>
                        <button class="modal-close" onclick="closeModal_{i}()">×</button>
                    </div>
                    
                    <div class="modal-body">
                        <div class="modal-grid">
                            <div class="modal-section">
                                <h4>📊 Información General</h4>
                                <div class="info-list">
                                    <div><strong>N° FCL:</strong> {fcl_number}</div>
                                    <div><strong>Fecha Despacho:</strong> {fcl_detail_row['FECHA DE DESPACHO'].strftime('%d/%m/%Y') if pd.notna(fcl_detail_row['FECHA DE DESPACHO']) else 'Sin fecha'}</div>
                                    <div><strong>Cliente:</strong> {row.get('CLIENTE', 'N/A')}</div>
                                    <div><strong>Empresa:</strong> {row.get('EMPRESA', 'N/A')}</div>
                                    <div><strong>Envío:</strong> {row.get('ENVIO', 'N/A')}</div>
                                    <div><strong>Estado:</strong> {row.get('ESTADO', 'N/A')}</div>
                                </div>
                            </div>
                            
                            <div class="modal-section">
                                <h4>🚚 Información del Despacho</h4>
                                <div class="info-list">
                                    <div><strong>ETD:</strong> {fcl_detail_row['ETD'].strftime('%d/%m/%Y') if pd.notna(fcl_detail_row.get('ETD')) else 'Sin fecha'}</div>
                                    <div><strong>ETA:</strong> {fcl_detail_row['ETA'].strftime('%d/%m/%Y') if pd.notna(fcl_detail_row.get('ETA')) else 'Sin fecha'}</div>
                                    <div><strong>Presentación:</strong> {fcl_detail_row.get('PRESENTACION', 'N/A')}</div>
                                    <div><strong>📸 Imágenes:</strong> {'✅ Disponibles' if True else '❌ No disponibles'}</div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="modal-actions">
                            <button class="action-btn export-btn" onclick="generatePDF_{i}()">📥 Exportar PDF</button>
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
                    fcl: '{fcl_number}',
                    data: {fcl_detail_row.to_dict()}
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


def format_value(value):
    """Formatear valores para mostrar de manera legible"""
    if pd.isna(value) or value == "-" or value == "" or str(value).strip() == "":
        return "N/A"
    
    # Si es una fecha, formatearla
    if isinstance(value, (pd.Timestamp, datetime)):
        return value.strftime('%d/%m/%Y') if pd.notna(value) else "N/A"
    
    return str(value).strip()

def generate_corporate_print_format(fcl_data, fcl_number):
    """Generar formato corporativo para impresión"""
    
    # CSS para el formato corporativo
    corporate_css = """
    <style>
    @media print {
        .no-print { display: none !important; }
        .print-only { display: block !important; }
        body { margin: 0; padding: 20px; }
    }
    .corporate-header {
        text-align: center;
        border-bottom: 3px solid #2E86AB;
        padding-bottom: 20px;
        margin-bottom: 30px;
    }
    .company-logo {
        font-size: 28px;
        font-weight: bold;
        color: #2E86AB;
        margin-bottom: 10px;
    }
    .document-title {
        font-size: 24px;
        font-weight: bold;
        color: #333;
        margin-bottom: 5px;
    }
    .document-subtitle {
        font-size: 16px;
        color: #666;
    }
    .info-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 30px;
        margin-bottom: 30px;
    }
    .info-section {
        background: #f8f9fa;
        padding: 20px;
        border-radius: 8px;
        border-left: 4px solid #2E86AB;
    }
    .section-title {
        font-size: 18px;
        font-weight: bold;
        color: #2E86AB;
        margin-bottom: 15px;
        border-bottom: 1px solid #ddd;
        padding-bottom: 5px;
    }
    .info-row {
        display: flex;
        justify-content: space-between;
        margin-bottom: 8px;
        padding: 5px 0;
    }
    .info-label {
        font-weight: bold;
        color: #333;
        min-width: 150px;
    }
    .info-value {
        color: #666;
        text-align: right;
        flex: 1;
    }
    .full-width-section {
        background: #f8f9fa;
        padding: 20px;
        border-radius: 8px;
        border-left: 4px solid #2E86AB;
        margin-bottom: 20px;
    }
    .footer {
        margin-top: 40px;
        text-align: center;
        color: #666;
        font-size: 12px;
        border-top: 1px solid #ddd;
        padding-top: 20px;
    }
    .print-button {
        background: #2E86AB;
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 5px;
        cursor: pointer;
        font-size: 14px;
        margin: 10px;
    }
    .print-button:hover {
        background: #1a5a7a;
    }
    </style>
    """
    
    # Generar el HTML del documento
    current_date = datetime.now().strftime('%d/%m/%Y %H:%M')
    
    html_content = f"""
    {corporate_css}
    
    <div class="corporate-header">
        <div class="company-logo">🍓 SAN LUCAR FRUIT</div>
        <div class="document-title">REPORTE DE DESPACHO</div>
        <div class="document-subtitle">FCL: {fcl_number}</div>
        <div class="document-subtitle">Generado el: {current_date}</div>
    </div>
    
    <div class="info-grid">
        <div class="info-section">
            <div class="section-title">📋 Información General</div>
            <div class="info-row">
                <span class="info-label">N° FCL:</span>
                <span class="info-value">{format_value(fcl_data.get('FCL', ''))}</span>
            </div>
            <div class="info-row">
                <span class="info-label">Código Original:</span>
                <span class="info-value">{format_value(fcl_data.get('CODIGO', ''))}</span>
            </div>
            <div class="info-row">
                <span class="info-label">Cliente:</span>
                <span class="info-value">{format_value(fcl_data.get('CLIENTE', ''))}</span>
            </div>
            <div class="info-row">
                <span class="info-label">Empresa:</span>
                <span class="info-value">{format_value(fcl_data.get('EMPRESA', ''))}</span>
            </div>
            <div class="info-row">
                <span class="info-label">CNEE:</span>
                <span class="info-value">{format_value(fcl_data.get('CNEE', ''))}</span>
            </div>
            <div class="info-row">
                <span class="info-label">Operador:</span>
                <span class="info-value">{format_value(fcl_data.get('OPERADOR', ''))}</span>
            </div>
        </div>
        
        <div class="info-section">
            <div class="section-title">📅 Información de Fechas</div>
            <div class="info-row">
                <span class="info-label">Fecha de Despacho:</span>
                <span class="info-value">{format_value(fcl_data.get('FECHA DE DESPACHO', ''))}</span>
            </div>
            <div class="info-row">
                <span class="info-label">Hora de Despacho:</span>
                <span class="info-value">{format_value(fcl_data.get('HORA DESP.', ''))}</span>
            </div>
            <div class="info-row">
                <span class="info-label">ETD:</span>
                <span class="info-value">{format_value(fcl_data.get('ETD', ''))}</span>
            </div>
            <div class="info-row">
                <span class="info-label">ETA:</span>
                <span class="info-value">{format_value(fcl_data.get('ETA', ''))}</span>
            </div>
            <div class="info-row">
                <span class="info-label">Semana ETD:</span>
                <span class="info-value">{format_value(fcl_data.get('SEM ETD', ''))}</span>
            </div>
            <div class="info-row">
                <span class="info-label">Semana Despacho:</span>
                <span class="info-value">{format_value(fcl_data.get('SEM DESP.', ''))}</span>
            </div>
        </div>
    </div>
    
    <div class="info-grid">
        <div class="info-section">
            <div class="section-title">🚚 Información de Transporte</div>
            <div class="info-row">
                <span class="info-label">Tipo de Envío:</span>
                <span class="info-value">{format_value(fcl_data.get('ENVIO', ''))}</span>
            </div>
            <div class="info-row">
                <span class="info-label">Transporte:</span>
                <span class="info-value">{format_value(fcl_data.get('TRASNPORTE', ''))}</span>
            </div>
            <div class="info-row">
                <span class="info-label">Nave:</span>
                <span class="info-value">{format_value(fcl_data.get('NAVE', ''))}</span>
            </div>
            <div class="info-row">
                <span class="info-label">Aerolínea:</span>
                <span class="info-value">{format_value(fcl_data.get('AEROLINEA', ''))}</span>
            </div>
            <div class="info-row">
                <span class="info-label">Línea Naviera:</span>
                <span class="info-value">{format_value(fcl_data.get('LINEA NAVIERA', ''))}</span>
            </div>
            <div class="info-row">
                <span class="info-label">Itinerario:</span>
                <span class="info-value">{format_value(fcl_data.get('ITINERARIO', ''))}</span>
            </div>
        </div>
        
        <div class="info-section">
            <div class="section-title">📍 Información de Destino</div>
            <div class="info-row">
                <span class="info-label">POD:</span>
                <span class="info-value">{format_value(fcl_data.get('POD', ''))}</span>
            </div>
            <div class="info-row">
                <span class="info-label">POL:</span>
                <span class="info-value">{format_value(fcl_data.get('POL', ''))}</span>
            </div>
            <div class="info-row">
                <span class="info-label">Planta:</span>
                <span class="info-value">{format_value(fcl_data.get('PLANTA', ''))}</span>
            </div>
            <div class="info-row">
                <span class="info-label">BK:</span>
                <span class="info-value">{format_value(fcl_data.get('BK', ''))}</span>
            </div>
            <div class="info-row">
                <span class="info-label">Estado:</span>
                <span class="info-value">{format_value(fcl_data.get('ESTADO', ''))}</span>
            </div>
        </div>
    </div>
    
    <div class="full-width-section">
        <div class="section-title">📦 Información del Producto</div>
        <div class="info-grid">
            <div>
                <div class="info-row">
                    <span class="info-label">Presentación:</span>
                    <span class="info-value">{format_value(fcl_data.get('PRESENTACION', ''))}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Pallets:</span>
                    <span class="info-value">{format_value(fcl_data.get('PALLETS', ''))}</span>
                </div>
            </div>
            <div>
                <div class="info-row">
                    <span class="info-label">Expediente Fito:</span>
                    <span class="info-value">{format_value(fcl_data.get('EXPEDIENTE FITO.', ''))}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Semana PRO:</span>
                    <span class="info-value">{format_value(fcl_data.get('SEM PRO', ''))}</span>
                </div>
            </div>
        </div>
    </div>
    
    <div class="footer">
        <p>Este documento fue generado automáticamente por el Sistema de Control de Calidad</p>
        <p>© 2025 San Lucar Fruit - Todos los derechos reservados</p>
    </div>
    """
    
    return html_content

def generate_despacho_pdf_report(fcl_data, fcl_number):
    """
    Generar reporte PDF corporativo para despacho
    
    Args:
        fcl_data: Serie de pandas con datos del FCL
        fcl_number: Número del FCL
        
    Returns:
        BytesIO buffer con contenido PDF
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=20*mm,
        leftMargin=20*mm,
        topMargin=30*mm,
        bottomMargin=20*mm
    )
    
    # Setup styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    header_style = ParagraphStyle(
        'CustomHeader',
        parent=styles['Heading1'],
        fontSize=20,
        spaceAfter=10,
        textColor=colors.HexColor('#2E86AB'),
        alignment=1  # Center
    )
    
    subheader_style = ParagraphStyle(
        'CustomSubHeader',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=8,
        textColor=colors.HexColor('#2E86AB'),
        leftIndent=0
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=4,
        textColor=colors.HexColor('#333333')
    )
    
    # Story elements
    story = []
    
    # Header with logo and title
    
    story.append(Paragraph("REPORTE DE DESPACHO", header_style))
    story.append(Paragraph(f"FCL: {fcl_number}", subheader_style))
    story.append(Paragraph(f"Generado el: {datetime.now().strftime('%d/%m/%Y %H:%M')}", body_style))
    story.append(Spacer(1, 20))
    
    # Información General
    story.append(Paragraph("INFORMACIÓN GENERAL", subheader_style))
    
    general_data = [
        ['Campo', 'Valor'],
        ['N° FCL', format_value(fcl_data.get('FCL', ''))],
        ['Código Original', format_value(fcl_data.get('CODIGO', ''))],
        ['Cliente', format_value(fcl_data.get('CLIENTE', ''))],
        ['Empresa', format_value(fcl_data.get('EMPRESA', ''))],
        ['CNEE', format_value(fcl_data.get('CNEE', ''))],
        ['Operador', format_value(fcl_data.get('OPERADOR', ''))],
        ['Estado', format_value(fcl_data.get('ESTADO', ''))]
    ]
    
    general_table = Table(general_data, colWidths=[60*mm, 100*mm])
    general_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E86AB')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')])
    ]))
    
    story.append(general_table)
    story.append(Spacer(1, 15))
    
    # Información de Fechas
    story.append(Paragraph("INFORMACIÓN DE FECHAS", subheader_style))
    
    date_data = [
        ['Campo', 'Valor'],
        ['Fecha de Despacho', format_value(fcl_data.get('FECHA DE DESPACHO', ''))],
        ['Hora de Despacho', format_value(fcl_data.get('HORA DESP.', ''))],
        ['ETD', format_value(fcl_data.get('ETD', ''))],
        ['ETA', format_value(fcl_data.get('ETA', ''))],
        ['Semana ETD', format_value(fcl_data.get('SEM ETD', ''))],
        ['Semana Despacho', format_value(fcl_data.get('SEM DESP.', ''))],
        ['Semana PRO', format_value(fcl_data.get('SEM PRO', ''))]
    ]
    
    date_table = Table(date_data, colWidths=[60*mm, 100*mm])
    date_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E86AB')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')])
    ]))
    
    story.append(date_table)
    story.append(Spacer(1, 15))
    
    # Información de Transporte
    story.append(Paragraph("INFORMACIÓN DE TRANSPORTE", subheader_style))
    
    transport_data = [
        ['Campo', 'Valor'],
        ['Tipo de Envío', format_value(fcl_data.get('ENVIO', ''))],
        ['Transporte', format_value(fcl_data.get('TRASNPORTE', ''))],
        ['Nave', format_value(fcl_data.get('NAVE', ''))],
        ['Aerolínea', format_value(fcl_data.get('AEROLINEA', ''))],
        ['Línea Naviera', format_value(fcl_data.get('LINEA NAVIERA', ''))],
        ['Itinerario', format_value(fcl_data.get('ITINERARIO', ''))]
    ]
    
    transport_table = Table(transport_data, colWidths=[60*mm, 100*mm])
    transport_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E86AB')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')])
    ]))
    
    story.append(transport_table)
    story.append(Spacer(1, 15))
    
    # Información de Ubicación y Producto
    story.append(Paragraph("INFORMACIÓN DE UBICACIÓN Y PRODUCTO", subheader_style))
    
    location_product_data = [
        ['Campo', 'Valor'],
        ['POD', format_value(fcl_data.get('POD', ''))],
        ['POL', format_value(fcl_data.get('POL', ''))],
        ['Planta', format_value(fcl_data.get('PLANTA', ''))],
        ['BK', format_value(fcl_data.get('BK', ''))],
        ['Presentación', format_value(fcl_data.get('PRESENTACION', ''))],
        ['Pallets', format_value(fcl_data.get('PALLETS', ''))],
        ['Expediente Fito', format_value(fcl_data.get('EXPEDIENTE FITO.', ''))]
    ]
    
    location_product_table = Table(location_product_data, colWidths=[60*mm, 100*mm])
    location_product_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E86AB')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')])
    ]))
    
    story.append(location_product_table)
    story.append(Spacer(1, 20))
    
    # Footer
    story.append(Paragraph("Este documento fue generado automáticamente", 
                          ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, 
                                       textColor=colors.HexColor('#666666'), alignment=1)))
    story.append(Paragraph("© 2025 APG Packing - Todos los derechos reservados", 
                          ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, 
                                       textColor=colors.HexColor('#666666'), alignment=1)))
    
    # Build PDF
    doc.build(story)
    
    buffer.seek(0)
    return buffer

def show_despacho_detail_view():
    """Mostrar la vista detallada de un FCL de despacho específico"""
    
    # Verificar que tenemos los datos necesarios
    if not hasattr(st.session_state, 'selected_fcl') or not hasattr(st.session_state, 'selected_fcl_data'):
        st.error("No se encontraron datos del FCL seleccionado")
        st.button("← Volver a la lista", on_click=go_back_to_despacho_list)
        return
    
    fcl_number = st.session_state.selected_fcl
    row = st.session_state.selected_fcl_data
    
    # Cargar datos completos
    dff = get_programacion_despachos()
    
    # Convertir fechas
    date_columns = ['FECHA DE DESPACHO', 'ETD', 'ETA']
    for col in date_columns:
        if col in dff.columns:
            dff[col] = pd.to_datetime(dff[col], errors='coerce')
    
    # Fill NaN values
    dff = dff.fillna("-")
    
    # Limpiar strings
    string_columns = ["FCL", "CLIENTE", "EMPRESA", "DESTINO", "ENVIO", "ESTADO", "PRESENTACION"]
    for col in string_columns:
        if col in dff.columns:
            dff[col] = dff[col].astype(str).str.strip()
    
    # Filtrar datos válidos
    dff = dff[dff["FCL"] != "-"]
    dff = dff[dff["FCL"].notna()]
    
    # Obtener datos actualizados del FCL específico
    fcl_details = dff[dff['FCL'] == fcl_number]
    if not fcl_details.empty:
        row = fcl_details.iloc[0]  # Usar los datos más actualizados
    
    # Header con botón de regreso y botón de impresión
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        st.markdown(f'<h1 class="main-header">🚚 Detalle del Despacho: {fcl_number}</h1>', unsafe_allow_html=True)
    
    with col2:
        # Generar PDF directamente
        try:
            pdf_buffer = generate_despacho_pdf_report(row, fcl_number)
            filename = f"Despacho_Report_{fcl_number}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            
            st.download_button(
                label="📥 Descargar PDF",
                data=pdf_buffer.getvalue(),
                file_name=filename,
                mime="application/pdf",
                key=f"download_despacho_pdf_{fcl_number}",
                help="Descargar reporte de despacho en formato PDF corporativo"
            )
        except Exception as e:
            st.error(f"Error al generar PDF: {str(e)}")
            if st.button("🖨️ Vista Previa", key="print_button_fallback"):
                # Fallback: mostrar vista previa HTML si falla el PDF
                corporate_format = generate_corporate_print_format(row, fcl_number)
                with st.expander("📄 Vista Previa del Reporte", expanded=True):
                    st.markdown(corporate_format, unsafe_allow_html=True)
    
    with col3:
        if st.button("← Volver a la lista", key="back_button"):
            go_back_to_despacho_list()
    
    # Información detallada completa
    st.markdown("### 📋 Información Completa del Despacho")
    
    # Organizar las columnas por categorías
    general_info = ['FCL', 'CODIGO', 'CLIENTE', 'EMPRESA', 'CNEE', 'OPERADOR', 'ESTADO']
    date_info = ['FECHA DE DESPACHO', 'HORA DESP.', 'ETD', 'ETA', 'SEM ETD', 'SEM DESP.']
    transport_info = ['ENVIO', 'TRASNPORTE', 'NAVE', 'AEROLINEA', 'LINEA NAVIERA', 'ITINERARIO']
    location_info = ['POD', 'POL', 'PLANTA', 'BK']
    product_info = ['PRESENTACION', 'PALLETS', 'EXPEDIENTE FITO.']
    
    # Crear tabs para organizar la información
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 General", "📅 Fechas", "🚚 Transporte", "📍 Ubicación", "📦 Producto"])
    
    with tab1:
        st.markdown("**Información General**")
        col1, col2 = st.columns(2)
        with col1:
            for i, field in enumerate(general_info[:len(general_info)//2 + 1]):
                if field in row:
                    st.write(f"**{field}:** {format_value(row[field])}")
        with col2:
            for field in general_info[len(general_info)//2 + 1:]:
                if field in row:
                    st.write(f"**{field}:** {format_value(row[field])}")
    
    with tab2:
        st.markdown("**Información de Fechas**")
        col1, col2 = st.columns(2)
        with col1:
            for i, field in enumerate(date_info[:len(date_info)//2 + 1]):
                if field in row:
                    st.write(f"**{field}:** {format_value(row[field])}")
        with col2:
            for field in date_info[len(date_info)//2 + 1:]:
                if field in row:
                    st.write(f"**{field}:** {format_value(row[field])}")
    
    with tab3:
        st.markdown("**Información de Transporte**")
        col1, col2 = st.columns(2)
        with col1:
            for i, field in enumerate(transport_info[:len(transport_info)//2 + 1]):
                if field in row:
                    st.write(f"**{field}:** {format_value(row[field])}")
        with col2:
            for field in transport_info[len(transport_info)//2 + 1:]:
                if field in row:
                    st.write(f"**{field}:** {format_value(row[field])}")
    
    with tab4:
        st.markdown("**Información de Ubicación**")
        col1, col2 = st.columns(2)
        with col1:
            for i, field in enumerate(location_info[:len(location_info)//2 + 1]):
                if field in row:
                    st.write(f"**{field}:** {format_value(row[field])}")
        with col2:
            for field in location_info[len(location_info)//2 + 1:]:
                if field in row:
                    st.write(f"**{field}:** {format_value(row[field])}")
    
    with tab5:
        st.markdown("**Información del Producto**")
        col1, col2 = st.columns(2)
        with col1:
            for i, field in enumerate(product_info[:len(product_info)//2 + 1]):
                if field in row:
                    st.write(f"**{field}:** {format_value(row[field])}")
        with col2:
            for field in product_info[len(product_info)//2 + 1:]:
                if field in row:
                    st.write(f"**{field}:** {format_value(row[field])}")
    
    # Mostrar todas las columnas disponibles en una tabla expandible
    st.markdown("### 📊 Datos Completos en Tabla")
    with st.expander("Ver todos los campos en formato tabla"):
        if not fcl_details.empty:
            fcl_details = fcl_details.transpose().reset_index()
            fcl_details.columns = ["", " "]
            print(fcl_details.columns)
            st.dataframe(fcl_details, use_container_width=True,hide_index=True)
        else:
            st.info("No se encontraron registros detallados para este FCL")
    
    # Sección de imágenes (mantenida para futura implementación)

    try:
        img_df = get_img_despacho_data(fcl_number)
        if img_df is None:
            img_df = pd.DataFrame(columns=['FCL', 'image_base64'])
        
        img_df = img_df[img_df["image_base64"].notna()]
        img_df = img_df["image_base64"].to_list()
        
        st.markdown("### 📸 Imágenes")
        with st.expander("Imágenes del Despacho"):
            if len(img_df) > 0:
                col_img = st.columns(3)
                for i, img_url in enumerate(img_df):
                    with col_img[i % 3]:
                        st.image(img_url, width=200)
            else:
                st.info("📷 No hay imágenes disponibles para este despacho")
    except Exception as e:
        st.info("📷 No hay imágenes disponibles para este despacho")
    #st.info("📷 Funcionalidad de imágenes en desarrollo")


def go_back_to_despacho_list():
    """Función para volver a la lista principal de despachos"""
    if hasattr(st.session_state, 'current_view'):
        del st.session_state.current_view
    if hasattr(st.session_state, 'selected_fcl'):
        del st.session_state.selected_fcl
    if hasattr(st.session_state, 'selected_fcl_data'):
        del st.session_state.selected_fcl_data
    st.rerun()

"""
try:
        img_df = get_img_despacho_data(fcl_number)
        if img_df is None:
            img_df = pd.DataFrame(columns=['FCL', 'image_base64'])
        
        img_df = img_df[img_df["image_base64"].notna()]
        img_df = img_df["image_base64"].to_list()
        
        st.markdown("### 📸 Imágenes")
        with st.expander("Imágenes del Despacho"):
            if len(img_df) > 0:
                col_img = st.columns(3)
                for i, img_url in enumerate(img_df):
                    with col_img[i % 3]:
                        st.image(img_url, width=200)
            else:
                st.info("📷 No hay imágenes disponibles para este despacho")
    except Exception as e:
"""