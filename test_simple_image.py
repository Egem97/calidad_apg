"""
Test simple para mostrar una imagen específica de Google Drive
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
        # Definir scopes necesarios
        SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
        
        # Cargar credenciales desde el archivo JSON
        credentials = service_account.Credentials.from_service_account_file(
            'nifty-might-269005-cd303aaaa33f.json', 
            scopes=SCOPES
        )
        
        # Construir el servicio de Drive
        service = build('drive', 'v3', credentials=credentials)
        return service
        
    except Exception as e:
        st.error(f"❌ Error en autenticación: {str(e)}")
        return None


def extract_file_id_from_url(url):
    """Extraer file ID de URL de Google Drive"""
    if not url:
        return None
        
    # Patrones comunes para URLs de Google Drive
    patterns = [
        r'/file/d/([a-zA-Z0-9-_]+)',  # /file/d/FILE_ID
        r'id=([a-zA-Z0-9-_]+)',       # id=FILE_ID
        r'/d/([a-zA-Z0-9-_]+)',       # /d/FILE_ID
        r'open\?id=([a-zA-Z0-9-_]+)'  # open?id=FILE_ID
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None


def download_image_as_base64(service, file_id):
    """Descargar imagen y convertir a base64"""
    try:
        # Obtener metadata del archivo
        st.write(f"🔍 Obteniendo metadata para file_id: {file_id}")
        file_metadata = service.files().get(fileId=file_id).execute()
        mime_type = file_metadata.get('mimeType', '')
        file_name = file_metadata.get('name', 'Sin nombre')
        
        st.write(f"📄 Archivo: {file_name}")
        st.write(f"📋 MIME Type: {mime_type}")
        
        if not mime_type.startswith('image/'):
            st.warning(f"⚠️ El archivo no es una imagen: {mime_type}")
            return None
        
        # Descargar contenido del archivo
        st.write("⬇️ Iniciando descarga...")
        request = service.files().get_media(fileId=file_id)
        file_content = io.BytesIO()
        
        # Descargar en chunks
        downloader = request
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            if status:
                file_content.write(status)
        
        # Verificar que se descargó algo
        file_content.seek(0)
        image_bytes = file_content.getvalue()
        
        if not image_bytes:
            st.error("❌ No se descargó ningún contenido")
            return None
        
        st.write(f"📦 Bytes descargados: {len(image_bytes)}")
        
        # Convertir a base64
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        # Determinar formato de imagen
        if 'png' in mime_type:
            format_type = 'png'
        elif 'jpeg' in mime_type or 'jpg' in mime_type:
            format_type = 'jpeg'
        elif 'gif' in mime_type:
            format_type = 'gif'
        elif 'webp' in mime_type:
            format_type = 'webp'
        else:
            format_type = 'jpeg'  # default
        
        result = f"data:image/{format_type};base64,{image_base64}"
        st.write(f"✅ Base64 generado: {len(result)} caracteres")
        
        return result
        
    except HttpError as e:
        if e.resp.status == 404:
            st.error("❌ Imagen no encontrada en Google Drive")
        elif e.resp.status == 403:
            st.error("❌ Sin permisos para acceder a la imagen")
        else:
            st.error(f"❌ Error HTTP: {e}")
        return None
        
    except Exception as e:
        st.error(f"❌ Error inesperado: {str(e)}")
        st.error(f"🔍 Tipo de error: {type(e).__name__}")
        import traceback
        st.error(f"📋 Traceback: {traceback.format_exc()}")
        return None


def main():
    st.title("🧪 Test Simple - Imagen Google Drive")
    
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
        st.write("🔍 Verificando que el archivo existe...")
        file_metadata = service.files().get(fileId=file_id).execute()
        st.write(f"✅ Archivo encontrado: {file_metadata.get('name', 'Sin nombre')}")
    except Exception as e:
        st.error(f"❌ Error al verificar archivo: {str(e)}")
        return
    
    # Descargar imagen
    st.write("🚀 Iniciando descarga de imagen...")
    img_base64 = download_image_as_base64(service, file_id)
    
    if img_base64:
        st.success("✅ Imagen descargada exitosamente")
        
        # Mostrar imagen
        st.markdown("### 📸 Imagen Descargada")
        try:
            st.image(img_base64, caption="Imagen desde Google Drive", use_column_width=True)
            st.success("✅ Imagen mostrada correctamente")
        except Exception as e:
            st.error(f"❌ Error al mostrar imagen: {str(e)}")
        
        # Información adicional
        st.markdown("### ℹ️ Información")
        st.write(f"**File ID:** {file_id}")
        st.write(f"**URL original:** {test_url}")
        st.write(f"**Tamaño base64:** {len(img_base64)} caracteres")
        
    else:
        st.error("❌ No se pudo descargar la imagen")


if __name__ == "__main__":
    main()
