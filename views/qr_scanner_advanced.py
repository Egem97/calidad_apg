"""
QR Scanner Advanced View
Versión avanzada con acceso real a la cámara usando streamlit-webrtc
"""

import streamlit as st
import cv2
import numpy as np
from pyzbar import pyzbar
import time
from PIL import Image
import io
import base64
import json

# Intentar importar streamlit-webrtc (opcional)
try:
    from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration
    WEBRTC_AVAILABLE = True
except ImportError:
    WEBRTC_AVAILABLE = False
    st.warning("⚠️ Para acceso completo a la cámara, instala: `pip install streamlit-webrtc`")

def show_advanced_qr_scanner():
    """Vista avanzada del escáner de QR con cámara real"""
    
    st.title("📱 Escáner de Códigos QR - Avanzado")
    st.markdown("---")
    
    # Configuración de la página
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🔍 Escáner de Código QR")
        
        # Opciones de escaneo
        scan_mode = st.radio(
            "Modo de escaneo:",
            ["📹 Cámara en vivo", "📷 Subir imagen", "🎯 Entrada manual"],
            horizontal=True
        )
        
        if scan_mode == "📹 Cámara en vivo":
            show_advanced_live_scanner()
        elif scan_mode == "📷 Subir imagen":
            show_upload_scanner()
        else:
            show_manual_input()
    
    with col2:
        st.subheader("📋 Resultados")
        show_results_panel()

