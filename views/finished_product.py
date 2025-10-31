
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from utils.get_api import listar_archivos_en_carpeta_compartida, get_download_url_by_name
from utils.get_token import get_access_token, get_access_token_alza
from utils.pdf_generator import generate_fcl_pdf_report
from utils.handler_db import get_img_evacalidad_data
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode ,JsCode
import base64
import zipfile
import io
import json
def categorize_presentation(presentation):
        if pd.isna(presentation):
            return "NO_ESPECIFICADO"
        presentation_upper = str(presentation).upper()
        
        if "4.4" in presentation_upper:
            return "4.4 OZ"
        
        elif "3.3" in presentation_upper:
            return "BANDEJA BLANCA 3.3KG"
        elif "3KG" in presentation_upper:
            return "BANDEJA BLANCA 3KG"
        elif "8X18OZ" in presentation_upper:
            return "8X18 OZ"
        elif "9.8OZ" in presentation_upper:
            return "9.8 OZ PINTA PLANA"
        elif "6OZ" in presentation_upper:
            return "6 OZ"
        elif "12X18" in presentation_upper:
            return "12X18 OZ"
        #elif "BANDEJA" in presentation_upper:
        #    return "BANDEJA"
        else:
            return presentation_upper

@st.cache_data(show_spinner="Cargando datos...", ttl=300)
def get_data():
    """Cargar datos principales con cache optimizado"""
    access_token = get_access_token()
    DATAS = listar_archivos_en_carpeta_compartida(access_token, "b!k0xKW2h1VkGnxasDN0z40PeA8yi0BwBKgEf_EOEPStmAWVEVjX8MQIydW1yMzk1b", "01SPKVU4I6RWNBBAVFIJF3GHBOYOFMUKZS")
    data_ = get_download_url_by_name(DATAS, "BD EVALUACION DE CALIDAD DE PRODUCTO TERMINADO.xlsx")
    df = pd.read_excel(data_, sheet_name="CALIDAD PRODUCTO TERMINADO")
    return df


