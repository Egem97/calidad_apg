import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from styles import styles_
import plotly.express as px
import plotly.graph_objects as go
from utils.get_api import listar_archivos_en_carpeta_compartida, get_download_url_by_name
from utils.get_token import get_access_token, get_access_token_alza
from utils.pdf_generator import generate_fcl_pdf_report
from utils.handler_db import get_img_evacalidad_data
from views.finished_product import *
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode ,JsCode

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

    empresa_mapping = {
        'GMH BERRIES S.A.C': 'AGRICOLA BLUE GOLD S.A.C.',
        'BIG BERRIES S.A.C': 'AGRICOLA BLUE GOLD S.A.C.',
        'CANYON BERRIES S.A.C': 'AGRICOLA BLUE GOLD S.A.C.',
        'AGRICOLA BLUE GOLD S.A.C': 'AGRICOLA BLUE GOLD S.A.C.',
        'EXCELLENCE FRUIT S.A.C': "SAN LUCAR S.A.",
        'GAP BERRIES S.A.C': "SAN LUCAR S.A.",
        'SAN EFISIO S.A.C': "SAN LUCAR S.A.",
        'TARA FARMS S.A.C': "SAN LUCAR S.A.",
        #'TARA FARMS S.A.C': "SAN LUCAR S.A.",
        'QBERRIES S.A.C': "SAN LUCAR S.A.",
    }
    df["EMPRESA"] = df["PRODUCTOR"].replace(empresa_mapping)
    df = df[df["N° FCL"] != "-"]
    df = df[df["N° FCL"] != "nan"]
    df = df[df["N° FCL"] != "NaN"]
    df = df[df["N° FCL"] != "None"]
    df = df[df["N° FCL"].notna()]  # Eliminar valores NaN de pandas
    df.columns = df.columns.str.strip()
    
    numeric_columns = df.select_dtypes(include=['float64', 'int64']).columns
    df[numeric_columns] = df[numeric_columns].fillna(0)

    df = df[df["EMPRESA"] == "SAN LUCAR S.A."]
    df = df.sort_values(by="FECHA DE PROCESO", ascending=False)
    df["PRESENTACION"] = df["PRESENTACION"].str.upper()
    df["PRESENTACION"] = df["PRESENTACION"].str.replace(" ", "")
    df["PRESENTACION"] = df["PRESENTACION"].apply(categorize_presentation)
    return df

def muestras_calidad():
    styles_(1)
    #st.markdown('<h1 class="main-header">🫐 Evaluación de Producto Terminado</h1>', unsafe_allow_html=True)
    col_head_1,col_head_2 = st.columns([3,1])
    with col_head_1:
        st.title("🫐 Evaluación de Producto Terminado",)

    df = clean_data()

    with col_head_2:
        search_term = st.selectbox("Buscar FCL", df["N° FCL"].unique(),index=None,placeholder="Seleccione N° FCL")
    #st.title("Evaluación de Producto Terminado")
    
    
    if search_term != None :
        df = df[df["N° FCL"]==search_term]
        #st.dataframe(df)
        row = df.copy()
        #st.markdown(f'<h1 class="main-header">📋 Detalle del FCL: {search_term}</h1>', unsafe_allow_html=True)
        st.subheader(f"📋 Detalle del FCL: {search_term}",divider="blue")
       
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**🫐 Información Básica**")
            st.write(f"**Variedades:** {', '.join(row['VARIEDAD'].unique())}")
            st.write(f"**Productores:** {', '.join(row['PRODUCTOR'].unique())}")
            st.write(f"**Tipos:** {', '.join(row['TIPO DE PRODUCTO'].unique())}")
            st.write(f"**Fundos:** {', '.join(row['FUNDO'].unique())}")
            st.write(f"**Presentaciones:** {', '.join(row['PRESENTACION'].unique())}")
        
    
        with col2:
            st.markdown("**📅 Información de Proceso**")
            st.write(f"**N° FCL:** {', '.join(row['N° FCL'].unique())}")
            st.write(f"**Fechas MP:** {', '.join(row['FECHA DE MP'].dt.strftime('%d/%m/%Y').unique())}")
            st.write(f"**Fechas Proceso:** {', '.join(row['FECHA DE PROCESO'].dt.strftime('%d/%m/%Y').unique())}")
            st.write(f"**Semanas:** {', '.join(row['SEMANA'].astype(str).unique())}")
            st.write(f"**Destinos:** {', '.join(row['DESTINO'].unique())}")
        st.markdown("### 📋 Registros Detallados del FCL")
        gb = GridOptionsBuilder.from_dataframe(df)
        gb.configure_column("FECHA DE PROCESO",width=400)
        #gb.configure_selection(selection_mode="multiple", use_checkbox=True,header_checkbox=True,)
                #
            
        num_rows = len(df)
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
                df,  # Dataframe a mostrar
                gridOptions=grid_options,
                enable_enterprise_modules=False,
                update_mode=GridUpdateMode.SELECTION_CHANGED,
                height=table_height,  # Altura dinámica
                #fit_columns_on_grid_load=True
            )
         
        try:
            
            img_df = get_img_evacalidad_data(search_term)
            
            if img_df is None:
                img_df = pd.DataFrame(columns=['N° FCL','imagen'])
            img_df = img_df[img_df["imagen"].notna()]
            img_df = img_df["imagen"].to_list()

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

        col1, col2, col3, col4 = st.columns(4)
    
        with col1:
            try:
                generate_and_download_pdf(search_term, df.iloc[0], df,img_df)
            except:
                generate_and_download_pdf(search_term, df.iloc[0], df,[])
        
        

    else:
        st.warning("Por favor, seleccione al menos un FCL para buscar.")

