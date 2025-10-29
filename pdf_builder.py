import os
import qrcode
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.graphics.shapes import Drawing, Circle, String
from styles_manager import StylesManager
from PIL import Image as PILImage

class PDFBuilder:
    def __init__(self, content_width):
        self.content_width = content_width
        self.styles_manager = StylesManager()  # Una sola instancia
    
    def generate_qr_code(self, data, filename="answer_key.png"):
        """Genera un código QR simple y legible"""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=3,
            border=1,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(filename)
        return filename
    
    def convert_image_to_bw(self, image_path):
        """Convierte una imagen a escala de grises manejando el canal alpha"""
        try:
            # Abrir la imagen
            img = PILImage.open(image_path)
            
            # Manejar el canal alpha si existe
            if img.mode in ('RGBA', 'LA'):
                # Crear un fondo blanco para compositar la transparencia
                background = PILImage.new('RGB', img.size, (255, 255, 255))
                # Compositar la imagen con transparencia sobre fondo blanco
                if img.mode == 'RGBA':
                    background.paste(img, mask=img.split()[-1])  # Usar canal alpha como máscara
                else:  # LA mode
                    background.paste(img, mask=img.split()[-1])
                img = background
            
            # Convertir a escala de grises (modo 'L' es 8-bit por pixel, escala de grises)
            img_gray = img.convert('L')
            
            # Crear nombre de archivo para la versión en escala de grises
            name, ext = os.path.splitext(image_path)
            gray_path = f"{name}_gray{ext}"
            
            # Guardar la imagen en escala de grises
            img_gray.save(gray_path)
            
            return gray_path
            
        except Exception as e:
            print(f"Error convirtiendo imagen a escala de grises: {e}")
            # Si hay error, devolver la imagen original
            return image_path
    
    def create_circle_drawing(self, size=0.5*cm, letter=None, filled=False):
        """Crea un dibujo con un círculo perfecto y opcionalmente una letra dentro"""
        d = Drawing(size, size)
        # Círculo con buen padding - usar la mayor parte del espacio disponible
        circle = Circle(size/2, size/2, size/2 - 2)
        
        if filled:
            # Círculo relleno para respuestas correctas
            circle.fillColor = colors.black
            circle.strokeColor = colors.black
        else:
            # Círculo vacío para opciones normales
            circle.fillColor = None
            circle.strokeColor = colors.black
            
        circle.strokeWidth = 1
        d.add(circle)
        
        # Agregar letra dentro del círculo si se proporciona
        if letter:
            # Centrar perfectamente la letra tanto horizontal como verticalmente
            text = String(size/2, size/2 - 2.5, letter)  # Ajustar para centrado perfecto
            text.fontName = 'Helvetica-Bold'
            text.fontSize = 8  # Tamaño apropiado para el círculo
            
            if filled:
                # Letra blanca en círculo negro
                text.fillColor = colors.white
            else:
                # Letra gris claro en círculo vacío
                text.fillColor = colors.Color(0.8, 0.8, 0.8)  # Gris medio
                
            text.textAnchor = 'middle'
            d.add(text)
            
        return d
    
    def create_header(self, test_config, styles, qr_path=None):
        """Header mejorado con logo, QR y cuadro de calificación"""
        header_elements = []
        
        # Tamaño estándar para logo y QR
        logo_qr_size = 0.6*2.54*cm  # Mismo tamaño para ambos
        
        # Logo (izquierda) - convertido a escala de grises
        logo_cell = ""
        if os.path.exists(test_config.logo_path):
            # Convertir logo a escala de grises
            logo_bw_path = self.convert_image_to_bw(test_config.logo_path)
            logo = Image(logo_bw_path, width=logo_qr_size, height=logo_qr_size)
            logo_cell = logo
        
        # QR Code (derecha del logo)
        qr_cell = ""
        if qr_path and os.path.exists(qr_path):
            qr_code = Image(qr_path, width=logo_qr_size, height=logo_qr_size)
            qr_cell = qr_code
        
        # Contenido central (vacío para el encabezado)
        center_cell = ""
        
        # Cuadro de calificación (derecha)
        grade_box_size = 0.8 * 2.54 * cm  # 0.8 pulgadas a cm
        
        grade_data = [
            [""],  # Espacio vacío para escribir la calificación
            [""],
            [""],
            ["Calificación"]  # Texto en la parte inferior
        ]
        
        grade_table = Table(grade_data, 
                           colWidths=[grade_box_size], 
                           rowHeights=[grade_box_size*0.6, grade_box_size*0.1, grade_box_size*0.1, grade_box_size*0.2])
        
        grade_table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 1, colors.black),  # Borde del cuadro
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (0, 2), 'MIDDLE'),  # Centrar el espacio para la calificación
            ('VALIGN', (0, 3), (0, 3), 'BOTTOM'),   # Texto "Calificación" en la parte inferior
            ('FONTSIZE', (0, 3), (0, 3), 8),
            ('FONTNAME', (0, 3), (0, 3), 'Helvetica'),
            ('LEFTPADDING', (0, 0), (-1, -1), 2),
            ('RIGHTPADDING', (0, 0), (-1, -1), 2),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ]))
        
        # Tabla principal para posicionar logo, QR, contenido y cuadro
        # Calcular anchos: logo + pequeño espacio + QR + espacio + contenido + cuadro
        logo_width = logo_qr_size + 0.1*cm
        qr_width = logo_qr_size + 0.2*cm if qr_cell else 0
        remaining_width = self.content_width - logo_width - qr_width - grade_box_size
        
        main_header_data = [[logo_cell, qr_cell, center_cell, grade_table]]
        main_header_table = Table(main_header_data, 
                                 colWidths=[logo_width, 
                                           qr_width,
                                           remaining_width, 
                                           grade_box_size])
        
        main_header_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),    # Logo a la izquierda
            ('ALIGN', (1, 0), (1, 0), 'LEFT'),    # QR pegado al logo
            ('ALIGN', (2, 0), (2, 0), 'CENTER'),  # Contenido centrado
            ('ALIGN', (3, 0), (3, 0), 'RIGHT'),   # Cuadro a la derecha
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ]))
        
        header_elements.append(main_header_table)
        header_elements.append(Spacer(1, -grade_box_size + 0.2*cm))  # Compensar el espacio
        
        # Nombre del instituto - más prominente con soporte Unicode
        institute_para = self.styles_manager.create_paragraph_with_unicode_support(
            f"<b>{test_config.institute_name}</b>", 
            ParagraphStyle(
                'InstituteHeader',
                fontSize=12,
                alignment=TA_CENTER,
                spaceAfter=5,
                fontName=self.styles_manager.font_name_bold,
                encoding='utf-8'
            )
        )
        
        # Curso en línea separada con soporte Unicode
        course_para = self.styles_manager.create_paragraph_with_unicode_support(
            test_config.course, 
            ParagraphStyle(
                'CourseHeader',
                fontSize=10,
                alignment=TA_CENTER,
                spaceAfter=8,
                fontName=self.styles_manager.font_name,
                encoding='utf-8'
            )
        )
        
        # Información reorganizada en tabla 3x3 para incluir el valor
        info_data = [
            [test_config.class_name, test_config.professor_name, "Fecha: ________________"],  # Clase y profesor en primera línea
            [test_config.student_name, "", "#Lista: ________________"],  # Solo alumno en segunda línea
            [test_config.course_section, test_config.exam_period, test_config.test_value]  # Curso, parcial y valor en tercera línea
        ]
        
        info_table = Table(info_data, colWidths=[self.content_width/3, self.content_width/3, self.content_width/3])
        info_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        
        # Instrucciones del test con soporte Unicode
        instructions = self.styles_manager.create_paragraph_with_unicode_support(
            "<b>INSTRUCCIONES:</b> Lea cuidadosamente cada pregunta y seleccione la respuesta correcta rellenando completamente el círculo correspondiente. Use únicamente lápiz No. 2 o bolígrafo azul o negro.",
            ParagraphStyle(
                'Instructions',
                fontSize=9,
                alignment=TA_LEFT,
                spaceAfter=10,
                spaceBefore=5,
                fontName=self.styles_manager.font_name,
                encoding='utf-8'
            )
        )
        
        header_elements.extend([
            institute_para,
            course_para,
            info_table,
            instructions
        ])
        
        return header_elements
    
    def create_answer_sheet_section(self, max_questions=25, correct_answers=None):
        """Crea la sección de respuestas de rellenado al inicio del test"""
        # Título de la sección con soporte Unicode
        answer_title = self.styles_manager.create_paragraph_with_unicode_support(
            "<b>HOJA DE RESPUESTAS</b>", 
            ParagraphStyle(
                'AnswerTitle',
                fontSize=11,
                alignment=TA_CENTER,
                spaceAfter=8,
                fontName=self.styles_manager.font_name_bold,
                encoding='utf-8'
            )
        )
        
        # Crear tabla de respuestas en formato compacto
        # 5 filas x 5 columnas = 25 preguntas máximo
        answer_data = []
        
        for row in range(5):
            row_data = []
            for col in range(5):
                question_num = row * 5 + col + 1
                if question_num <= max_questions:
                    # Crear mini tabla para cada pregunta con círculos A, B, C, D
                    circles_row = []
                    circles_row.append(self.styles_manager.create_paragraph_with_unicode_support(
                        f"<b>{question_num}.</b>", 
                        ParagraphStyle(
                            'QuestionNum',
                            fontSize=9,
                            fontName=self.styles_manager.font_name_bold,
                            alignment=TA_CENTER,
                            encoding='utf-8'
                        )
                    ))
                    
                    for i, letter in enumerate(['A', 'B', 'C', 'D']):
                        # Marcar el círculo si es la respuesta correcta y se proporcionaron las respuestas
                        is_correct = (correct_answers is not None and 
                                    question_num <= len(correct_answers) and 
                                    i == correct_answers[question_num - 1])
                        
                        circles_row.append(self.create_circle_drawing(size=0.5*cm, letter=letter, filled=is_correct))
                    
                    mini_table = Table([circles_row], colWidths=[0.6*cm, 0.5*cm, 0.5*cm, 0.5*cm, 0.5*cm])
                    mini_table.setStyle(TableStyle([
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                        ('LEFTPADDING', (0, 0), (-1, -1), 1),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 1),
                        ('TOPPADDING', (0, 0), (-1, -1), 2),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                    ]))
                    row_data.append(mini_table)
                else:
                    row_data.append("")  # Celda vacía
            answer_data.append(row_data)
        
        # Crear tabla principal de respuestas
        answer_table = Table(answer_data, colWidths=[self.content_width/5]*5)
        answer_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.gray),
            ('LEFTPADDING', (0, 0), (-1, -1), 3),
            ('RIGHTPADDING', (0, 0), (-1, -1), 3),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        
        return [answer_title, answer_table, Spacer(1, 0.5*cm)]
    
    def create_two_column_questions(self, questions, styles, start_question=1):
        """Crea preguntas organizadas en dos columnas"""
        if not questions:
            return []
        
        elements = []
        
        # Dividir preguntas en pares para las dos columnas
        for i in range(0, len(questions), 2):
            left_question = questions[i] if i < len(questions) else None
            right_question = questions[i + 1] if i + 1 < len(questions) else None
            
            # Crear columna izquierda
            left_content = ""
            if left_question:
                left_content = self.create_compact_question(left_question, start_question + i, styles)
            
            # Crear columna derecha
            right_content = ""
            if right_question:
                right_content = self.create_compact_question(right_question, start_question + i + 1, styles)
            
            # Crear tabla de dos columnas
            two_col_data = [[left_content, right_content]]
            two_col_table = Table(two_col_data, colWidths=[self.content_width/2, self.content_width/2])
            two_col_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (0, 0), 0),
                ('RIGHTPADDING', (0, 0), (0, 0), 5),
                ('LEFTPADDING', (1, 0), (1, 0), 5),
                ('RIGHTPADDING', (1, 0), (1, 0), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ]))
            
            elements.append(two_col_table)
            elements.append(Spacer(1, 0.3*cm))
        
        return elements
    
    def create_compact_question(self, question_data, question_num, styles):
        """Crea una pregunta en formato compacto para columnas"""
        # Pregunta con formato más compacto y soporte Unicode
        question_text = f"<b>{question_num}.</b> {question_data['question']}"
        question_para = self.styles_manager.create_paragraph_with_unicode_support(
            question_text, 
            ParagraphStyle(
                'CompactQuestion',
                fontSize=11,
                fontName=self.styles_manager.font_name,
                leading=13,
                spaceAfter=4,
                encoding='utf-8'
            )
        )
        
        # Opciones en formato vertical compacto
        options = question_data['options']
        while len(options) < 4:
            options.append("")
        
        option_elements = []
        for i, option in enumerate(options):
            letter = chr(65 + i)  # A, B, C, D
            
            if option:
                option_text = f"{letter}) {option}"
            else:
                option_text = f"{letter}) "
                
            option_para = self.styles_manager.create_paragraph_with_unicode_support(
                option_text,
                ParagraphStyle(
                    'CompactOption',
                    fontSize=10,
                    fontName=self.styles_manager.font_name,
                    leading=12,
                    leftIndent=0.3*cm,
                    encoding='utf-8'
                )
            )
            option_elements.append(option_para)
        
        # Crear tabla para la pregunta completa
        question_elements = [question_para] + option_elements + [Spacer(1, 0.2*cm)]
        
        question_table_data = [[elem] for elem in question_elements]
        question_table = Table(question_table_data, colWidths=[self.content_width/2 - 0.5*cm])
        question_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ]))
        
        return question_table
    
    def create_question_table(self, question_data, question_num, styles):
        """Crea una tabla para cada pregunta con opciones en una sola línea"""
        # Pregunta con soporte Unicode mejorado
        question_text = f"{question_num}. {question_data['question']}"
        question_para = self.styles_manager.create_paragraph_with_unicode_support(question_text, styles['question'])
        
        # Crear opciones en una sola fila
        options = question_data['options']
        
        # Asegurar que tenemos exactamente 4 opciones
        while len(options) < 4:
            options.append("")
        
        # Crear una sola fila con las 4 opciones
        options_row = []
        for i, option in enumerate(options):
            letter = chr(65 + i)  # A, B, C, D
            
            # Crear Paragraph para el texto de la opción con soporte Unicode
            if option:
                option_text = option
            else:
                option_text = ""
                
            option_para = self.styles_manager.create_paragraph_with_unicode_support(
                option_text, 
                ParagraphStyle(
                    'OptionText',
                    fontSize=10,
                    fontName=self.styles_manager.font_name,
                    leading=12,
                    encoding='utf-8'
                )
            )
            
            # Crear mini tabla para cada opción (círculo con letra + texto)
            option_data = [[self.create_circle_drawing(letter=letter), option_para]]
            
            option_table = Table(option_data, colWidths=[0.6*cm, None])
            option_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, 0), 'CENTER'),
                ('ALIGN', (1, 0), (1, 0), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 1),
                ('RIGHTPADDING', (0, 0), (-1, -1), 3),
                ('TOPPADDING', (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ]))
            
            options_row.append(option_table)
        
        # Crear tabla principal para las opciones en una sola fila
        options_table = Table([options_row], colWidths=[self.content_width/4]*4)
        options_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        
        # Crear tabla principal que contenga pregunta y opciones
        main_data = [
            [question_para],
            [options_table],
            [Spacer(1, 0.3*cm)]  # Espacio entre preguntas
        ]
        
        main_table = Table(main_data, colWidths=[self.content_width])
        main_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ]))
        
        return main_table
    
    def create_question_table_with_answer(self, question_data, question_num, styles):
        """Crea una tabla para cada pregunta con la respuesta correcta marcada"""
        # Pregunta con soporte Unicode
        question_text = f"{question_num}. {question_data['question']}"
        question_para = self.styles_manager.create_paragraph_with_unicode_support(question_text, styles['question'])
        
        # Crear opciones en una sola fila
        options = question_data['options']
        correct_answer_index = question_data['correct_answer']
        
        # Asegurar que tenemos exactamente 4 opciones
        while len(options) < 4:
            options.append("")
        
        # Crear una sola fila con las 4 opciones
        options_row = []
        for i, option in enumerate(options):
            letter = chr(65 + i)  # A, B, C, D
            
            # Crear Paragraph para el texto de la opción con soporte Unicode
            if option:
                option_text = option
            else:
                option_text = ""
                
            option_para = self.styles_manager.create_paragraph_with_unicode_support(
                option_text,
                ParagraphStyle(
                    'OptionText',
                    fontSize=10,
                    fontName=self.styles_manager.font_name,
                    leading=12,
                    encoding='utf-8'
                )
            )
            
            # Crear círculo marcado si es la respuesta correcta
            is_correct = (i == correct_answer_index)
            circle_drawing = self.create_circle_drawing(letter=letter, filled=is_correct)
            
            # Crear mini tabla para cada opción (círculo con letra + texto)
            option_data = [[circle_drawing, option_para]]
            
            option_table = Table(option_data, colWidths=[0.6*cm, None])
            option_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, 0), 'CENTER'),
                ('ALIGN', (1, 0), (1, 0), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 1),
                ('RIGHTPADDING', (0, 0), (-1, -1), 3),
                ('TOPPADDING', (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ]))
            
            options_row.append(option_table)
        
        # Crear tabla principal para las opciones en una sola fila
        options_table = Table([options_row], colWidths=[self.content_width/4]*4)
        options_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        
        # Crear tabla principal que contenga pregunta y opciones
        main_data = [
            [question_para],
            [options_table],
            [Spacer(1, 0.3*cm)]  # Espacio entre preguntas
        ]
        
        main_table = Table(main_data, colWidths=[self.content_width])
        main_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ]))
        
        return main_table
    
    def create_compact_question_with_answer(self, question_data, question_num, styles):
        """Crea una pregunta compacta con la respuesta correcta marcada"""
        # Pregunta con formato más compacto y soporte Unicode
        question_text = f"<b>{question_num}.</b> {question_data['question']}"
        question_para = self.styles_manager.create_paragraph_with_unicode_support(
            question_text,
            ParagraphStyle(
                'CompactQuestion',
                fontSize=11,
                fontName=self.styles_manager.font_name,
                leading=13,
                spaceAfter=4,
                encoding='utf-8'
            )
        )
        
        # Opciones en formato vertical compacto con respuesta marcada
        options = question_data['options']
        correct_answer_index = question_data['correct_answer']
        
        while len(options) < 4:
            options.append("")
        
        option_elements = []
        for i, option in enumerate(options):
            letter = chr(65 + i)  # A, B, C, D
            
            if option:
                if i == correct_answer_index:
                    option_text = f"<b>{letter}) {option} ✓</b>"  # Marcar respuesta correcta
                else:
                    option_text = f"{letter}) {option}"
            else:
                option_text = f"{letter}) "
                
            option_para = self.styles_manager.create_paragraph_with_unicode_support(
                option_text,
                ParagraphStyle(
                    'CompactOption',
                    fontSize=10,
                    fontName=self.styles_manager.font_name,
                    leading=12,
                    leftIndent=0.3*cm,
                    encoding='utf-8'
                )
            )
            option_elements.append(option_para)
        
        # Crear tabla para la pregunta completa
        question_elements = [question_para] + option_elements + [Spacer(1, 0.2*cm)]
        
        question_table_data = [[elem] for elem in question_elements]
        question_table = Table(question_table_data, colWidths=[self.content_width/2 - 0.5*cm])
        question_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ]))
        
        return question_table
    
    def create_two_column_questions_with_answers(self, questions, styles, start_question=1):
        """Crea preguntas con respuestas organizadas en dos columnas"""
        if not questions:
            return []
        
        elements = []
        
        # Dividir preguntas en pares para las dos columnas
        for i in range(0, len(questions), 2):
            left_question = questions[i] if i < len(questions) else None
            right_question = questions[i + 1] if i + 1 < len(questions) else None
            
            # Crear columna izquierda
            left_content = ""
            if left_question:
                left_content = self.create_compact_question_with_answer(left_question, start_question + i, styles)
            
            # Crear columna derecha
            right_content = ""
            if right_question:
                right_content = self.create_compact_question_with_answer(right_question, start_question + i + 1, styles)
            
            # Crear tabla de dos columnas
            two_col_data = [[left_content, right_content]]
            two_col_table = Table(two_col_data, colWidths=[self.content_width/2, self.content_width/2])
            two_col_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (0, 0), 0),
                ('RIGHTPADDING', (0, 0), (0, 0), 5),
                ('LEFTPADDING', (1, 0), (1, 0), 5),
                ('RIGHTPADDING', (1, 0), (1, 0), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ]))
            
            elements.append(two_col_table)
            elements.append(Spacer(1, 0.3*cm))
        
        return elements