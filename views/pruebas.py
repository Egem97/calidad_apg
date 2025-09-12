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

def show_pruebas():
    st.markdown("### PRUEBAS")
    input_fcl = st.text_input("Ingrese el número de FCL")
    img_df = get_img_despacho_data(input_fcl)
    st.dataframe(img_df)
    img_df = img_df[img_df["image_base64"].notna()]
    img_df = img_df["image_base64"].to_list()
    if len(img_df) > 0:
        col_img = st.columns(3)
        for i, img_url in enumerate(img_df):
            with col_img[i % 3]:
                st.image(img_url, width=200)
    input_image = st.text_input("Ingrese la imagen en base64")
    try:
        st.image(input_image, width=200)
    except Exception as e:
        st.error(f"Error al mostrar la imagen: {e}")