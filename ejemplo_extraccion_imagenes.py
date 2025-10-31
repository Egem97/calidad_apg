"""
Ejemplo de uso para extraer imágenes de Excel por fila
"""
import pandas as pd
import openpyxl
from pathlib import Path
import os

try:
    from openpyxl_image_loader import SheetImageLoader
    OPENPYXL_IMAGE_LOADER_AVAILABLE = True
except ImportError:
    OPENPYXL_IMAGE_LOADER_AVAILABLE = False
    print("Para extraer imágenes embebidas en celdas, instala: pip install openpyxl-image-loader")

def ejemplo_extraccion_basica():
    """Ejemplo básico de extracción de imágenes"""
    
    excel_file = "Resultados de CONTRAMUESTRAS - SAN LUCAR 2025.xlsx"
    sheet_name = "FOTOS"
    
    if not os.path.exists(excel_file):
        print(f"Archivo {excel_file} no encontrado")
        return
    
    # Crear carpeta de salida
    output_folder = Path("imagenes_extraidas")
    output_folder.mkdir(exist_ok=True)
    
    try:
        # Cargar workbook
        wb = openpyxl.load_workbook(excel_file)
        sheet = wb[sheet_name]
        
        # Cargar DataFrame
        df = pd.read_excel(excel_file, sheet_name=sheet_name, skiprows=2)
        print(f"DataFrame cargado con {len(df)} filas y {len(df.columns)} columnas")
        print("Columnas disponibles:", df.columns.tolist())
        
        # Método 1: Extraer imágenes como shapes/objetos
        print("\n=== Extrayendo imágenes como shapes/objetos ===")
        if hasattr(sheet, '_images') and sheet._images:
            for idx, img in enumerate(sheet._images):
                try:
                    image_filename = f"shape_imagen_{idx + 1}.png"
                    image_path = output_folder / image_filename
                    
                    with open(image_path, 'wb') as f:
                        f.write(img._data())
                    
                    print(f"✅ Extraída: {image_filename}")
                except Exception as e:
                    print(f"❌ Error extrayendo shape {idx}: {e}")
        else:
            print("No se encontraron imágenes como shapes/objetos")
        
        # Método 2: Extraer imágenes embebidas en celdas
        if OPENPYXL_IMAGE_LOADER_AVAILABLE:
            print("\n=== Extrayendo imágenes embebidas en celdas ===")
            image_loader = SheetImageLoader(sheet)
            
            # Buscar en un rango específico (por ejemplo, primeras 10 filas y 10 columnas)
            for row in range(1, 11):  # Filas 1-10
                for col in range(1, 11):  # Columnas A-J
                    cell_address = f"{openpyxl.utils.get_column_letter(col)}{row}"
                    
                    if image_loader.image_in(cell_address):
                        try:
                            image = image_loader.get(cell_address)
                            image_filename = f"celda_{cell_address}.jpg"
                            image_path = output_folder / image_filename
                            
                            image.save(str(image_path), 'JPEG')
                            print(f"✅ Extraída de celda {cell_address}: {image_filename}")
                        except Exception as e:
                            print(f"❌ Error extrayendo de {cell_address}: {e}")
        
        print(f"\n🎉 Proceso completado. Revisa la carpeta: {output_folder}")
        
    except Exception as e:
        print(f"❌ Error procesando archivo: {e}")

def ejemplo_extraccion_por_fila():
    """Ejemplo de extracción asociando imágenes con filas específicas"""
    
    excel_file = "Resultados de CONTRAMUESTRAS - SAN LUCAR 2025.xlsx"
    sheet_name = "FOTOS"
    
    if not os.path.exists(excel_file):
        print(f"Archivo {excel_file} no encontrado")
        return
    
    try:
        # Cargar DataFrame
        df = pd.read_excel(excel_file, sheet_name=sheet_name, skiprows=2)
        
        if df.empty:
            print("El DataFrame está vacío")
            return
        
        print("Ejemplo de datos por fila:")
        print("=" * 50)
        
        for index, row in df.head(3).iterrows():  # Mostrar solo las primeras 3 filas
            print(f"\nFila {index + 3}:")  # +3 por skiprows=2 y header
            for col_name, value in row.items():
                if pd.notna(value):
                    print(f"  {col_name}: {value}")
            
            # Aquí es donde buscarías imágenes asociadas a esta fila
            # usando las funciones de extracción que implementamos
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🖼️ Ejemplo de extracción de imágenes de Excel")
    print("=" * 50)
    
    # Ejecutar ejemplos
    ejemplo_extraccion_basica()
    print("\n" + "=" * 50)
    ejemplo_extraccion_por_fila()