import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from utils.get_api import listar_archivos_en_carpeta_compartida, get_download_url_by_name
from utils.get_token import get_access_token, get_access_token_alza


st.markdown('<h1 class="main-header">🫐Test imagenes ONE DRIVE</h1>', unsafe_allow_html=True)

@st.cache_data(show_spinner="Cargando images...",ttl=3600)
def get_images():
    """Cargar solo metadatos de imágenes para optimizar rendimiento"""
    access_token = get_access_token_alza()
    DATAS = listar_archivos_en_carpeta_compartida(access_token, "b!M5ucw3aa_UqBAcqv3a6affR7vTZM2a5ApFygaKCcATxyLdOhkHDiRKl9EvzaYbuR", "01XOBWFSBLVGULAQNEKNG2WR7CPRACEN7Q")
    data_ = get_download_url_by_name(DATAS, "despacho_img.xlsx")
    
    df = pd.read_excel(data_)
    
    return df
df = get_images()
st.dataframe(df)






