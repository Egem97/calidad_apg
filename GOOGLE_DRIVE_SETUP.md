# Configuración de Google Drive para Imágenes

## Resumen
Este documento explica cómo configurar la autenticación con Google Drive para mostrar imágenes en la aplicación de Control de Calidad.

## Archivos Modificados

### 1. Nuevos Archivos Creados
- `utils/google_drive_auth.py` - Manejo de autenticación y descarga de imágenes
- `utils/google_config.py` - Configuración y validación de credenciales
- `test_google_drive.py` - Script de prueba para verificar la conexión

### 2. Archivos Modificados
- `requirements.txt` - Agregada dependencia `google-api-python-client==2.149.0`
- `views/finished_product.py` - Actualizada función `show_fcl_detail_view` para usar Google Drive API

## Instalación de Dependencias

```bash
pip install -r requirements.txt
```

## Configuración

### 1. Credenciales de Service Account
El archivo `nifty-might-269005-cd303aaaa33f.json` debe estar en la raíz del proyecto con las siguientes características:
- Tipo: `service_account`
- Permisos: `https://www.googleapis.com/auth/drive.readonly`

### 2. Permisos de Google Drive
Asegúrate de que la cuenta de servicio tenga acceso a las carpetas de Google Drive que contienen las imágenes.

## Uso

### 1. Visualización de Imágenes
Cuando accedas a la vista detallada de un FCL:
1. La aplicación verificará automáticamente la conexión con Google Drive
2. Descargará las imágenes usando la API de Google Drive
3. Mostrará un progress bar durante la descarga
4. Displayará las imágenes en un grid de 3 columnas

### 2. Generación de PDF
Las imágenes descargadas también se incluirán automáticamente en los reportes PDF.

## Solución de Problemas

### Error: "No se pudo conectar con Google Drive"
- Verifica que el archivo de credenciales esté presente
- Confirma que la cuenta de servicio tenga los permisos correctos
- Revisa que las URLs de las imágenes sean válidas

### Error: "Sin permisos para acceder a la imagen"
- La cuenta de servicio debe tener acceso compartido a las carpetas de Google Drive
- Verifica que los archivos no estén en modo privado

### Error: "Imagen no encontrada"
- Verifica que las URLs en la base de datos sean correctas
- Confirma que los archivos no hayan sido eliminados o movidos

## Testing

Para probar la conexión, ejecuta:

```bash
streamlit run test_google_drive.py
```

Este script verificará:
1. Validación de credenciales
2. Conexión con Google Drive
3. Descarga de una imagen de prueba

## Funcionalidades Implementadas

### ✅ Completadas
1. ✅ Autenticación con Google Service Account
2. ✅ Descarga de imágenes desde Google Drive
3. ✅ Cache de imágenes para optimizar rendimiento
4. ✅ Visualización en grid responsive (3 columnas)
5. ✅ Progress bar durante descarga
6. ✅ Inclusión de imágenes en PDFs
7. ✅ Manejo de errores y validaciones

### 🔄 Funcionalidades Adicionales Posibles
- Redimensionamiento automático de imágenes
- Soporte para más formatos de imagen
- Descarga en lotes optimizada
- Previsualización de miniaturas

## Estructura de URLs Soportadas

La aplicación puede extraer file IDs de estos formatos de URL:
- `https://drive.google.com/file/d/FILE_ID/view`
- `https://drive.google.com/open?id=FILE_ID`
- `https://drive.google.com/uc?id=FILE_ID`
- URLs con parámetros adicionales

## Notas de Seguridad

- Las credenciales de service account están en el archivo JSON
- Se recomienda usar variables de entorno en producción
- El cache de imágenes tiene TTL de 1 hora para optimizar rendimiento
- Las imágenes se descargan bajo demanda, no se almacenan permanentemente
