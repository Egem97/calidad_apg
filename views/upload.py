import streamlit as st
import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta
from styles import styles_
import plotly.express as px
import plotly.graph_objects as go
from utils.get_api import listar_archivos_en_carpeta_compartida, get_download_url_by_name
from utils.get_token import get_access_token, get_access_token_alza
from utils.pdf_generator import generate_fcl_pdf_report
from utils.handler_db import get_img_evacalidad_data
from views.finished_product import *
from utils.get_sheets import list_folders,authenticate_google_drive,list_images_in_folder,download_image,image_to_base64


def share_img():
    styles_(1)
    #st.markdown('<h1 class="main-header">🫐 Evaluación de Producto Terminado</h1>', unsafe_allow_html=True)
    col_head_1,col_head_2,col_head_3 = st.columns([3,1,1])
    with col_head_1:
        st.title("Buscar IMG",)
    with col_head_2:
        fcl_input = st.text_input("Selecciona FCL", placeholder="Ingresa FCL")
    with col_head_3:
        btn = st.button("Buscar")
    
    if btn:
        service = authenticate_google_drive()
        folders = list_folders(service, "1OqY3VnNgsbnKRuqVZqFi6QSXqKDC4uox", fcl_input)
        all_data = []

        for i, folder in enumerate(folders, 1):
            print(f"\n📂 Procesando carpeta {i}/{len(folders)}: {folder['name']}")
            
            # Obtener imágenes en la carpeta
            images = list_images_in_folder(service, folder['id'])
            
            if not images:
                print(f"   ⚠️  No se encontraron imágenes en '{folder['name']}'")
                # Agregar carpeta sin imágenes como una fila
                all_data.append({
                    'folder_id': folder['id'],
                    'folder_name': folder['name'],
                    'folder_webViewLink': folder['webViewLink'],
                    'folder_modifiedTime': folder.get('modifiedTime'),
                    'image_id': None,
                    'image_name': None,
                    'image_webViewLink': None,
                    'image_modifiedTime': None,
                    'image_base64': None,
                    'image_size_mb': 0
                })
                continue
            
            print(f"   ✅ Se encontraron {len(images)} imágenes")
            
            # Procesar cada imagen como una fila separada
            for j, image in enumerate(images, 1):
                original_size_mb = int(image.get('size', 0)) / (1024 * 1024)
                print(f"      🖼️  Procesando imagen {j}/{len(images)}: {image['name']} ({original_size_mb:.2f}MB)")
                
                # Descargar imagen
                image_data = download_image(service, image['id'])
                if not image_data:
                    print(f"         ❌ Error al descargar {image['name']}")
                    # Agregar fila con error
                    all_data.append({
                        'folder_id': folder['id'],
                        'folder_name': folder['name'],
                        'folder_webViewLink': folder['webViewLink'],
                        'folder_modifiedTime': folder.get('modifiedTime'),
                        'image_id': image['id'],
                        'image_name': image['name'],
                        'image_webViewLink': image.get('webViewLink'),
                        'image_modifiedTime': image.get('modifiedTime'),
                        'image_base64': None,
                        'image_size_mb': original_size_mb
                    })
                    continue
                
                # Convertir a base64
                base64_image = image_to_base64(image_data)
                if base64_image:
                    # Calcular tamaño optimizado
                    optimized_size_mb = len(base64_image) * 0.75 / (1024 * 1024)
                    reduction_percent = (1 - optimized_size_mb / original_size_mb) * 100 if original_size_mb > 0 else 0
                    
                    # Agregar fila con imagen procesada
                    all_data.append({
                        'folder_id': folder['id'],
                        'folder_name': folder['name'],
                        'folder_webViewLink': folder['webViewLink'],
                        'folder_modifiedTime': folder.get('modifiedTime'),
                        'image_id': image['id'],
                        'image_name': image['name'],
                        'image_webViewLink': image.get('webViewLink'),
                        'image_modifiedTime': image.get('modifiedTime'),
                        'image_base64': base64_image,
                        'image_size_mb': optimized_size_mb
                    })
                else:
                    
                    # Agregar fila con error
                    all_data.append({
                        'folder_id': folder['id'],
                        'folder_name': folder['name'],
                        'folder_webViewLink': folder['webViewLink'],
                        'folder_modifiedTime': folder.get('modifiedTime'),
                        'image_id': image['id'],
                        'image_name': image['name'],
                        'image_webViewLink': image.get('webViewLink'),
                        'image_modifiedTime': image.get('modifiedTime'),
                        'image_base64': None,
                        'image_size_mb': original_size_mb
                    })
        dff = pd.DataFrame(all_data)
        #st.dataframe(dff)
        #print(dff.columns)
        if not os.path.exists("./img/bd_img.parquet"):
            bd_img = pd.DataFrame(columns=['folder_id', 'folder_name', 'folder_webViewLink', 'folder_modifiedTime',
        'image_id', 'image_name', 'image_webViewLink', 'image_modifiedTime',
        'image_base64', 'image_size_mb'])
        else:
            bd_img = pd.read_parquet("./img/bd_img.parquet")
        #    os.makedirs("./img")
        bd_img = pd.concat([bd_img, dff], ignore_index=True)
        bd_img = bd_img.drop_duplicates()
        bd_img.to_parquet("./img/bd_img.parquet", index=False)
        st.write(bd_img.shape)
        st.dataframe(bd_img)
        st.success(f"✅ Imágenes procesadas y guardadas en Parquet")
            
