# test_shared_folder_images.py
"""
Test para listar y descargar imágenes de la carpeta compartida "CALIDAD - SAN LUCAR"
"""

import streamlit as st
import requests
import base64
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import io
import re


def get_google_drive_service():
    """Obtener servicio de Google Drive usando service account"""
    try:
        SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
        credentials = service_account.Credentials.from_service_account_file(
            'nifty-might-269005-cd303aaaa33f.json', 
            scopes=SCOPES
        )
        service = build('drive', 'v3', credentials=credentials)
        return service
    except Exception as e:
        st.error(f"❌ Error en autenticación: {str(e)}")
        return None


def list_shared_images(service):
    """Listar todas las imágenes disponibles en carpetas compartidas"""
    try:
        st.write("🔍 Buscando imágenes en carpetas compartidas...")
        
        # Buscar archivos de imagen
        results = service.files().list(
            pageSize=50,
            fields="nextPageToken, files(id, name, mimeType, size, parents, webViewLink)",
            q="mimeType contains 'image/' and trashed=false"
        ).execute()
        
        files = results.get('files', [])
        
        if not files:
            st.warning("⚠️ No se encontraron archivos de imagen")
            return []
        
        st.success(f"✅ Encontrados {len(files)} archivos de imagen")
        return files
        
    except Exception as e:
        st.error(f"❌ Error al listar archivos: {str(e)}")
        return []


def download_image(service, file_id):
    """Descargar imagen y convertir a base64"""
    try:
        # Obtener metadata
        file_metadata = service.files().get(fileId=file_id).execute()
        file_name = file_metadata.get('name', 'Sin nombre')
        mime_type = file_metadata.get('mimeType', '')
        
        st.write(f"�� Descargando: {file_name}")
        
        # Descargar archivo
        request = service.files().get_media(fileId=file_id)
        file_content = io.BytesIO()
        
        downloader = request
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            if status:
                file_content.write(status)
        
        # Convertir a base64
        file_content.seek(0)
        image_bytes = file_content.getvalue()
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        # Determinar formato
        if 'png' in mime_type:
            format_type = 'png'
        elif 'jpeg' in mime_type or 'jpg' in mime_type:
            format_type = 'jpeg'
        elif 'gif' in mime_type:
            format_type = 'gif'
        elif 'webp' in mime_type:
            format_type = 'webp'
        else:
            format_type = 'jpeg'
        
        result = f"data:image/{format_type};base64,{image_base64}"
        return result, file_name, mime_type
        
    except Exception as e:
        st.error(f"❌ Error al descargar {file_name}: {str(e)}")
        return None, None, None


def main():
    st.title("�� Test - Imágenes de Carpeta Compartida")
    
    st.markdown("""
    ### �� Objetivo:
    Listar y descargar imágenes de la carpeta "CALIDAD - SAN LUCAR" compartida con la cuenta de servicio.
    """)
    
    # Conectar a Google Drive
    with st.spinner("Conectando con Google Drive..."):
        service = get_google_drive_service()
    
    if not service:
        st.error("❌ No se pudo conectar con Google Drive")
        return
    
    st.success("✅ Conexión exitosa con Google Drive")
    
    # Listar imágenes
    if st.button("🔍 Listar Imágenes Disponibles"):
        files = list_shared_images(service)
        
        if files:
            st.markdown("### �� Archivos de Imagen Encontrados:")
            
            # Mostrar lista de archivos
            for i, file in enumerate(files):
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.write(f"**{file['name']}**")
                    st.write(f"ID: `{file['id']}` | Tipo: {file['mimeType']}")
                    if 'size' in file:
                        st.write(f"Tamaño: {int(file['size']):,} bytes")
                
                with col2:
                    if st.button(f"📥 Descargar {i+1}", key=f"download_{i}"):
                        with st.spinner(f"Descargando {file['name']}..."):
                            img_base64, file_name, mime_type = download_image(service, file['id'])
                            
                            if img_base64:
                                st.success("✅ Descarga exitosa")
                                
                                # Mostrar imagen
                                st.markdown(f"### 📸 {file_name}")
                                st.image(img_base64)
                                
                                # Información
                                st.markdown("### ℹ️ Información")
                                st.write(f"**Nombre:** {file_name}")
                                st.write(f"**MIME Type:** {mime_type}")
                                st.write(f"**File ID:** {file['id']}")
                                st.write(f"**Tamaño base64:** {len(img_base64):,} caracteres")
                            else:
                                st.error("❌ Error en la descarga")
                
                with col3:
                    if st.button(f"🔗 Ver URL {i+1}", key=f"url_{i}"):
                        if 'webViewLink' in file:
                            st.write(f"**URL:** {file['webViewLink']}")
                        else:
                            st.write("URL no disponible")
                
                st.markdown("---")
    
    # Opción para ingresar File ID manualmente
    st.markdown("### 🔧 Probar File ID Específico")
    manual_file_id = st.text_input(
        "File ID de Google Drive:",
        placeholder="Ingresa un File ID específico"
    )
    
    if manual_file_id and st.button("�� Descargar por File ID"):
        with st.spinner("Descargando imagen..."):
            img_base64, file_name, mime_type = download_image(service, manual_file_id)
            
            if img_base64:
                st.success("✅ Descarga exitosa")
                st.image(img_base64)
                
                st.markdown("### ℹ️ Información")
                st.write(f"**Nombre:** {file_name}")
                st.write(f"**MIME Type:** {mime_type}")
                st.write(f"**File ID:** {manual_file_id}")
                st.write(f"**Tamaño base64:** {len(img_base64):,} caracteres")
            else:
                st.error("❌ No se pudo descargar la imagen")


if __name__ == "__main__":
    main()