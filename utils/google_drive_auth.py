"""
Google Drive authentication and image download utilities
"""

import os
import io
import base64
import streamlit as st
import requests
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from PIL import Image
import re
from .google_config import get_google_credentials_path, validate_google_credentials


class GoogleDriveImageHandler:
    """Handles Google Drive authentication and image operations"""
    
    def __init__(self):
        """
        Initialize with service account credentials
        """
        self.service_account_path = get_google_credentials_path()
        self.service = None
        if self.service_account_path and validate_google_credentials():
            self._authenticate()
        else:
            st.error("❌ No se pudieron validar las credenciales de Google Drive")
    
    def _authenticate(self):
        """Authenticate using service account credentials"""
        try:
            # Define the scopes needed for Google Drive access
            SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
            
            # Load credentials from service account file
            credentials = service_account.Credentials.from_service_account_file(
                self.service_account_path, 
                scopes=SCOPES
            )
            
            # Build the Drive service
            self.service = build('drive', 'v3', credentials=credentials)
            
            st.success("✅ Autenticación con Google Drive exitosa")
            
        except Exception as e:
            st.error(f"❌ Error en autenticación con Google Drive: {str(e)}")
            self.service = None
    
    def extract_file_id_from_url(self, url):
        """
        Extract file ID from various Google Drive URL formats
        
        Args:
            url (str): Google Drive URL
            
        Returns:
            str: File ID or None if not found
        """
        if not url or not isinstance(url, str):
            return None
            
        # Common patterns for Google Drive URLs
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
    
    def download_image_as_base64(self, file_id):
        """
        Download an image from Google Drive and convert to base64
        
        Args:
            file_id (str): Google Drive file ID
            
        Returns:
            str: Base64 encoded image with data URI prefix, or None if error
        """
        if not self.service:
            st.error("❌ Servicio de Google Drive no disponible")
            return None
            
        try:
            # Get file metadata to check if it's an image
            file_metadata = self.service.files().get(fileId=file_id).execute()
            mime_type = file_metadata.get('mimeType', '')
            
            if not mime_type.startswith('image/'):
                st.warning(f"⚠️ El archivo no es una imagen: {mime_type}")
                return None
            
            # Download the file content
            request = self.service.files().get_media(fileId=file_id)
            file_content = io.BytesIO()
            
            # Download in chunks
            downloader = request
            done = False
            while done is False:
                status, done = downloader.next_chunk()
                if status:
                    file_content.write(status)
            
            # Convert to base64
            file_content.seek(0)
            image_bytes = file_content.getvalue()
            
            # Encode to base64
            image_base64 = base64.b64encode(image_bytes).decode('utf-8')
            
            # Determine image format for data URI
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
            
            return f"data:image/{format_type};base64,{image_base64}"
            
        except HttpError as e:
            if e.resp.status == 404:
                st.error("❌ Imagen no encontrada en Google Drive")
            elif e.resp.status == 403:
                st.error("❌ Sin permisos para acceder a la imagen")
            else:
                st.error(f"❌ Error HTTP al descargar imagen: {e}")
            return None
            
        except Exception as e:
            st.error(f"❌ Error inesperado al descargar imagen: {str(e)}")
            return None
    
    def download_image_from_url(self, url):
        """
        Download an image from a Google Drive URL
        
        Args:
            url (str): Google Drive URL
            
        Returns:
            str: Base64 encoded image with data URI prefix, or None if error
        """
        if not url or not isinstance(url, str):
            st.warning(f"⚠️ URL inválida o vacía: {url}")
            return None
            
        file_id = self.extract_file_id_from_url(url)
        if not file_id:
            st.warning(f"⚠️ No se pudo extraer el ID del archivo de la URL: {url}")
            return None
        
        return self.download_image_as_base64(file_id)
    
    def test_connection(self):
        """Test the Google Drive connection"""
        if not self.service:
            return False
            
        try:
            # Try to list files (limited to 1 for testing)
            results = self.service.files().list(pageSize=1).execute()
            return True
        except Exception as e:
            st.error(f"❌ Error al probar conexión: {str(e)}")
            return False


@st.cache_resource
def get_google_drive_handler():
    """Get cached Google Drive handler instance"""
    return GoogleDriveImageHandler()


@st.cache_data(show_spinner="Descargando imagen...", ttl=3600)
def download_google_drive_image_cached(url):
    """
    Cached version of image download from Google Drive
    
    Args:
        url (str): Google Drive URL
        
    Returns:
        str: Base64 encoded image or None
    """
    handler = get_google_drive_handler()
    return handler.download_image_from_url(url)