@st.cache_data(show_spinner="Cargando images...",ttl=500)
def get_images():
    """Cargar solo metadatos de imágenes para optimizar rendimiento"""
    access_token = get_access_token_alza()
    DATAS = listar_archivos_en_carpeta_compartida(access_token, "b!M5ucw3aa_UqBAcqv3a6affR7vTZM2a5ApFygaKCcATxyLdOhkHDiRKl9EvzaYbuR", "01XOBWFSBLVGULAQNEKNG2WR7CPRACEN7Q")
    data_ = get_download_url_by_name(DATAS, "imges_url_gd_calidad.parquet")
    
    df = pd.read_parquet(data_)
    
    df["folder_name"] = df["folder_name"].str.strip()
    #df["folder_name"] = df["folder_name"].str.strip()
    df = df.groupby(["folder_name"]).agg({
        "image_download_url": lambda x: x.tolist(),
        "image_thumbnail_url": lambda x: x.tolist(),
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
        'SAN EFISIO S.A.C': "SAN LUCAR S.A.",
        'TARA FARMS S.A.C': "SAN LUCAR S.A.",
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
    df = df[df["EMPRESA"] == "SAN LUCAR S.A."]
    
    return df





def show_finished_product():
    """Mostrar la página de evaluaciones de producto terminado"""
    
    # Verificar si hay una vista específica seleccionada
    if hasattr(st.session_state, 'current_view') and st.session_state.current_view == "fcl_detail":
        show_fcl_detail_view()
        return
    
    df = clean_data()
    
    
    
    st.markdown('<h1 class="main-header">🫐 Evaluación de Producto Terminado</h1>', unsafe_allow_html=True)
    #st.markdown('<h4 style="text-align: center; color: #666;">Datos de calidad de arándanos por contenedor</h4>', unsafe_allow_html=True)

   
    df = df.sort_values(by="FECHA DE PROCESO", ascending=False)
    #st.dataframe(df)
    # Barra de búsqueda y filtros
    col1, col2,  = st.columns([5, 2])
    

    with col1:
        
        search_term = st.multiselect("Buscar FCL", df["N° FCL"].unique())
        if search_term != [] or len(search_term )>0:
            df = df[df["N° FCL"].isin(search_term)]
        
    

    df["PRESENTACION"] = df["PRESENTACION"].str.upper()
    df["PRESENTACION"] = df["PRESENTACION"].str.replace(" ", "")
    
    df["PRESENTACION"] = df["PRESENTACION"].apply(categorize_presentation)
    
    resumen_pag_df = df[['N° FCL','FECHA DE PROCESO','SEMANA','VARIEDAD','PRODUCTOR']]
    resumen_pag_df = resumen_pag_df.groupby(["N° FCL","SEMANA","VARIEDAD","PRODUCTOR"]).agg({"FECHA DE PROCESO": "max"}).reset_index()
    resumen_pag_df["SEMANA"] = resumen_pag_df["SEMANA"].astype(int)
    resumen_pag_df = resumen_pag_df.drop_duplicates()
    resumen_pag_df = resumen_pag_df.reset_index(drop=True)
    if search_term == [] or len(search_term )==0:
        resumen_pag_df = resumen_pag_df.sort_values(by="FECHA DE PROCESO", ascending=False)
        resumen_pag_df = resumen_pag_df.head(10)
        
    # Mostrar tarjetas de evaluación para la página actual
    
        
    
    
    # Usar st.container para optimizar el renderizado
    with st.container():
        for i, row2 in resumen_pag_df.iterrows():
            # Obtener el primer registro del FCL para mostrar información detallada
            fcl_number = row2['N° FCL']
            fcl_detail_row = df[df['N° FCL'] == fcl_number].iloc[0]
            #fcl_detail_row = fcl_detail_row.groupby(["N° FCL","SEMANA","VARIEDAD","PRODUCTOR","PRESENTACION"]).agg({"FECHA DE PROCESO": "max"}).reset_index()
            
            # Crear tarjeta clickeable con modal
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"""
                <div class="clickable-card" onclick="openModal_{i}()" style="cursor: pointer;">
                    <div class="card-main-info">
                        <h3 style="margin: 0; color: var(--text-color, #333);">📦 {row2['N° FCL']}</h3>
                        <p style="margin: 5px 0; color: var(--text-color, #666); font-size: 13px; opacity: 0.8;">
                            📅 {fcl_detail_row['FECHA DE PROCESO'].strftime('%d %b %Y')} | 🗓️ Semana {row2['SEMANA']}
                        </p>
                        <p style="margin: 2px 0; font-size: 13px; color: var(--text-color, #666); opacity: 0.9;"><strong>Variedad:</strong> {row2['VARIEDAD']}</p>
                        <p style="margin: 2px 0; font-size: 13px; color: var(--text-color, #666); opacity: 0.9;"><strong>Productor:</strong> {row2['PRODUCTOR']}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                if st.button("👁️ Ver Detalles", key=f"detail_{i}", help="Ver detalles completos",use_container_width=True):
                    # Guardar el FCL seleccionado en session_state para la nueva vista
                    st.session_state.selected_fcl = fcl_number
                    st.session_state.selected_fcl_data = fcl_detail_row
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
                        <h2>📋 Detalle de Evaluación - {fcl_number}</h2>
                        <button class="modal-close" onclick="closeModal_{i}()">×</button>
                    </div>
                    
                    <div class="modal-body">
                        <div class="modal-grid">
                            <div class="modal-section">
                                <h4>📊 Información General</h4>
                                <div class="info-list">
                                    <div><strong>N° FCL:</strong> {fcl_number}</div>
                                    <div><strong>Fecha Proceso:</strong> {fcl_detail_row['FECHA DE PROCESO'].strftime('%d/%m/%Y %H:%M')}</div>
                                    <div><strong>Fecha MP:</strong> {fcl_detail_row['FECHA DE MP'].strftime('%d/%m/%Y %H:%M')}</div>
                                    <div><strong>Semana:</strong> {row2['SEMANA']}</div>
                                    <div><strong>BRIX:</strong> {fcl_detail_row['BRIX']:.2f}</div>
                                    <div><strong>Acidez:</strong> {fcl_detail_row['ACIDEZ']:.2f}</div>
                                </div>
                            </div>
                            
                            <div class="modal-section">
                                <h4>🍇 Información del Producto</h4>
                                <div class="info-list">
                                    <div><strong>Variedad:</strong> {fcl_detail_row['VARIEDAD']}</div>
                                    <div><strong>Productor:</strong> {fcl_detail_row['PRODUCTOR']}</div>
                                    <div><strong>Tipo:</strong> {fcl_detail_row['TIPO DE PRODUCTO']}</div>
                                    <div><strong>Fundo:</strong> {fcl_detail_row['FUNDO']}</div>
                                    <div><strong>Presentación:</strong> {fcl_detail_row['PRESENTACION']}</div>
                                    <div><strong>Destino:</strong> {fcl_detail_row['DESTINO']}</div>
                                    <div><strong>📸 Imágenes:</strong> {'✅ Disponibles' if fcl_detail_row.get('images', False) else '❌ No disponibles'}</div>
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
    df["PRESENTACION"] = df["PRESENTACION"].str.upper()
    df["PRESENTACION"] = df["PRESENTACION"].str.replace(" ", "")
    df["PRESENTACION"] = df["PRESENTACION"].apply(categorize_presentation)
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
        
    
    with col2:
        st.markdown("**📅 Información de Proceso**")
        st.write(f"**N° FCL:** {row['N° FCL']}")
        st.write(f"**Fecha MP:** {row['FECHA DE MP'].strftime('%d/%m/%Y')}")
        st.write(f"**Fecha Proceso:** {row['FECHA DE PROCESO'].strftime('%d/%m/%Y')}")
        st.write(f"**Semana:** {row['SEMANA']}")
        st.write(f"**Destino:** {row['DESTINO']}")
        #st.write(f"**BRIX:** {row['BRIX']:.2f}")
        #st.write(f"**Acidez:** {row['ACIDEZ']:.2f}")
    
    # Obtener datos detallados del FCL específico
    fcl_details = df[df['N° FCL'] == fcl_number]
    #fcl_details = fcl_details.reset_index()
    st.markdown("### 📋 Registros Detallados del FCL")
    
    gb = GridOptionsBuilder.from_dataframe(fcl_details)
    gb.configure_column("FECHA DE PROCESO",width=400)
    gb.configure_selection(selection_mode="multiple", use_checkbox=True,header_checkbox=True,)
        #
    
    num_rows = len(fcl_details)
    if num_rows <= 5:
        # Si hay pocas filas, altura automática
        gb.configure_grid_options(
            domLayout='normal',
            suppressRowHoverHighlight=False
        )
        table_height = None  # Altura automática
    else:
        # Si hay muchas filas, altura fija con scroll
        gb.configure_grid_options(
            domLayout='normal',
            suppressRowHoverHighlight=False,
            rowHeight=35  # Altura de cada fila
        )
        table_height = 350  # Altura máxima
    
    grid_options = gb.build()

    grid_response = AgGrid(
        fcl_details,  # Dataframe a mostrar
        gridOptions=grid_options,
        enable_enterprise_modules=False,
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        height=table_height,  # Altura dinámica
        #fit_columns_on_grid_load=True
    )
    
    # Guardar la respuesta del grid en session_state para acceder desde otras funciones
    st.session_state.grid_response = grid_response
    # Mostrar información sobre las filas seleccionadas
    selected_rows = grid_response['selected_rows']
    
    print("DEBUG - Tipo de selected_rows:", type(selected_rows))
    print("DEBUG - Contenido de selected_rows:", selected_rows)
    
    if not num_rows == None:
        #print(f"📋 Se han seleccionado {len(selected_rows)} filas para el reporte PDF")
        print("Filas seleccionadas:", selected_rows)
    
    else:
        st.info("📋 No se han seleccionado filas específicas. Se generará el reporte con todas las filas.")
    try:
        img_df = get_img_evacalidad_data(fcl_number)
        if img_df is None:
            img_df = pd.DataFrame(columns=['N° FCL','imagen'])
    
        #st.dataframe(img_df)
    
        
        
        img_df = img_df[img_df["imagen"].notna()]
    
        
        img_df = img_df["imagen"].to_list()
        
        # Tabla de datos completos
        
        
        # Sección de imágenes
        st.markdown("### 📸 Imágenes")
        with st.expander("Imágenes"):
            if len(img_df) > 0:
                
                col_img = st.columns(3)
                for i, img_url in enumerate(img_df):
                    
                    
            
                    with col_img[i % 3]:
                        st.image(img_url,width=200)
        
                    
                
            else:
                st.info("📷 No hay imágenes disponibles para este FCL")
    except:
        st.info("📷 No hay imágenes disponibles para este FCL")

    
    
    
    # Botones de acción
    #st.markdown("### ⚡ Acciones")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        try:
            generate_and_download_pdf(fcl_number, row, fcl_details,img_df)
        except:
            generate_and_download_pdf(fcl_number, row, fcl_details,[])
    
    
    
    with col4:
        if st.button("❌ Cerrar", key=f"close_{fcl_number}"):
            go_back_to_list()


def generate_and_download_pdf(fcl_number, fcl_data, detailed_records, img_df):
    """Generate and provide download link for FCL PDF report"""
    
    # Obtener las filas seleccionadas del grid
    selected_rows = pd.DataFrame()  # DataFrame vacío por defecto
    
    # Verificar si existe grid_response en session_state
    if hasattr(st.session_state, 'grid_response') and st.session_state.grid_response is not None:
        grid_response = st.session_state.grid_response
        
        # Obtener las filas seleccionadas del grid
        if 'selected_rows' in grid_response:
            selected_rows = grid_response['selected_rows']
            
        else:
            print("DEBUG - No hay filas seleccionadas en grid_response")
    
    print("DEBUG - Tipo de selected_rows:", type(selected_rows))
    print("DEBUG - Contenido de selected_rows:", selected_rows)
    
    # Determinar qué registros incluir en el PDF
    if selected_rows is None or len(selected_rows) == 0:
        # No hay filas seleccionadas, usar todas las filas
        records_to_include = detailed_records
       
    else:
        # Hay filas seleccionadas, filtrar solo esas
        try:
            # Verificar que selected_rows sea un DataFrame válido
            if isinstance(selected_rows, pd.DataFrame) and not selected_rows.empty:
                # Obtener los índices de las filas seleccionadas
                if 'index' in selected_rows.columns:
                    selected_indices = selected_rows['index'].tolist()
                    print(f"DEBUG - Índices seleccionados: {selected_indices}")
                    
                    # Verificar que los índices sean válidos
                    if all(0 <= idx < len(detailed_records) for idx in selected_indices):
                        # Filtrar los registros por los índices seleccionados
                        records_to_include = detailed_records.iloc[selected_indices].copy()
                        
                    else:
                        st.warning("⚠️ Índices de selección fuera de rango, usando todas las filas")
                        records_to_include = detailed_records
                else:
                    # Si no hay columna 'index', usar todas las filas
                    #st.warning("⚠️ No se encontró índice de filas seleccionadas, usando todas las filas")
                    records_to_include = detailed_records
            else:
                # selected_rows no es un DataFrame válido
                st.warning("⚠️ Formato de selección inválido, usando todas las filas")
                records_to_include = detailed_records
                
        except Exception as e:
            st.error(f"❌ Error al procesar filas seleccionadas: {str(e)}")
            st.info("📋 Usando todas las filas disponibles debido al error")
            records_to_include = detailed_records
    
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
        'ACIDEZ': fcl_data['ACIDEZ'],
        'FECHA DE MP': fcl_data['FECHA DE MP'].strftime('%Y/%m/%d'),
        'FECHA DE PROCESO': fcl_data['FECHA DE PROCESO'].strftime('%Y/%m/%d'),
    }

    if not records_to_include.empty:
        print(records_to_include.head(2))
    
    # Generate PDF with selected rows
    pdf_buffer = generate_fcl_pdf_report(fcl_info, records_to_include.reset_index(drop=True), images_list=img_df)
    
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
