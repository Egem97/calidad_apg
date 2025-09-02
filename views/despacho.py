import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from utils.get_api import listar_archivos_en_carpeta_compartida, get_download_url_by_name, test_json
from utils.get_token import get_access_token, get_access_token_alza
from utils.pdf_generator import generate_fcl_pdf_report
import base64
import zipfile
import io
import json


def show_despacho():
    """Mostrar la página de despacho"""
    
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
    
    exc_despachos_df = get_data()
    st.dataframe(exc_despachos_df)
    #exc_despachos_img_df = get_data_img()
    #st.dataframe(exc_despachos_img_df)
    