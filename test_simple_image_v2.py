"""
Test simple v2 - Enfoque alternativo para mostrar imagen de Google Drive
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


def download_image_simple(service, file_id):
    """Descarga simple de imagen usando requests con token de acceso"""
    try:
        # Obtener token de acceso
        credentials = service._credentials
        credentials.refresh(requests.Request())
        access_token = credentials.token
        
        # Construir URL de descarga directa
        download_url = f"https://www.googleapis.com/drive/v3/files/{file_id}?alt=media"
        
        # Headers con autorización
        headers = {
            'Authorization': f'Bearer {access_token}',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        st.write(f"🔗 URL de descarga: {download_url}")
        st.write(f"🔑 Token: {access_token[:20]}...")
        
        # Descargar imagen
        response = requests.get(download_url, headers=headers, timeout=30)
        
        st.write(f"📊 Status Code: {response.status_code}")
        st.write(f"📦 Content Length: {len(response.content)} bytes")
        st.write(f"📋 Content Type: {response.headers.get('content-type', 'No especificado')}")
        
        if response.status_code == 200:
            # Convertir a base64
            image_base64 = base64.b64encode(response.content).decode('utf-8')
            
            # Determinar formato basado en content-type
            content_type = response.headers.get('content-type', '')
            if 'png' in content_type:
                format_type = 'png'
            elif 'jpeg' in content_type or 'jpg' in content_type:
                format_type = 'jpeg'
            elif 'gif' in content_type:
                format_type = 'gif'
            elif 'webp' in content_type:
                format_type = 'webp'
            else:
                format_type = 'jpeg'  # default
            
            result = f"data:image/{format_type};base64,{image_base64}"
            st.write(f"✅ Base64 generado: {len(result)} caracteres")
            return result
        else:
            st.error(f"❌ Error HTTP: {response.status_code}")
            st.error(f"📋 Respuesta: {response.text[:200]}...")
            return None
            
    except Exception as e:
        st.error(f"❌ Error inesperado: {str(e)}")
        import traceback
        st.error(f"📋 Traceback: {traceback.format_exc()}")
        return None


def main():
    st.title("🧪 Test Simple v2 - Imagen Google Drive")
    
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
        file_name = file_metadata.get('name', 'Sin nombre')
        mime_type = file_metadata.get('mimeType', 'No especificado')
        st.write(f"✅ Archivo encontrado: {file_name}")
        st.write(f"📋 MIME Type: {mime_type}")
        
        if not mime_type.startswith('image/'):
            st.warning(f"⚠️ El archivo no parece ser una imagen: {mime_type}")
            
    except Exception as e:
        st.error(f"❌ Error al verificar archivo: {str(e)}")
        return
    
    # Descargar imagen
    st.write("🚀 Iniciando descarga de imagen...")
    img_base64 = download_image_simple(service, file_id)
    
    if img_base64:
        st.success("✅ Imagen descargada exitosamente")
        
        # Mostrar imagen
        st.markdown("### 📸 Imagen Descargada")
        try:
            st.image(img_base64, caption=f"Imagen: {file_name}", use_column_width=True)
            st.success("✅ Imagen mostrada correctamente")
        except Exception as e:
            st.error(f"❌ Error al mostrar imagen: {str(e)}")
        
        # Información adicional
        st.markdown("### ℹ️ Información")
        st.write(f"**File ID:** {file_id}")
        st.write(f"**Nombre:** {file_name}")
        st.write(f"**MIME Type:** {mime_type}")
        st.write(f"**URL original:** {test_url}")
        st.write(f"**Tamaño base64:** {len(img_base64)} caracteres")
        
    else:
        st.error("❌ No se pudo descargar la imagen")


if __name__ == "__main__":
    main()