def show_advanced_live_scanner():
    """Mostrar escáner en vivo con cámara real"""
    
    if not WEBRTC_AVAILABLE:
        st.error("❌ streamlit-webrtc no está disponible")
        st.info("💡 Instala con: `pip install streamlit-webrtc`")
        return
    
    st.subheader("📹 Cámara en vivo")
    
    # Configuración de WebRTC
    rtc_configuration = RTCConfiguration({
        "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]
    })
    
    # Función para procesar frames de video
    def video_frame_callback(frame):
        img = frame.to_ndarray(format="bgr24")
        
        # Detectar códigos QR
        barcodes = pyzbar.decode(img)
        
        # Dibujar rectángulos alrededor de los códigos QR detectados
        for barcode in barcodes:
            points = barcode.polygon
            if len(points) > 4:
                hull = cv2.convexHull(np.array([point for point in points], dtype=np.float32))
                points = hull
            
            n = len(points)
            for j in range(n):
                cv2.line(img, tuple(points[j]), tuple(points[(j + 1) % n]), (0, 255, 0), 3)
            
            # Extraer datos del QR
            barcode_data = barcode.data.decode("utf-8")
            barcode_type = barcode.type
            
            # Mostrar datos en el frame
            cv2.putText(img, barcode_data, (barcode.rect.left, barcode.rect.top - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            # Guardar resultado en session state
            st.session_state.qr_result = barcode_data
            st.session_state.qr_type = barcode_type
        
        return frame
    
    # Streamer de WebRTC
    webrtc_ctx = webrtc_streamer(
        key="qr-scanner",
        mode=WebRtcMode.SENDONLY,
        rtc_configuration=rtc_configuration,
        video_frame_callback=video_frame_callback,
        media_stream_constraints={"video": True, "audio": False},
        async_processing=True,
    )
    
    # Controles adicionales
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Reiniciar Escáner"):
            st.session_state.qr_result = None
            st.rerun()
    
    with col2:
        if st.button("📸 Capturar QR"):
            if 'qr_result' in st.session_state and st.session_state.qr_result:
                st.success(f"✅ QR capturado: {st.session_state.qr_result}")
            else:
                st.warning("⚠️ No se detectó ningún QR")

def show_upload_scanner():
    """Mostrar escáner para subir imágenes"""
    
    st.subheader("📷 Subir imagen con código QR")
    
    uploaded_file = st.file_uploader(
        "Selecciona una imagen que contenga un código QR:",
        type=['png', 'jpg', 'jpeg', 'bmp', 'tiff'],
        help="Formatos soportados: PNG, JPG, JPEG, BMP, TIFF"
    )
    
    if uploaded_file is not None:
        # Mostrar imagen subida
        image = Image.open(uploaded_file)
        st.image(image, caption="Imagen subida", use_column_width=True)
        
        # Procesar imagen para detectar QR
        if st.button("🔍 Escanear QR"):
            with st.spinner("Procesando imagen..."):
                qr_data = scan_qr_from_image(image)
                
                if qr_data:
                    st.session_state.qr_result = qr_data
                    st.success(f"✅ QR detectado: {qr_data}")
                else:
                    st.error("❌ No se detectó ningún código QR en la imagen")

def show_manual_input():
    """Mostrar entrada manual de datos QR"""
    
    st.subheader("🎯 Entrada manual de datos")
    
    # Campo para entrada manual
    manual_qr_data = st.text_area(
        "Ingresa los datos del código QR:",
        placeholder="Ejemplo: FCL:EXC082|Productor:EXCELLENCE FRUIT S.A.C|Variedad:SEKOYA POP",
        height=100
    )
    
    if st.button("📝 Procesar datos"):
        if manual_qr_data.strip():
            st.session_state.qr_result = manual_qr_data.strip()
            st.success("✅ Datos procesados correctamente")
        else:
            st.error("❌ Por favor ingresa datos válidos")

def scan_qr_from_image(image):
    """Escanear código QR desde una imagen PIL"""
    try:
        # Convertir PIL Image a OpenCV format
        opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Detectar códigos QR
        barcodes = pyzbar.decode(opencv_image)
        
        if barcodes:
            # Retornar el primer código QR encontrado
            return barcodes[0].data.decode('utf-8')
        else:
            return None
            
    except Exception as e:
        st.error(f"Error al procesar imagen: {str(e)}")
        return None

def show_results_panel():
    """Mostrar panel de resultados y campos de texto"""
    
    # Mostrar resultado del escaneo
    if 'qr_result' in st.session_state and st.session_state.qr_result:
        st.success("✅ Código QR detectado")
        
        # Mostrar datos del QR
        qr_data = st.session_state.qr_result
        st.text_area("📄 Datos del QR:", qr_data, height=100)
        
        # Parsear datos del QR
        parsed_data = parse_qr_data(qr_data)
        
        if parsed_data:
            st.subheader("📋 Campos automáticos:")
            
            # Campos comunes para FCL
            fcl_fields = {
                'FCL': '',
                'Productor': '',
                'Variedad': '',
                'Presentación': '',
                'Destino': '',
                'Brix': '',
                'Acidez': ''
            }
            
            # Llenar campos con datos del QR
            for field, value in parsed_data.items():
                if field in fcl_fields:
                    fcl_fields[field] = value
            
            # Mostrar campos de texto
            col1, col2 = st.columns(2)
            
            with col1:
                fcl_fields['FCL'] = st.text_input("N° FCL:", fcl_fields['FCL'])
                fcl_fields['Productor'] = st.text_input("Productor:", fcl_fields['Productor'])
                fcl_fields['Presentación'] = st.text_input("Presentación:", fcl_fields['Presentación'])
                fcl_fields['Brix'] = st.text_input("Brix:", fcl_fields['Brix'])
            
            with col2:
                fcl_fields['Variedad'] = st.text_input("Variedad:", fcl_fields['Variedad'])
                fcl_fields['Destino'] = st.text_input("Destino:", fcl_fields['Destino'])
                fcl_fields['Acidez'] = st.text_input("Acidez:", fcl_fields['Acidez'])
            
            # Botón para guardar datos
            if st.button("💾 Guardar Datos"):
                st.success("✅ Datos guardados correctamente")
                # Aquí puedes agregar lógica para guardar en base de datos
                
            # Botón para limpiar
            if st.button("🗑️ Limpiar"):
                st.session_state.qr_result = None
                st.rerun()
        
        else:
            st.warning("⚠️ Formato de QR no reconocido")
            st.text_area("📝 Datos manuales:", qr_data, height=100)
    
    else:
        st.info("📱 Escanea un código QR para ver los resultados aquí")

def parse_qr_data(qr_data):
    """Parsear datos del QR en formato diccionario"""
    try:
        # Intentar diferentes formatos de parsing
        parsed = {}
        
        # Formato: FCL:EXC082|Productor:EXCELLENCE FRUIT S.A.C|...
        if '|' in qr_data:
            pairs = qr_data.split('|')
            for pair in pairs:
                if ':' in pair:
                    key, value = pair.split(':', 1)
                    parsed[key.strip()] = value.strip()
        
        # Formato: FCL=EXC082&Productor=EXCELLENCE FRUIT S.A.C&...
        elif '&' in qr_data:
            pairs = qr_data.split('&')
            for pair in pairs:
                if '=' in pair:
                    key, value = pair.split('=', 1)
                    parsed[key.strip()] = value.strip()
        
        # Formato JSON
        elif qr_data.startswith('{') and qr_data.endswith('}'):
            parsed = json.loads(qr_data)
        
        # Formato simple: solo FCL
        elif qr_data.startswith('FCL:'):
            parsed['FCL'] = qr_data.replace('FCL:', '').strip()
        
        return parsed
        
    except Exception as e:
        st.error(f"Error al parsear datos del QR: {str(e)}")
        return None

def generate_qr_code(data, filename="qr_code.png"):
    """Generar código QR (función auxiliar)"""
    try:
        import qrcode
        
        # Crear código QR
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        # Crear imagen
        qr_image = qr.make_image(fill_color="black", back_color="white")
        
        # Guardar imagen
        qr_image.save(filename)
        
        return filename
        
    except Exception as e:
        st.error(f"Error al generar QR: {str(e)}")
        return None

# Función para mostrar la vista completa
def show_advanced_qr_scanner_view():
    """Vista completa del escáner QR avanzado"""
    show_advanced_qr_scanner()
