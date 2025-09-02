"""
Configuration for Google Drive authentication
"""

import os
import streamlit as st


def get_google_credentials_path():
    """
    Get the path to Google Service Account credentials
    
    Returns:
        str: Path to the credentials file
    """
    # Try to get from environment variable first (for production)
    credentials_path = os.environ.get('GOOGLE_CREDENTIALS_PATH')
    
    if credentials_path and os.path.exists(credentials_path):
        return credentials_path
    
    # Fallback to local file in project root
    local_path = "nifty-might-269005-cd303aaaa33f.json"
    if os.path.exists(local_path):
        return local_path
    
    # If neither exists, show error
    st.error("❌ No se encontraron las credenciales de Google Drive")
    st.error("Asegúrate de que el archivo 'nifty-might-269005-cd303aaaa33f.json' esté en la raíz del proyecto")
    return None


def validate_google_credentials():
    """
    Validate that Google credentials are available and properly formatted
    
    Returns:
        bool: True if credentials are valid, False otherwise
    """
    import json
    
    credentials_path = get_google_credentials_path()
    if not credentials_path:
        return False
    
    try:
        with open(credentials_path, 'r') as f:
            creds = json.load(f)
        
        # Check required fields
        required_fields = [
            'type', 'project_id', 'private_key_id', 'private_key',
            'client_email', 'client_id', 'auth_uri', 'token_uri'
        ]
        
        for field in required_fields:
            if field not in creds:
                st.error(f"❌ Campo requerido '{field}' no encontrado en las credenciales")
                return False
        
        if creds.get('type') != 'service_account':
            st.error("❌ Las credenciales deben ser de tipo 'service_account'")
            return False
        
        return True
        
    except json.JSONDecodeError:
        st.error("❌ El archivo de credenciales no es un JSON válido")
        return False
    except Exception as e:
        st.error(f"❌ Error al validar credenciales: {str(e)}")
        return False
