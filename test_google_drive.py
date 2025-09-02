"""
Script de prueba para verificar la autenticación con Google Drive
"""

import streamlit as st
from utils.google_drive_auth import get_google_drive_handler, download_google_drive_image_cached
from utils.google_config import validate_google_credentials


def test_google_drive_connection():
    """Test the Google Drive connection and authentication"""
    
    st.title("🧪 Test de Conexión Google Drive")
    
    # Step 1: Validate credentials
    st.markdown("### 1. Validación de Credenciales")
    
    if validate_google_credentials():
        st.success("✅ Credenciales válidas encontradas")
    else:
        st.error("❌ Error en las credenciales")
        return
    
    # Step 2: Test connection
    st.markdown("### 2. Test de Conexión")
    
    try:
        handler = get_google_drive_handler()
        if handler.test_connection():
            st.success("✅ Conexión con Google Drive exitosa")
        else:
            st.error("❌ No se pudo conectar con Google Drive")
            return
    except Exception as e:
        st.error(f"❌ Error al conectar: {str(e)}")
        return
    
    # Step 3: Test image download
    st.markdown("### 3. Test de Descarga de Imagen")
    
    # You can replace this with an actual Google Drive URL from your data
    test_url = st.text_input(
        "URL de prueba de Google Drive:", 
        placeholder="https://drive.google.com/file/d/YOUR_FILE_ID/view"
    )
    
    if test_url and st.button("Probar Descarga"):
        with st.spinner("Descargando imagen de prueba..."):
            img_base64 = download_google_drive_image_cached(test_url)
            
            if img_base64:
                st.success("✅ Imagen descargada exitosamente")
                st.image(img_base64, caption="Imagen de prueba", use_column_width=True)
            else:
                st.error("❌ No se pudo descargar la imagen")
    
    # Step 4: Show handler info
    st.markdown("### 4. Información del Handler")
    
    if 'handler' in locals():
        st.write(f"**Archivo de credenciales:** {handler.service_account_path}")
        st.write(f"**Servicio disponible:** {'✅ Sí' if handler.service else '❌ No'}")


if __name__ == "__main__":
    test_google_drive_connection()
