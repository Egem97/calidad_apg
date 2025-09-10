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
    print("Columnas disponibles:", dff.columns.tolist())
    
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
    
    # Header con botón de regreso
    col1, col2 = st.columns([4, 1])
    
    with col1:
        st.markdown(f'<h1 class="main-header">🚚 Detalle del Despacho: {fcl_number}</h1>', unsafe_allow_html=True)
    
    with col2:
        if st.button("← Volver a la lista", key="back_button"):
            go_back_to_despacho_list()
    
    # Información detallada
    st.markdown("### 📋 Información del Despacho")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🚚 Información Básica**")
        st.write(f"**FCL:** {row['FCL']}")
        st.write(f"**Cliente:** {row.get('CLIENTE', 'N/A')}")
        st.write(f"**Empresa:** {row.get('EMPRESA', 'N/A')}")
        st.write(f"**Tipo de Envío:** {row.get('ENVIO', 'N/A')}")
        st.write(f"**Estado:** {row.get('ESTADO', 'N/A')}")
        
    with col2:
        st.markdown("**📅 Información de Fechas**")
        st.write(f"**Fecha de Despacho:** {row['FECHA DE DESPACHO'].strftime('%d/%m/%Y') if pd.notna(row['FECHA DE DESPACHO']) else 'Sin fecha'}")
        # Agregar más campos de fecha si están disponibles en el dataframe
        if 'ETD' in row and pd.notna(row.get('ETD')):
            st.write(f"**ETD:** {row['ETD'].strftime('%d/%m/%Y')}")
        if 'ETA' in row and pd.notna(row.get('ETA')):
            st.write(f"**ETA:** {row['ETA'].strftime('%d/%m/%Y')}")
        if 'PRESENTACION' in row:
            st.write(f"**Presentación:** {row.get('PRESENTACION', 'N/A')}")
    
    # Obtener datos detallados del FCL específico
    fcl_details = dff[dff['FCL'] == fcl_number]
    
    st.markdown("### 📋 Registros Detallados del Despacho")
    
    # Mostrar tabla con todos los registros del FCL
    #if not fcl_details.empty:
    #    st.dataframe(fcl_details, use_container_width=True)
    #else:
    #    st.info("No se encontraron registros detallados para este FCL")
    
    # Sección de imágenes
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
    
    # Botones de acción
    col1, col2, col3, col4 = st.columns(4)
    
    #with col1:
    #    if st.button("📥 Exportar PDF", key=f"export_{fcl_number}"):
    #        st.info("Funcionalidad de exportación PDF en desarrollo")
    
    #with col4:
    #    if st.button("❌ Cerrar", key=f"close_{fcl_number}"):
    #        go_back_to_despacho_list()


def go_back_to_despacho_list():
    """Función para volver a la lista principal de despachos"""
    if hasattr(st.session_state, 'current_view'):
        del st.session_state.current_view
    if hasattr(st.session_state, 'selected_fcl'):
        del st.session_state.selected_fcl
    if hasattr(st.session_state, 'selected_fcl_data'):
        del st.session_state.selected_fcl_data
    st.rerun()