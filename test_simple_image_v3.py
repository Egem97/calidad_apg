"""
Test simple v3 - Múltiples enfoques para mostrar imagen de Google Drive
"""

import streamlit as st
import requests
import base64
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import io
import re
from PIL import Image


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


def extract_file_id_from_url(url):
    """Extraer file ID de URL de Google Drive"""
    if not url:
        return None
    
    # Buscar el patrón id= en la URL
    match = re.search(r'id=([a-zA-Z0-9-_]+)', url)
    if match:
        return match.group(1)
    return None


def try_download_method_1(service, file_id):
    """Método 1: Usando la API de Google Drive directamente"""
    try:
        st.write("🔄 Probando Método 1: API directa...")
        
        # Obtener metadata
        file_metadata = service.files().get(fileId=file_id).execute()
        mime_type = file_metadata.get('mimeType', '')
        
        if not mime_type.startswith('image/'):
            st.warning(f"⚠️ No es una imagen: {mime_type}")
            return None
        
        # Descargar usando get_media
        request = service.files().get_media(fileId=file_id)
        file_content = io.BytesIO()
        
        downloader = request
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            if status:
                file_content.write(status)
        
        file_content.seek(0)
        image_bytes = file_content.getvalue()
        
        if not image_bytes:
            st.error("❌ No se descargó contenido")
            return None
        
        # Convertir a base64
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        # Determinar formato
        if 'png' in mime_type:
            format_type = 'png'
        elif 'jpeg' in mime_type or 'jpg' in mime_type:
            format_type = 'jpeg'
        else:
            format_type = 'jpeg'
        
        result = f"data:image/{format_type};base64,{image_base64}"
        st.success(f"✅ Método 1 exitoso: {len(result)} caracteres")
        return result
        
    except Exception as e:
        st.error(f"❌ Método 1 falló: {str(e)}")
        return None


def try_download_method_2(service, file_id):
    """Método 2: Usando requests con token de acceso"""
    try:
        st.write("🔄 Probando Método 2: Requests con token...")
        
        # Obtener token
        credentials = service._credentials
        credentials.refresh(requests.Request())
        access_token = credentials.token
        
        # URL de descarga
        download_url = f"https://www.googleapis.com/drive/v3/files/{file_id}?alt=media"
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(download_url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            # Convertir a base64
            image_base64 = base64.b64encode(response.content).decode('utf-8')
            
            # Determinar formato
            content_type = response.headers.get('content-type', '')
            if 'png' in content_type:
                format_type = 'png'
            elif 'jpeg' in content_type or 'jpg' in content_type:
                format_type = 'jpeg'
            else:
                format_type = 'jpeg'
            
            result = f"data:image/{format_type};base64,{image_base64}"
            st.success(f"✅ Método 2 exitoso: {len(result)} caracteres")
            return result
        else:
            st.error(f"❌ Método 2 falló: HTTP {response.status_code}")
            return None
            
    except Exception as e:
        st.error(f"❌ Método 2 falló: {str(e)}")
        return None


def try_download_method_3(service, file_id):
    """Método 3: Usando URL de descarga directa"""
    try:
        st.write("🔄 Probando Método 3: URL directa...")
        
        # Obtener URL de descarga
        file_metadata = service.files().get(fileId=file_id, fields="webContentLink").execute()
        download_url = file_metadata.get('webContentLink')
        
        if not download_url:
            st.error("❌ No se pudo obtener URL de descarga")
            return None
        
        # Descargar usando requests
        response = requests.get(download_url, timeout=30)
        
        if response.status_code == 200:
            # Convertir a base64
            image_base64 = base64.b64encode(response.content).decode('utf-8')
            
            # Determinar formato
            content_type = response.headers.get('content-type', '')
            if 'png' in content_type:
                format_type = 'png'
            elif 'jpeg' in content_type or 'jpg' in content_type:
                format_type = 'jpeg'
            else:
                format_type = 'jpeg'
            
            result = f"data:image/{format_type};base64,{image_base64}"
            st.success(f"✅ Método 3 exitoso: {len(result)} caracteres")
            return result
        else:
            st.error(f"❌ Método 3 falló: HTTP {response.status_code}")
            return None
            
    except Exception as e:
        st.error(f"❌ Método 3 falló: {str(e)}")
        return None


def main():
    st.title("🧪 Test Simple v3 - Múltiples Métodos")
    
    # URL de prueba
    test_url = "https://drive.google.com/thumbnail?id=1m7T9_aMITUrQ9McfbA152gam0Sj0iOYJ&sz=w800"
    
    st.write(f"**URL de prueba:** {test_url}")
    
    # Extraer file ID
    file_id = extract_file_id_from_url(test_url)
    st.write(f"**File ID extraído:** {file_id}")
    
    if not file_id:
        st.error("❌ No se pudo extraer el File ID de la URL")
        return
    
    # Obtener servicio de Google Drive
    with st.spinner("Conectando con Google Drive..."):
        service = get_google_drive_service()
    
    if not service:
        st.error("❌ No se pudo conectar con Google Drive")
        return
    
    st.success("✅ Conexión exitosa con Google Drive")
    
    # Verificar que el archivo existe
    try:
        st.write("🔍 Verificando archivo...")
        file_metadata = service.files().get(fileId=file_id).execute()
        file_name = file_metadata.get('name', 'Sin nombre')
        mime_type = file_metadata.get('mimeType', 'No especificado')
        st.write(f"✅ Archivo: {file_name}")
        st.write(f"📋 MIME Type: {mime_type}")
        
    except Exception as e:
        st.error(f"❌ Error al verificar archivo: {str(e)}")
        return
    
    # Probar diferentes métodos
    st.markdown("### 🔄 Probando Métodos de Descarga")
    
    img_base64 = None
    
    # Método 1
    img_base64 = try_download_method_1(service, file_id)
    if img_base64:
        st.success("🎉 ¡Método 1 funcionó!")
    else:
        # Método 2
        img_base64 = try_download_method_2(service, file_id)
        if img_base64:
            st.success("🎉 ¡Método 2 funcionó!")
        else:
            # Método 3
            img_base64 = try_download_method_3(service, file_id)
            if img_base64:
                st.success("🎉 ¡Método 3 funcionó!")
    
    # Mostrar resultado
    if img_base64:
        st.markdown("### 📸 Imagen Descargada")
        try:
            st.image(img_base64, caption=f"Imagen: {file_name}", use_column_width=True)
            st.success("✅ Imagen mostrada correctamente")
        except Exception as e:
            st.error(f"❌ Error al mostrar imagen: {str(e)}")
        
        # Información
        st.markdown("### ℹ️ Información")
        st.write(f"**File ID:** {file_id}")
        st.write(f"**Nombre:** {file_name}")
        st.write(f"**MIME Type:** {mime_type}")
        st.write(f"**Tamaño base64:** {len(img_base64)} caracteres")
        
    else:
        st.error("❌ Ningún método funcionó para descargar la imagen")


if __name__ == "__main__":
    main()