##Resultados de CONTRAMUESTRAS - SAN LUCAR 2025
def contramuestras_calidad():
    styles_(1)
    #st.markdown('<h1 class="main-header">🫐 Evaluación de Producto Terminado</h1>', unsafe_allow_html=True)
    col_head_1,col_head_2 = st.columns([3,1])
    with col_head_1:
        st.title("🫐 Contramuestras")
    df = pd.read_excel("Resultados de CONTRAMUESTRAS - SAN LUCAR 2025.xlsx",sheet_name="CALIDAD + CONDICIÓN")
    with col_head_2:
        st.markdown("**🔍 Búsqueda por N° FCL**")
        input_fcl = st.selectbox("Ingrese el N° FCL:", df[df['N° FCL'].notna()]['N° FCL'].unique(),index=None)
    
    if input_fcl is not None:
        df = df[df['N° FCL']==input_fcl]
    st.write(input_fcl)
    columns_ = ['N° FCL',# 'N° CONTENEDOR', #'N° DE CONTRAMUESTRA',#'DÍAS EVALUADOS',
       'MERCADO', 'PRESENTACIÓN', 'FECHA DE PRODUCCIÓN', 'FECHA DE EVALUACIÓN',
       #'DÍAS DE LA FRUTA DESDE LA COSECHA HASTA LA EVALUACIÓN', 
       'PROVEEDOR',
       'VARIEDAD', 
       'PUDRICIÓN  (Micelio-Piel Suelta) - COLAPSADO\n(A: 0% / B: 0%)',
       'HERIDAS ABIERTAS (Desgarros Humedos) \n(A: 0% / B: 0% - 1%)',
       'BLANDOS (Sobremaduros)\n(A: 0% / B: 0% - 3%)2',
       'MACHUCONES\n(A: < 2% / B: 2.1% - 3%)',
       'DESHIDRATADOS\n(A: < 2% / B: 2.1% - 3%)',
       'HERIDAS CICATRIZADAS, DEFORMES, RUSSET\n(1: 0% - 2% / 2: 2.1% - 4%)   ',
       'PRESENCIA DE PEDICELO \n(1: 0% - 2% / 2: 2.1% - 6%)',
       'RESTOS FLORALES \n(1: 0% - 2% / 2: 2.1% - 4% / 3: 4.1% - 5% / 4: >5.0%)',
       'FRUTOS INMADUROS \n(1: 0% - 1% / 2: 1.1% - 3%)   ',
       'BAYAS SIN BLOOM \n(1: 0% - 3% / 2: 3.1% - 5% / 3: 5.1% - 20% / 4: >20%)   ',
       'INSECTOS, LARVAS \n(0%)', 
       'TIERRA\n(0%)',
       'POLVO DENTRO DE LA COROLA O SUPERFICIAL EN LA CASCARA  \n(0%)',
    ]
    df = df[columns_]
    #df['N° CONTENEDOR'] = df['N° CONTENEDOR'].fillna("-")
    #df = df[df['N° CONTENEDOR']!="-"]
    df = df[df['N° FCL'].notna()]
    df['PROVEEDOR'] = df['PROVEEDOR'].fillna("NO ESPECIFICADO")
    df['PROVEEDOR'] = df['PROVEEDOR'].str.strip()
    df['VARIEDAD'] = df['VARIEDAD'].fillna("NO ESPECIFICADO")

    df['N° FCL'] = df['N° FCL'].str.strip()
    #df['N° CONTENEDOR'] = df['N° CONTENEDOR'].str.strip()
    df['MERCADO'] = df['MERCADO'].str.strip()
    df['PRESENTACIÓN'] = df['PRESENTACIÓN'].str.strip()
    df['PRESENTACIÓN'] = df['PRESENTACIÓN'].str.upper()
    df['PRESENTACIÓN'] = df['PRESENTACIÓN'].str.replace(".0","")
    df['PRESENTACIÓN'] = df['PRESENTACIÓN'].replace("4.4 OZ","4.4OZ")
    df['VARIEDAD'] = df['VARIEDAD'].str.strip()
    #df['DÍAS DE LA FRUTA DESDE LA COSECHA HASTA LA EVALUACIÓN'] = df['DÍAS DE LA FRUTA DESDE LA COSECHA HASTA LA EVALUACIÓN'].astype(int)
    df = df.rename(columns=
        {
            
            'PUDRICIÓN  (Micelio-Piel Suelta) - COLAPSADO\n(A: 0% / B: 0%)':'PUDRICIÓN',
            'HERIDAS ABIERTAS (Desgarros Humedos) \n(A: 0% / B: 0% - 1%)':'HERIDAS ABIERTAS',
            'BLANDOS (Sobremaduros)\n(A: 0% / B: 0% - 3%)2':'BLANDOS',
            'MACHUCONES\n(A: < 2% / B: 2.1% - 3%)':'MACHUCONES',
            'DESHIDRATADOS\n(A: < 2% / B: 2.1% - 3%)':'DESHIDRATADOS', 
            'HERIDAS CICATRIZADAS, DEFORMES, RUSSET\n(1: 0% - 2% / 2: 2.1% - 4%)   ':'HERIDAS CICATRIZADAS, DEFORMES, RUSSET',
            'PRESENCIA DE PEDICELO \n(1: 0% - 2% / 2: 2.1% - 6%)':'PRESENCIA DE PEDICELO',
            'RESTOS FLORALES \n(1: 0% - 2% / 2: 2.1% - 4% / 3: 4.1% - 5% / 4: >5.0%)':'RESTOS FLORALES',
            'FRUTOS INMADUROS \n(1: 0% - 1% / 2: 1.1% - 3%)   ':'FRUTOS INMADUROS',
            'BAYAS SIN BLOOM \n(1: 0% - 3% / 2: 3.1% - 5% / 3: 5.1% - 20% / 4: >20%)   ':'BAYAS SIN BLOOM',
            'INSECTOS, LARVAS \n(0%)':'INSECTOS, LARVAS', 
            'TIERRA\n(0%)':'TIERRA',
            'POLVO DENTRO DE LA COROLA O SUPERFICIAL EN LA CASCARA  \n(0%)':'POLVO DENTRO DE LA COROLA O SUPERFICIAL EN LA CASCARA',    
        }
    )
    
    #print(df.columns)
    cols_numerics = [
        'PUDRICIÓN', 'HERIDAS ABIERTAS', 'BLANDOS', 'MACHUCONES',
        'DESHIDRATADOS', 'HERIDAS CICATRIZADAS, DEFORMES, RUSSET',
        'PRESENCIA DE PEDICELO', 'RESTOS FLORALES', 'FRUTOS INMADUROS',
        'BAYAS SIN BLOOM', 'INSECTOS, LARVAS', 'TIERRA',
        'POLVO DENTRO DE LA COROLA O SUPERFICIAL EN LA CASCARA'
    ]
    for col in cols_numerics:
        df[col] = df[col].fillna(0)
        df[col] = df[col].astype(float)
    df = df.reset_index(drop=True)
    
    #print(df.info())
    #st.dataframe(df)
    firmeza_df = pd.read_excel("Resultados de CONTRAMUESTRAS - SAN LUCAR 2025.xlsx",sheet_name="FIRMEZA, COLOR DE PULPA",skiprows=1)
    if input_fcl is not None:
        firmeza_df = firmeza_df[firmeza_df['N° FCL']==input_fcl]
    cols_firmeza =['N° FCL', #'N° CONTENEDOR',#, 'N° DE CONTRAMUESTRA', 'DÍAS EVALUADOS',
       #'MERCADO', 
       'PRESENTACIÓN', 'FECHA DE PRODUCCIÓN', 'FECHA DE EVALUACIÓN',
       'DÍAS DE LA FRUTA DESDE LA COSECHA HASTA LA EVALUACIÓN', 'PROVEEDOR',
       'VARIEDAD','<60', '60-69',
       '70-80', '>80', '< 60', '60 - 693', '70 - 80', '> 80',
       '° BRIX \n> = 11', '% ACIDEZ\n< = 1.4', 'RATIO\n> = 8', 
    ]
    firmeza_df = firmeza_df[cols_firmeza]
    #firmeza_df['N° CONTENEDOR'] = firmeza_df['N° CONTENEDOR'].fillna("-")
    #firmeza_df = firmeza_df[firmeza_df['N° CONTENEDOR']!="-"]
    firmeza_df = firmeza_df[firmeza_df['N° FCL'].notna()]
    firmeza_df['PROVEEDOR'] = firmeza_df['PROVEEDOR'].fillna("NO ESPECIFICADO")
    firmeza_df['PROVEEDOR'] = firmeza_df['PROVEEDOR'].str.strip()
    firmeza_df['VARIEDAD'] = firmeza_df['VARIEDAD'].fillna("NO ESPECIFICADO")

    firmeza_df['N° FCL'] = firmeza_df['N° FCL'].str.strip()
    #firmeza_df['N° CONTENEDOR'] = firmeza_df['N° CONTENEDOR'].str.strip()
    #firmeza_df['MERCADO'] = firmeza_df['MERCADO'].fillna("NO ESPECIFICADO")
    #firmeza_df['MERCADO'] = firmeza_df['MERCADO'].str.strip()
    firmeza_df['PRESENTACIÓN'] = firmeza_df['PRESENTACIÓN'].str.strip()
    firmeza_df['PRESENTACIÓN'] = firmeza_df['PRESENTACIÓN'].str.upper()
    firmeza_df['PRESENTACIÓN'] = firmeza_df['PRESENTACIÓN'].replace("4.4 OZ","4.4OZ")
    firmeza_df['VARIEDAD'] = firmeza_df['VARIEDAD'].str.strip()
    firmeza_df['DÍAS DE LA FRUTA DESDE LA COSECHA HASTA LA EVALUACIÓN'] = firmeza_df['DÍAS DE LA FRUTA DESDE LA COSECHA HASTA LA EVALUACIÓN'].astype(int)
    
    firmeza_df = firmeza_df.rename(columns=
        {
            
            '° BRIX \n> = 11':'BRIX',
            '% ACIDEZ\n< = 1.4':'ACIDEZ',
            'RATIO\n> = 8':'RATIO',

        }
    )
    cols_numerics_f = ['<60', '60-69', '70-80', '>80', '< 60', '60 - 693',
       '70 - 80', '> 80', 'BRIX', 'ACIDEZ', 'RATIO']
    for col in cols_numerics_f:
        firmeza_df[col] = firmeza_df[col].fillna(0)
        firmeza_df[col] = firmeza_df[col].astype(float)
    firmeza_df = firmeza_df.reset_index(drop=True)
    #st.dataframe(firmeza_df)
    pesos_df = pd.read_excel("Resultados de CONTRAMUESTRAS - SAN LUCAR 2025.xlsx",sheet_name="PESOS",skiprows=2)
    cols_pesos=['N° FCL', 'N° CONTENEDOR', 'N° DE CONTRAMUESTRA', 'DÍAS EVALUADOS',
       'MERCADO', 'PRESENTACIÓN', 'FECHA DE PRODUCIÓN', 'PROVEEDOR',
       'VARIEDAD', 'PESO 1\n(gramos)\n>=135',
       'PESO 2\n(gramos)\n>=135', 'PESO 3\n(gramos)\n>=135',
       'PESO 4\n(gramos)\n>=135', 'PESO 5\n(gramos)\n>=135',
       'PESO 6\n(gramos)\n>=135', 'PESO 7\n(gramos)\n>=135',
       'PESO 8\n(gramos)\n>=135', 'PESO 9\n(gramos)\n>=135',
       'PESO 10\n(gramos)\n>=135', 'PESO 11\n(gramos)\n>=135',
       'PESO 12\n(gramos)\n>=135', 'PESO BRUTO PROMEDIO\n(gramos)\n>=135']
    pesos_df = pesos_df[cols_pesos]
    pesos_df['N° CONTENEDOR'] = pesos_df['N° CONTENEDOR'].fillna("-")
    pesos_df = pesos_df[pesos_df['N° CONTENEDOR']!="-"]
    pesos_df['PROVEEDOR'] = pesos_df['PROVEEDOR'].fillna("NO ESPECIFICADO")
    pesos_df['PROVEEDOR'] = pesos_df['PROVEEDOR'].str.strip()
    pesos_df['VARIEDAD'] = pesos_df['VARIEDAD'].fillna("NO ESPECIFICADO")

    pesos_df['N° FCL'] = pesos_df['N° FCL'].str.strip()
    pesos_df['N° CONTENEDOR'] = pesos_df['N° CONTENEDOR'].str.strip()
    pesos_df['MERCADO'] = pesos_df['MERCADO'].str.strip()
    pesos_df['PRESENTACIÓN'] = pesos_df['PRESENTACIÓN'].str.strip()
    pesos_df['VARIEDAD'] = pesos_df['VARIEDAD'].str.strip()
    pesos_df = pesos_df.rename(columns ={
        'PESO 1\n(gramos)\n>=135':'PESO 1',
        'PESO 2\n(gramos)\n>=135':'PESO 2',
        'PESO 3\n(gramos)\n>=135':'PESO 3',
        'PESO 4\n(gramos)\n>=135':'PESO 4',
        'PESO 5\n(gramos)\n>=135':'PESO 5',
        'PESO 6\n(gramos)\n>=135':'PESO 6',
        'PESO 7\n(gramos)\n>=135':'PESO 7',
        'PESO 8\n(gramos)\n>=135':'PESO 8',
        'PESO 9\n(gramos)\n>=135':'PESO 9',
        'PESO 10\n(gramos)\n>=135':'PESO 10',
        'PESO 11\n(gramos)\n>=135':'PESO 11',
        'PESO 12\n(gramos)\n>=135':'PESO 12',
        'PESO BRUTO PROMEDIO\n(gramos)\n>=135':'PESO BRUTO PROMEDIO',
    })
    cols_numerics_p = ['PESO 1', 'PESO 2', 'PESO 3', 'PESO 4', 'PESO 5', 'PESO 6',
       'PESO 7', 'PESO 8', 'PESO 9', 'PESO 10', 'PESO 11', 'PESO 12',
       'PESO BRUTO PROMEDIO']
    for col in cols_numerics_p:
        pesos_df[col] = pesos_df[col].replace("-",0)
        pesos_df[col] = pesos_df[col].fillna(0)
        pesos_df[col] = pesos_df[col].astype(float)
    #print(pesos_df.info())
    st.subheader("FIRMEZA, COLOR DE PULPA")
    st.dataframe(df)
    st.subheader("CALIDAD + CONDICIÓN")
    st.dataframe(firmeza_df)
    #st.dataframe(pesos_df)
    st.subheader("JOINS",divider="blue")
    df = pd.merge(df, firmeza_df, on=['N° FCL','PRESENTACIÓN','FECHA DE PRODUCCIÓN'], how='left')# 'N° CONTENEDOR', 
    #df = pd.merge(df, pesos_df, on=['N° FCL', 'N° CONTENEDOR'], how='left')
    st.write(df.shape)
    st.dataframe(df)
    #img_df = pd.read_excel("Resultados de CONTRAMUESTRAS - SAN LUCAR 2025.xlsx",sheet_name="FOTOS",skiprows=2)
    #st.dataframe(img_df)