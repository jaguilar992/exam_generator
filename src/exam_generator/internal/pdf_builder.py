# -*- coding: utf-8 -*-
"""
PDF Builder for creating exam documents.
Consolidated version without code duplication.
"""

import os
import tempfile
from typing import List, Dict, Any, Optional
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.graphics.shapes import Drawing, Circle, String, Rect
from PIL import Image as PILImage

from .styles import StylesManager
from ..config import ExamConfig
from ..i18n import get_text_strings, get_instructions_text, get_answer_sheet_title


class PDFBuilder:
    """
    Builds PDF content for exams with consolidated, non-duplicated methods.
    """
    
    def __init__(self, content_width: float, margin: float):
        """
        Initialize PDF builder.
        
        Args:
            content_width (float): Width of content area in points
            margin (float): Page margin in points
        """
        self.content_width = content_width
        self.margin = margin
        self.styles_manager = StylesManager()
        self.styles = self.styles_manager.create_styles()
    
    def build_student_exam_story(
        self, 
        questions: List[Dict[str, Any]], 
        config: ExamConfig,
        qr_image_path: Optional[str] = None
    ) -> List[Any]:
        """
        Build the complete story for student exam PDF.
        
        Args:
            questions: List of question dictionaries
            config: Exam configuration
            qr_image_path: Path to QR code image
            
        Returns:
            List of PDF story elements
        """
        story = []
        
        # Header
        story.extend(self._create_header(config, qr_image_path))
        
        # Answer sheet section
        story.extend(self._create_answer_sheet_section(len(questions), config))
        
        # Questions section con espaciado mínimo
        story.append(Spacer(1, 0.25*cm))  # Reducido de 0.3cm a 0.1cm
        story.extend(self._create_two_column_questions(questions))
        
        return story
    
    def build_answer_key_story(
        self,
        questions: List[Dict[str, Any]],
        config: ExamConfig,
        qr_image_path: Optional[str] = None
    ) -> List[Any]:
        """
        Build the complete story for answer key PDF.
        
        Args:
            questions: List of question dictionaries
            config: Exam configuration  
            qr_image_path: Path to QR code image
            
        Returns:
            List of PDF story elements
        """
        story = []
        
        # Header
        story.extend(self._create_header(config, qr_image_path))
        
        # Answer sheet with marked answers
        correct_answers = [q['correct_answer'] for q in questions]
        story.extend(self._create_answer_sheet_section(len(questions), config, correct_answers))
        
        # Questions with marked answers
        story.append(Spacer(1, 0.3*cm))
        story.extend(self._create_two_column_questions_with_answers(questions))
        
        return story
    
    def _create_header(self, config: ExamConfig, qr_image_path: Optional[str] = None) -> List[Any]:
        """Create document header with logo, QR code, and grade box."""
        elements = []
        
        # Standard sizes
        logo_qr_size = 0.6 * 2.54 * cm
        grade_box_size = 0.8 * 2.54 * cm
        
        # Prepare header components
        logo_cell = self._create_logo_cell(config.logo_path, logo_qr_size)
        qr_cell = self._create_qr_cell(qr_image_path, logo_qr_size)
        grade_box = self._create_grade_box(grade_box_size, config)
        
        # Main header table
        header_table = self._create_header_table(logo_cell, qr_cell, grade_box, logo_qr_size, grade_box_size)
        elements.append(header_table)
        elements.append(Spacer(1, -grade_box_size + 0.25*cm))  # Reducido de 0.2cm a 0.25cm
        
        # Institution and course info
        elements.extend(self._create_institution_info(config))
        
        # Student/exam info table
        elements.append(self._create_info_table(config))
        
        # Separación entre info table e instrucciones
        elements.append(Spacer(1, 0.15*cm))
        
        # Instructions
        elements.append(self._create_instructions(config))
        
        return elements
    
    def _create_logo_cell(self, logo_path: Optional[str], size: float) -> Any:
        """Create logo cell for header."""
        if not logo_path or not os.path.exists(logo_path):
            return ""
        
        try:
            # Convert to grayscale
            gray_path = self._convert_image_to_grayscale(logo_path)
            return Image(gray_path, width=size, height=size)
        except Exception:
            return ""
    
    def _create_qr_cell(self, qr_path: Optional[str], size: float) -> Any:
        """Create QR code cell for header."""
        if not qr_path or not os.path.exists(qr_path):
            return ""
        
        try:
            return Image(qr_path, width=size, height=size)
        except Exception:
            return ""
    
    def _create_grade_box(self, size: float, config: ExamConfig) -> Table:
        """Create grade box for header."""
        # Get grade label based on config language
        grade_label = get_text_strings(config.language).get('grade_label') if hasattr(config, 'language') else "Grade"
        
        grade_data = [
            [""],  # Space for grade
            [""],
            [""],
            [grade_label]
        ]
        
        grade_table = Table(
            grade_data,
            colWidths=[size],
            rowHeights=[size*0.6, size*0.1, size*0.1, size*0.2]
        )
        
        grade_table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (0, 2), 'MIDDLE'),
            ('VALIGN', (0, 3), (0, 3), 'BOTTOM'),
            ('FONTSIZE', (0, 3), (0, 3), 8),
            ('FONTNAME', (0, 3), (0, 3), 'Helvetica'),
        ] + self._get_table_padding_style()))
        
        return grade_table
    
    def _create_header_table(self, logo_cell: Any, qr_cell: Any, grade_box: Table, logo_size: float, grade_size: float) -> Table:
        """Create main header table layout."""
        logo_width = logo_size + 0.1*cm
        qr_width = (logo_size + 0.2*cm) if qr_cell else 0
        remaining_width = self.content_width - logo_width - qr_width - grade_size
        
        header_data = [[logo_cell, qr_cell, "", grade_box]]
        header_table = Table(
            header_data,
            colWidths=[logo_width, qr_width, remaining_width, grade_size]
        )
        
        header_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'LEFT'),
            ('ALIGN', (2, 0), (2, 0), 'CENTER'),
            ('ALIGN', (3, 0), (3, 0), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ] + self._get_no_padding_style()))
        
        return header_table
    
    def _create_institution_info(self, config: ExamConfig) -> List[Any]:
        """Create institution and course information."""
        elements = []
        
        # Institute name con fuente y tamaño igual a las opciones
        compact_institute_style = ParagraphStyle(
            'CompactInstituteHeader',
            parent=self.styles['institute_header'],
            fontSize=10,  # Igual que las opciones
            fontName=self.styles_manager.font_name  # Fuente normal, no bold
        )
        institute_para = self.styles_manager.create_paragraph_with_unicode_support(
            f"<b>{config.institute_name}</b>",
            compact_institute_style
        )
        elements.append(institute_para)
        
        # Course name con fuente y tamaño igual a las opciones
        compact_course_style = ParagraphStyle(
            'CompactCourseHeader',
            parent=self.styles['course_header'],
            fontSize=10,  # Igual que las opciones
            fontName=self.styles_manager.font_name  # Fuente normal, igual que opciones
        )
        course_para = self.styles_manager.create_paragraph_with_unicode_support(
            config.course,
            compact_course_style
        )
        elements.append(course_para)
        
        return elements
    
    def _create_info_table(self, config: ExamConfig) -> Table:
        """Create student and exam information table."""
        # Get text strings based on config language
        text_strings = get_text_strings(config.language if hasattr(config, 'language') else None)
        
        info_data = [
            [config.class_name, config.professor_name, text_strings.get('date_blank')],
            [config.student_name, "", text_strings.get('list_number_blank')],
            [config.course_section, config.exam_period, config.test_value]
        ]
        
        info_table = Table(info_data, colWidths=[self.content_width/3] * 3)
        info_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),  # Aumentado de 8 a 10 para mejor legibilidad
            ('TOPPADDING', (0, 0), (-1, -1), 1), # Reducido de 3 a 1
            ('BOTTOMPADDING', (0, 0), (-1, -1), 1), # Reducido de 3 a 1
        ]))
        
        return info_table
    
    def _create_instructions(self, config: ExamConfig) -> Paragraph:
        """Create exam instructions."""
        # Get instructions text based on config language
        instructions_text = get_instructions_text(config.language if hasattr(config, 'language') else None)
        
        # Estilo compacto para las instrucciones
        compact_instructions_style = ParagraphStyle(
            'CompactInstructions',
            parent=self.styles['instructions'],
            fontSize=10,        # Aumentado de 8 a 10 para mejor legibilidad
            spaceAfter=5,       # Reducido de 10 a 5
            spaceBefore=2       # Reducido de 5 a 2
        )
        
        return self.styles_manager.create_paragraph_with_unicode_support(
            instructions_text,
            compact_instructions_style
        )
    
    def _create_answer_sheet_section(
        self, 
        max_questions: int, 
        config: ExamConfig,
        correct_answers: Optional[List[int]] = None
    ) -> List[Any]:
        """Create answer sheet section with bubble grid."""
        elements = []
        
        # Title con espacio reducido después
        title_text = get_answer_sheet_title(config.language if hasattr(config, 'language') else None)
        title_style = ParagraphStyle(
            'CompactAnswerTitle',
            parent=self.styles['answer_title'],
            spaceAfter=4  # Reducido de 8 a 4
        )
        title = self.styles_manager.create_paragraph_with_unicode_support(
            title_text,
            title_style
        )
        elements.append(title)
        
        # Create 5x5 grid of questions
        answer_data = []
        for row in range(5):
            row_data = []
            for col in range(5):
                question_num = row * 5 + col + 1
                if question_num <= max_questions:
                    # Primera fila (preguntas 1-5) tiene letras arriba de los círculos
                    is_first_row = (row == 0)
                    question_cell = self._create_question_bubble_row(
                        question_num, 
                        correct_answers[question_num - 1] if correct_answers and question_num <= len(correct_answers) else None,
                        is_first_row=is_first_row
                    )
                    row_data.append(question_cell)
                else:
                    row_data.append("")
            answer_data.append(row_data)
        
        # Answer sheet table con padding reducido
        answer_table = Table(answer_data, colWidths=[self.content_width/5] * 5)
        answer_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.grey),  # Cambiar grosor 1→0.5 y color black→grey
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.grey),  # Cambiar color gray→grey
        ] + self._get_table_padding_style(1, 1)))  # Reducido de 3 a 1
        
        # Spacer final mínimo
        elements.extend([answer_table, Spacer(1, 0.05*cm)])  # Reducido de 0.2cm a 0.05cm
        return elements
    
    def _create_question_bubble_row(self, question_num: int, correct_answer: Optional[int] = None, is_first_row: bool = False) -> Table:
        """Create a row of bubbles for one question."""
        # Question number con estilo compacto
        compact_number_style = ParagraphStyle(
            'CompactQuestionNumber',
            parent=self.styles['question_number'],
            spaceBefore=0,
            spaceAfter=0,
            leading=8  # Interlineado reducido
        )
        num_para = self.styles_manager.create_paragraph_with_unicode_support(
            f"<b>{question_num}.</b>",
            compact_number_style
        )
        
        if is_first_row:
            # Primera fila: letras arriba, círculos sin letras
            table_data = []
            
            # Fila de letras arriba
            letter_row = [""]  # Celda vacía para el número de pregunta
            for letter in ['A', 'B', 'C', 'D']:
                letter_para = self.styles_manager.create_paragraph_with_unicode_support(
                    f"<b>{letter}</b>",
                    compact_number_style
                )
                letter_row.append(letter_para)
            table_data.append(letter_row)
            
            # Fila de círculos sin letras
            bubble_row = [num_para]
            for i in range(4):  # A, B, C, D
                is_filled = (correct_answer is not None and i == correct_answer)
                bubble = self._create_circle_drawing(size=0.45*cm, letter=None, filled=is_filled)  # Círculos ligeramente más pequeños
                bubble_row.append(bubble)
            table_data.append(bubble_row)
            
            bubble_table = Table(table_data, colWidths=[0.6*cm, 0.5*cm, 0.5*cm, 0.5*cm, 0.5*cm])
            bubble_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ] + self._get_table_padding_style(0.5, 1)))  # Padding aún más reducido
        else:
            # Resto de filas: círculos sin letras también
            bubbles = [num_para]
            for i in range(4):  # A, B, C, D
                is_filled = (correct_answer is not None and i == correct_answer)
                bubble = self._create_circle_drawing(size=0.45*cm, letter=None, filled=is_filled)  # Círculos ligeramente más pequeños
                bubbles.append(bubble)
            
            bubble_table = Table([bubbles], colWidths=[0.6*cm, 0.5*cm, 0.5*cm, 0.5*cm, 0.5*cm])
            bubble_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ] + self._get_table_padding_style(0.5, 1)))  # Padding aún más reducido
        
        # Crear marcador flotante que se superpone sin afectar el layout
        position_marker = self._create_position_marker()
        
        # Crear tabla contenedora con superposición absoluta
        # El contenido mantiene su tamaño original, el marcador flota en esquina inferior derecha
        # Estructura: [content, marker]
        #             [empty,   empty ]
        marker_data = [[bubble_table, position_marker]]
        
        # Ancho total de la celda original
        total_width = self.content_width / 5
        marker_size = 0.2*cm  # 2mm exactos
        
        # El marcador no ocupa espacio horizontal real, el contenido usa todo el ancho
        wrapper_table = Table(marker_data, 
                             colWidths=[total_width, 0])  # Contenido usa todo el ancho, marcador ancho 0 (flotante)
        
        wrapper_table.setStyle(TableStyle([
            # Contenido ocupa toda la celda normalmente
            ('ALIGN', (0, 0), (0, 0), 'CENTER'),
            ('VALIGN', (0, 0), (0, 0), 'TOP'),
            # Marcador flotante en esquina inferior derecha (ancho 0 = flotante)
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('VALIGN', (1, 0), (1, 0), 'BOTTOM'),
            # Contenido con padding normal
            ('LEFTPADDING', (0, 0), (0, 0), 0),
            ('RIGHTPADDING', (0, 0), (0, 0), 0),
            ('TOPPADDING', (0, 0), (0, 0), 0),
            ('BOTTOMPADDING', (0, 0), (0, 0), 0),
            # Sin padding para posicionamiento exacto del marcador
            ('LEFTPADDING', (1, 0), (1, 0), 0),
            ('RIGHTPADDING', (1, 0), (1, 0), 0),
            ('TOPPADDING', (1, 0), (1, 0), 0),
            ('BOTTOMPADDING', (1, 0), (1, 0), 0),
        ]))
        
        return wrapper_table
    
    def _create_two_column_questions(self, questions: List[Dict[str, Any]]) -> List[Any]:
        """Create questions in two-column layout."""
        return self._create_question_columns(questions, include_answers=False)
    
    def _create_two_column_questions_with_answers(self, questions: List[Dict[str, Any]]) -> List[Any]:
        """Create questions with answers in two-column layout."""
        return self._create_question_columns(questions, include_answers=True)
    
    def _create_question_columns(self, questions: List[Dict[str, Any]], include_answers: bool = False) -> List[Any]:
        """Create questions in two-column format with 0.7cm spacing."""
        elements = []
        
        for i in range(0, len(questions), 2):
            left_question = questions[i] if i < len(questions) else None
            right_question = questions[i + 1] if i + 1 < len(questions) else None
            
            left_content = ""
            right_content = ""
            
            if left_question:
                left_content = self._create_compact_question(
                    left_question, i + 1, include_answers, is_right_column=False
                )
            
            if right_question:
                right_content = self._create_compact_question(
                    right_question, i + 2, include_answers, is_right_column=True
                )
            
            # Two-column table with exact 0.7cm horizontal spacing
            col_data = [[left_content, right_content]]
            column_width = (self.content_width - 0.7*cm) / 2
            col_table = Table(col_data, colWidths=[column_width, column_width])
            col_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (0, 0), 0),
                ('RIGHTPADDING', (0, 0), (0, 0), 0.35*cm),  # Half of 0.7cm spacing
                ('LEFTPADDING', (1, 0), (1, 0), 0.35*cm),   # Half of 0.7cm spacing
                ('RIGHTPADDING', (1, 0), (1, 0), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ]))
            
            # Add moderate vertical spacing between question rows
            elements.extend([col_table, Spacer(1, 0.3*cm)])  # Aumentado de 0.1cm a 0.2cm para mejor legibilidad
        
        return elements
    
    def _create_compact_question(
        self, 
        question_data: Dict[str, Any], 
        question_num: int, 
        include_answer: bool = False,
        is_right_column: bool = False
    ) -> Table:
        """Create a compact question for column layout with border."""
        # Question text con estilo ultra-compacto
        question_text = f"<b>{question_num}.</b> {question_data['question']}"
        ultra_compact_question_style = ParagraphStyle(
            'UltraCompactQuestion',
            parent=self.styles['compact_question'],
            fontSize=10,        # Reducido de 11 a 10
            leading=11,         # Reducido de 13 a 11
            spaceAfter=2        # Reducido de 4 a 2
        )
        question_para = self.styles_manager.create_paragraph_with_unicode_support(
            question_text,
            ultra_compact_question_style
        )
        
        # Options
        options = question_data['options']
        correct_answer_index = question_data.get('correct_answer', 0) if include_answer else None
        
        # Ensure 4 options
        while len(options) < 4:
            options.append("")
        
        option_elements = []
        for i, option in enumerate(options):
            letter = chr(65 + i)  # A, B, C, D
            
            if include_answer and correct_answer_index is not None and i == correct_answer_index:
                option_text = f"<b>{letter}) {option} ✓</b>" if option else f"<b>{letter}) ✓</b>"
            else:
                option_text = f"{letter}) {option}" if option else f"{letter}) "
            
            option_para = self.styles_manager.create_paragraph_with_unicode_support(
                option_text,
                ParagraphStyle(
                    'UltraCompactOption',
                    parent=self.styles['compact_option'],
                    leftIndent=0.3*cm,
                    spaceBefore=0,      # Eliminar espacio antes
                    spaceAfter=0,       # Eliminar espacio después
                    leading=11,         # Interlineado ajustado para tamaño 10
                    fontSize=10         # Tamaño mínimo de 10 puntos
                )
            )
            option_elements.append(option_para)
        
        # Build question table with border and padding
        question_elements = [question_para] + option_elements
        question_table_data = [[elem] for elem in question_elements]
        
        question_table = Table(question_table_data, colWidths=[(self.content_width - 0.7*cm) / 2])
        
        # Definir estilos de borde basados en la columna
        border_styles = [
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LINEABOVE', (0, 0), (-1, 0), 0.5, colors.grey),  # Borde superior siempre
            ('LEFTPADDING', (0, 0), (-1, -1), 0.15*cm),   
            ('RIGHTPADDING', (0, 0), (-1, -1), 0.15*cm),  
            ('TOPPADDING', (0, 0), (-1, -1), 0.05*cm),    
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0.02*cm), 
        ]
        
        # Agregar borde vertical según la columna
        if is_right_column:
            border_styles.append(('LINEBEFORE', (0, 0), (0, -1), 0.5, colors.grey))  # Borde izquierdo para columna derecha
        else:
            border_styles.append(('LINEAFTER', (-1, 0), (-1, -1), 0.5, colors.grey))  # Borde derecho para columna izquierda
        
        question_table.setStyle(TableStyle(border_styles))
        
        return question_table
    
    def _create_position_marker(self) -> Drawing:
        """Create a small position marker for scanning correction."""
        # Marcador de exactamente 2mm
        marker_size = 0.2*cm  # 2 milímetros
        
        # Drawing con tamaño mínimo para que no afecte el layout
        d = Drawing(marker_size, marker_size)
        
        # Create a small square marker that ocupa todo el espacio
        marker = Rect(0, 0, marker_size, marker_size)
        marker.strokeWidth = 0
        
        marker.fillColor = colors.black
        
        d.add(marker)
        return d

    def _create_circle_drawing(self, size: float = 0.5*cm, letter: Optional[str] = None, filled: bool = False) -> Drawing:
        """Create a circle drawing with optional letter and fill."""
        d = Drawing(size, size)
        
        # Circle
        circle = Circle(size/2, size/2, size/2 - 2)
        circle.strokeWidth = 1
        circle.strokeColor = colors.black
        
        if filled:
            circle.fillColor = colors.black
        else:
            circle.fillColor = None
        
        d.add(circle)
        
        # Letter
        if letter:
            text = String(size/2, size/2 - 2.5, letter)
            text.fontName = 'Helvetica-Bold'
            text.fontSize = 8
            text.textAnchor = 'middle'
            
            if filled:
                text.fillColor = colors.white
            else:
                text.fillColor = colors.Color(0.8, 0.8, 0.8)
            
            d.add(text)
        
        return d
    
    def _convert_image_to_grayscale(self, image_path: str) -> str:
        """Convert image to grayscale and return path to converted image."""
        try:
            img = PILImage.open(image_path)
            
            # Handle transparency
            if img.mode in ('RGBA', 'LA'):
                background = PILImage.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'RGBA':
                    background.paste(img, mask=img.split()[-1])
                else:
                    background.paste(img, mask=img.split()[-1])
                img = background
            
            # Convert to grayscale
            img_gray = img.convert('L')
            
            # Save to temporary file with proper cleanup
            with tempfile.NamedTemporaryFile(suffix='_gray.png', delete=False) as temp_file:
                img_gray.save(temp_file.name)
                return temp_file.name
            
        except Exception:
            return image_path  # Return original on error
    
    def _get_table_padding_style(self, padding: float = 2, top_bottom: Optional[float] = None) -> List[tuple]:
        """Get standard table padding style."""
        tb_padding = top_bottom if top_bottom is not None else padding
        return [
            ('LEFTPADDING', (0, 0), (-1, -1), padding),
            ('RIGHTPADDING', (0, 0), (-1, -1), padding),
            ('TOPPADDING', (0, 0), (-1, -1), tb_padding),
            ('BOTTOMPADDING', (0, 0), (-1, -1), tb_padding),
        ]
    
    def _get_no_padding_style(self, *exclude_sides) -> List[tuple]:
        """Get zero padding style, optionally excluding certain sides."""
        style = []
        if 'LEFT' not in exclude_sides:
            style.append(('LEFTPADDING', (0, 0), (-1, -1), 0))
        if 'RIGHT' not in exclude_sides:
            style.append(('RIGHTPADDING', (0, 0), (-1, -1), 0))
        if 'TOP' not in exclude_sides:
            style.append(('TOPPADDING', (0, 0), (-1, -1), 0))
        if 'BOTTOM' not in exclude_sides:
            style.append(('BOTTOMPADDING', (0, 0), (-1, -1), 0))
        return style