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
from reportlab.graphics.shapes import Drawing, Circle, String
from PIL import Image as PILImage

from .styles import StylesManager
from ..config import ExamConfig


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
        story.extend(self._create_answer_sheet_section(len(questions)))
        
        # Questions section
        story.append(Spacer(1, 0.3*cm))
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
        story.extend(self._create_answer_sheet_section(len(questions), correct_answers))
        
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
        grade_box = self._create_grade_box(grade_box_size)
        
        # Main header table
        header_table = self._create_header_table(logo_cell, qr_cell, grade_box, logo_qr_size, grade_box_size)
        elements.append(header_table)
        elements.append(Spacer(1, -grade_box_size + 0.2*cm))
        
        # Institution and course info
        elements.extend(self._create_institution_info(config))
        
        # Student/exam info table
        elements.append(self._create_info_table(config))
        
        # Instructions
        elements.append(self._create_instructions())
        
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
    
    def _create_grade_box(self, size: float) -> Table:
        """Create grade box for header."""
        grade_data = [
            [""],  # Space for grade
            [""],
            [""],
            ["Calificación"]
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
        
        # Institute name
        institute_para = self.styles_manager.create_paragraph_with_unicode_support(
            f"<b>{config.institute_name}</b>",
            self.styles['institute_header']
        )
        elements.append(institute_para)
        
        # Course name
        course_para = self.styles_manager.create_paragraph_with_unicode_support(
            config.course,
            self.styles['course_header']
        )
        elements.append(course_para)
        
        return elements
    
    def _create_info_table(self, config: ExamConfig) -> Table:
        """Create student and exam information table."""
        info_data = [
            [config.class_name, config.professor_name, "Fecha: ________________"],
            [config.student_name, "", "#Lista: ________________"],
            [config.course_section, config.exam_period, config.test_value]
        ]
        
        info_table = Table(info_data, colWidths=[self.content_width/3] * 3)
        info_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        
        return info_table
    
    def _create_instructions(self) -> Paragraph:
        """Create exam instructions."""
        instructions_text = ("<b>INSTRUCCIONES:</b> Lea cuidadosamente cada pregunta y seleccione la respuesta "
                           "correcta rellenando completamente el círculo correspondiente. Use únicamente lápiz "
                           "No. 2 o bolígrafo azul o negro.")
        
        return self.styles_manager.create_paragraph_with_unicode_support(
            instructions_text,
            self.styles['instructions']
        )
    
    def _create_answer_sheet_section(
        self, 
        max_questions: int, 
        correct_answers: Optional[List[int]] = None
    ) -> List[Any]:
        """Create answer sheet section with bubble grid."""
        elements = []
        
        # Title
        title = self.styles_manager.create_paragraph_with_unicode_support(
            "<b>HOJA DE RESPUESTAS</b>",
            self.styles['answer_title']
        )
        elements.append(title)
        
        # Create 5x5 grid of questions
        answer_data = []
        for row in range(5):
            row_data = []
            for col in range(5):
                question_num = row * 5 + col + 1
                if question_num <= max_questions:
                    question_cell = self._create_question_bubble_row(
                        question_num, 
                        correct_answers[question_num - 1] if correct_answers and question_num <= len(correct_answers) else None
                    )
                    row_data.append(question_cell)
                else:
                    row_data.append("")
            answer_data.append(row_data)
        
        # Answer sheet table
        answer_table = Table(answer_data, colWidths=[self.content_width/5] * 5)
        answer_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.gray),
        ] + self._get_table_padding_style(3)))
        
        elements.extend([answer_table, Spacer(1, 0.5*cm)])
        return elements
    
    def _create_question_bubble_row(self, question_num: int, correct_answer: Optional[int] = None) -> Table:
        """Create a row of bubbles for one question."""
        # Question number
        num_para = self.styles_manager.create_paragraph_with_unicode_support(
            f"<b>{question_num}.</b>",
            self.styles['question_number']
        )
        
        # Create bubbles A, B, C, D
        bubbles = [num_para]
        for i, letter in enumerate(['A', 'B', 'C', 'D']):
            is_filled = (correct_answer is not None and i == correct_answer)
            bubble = self._create_circle_drawing(size=0.5*cm, letter=letter, filled=is_filled)
            bubbles.append(bubble)
        
        bubble_table = Table([bubbles], colWidths=[0.6*cm, 0.5*cm, 0.5*cm, 0.5*cm, 0.5*cm])
        bubble_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ] + self._get_table_padding_style(1, 2)))
        
        return bubble_table
    
    def _create_two_column_questions(self, questions: List[Dict[str, Any]]) -> List[Any]:
        """Create questions in two-column layout."""
        return self._create_question_columns(questions, include_answers=False)
    
    def _create_two_column_questions_with_answers(self, questions: List[Dict[str, Any]]) -> List[Any]:
        """Create questions with answers in two-column layout."""
        return self._create_question_columns(questions, include_answers=True)
    
    def _create_question_columns(self, questions: List[Dict[str, Any]], include_answers: bool = False) -> List[Any]:
        """Create questions in two-column format."""
        elements = []
        
        for i in range(0, len(questions), 2):
            left_question = questions[i] if i < len(questions) else None
            right_question = questions[i + 1] if i + 1 < len(questions) else None
            
            left_content = ""
            right_content = ""
            
            if left_question:
                left_content = self._create_compact_question(
                    left_question, i + 1, include_answers
                )
            
            if right_question:
                right_content = self._create_compact_question(
                    right_question, i + 2, include_answers
                )
            
            # Two-column table with 0.7cm spacing
            col_data = [[left_content, right_content]]
            column_width = (self.content_width - 0.7*cm) / 2
            col_table = Table(col_data, colWidths=[column_width, column_width])
            col_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (0, 0), 0),
                ('RIGHTPADDING', (0, 0), (0, 0), 0.35*cm),
                ('LEFTPADDING', (1, 0), (1, 0), 0.35*cm),
                ('RIGHTPADDING', (1, 0), (1, 0), 0),
            ] + self._get_no_padding_style('TOP', 'BOTTOM')))
            
            elements.extend([col_table, Spacer(1, 0.3*cm)])
        
        return elements
    
    def _create_compact_question(
        self, 
        question_data: Dict[str, Any], 
        question_num: int, 
        include_answer: bool = False
    ) -> Table:
        """Create a compact question for column layout."""
        # Question text
        question_text = f"<b>{question_num}.</b> {question_data['question']}"
        question_para = self.styles_manager.create_paragraph_with_unicode_support(
            question_text,
            self.styles['compact_question']
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
                    'CompactOption',
                    parent=self.styles['compact_option'],
                    leftIndent=0.3*cm
                )
            )
            option_elements.append(option_para)
        
        # Build question table
        question_elements = [question_para] + option_elements + [Spacer(1, 0.2*cm)]
        question_table_data = [[elem] for elem in question_elements]
        
        question_table = Table(question_table_data, colWidths=[(self.content_width - 0.7*cm) / 2])
        question_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ] + self._get_no_padding_style()))
        
        return question_table
    
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
    
    def _get_table_padding_style(self, padding: int = 2, top_bottom: Optional[int] = None) -> List[tuple]:
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