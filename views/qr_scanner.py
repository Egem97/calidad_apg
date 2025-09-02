"""
QR Scanner View
Permite escanear códigos QR usando la cámara web y llenar automáticamente campos
"""

import streamlit as st
import cv2
import numpy as np
from pyzbar import pyzbar
import time
from PIL import Image
import io
import base64

def show_qr_scanner():
    """Vista principal del escáner de QR"""
    
    st.title("📱 Escáner de Códigos QR")
    st.markdown("---")
    
    # Configuración de la página
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🔍 Escáner de Código QR")
        
        # Opciones de escaneo
        scan_mode = st.radio(
            "Modo de escaneo:",
            ["📹 Cámara en vivo", "📷 Subir imagen"],
            horizontal=True
        )
        
        if scan_mode == "📹 Cámara en vivo":
            show_live_scanner()
        else:
            show_upload_scanner()
    
    with col2:
        st.subheader("📋 Resultados")
        show_results_panel()

def show_live_scanner():
    """Mostrar escáner en vivo con cámara web"""
    
    # Configuración de la cámara
    camera_options = st.selectbox(
        "Seleccionar cámara:",
        ["Cámara frontal", "Cámara trasera", "Cámara por defecto"],
        index=2
    )
    
    # Botón para iniciar/detener escaneo
    if 'scanning' not in st.session_state:
        st.session_state.scanning = False
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🚀 Iniciar Escaneo" if not st.session_state.scanning else "⏹️ Detener Escaneo"):
            st.session_state.scanning = not st.session_state.scanning
    
    with col2:
        if st.button("🔄 Reiniciar"):
            st.session_state.scanning = False
            if 'qr_result' in st.session_state:
                del st.session_state.qr_result
    
    # Mostrar cámara en vivo
    if st.session_state.scanning:
        st.info("🔴 Escaneando... Coloca el código QR frente a la cámara")
        
        # Placeholder para la cámara (Streamlit no tiene cámara nativa)
        # Usaremos una alternativa con JavaScript
        camera_placeholder = st.empty()
        
        # Código JavaScript para acceder a la cámara
        js_code = """
        <script>
        async function startCamera() {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ 
                    video: { 
                        facingMode: 'environment' // Usar cámara trasera por defecto
                    } 
                });
                const video = document.createElement('video');
                video.srcObject = stream;
                video.play();
                
                // Crear canvas para capturar frames
                const canvas = document.createElement('canvas');
                const ctx = canvas.getContext('2d');
                
                // Función para procesar frames
                function processFrame() {
                    if (video.readyState === video.HAVE_ENOUGH_DATA) {
                        canvas.width = video.videoWidth;
                        canvas.height = video.videoHeight;
                        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
                        
                        // Aquí se procesaría el QR con JavaScript
                        // Por ahora solo mostramos el video
                    }
                    requestAnimationFrame(processFrame);
                }
                
                processFrame();
                
            } catch (error) {
                console.error('Error accessing camera:', error);
            }
        }
        
        startCamera();
        </script>
        """
        
        # Mostrar mensaje de instrucciones
        st.markdown("""
        ### 📱 Instrucciones para usar la cámara:
        
        **Nota:** Streamlit no tiene soporte nativo para cámara web. Para una implementación completa, 
        necesitarías usar una biblioteca como `streamlit-webrtc` o crear una aplicación web separada.
        
        **Alternativas:**
        1. **Subir imagen** - Usa la opción "Subir imagen" para escanear QR desde archivos
        2. **Aplicación móvil** - Usa una app de escaneo QR y copia el resultado
        3. **Webcam** - Usa herramientas online de escaneo QR
        """)
        
        # Botón para simular escaneo (para demostración)
        if st.button("🎯 Simular Escaneo (Demo)"):
            # Simular resultado de QR
            demo_qr_data = "FCL:EXC082|Productor:EXCELLENCE FRUIT S.A.C|Variedad:SEKOYA POP"
            st.session_state.qr_result = demo_qr_data
            st.success(f"✅ QR detectado: {demo_qr_data}")
    
    else:
        st.info("⏸️ Escáner detenido. Haz clic en 'Iniciar Escaneo' para comenzar.")

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
        
        # Parsear datos del QR (asumiendo formato FCL|Campo:Valor)
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
            import json
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
def show_qr_scanner_view():
    """Vista completa del escáner QR"""
    show_qr_scanner()
