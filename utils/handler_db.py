import psycopg2
import streamlit as st
from psycopg2.extras import RealDictCursor
import sqlalchemy
from sqlalchemy import create_engine, text
import io
import pandas as pd
from utils.config import load_config

config = load_config()
# Configuración de la base de datos PostgreSQL
DB_CONFIG = {
    'host': config['db']['host'],
    'port': config['db']['port'],
    'database': config['db']['database'],
    'user': config['db']['user'],
    'password': config['db']['password'],
    'options': '-c timezone=America/Lima'  # Configurar zona horaria de Lima
}
def create_database_connection():
    """Crear conexión a la base de datos PostgreSQL"""
    try:
        connection = psycopg2.connect(**DB_CONFIG)
        return connection
    except Exception as e:
        print(f"Error al conectar con la base de datos: {e}")
        return None


@st.cache_data(show_spinner="Cargando imagenes...", ttl=60)
def get_img_evacalidad_data(fcl = None):
    """Obtener datos de la tabla para verificación"""
    connection = create_database_connection()
    if not connection:
        return None
    
    try:
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""SELECT 
                            TRIM(folder_name) AS fcl,
                            image_base64 AS imagen
                        FROM images_fcl_drive 
                        where TRIM(folder_name) = %s
                        """, (fcl,)
        )
        data = cursor.fetchall()
        cursor.close()
        connection.close()
        
        if data:
            df = pd.DataFrame(data)
            return df
        else:
            return pd.DataFrame()
            
    except Exception as e:
        st.error(f"Error al obtener datos: {e}")
        if connection:
            connection.close()
        return None

@st.cache_data(show_spinner="Cargando imagenes...", ttl=3600)
def get_img_despacho_data(fcl = None):
    """Obtener datos de la tabla para verificación"""
    connection = create_database_connection()
    if not connection:
        return None
    
    try:
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
                    SELECT 
                        name, image_base64
                    FROM images_onedrive_despacho
                    WHERE name LIKE %s
                    
                """, (f"{fcl}",)
        )
        data = cursor.fetchall()
        cursor.close()
        connection.close()
        
        if data:
            df = pd.DataFrame(data)
            return df
        else:
            return pd.DataFrame()
            
    except Exception as e:
        st.error(f"Error al obtener datos: {e}")
        if connection:
            connection.close()
        return None