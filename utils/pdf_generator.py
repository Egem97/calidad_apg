"""
PDF Generator for Quality Control Reports
Generates professional PDF reports matching the quality control format
"""

import io
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.pdfgen import canvas
from reportlab.graphics.shapes import Drawing, Rect
from reportlab.graphics import renderPDF
import pandas as pd
import base64


class QualityControlReportGenerator:
    """Generator for Quality Control PDF Reports"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
        
    def setup_custom_styles(self):
        """Setup custom styles for the report"""
        # Header style
        self.header_style = ParagraphStyle(
            'CustomHeader',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=20,
            textColor=colors.HexColor('#1e3a8a'),
            alignment=1  # Center
        )
        
        # Subheader style
        self.subheader_style = ParagraphStyle(
            'CustomSubHeader',
            parent=self.styles['Heading2'],
            fontSize=12,
            spaceAfter=10,
            textColor=colors.HexColor('#1e3a8a'),
            leftIndent=0
        )
        
        # Body text style
        self.body_style = ParagraphStyle(
            'CustomBody',
            parent=self.styles['Normal'],
            fontSize=9,
            spaceAfter=6,
            textColor=colors.HexColor('#444444')
        )
        
        # Small text style
        self.small_style = ParagraphStyle(
            'SmallText',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#666666')
        )

    def generate_fcl_report(self, fcl_data, detailed_records, output_path=None,images_list=None):
        """
        Generate a complete FCL Quality Control Report
        
        Args:
            fcl_data: Dictionary with FCL summary information
            detailed_records: DataFrame with detailed quality records
            output_path: Optional file path to save PDF
            
        Returns:
            BytesIO buffer with PDF content
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=20*mm,
            leftMargin=20*mm,
            topMargin=20*mm,
            bottomMargin=20*mm
        )
        
        # Build the story (content)
        story = []
        
        # Add header
        story.extend(self._create_header())
        
        # Add FCL information section
        story.extend(self._create_fcl_info_section(fcl_data))
        
        # Add sample information (based on detailed records)
        
        
        # Add quality evaluation summary
        story.extend(self._create_quality_evaluation_summary(detailed_records))
        
        # Add detailed records table
        #story.extend(self._create_detailed_records_table(detailed_records))
        
        # Add photos section with actual images
        # Las imágenes se cargarán dinámicamente desde la vista de detalle
        # Por ahora, mostrar placeholder
        story.extend(self._create_photos_section(images_list))
        
        # Build PDF
        doc.build(story)
        
        if output_path:
            with open(output_path, 'wb') as f:
                f.write(buffer.getvalue())
        
        buffer.seek(0)
        return buffer

    def _create_header(self):
        """Create the report header"""
        story = []
        
        # Company logo placeholder and title
        header_table_data = [
            ['', 'INFORME DE CONTROL DE CALIDAD', ''],
        ]
        
        header_table = Table(header_table_data, colWidths=[2*inch, 4*inch, 2*inch])
        header_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (1, 0), (1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (1, 0), (1, 0), 16),
            ('TEXTCOLOR', (1, 0), (1, 0), colors.HexColor('#1e3a8a')),
        ]))
        
        story.append(header_table)
        story.append(Spacer(1, 20))
        
        return story

    def _create_fcl_info_section(self, fcl_data):
        """Create the FCL information section"""
        story = []
        
        # FCL basic information
        info_data = [
            ['FCL:', f"{fcl_data.get('N° FCL', 'N/A')}"],#, 'Empresa:', f"{fcl_data.get('EMPRESA', 'N/A')}"
            ['Productor:',  f"{fcl_data.get('PRODUCTOR', 'N/A')}", 'Variedad:', f"{fcl_data.get('VARIEDAD', 'N/A')}"],
            ['Presentación:',  f"{fcl_data.get('PRESENTACION', 'N/A')}", 'Destino:', f"{fcl_data.get('DESTINO', 'N/A')}"],
            ['Brix:',  f"{fcl_data.get('BRIX', 'N/A')}", 'Acidez:', f"{fcl_data.get('ACIDEZ', 'N/A')}"],
        ]
        
        info_table = Table(info_data, colWidths=[1*inch, 2.8*inch, 1*inch, 2.8*inch], hAlign='LEFT')#colWidths=[0.5*inch, 2.5*inch, 0.5*inch, 2.5*inch]
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ]))
        
        story.append(info_table)
        story.append(Spacer(1, 5))
        
        return story

    

    def _create_quality_evaluation_summary(self, detailed_records):
        """Create quality evaluation summary section"""
        story = []
        
        if detailed_records.empty:
            return story
            
        # Quality evaluation header
        story.append(Paragraph("Resumen de Evaluación de Calidad", self.subheader_style))
        
        # Get aggregated data from all records
        first_record = detailed_records.iloc[0]
        
        # Quality defects summary
        quality_defects_data = [
            ['Condición', 'Porcentaje', 'Condición', 'Porcentaje'],
            ['Frutos con Pedicelo', f"{first_record.get('FRUTOS CON PEDICELO', 0):.1f}%", 'Herida Abierta', f"{first_record.get('HERIDA ABIERTA', 0):.1f}%"],
            ['Fumagina', f"{first_record.get('FUMAGINA', 0):.1f}%", 'Queresa', f"{first_record.get('QUERESA', 0):.1f}%"],
            ['F.Bloom', f"{first_record.get('F.BLOOM', 0):.1f}%", 'Deshidratación Leve', f"{first_record.get('DESHIDRATACIÓN  LEVE', 0):.1f}%"],
            ['Herida Cicatrizada', f"{first_record.get('HERIDA CICATRIZADA', 0):.1f}%", 'Deshidratación Moderada', f"{first_record.get('DESHIDRATACION MODERADO', 0):.1f}%"],
            ['Excreta de Abeja', f"{first_record.get('EXCRETA DE ABEJA', 0):.1f}%", 'Deshidratación Severa', f"{first_record.get('DESHIDRATADO SEVERO', 0):.1f}%"],
            ['Russet', f"{first_record.get('RUSSET', 0):.1f}%", 'Machucón', f"{first_record.get('MACHUCON', 0):.1f}%"],
            ['Polvo', f"{first_record.get('POLVO', 0):.1f}%", 'Desgarro', f"{first_record.get('DESGARRO', 0):.1f}%"],
            ['Frutos Rojizos', f"{first_record.get('FRUTOS ROJIZOS', 0):.1f}%", 'Sobremaduro', f"{first_record.get('SOBREMADURO', 0):.1f}%"],
            ['Restos Florales', f"{first_record.get('RESTOS FLORALES', 0):.1f}%", 'Blanda Severa', f"{first_record.get('BLANDA SEVERA', 0):.1f}%"],
            ['Halo Verde', f"{first_record.get('HALO VERDE', 0):.1f}%", 'Blanda Moderada', f"{first_record.get('BLANDA MODERADO', 0):.1f}%"],
            ['Picado', f"{first_record.get('PICADO', 0):.1f}%", 'Excreta de Ave', f"{first_record.get('EXCRETA DE AVE', 0):.1f}%"],
            ['Bajo Calibre', f"{first_record.get('BAJO CALIBRE', 0):.1f}%", 'Hongos', f"{first_record.get('HONGOS', 0):.1f}%"],
            ['Chanchito Blanco', f"{first_record.get('CHANCHITO BLANCO', 0):.1f}%", 'Pudricion', f"{first_record.get('PUDRICION', 0):.1f}%"],
            ['F. Mojado', f"{first_record.get('F. MOJADA', 0):.1f}%", 'Baya Reventada', f"{first_record.get('BAYA REVENTADA', 0):.1f}%"],
            ['Daño de Trips', f"{first_record.get('DAÑO DE TRIPS', 0):.1f}%", 'Baya Colapsada', f"{first_record.get('BAYA COLAPSADA', 0):.1f}%"],
            ['Otros', f"{first_record.get('OTROS', 0):.1f}%", 'Presencia de Larva', f"{first_record.get('PRESENCIA DE LARVA', 0):.1f}%"],
            ['', '', 'Exudation', f"{first_record.get('EXUDACION', 0):.1f}%"],
            ['', '', 'Otros 2', f"{first_record.get('OTROS2', 0):.1f}%"],
           # ['TOTAL QUALITY DEFECTS:', f"{first_record.get('TOTAL DE DEFECTOS DE CALIDAD', 0):.1f}%", 'TOTAL CONDITION:', f"{first_record.get('TOTAL DE CONDICION', 0):.1f}%"],
            #['TOTAL EXPORTABLE:', f"{first_record.get('TOTAL DE EXPORTABLE', 0)}", 'TOTAL NO EXPORTABLE:', f"{first_record.get('TOTAL DE NO EXPORTABLE', 0)}"]
        ]
        
        quality_table = Table(quality_defects_data, colWidths=[2*inch, 1*inch, 2*inch, 1*inch])
        quality_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#dbeafe')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1e3a8a')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ('ALIGN', (3, 0), (3, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('LEFTPADDING', (0, 0), (-1, -1), 3),
            ('RIGHTPADDING', (0, 0), (-1, -1), 3),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('BACKGROUND', (0, -2), (-1, -1), colors.HexColor('#f0f4ff')),
            ('FONTNAME', (0, -2), (-1, -1), 'Helvetica-Bold'),
        ]))
        
        story.append(quality_table)
        story.append(Spacer(1, 15))
        
        return story

    def _create_detailed_records_table(self, detailed_records):
        """Create detailed records table"""
        story = []
        
        if detailed_records.empty:
            return story
            
        # Table header
        story.append(Paragraph("Detailed Quality Records", self.subheader_style))
        
        # Prepare table data with quality evaluation columns
        headers = [
            'FECHA MP', 'FECHA PROCESO', 'SEMANA', 'EVALUADOR', 'PRODUCTOR', 'TIPO', 'FUNDO', 
            'PESO MUESTRA', 'FRUTOS PEDICELO', 'FUMAGINA', 'F.BLOOM', 'HERIDA CICATRIZADA',
            'EXCRETA ABEJA', 'RUSSET', 'POLVO', 'FRUTOS ROJIZOS', 'RESTOS FLORALES',
            'HALO VERDE', 'PICADO', 'BAJO CALIBRE', 'CHANCHITO BLANCO', 'F. MOJADA',
            'DAÑO TRIPS', 'OTROS', 'TOTAL DEFECTOS', 'HERIDA ABIERTA', 'QUERESA',
            'DESHIDRATACIÓN LEVE', 'DESHIDRATACIÓN MODERADA', 'DESHIDRATACIÓN SEVERA',
            'MACHUCÓN', 'DESGARRO', 'SOBREMADURO', 'BLANDA SEVERA', 'BLANDA MODERADA',
            'EXCRETA AVE', 'HONGOS', 'PUDRICIÓN', 'BAYA REVENTADA', 'BAYA COLAPSADA',
            'PRESENCIA LARVA', 'EXUDACIÓN', 'OTROS2', 'TOTAL CONDICIÓN',
            'TOTAL EXPORTABLE', 'TOTAL NO EXPORTABLE', 'N° FCL', 'CALIBRE', 'BRIX', 'ACIDEZ'
        ]
        
        table_data = [headers]
        
        for _, row in detailed_records.iterrows():
            row_data = [
                row.get('FECHA DE MP', None).strftime('%Y-%m-%d') if pd.notna(row.get('FECHA DE MP')) else '',
                row.get('FECHA DE PROCESO', None).strftime('%Y-%m-%d') if pd.notna(row.get('FECHA DE PROCESO')) else '',
                str(row.get('SEMANA', '')),
                str(row.get('EVALUADOR', '')),
                str(row.get('PRODUCTOR', '')),
                str(row.get('TIPO DE PRODUCTO', '')),
                str(row.get('FUNDO', '')),
                str(row.get('PESO DE MUESTRA (g)', '')),
                str(row.get('FRUTOS CON PEDICELO', '')),
                str(row.get('FUMAGINA', '')),
                str(row.get('F.BLOOM', '')),
                str(row.get('HERIDA CICATRIZADA', '')),
                str(row.get('EXCRETA DE ABEJA', '')),
                str(row.get('RUSSET', '')),
                str(row.get('POLVO', '')),
                str(row.get('FRUTOS ROJIZOS', '')),
                str(row.get('RESTOS FLORALES', '')),
                str(row.get('HALO VERDE', '')),
                str(row.get('PICADO', '')),
                str(row.get('BAJO CALIBRE', '')),
                str(row.get('CHANCHITO BLANCO', '')),
                str(row.get('F. MOJADA', '')),
                str(row.get('DAÑO DE TRIPS', '')),
                str(row.get('OTROS', '')),
                str(row.get('TOTAL DE DEFECTOS DE CALIDAD', '')),
                str(row.get('HERIDA ABIERTA', '')),
                str(row.get('QUERESA', '')),
                str(row.get('DESHIDRATACIÓN  LEVE', '')),
                str(row.get('DESHIDRATACION MODERADO', '')),
                str(row.get('DESHIDRATADO SEVERO', '')),
                str(row.get('MACHUCON', '')),
                str(row.get('DESGARRO', '')),
                str(row.get('SOBREMADURO', '')),
                str(row.get('BLANDA SEVERA', '')),
                str(row.get('BLANDA MODERADO', '')),
                str(row.get('EXCRETA DE AVE', '')),
                str(row.get('HONGOS', '')),
                str(row.get('PUDRICION', '')),
                str(row.get('BAYA REVENTADA', '')),
                str(row.get('BAYA COLAPSADA', '')),
                str(row.get('PRESENCIA DE LARVA', '')),
                str(row.get('EXUDACION', '')),
                str(row.get('OTROS2', '')),
                str(row.get('TOTAL DE CONDICION', '')),
                str(row.get('TOTAL DE EXPORTABLE', '')),
                str(row.get('TOTAL DE NO EXPORTABLE', '')),
                str(row.get('N° FCL', '')),
                str(row.get('CALIBRE', '')),
                str(row.get('BRIX', '')),
                str(row.get('ACIDEZ', ''))
            ]
            table_data.append(row_data)
        
        # Create table with smaller font for detailed data
        records_table = Table(table_data, repeatRows=1)
        records_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#dbeafe')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1e3a8a')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('LEFTPADDING', (0, 0), (-1, -1), 2),
            ('RIGHTPADDING', (0, 0), (-1, -1), 2),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        
        story.append(records_table)
        story.append(Spacer(1, 15))
        
        return story

    def _create_photos_section(self, images_list):
        """Create photos section with actual images"""
        story = []

        # Debug: verificar el formato de las imágenes
        print(f"DEBUG _create_photos_section: images_list type: {type(images_list)}")
        print(f"DEBUG _create_photos_section: images_list length: {len(images_list) if images_list else 0}")
        if images_list and len(images_list) > 0:
            print(f"DEBUG _create_photos_section: First image type: {type(images_list[0])}")
            print(f"DEBUG _create_photos_section: First image length: {len(images_list[0]) if isinstance(images_list[0], str) else 'N/A'}")
            print(f"DEBUG _create_photos_section: First image starts with: {images_list[0][:50] if isinstance(images_list[0], str) else 'N/A'}")
        
        images_list = images_list or []
        
        # Photos header
        story.append(Paragraph("📸 IMAGENES ", self.subheader_style))
        
        if len(images_list) > 0:
            try:
                # Organizar imágenes en filas de 3 con tamaño optimizado
                cols_per_row = 3
                # Calcular ancho disponible (A4 - márgenes) / 3 columnas
                available_width = 7.5 * inch  # A4 width - margins
                img_width = available_width / cols_per_row - 0.1 * inch  # Pequeño espacio entre imágenes
                img_height = 1.8 * inch  # Altura estándar para buena proporción
                
                for i in range(0, len(images_list), cols_per_row):
                    row_images = []
                    for j in range(cols_per_row):
                        if i + j < len(images_list):
                            try:
                                # Verificar que la imagen sea un string base64 válido
                                img_base64 = images_list[i + j]
                                print(f"DEBUG: procesando imagen {i+j+1}, tipo: {type(img_base64)}")
                                
                                if not isinstance(img_base64, str):
                                    print(f"ERROR: imagen {i+j+1} no es string, es {type(img_base64)}")
                                    placeholder = Paragraph(f"Error: formato inválido", self.small_style)
                                    row_images.append(placeholder)
                                    continue
                                
                                # Limpiar el string base64 si tiene prefijo data:image
                                if img_base64.startswith('data:image'):
                                    # Extraer solo la parte base64
                                    img_base64 = img_base64.split(',')[1]
                                
                                # Decodificar imagen base64
                                try:
                                    img_data = base64.b64decode(img_base64)
                                    img_buffer = io.BytesIO(img_data)
                                except Exception as decode_error:
                                    print(f"ERROR decodificando imagen {i+j+1}: {str(decode_error)}")
                                    placeholder = Paragraph(f"Error: base64 inválido", self.small_style)
                                    row_images.append(placeholder)
                                    continue
                                
                                # Crear imagen para PDF con tamaño optimizado
                                img = Image(img_buffer, width=img_width, height=img_height, kind='proportional')
                                row_images.append(img)
                                print(f"SUCCESS: imagen {i+j+1} procesada correctamente")
                            except Exception as e:
                                # Si hay error, crear placeholder
                                print(f"ERROR procesando imagen {i+j+1}: {str(e)}")
                                placeholder = Paragraph(f"Error imagen {i+j+1}: {str(e)[:30]}", self.small_style)
                                row_images.append(placeholder)
                        else:
                            # Espacio vacío si no hay más imágenes
                            row_images.append(Paragraph("", self.small_style))
                    
                    # Crear tabla para esta fila de imágenes
                    if len(row_images) > 0:
                        img_table = Table([row_images], colWidths=[img_width, img_width, img_width])
                        img_table.setStyle(TableStyle([
                            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                            ('LEFTPADDING', (0, 0), (-1, -1), 3),
                            ('RIGHTPADDING', (0, 0), (-1, -1), 3),
                            ('TOPPADDING', (0, 0), (-1, -1), 3),
                            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                        ]))
                        story.append(img_table)
                        story.append(Spacer(1, 8))
                
                # Agregar información sobre las imágenes
                story.append(Paragraph(f"Total de imágenes incluidas: {len(images_list)}", self.small_style))
                
            except Exception as e:
                print(f"ERROR general en _create_photos_section: {str(e)}")
                story.append(Paragraph(f"Error al procesar imágenes: {str(e)}", self.small_style))
        else:
            story.append(Paragraph("No hay imágenes disponibles para este FCL", self.small_style))
        
        return story

    def create_download_link(self, pdf_buffer, filename="quality_control_report.pdf"):
        """Create a download link for the PDF"""
        pdf_buffer.seek(0)
        b64 = base64.b64encode(pdf_buffer.read()).decode()
        href = f'<a href="data:application/pdf;base64,{b64}" download="{filename}">Download PDF Report</a>'
        return href


def generate_fcl_pdf_report(fcl_data, detailed_records, images_list):
    """
    Convenience function to generate FCL PDF report
    
    Args:
        fcl_data: Dictionary with FCL summary information
        detailed_records: DataFrame with detailed quality records
        images_list: List of base64 encoded images
        
    Returns:
        BytesIO buffer with PDF content
    """
    generator = QualityControlReportGenerator()
    return generator.generate_fcl_report(fcl_data, detailed_records, images_list=images_list)
