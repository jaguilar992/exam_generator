# -*- coding: utf-8 -*-
"""
Styles management for PDF generation with embedded fonts.
"""

from typing import Dict
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT

from ..fonts import get_font_manager, ensure_fonts_available


class StylesManager:
    """
    Manages fonts and styles for PDF generation with Unicode support.
    Uses embedded fonts for system independence.
    """
    
    def __init__(self):
        """Initialize styles manager with embedded fonts."""
        # Ensure embedded fonts are available
        ensure_fonts_available()
        
        # Get font manager
        self.font_manager = get_font_manager()
        
        # Get font names from the embedded font system
        self.font_name = self.font_manager.get_font_name(bold=False)
        self.font_name_bold = self.font_manager.get_font_name(bold=True)
    
    def process_text_for_unicode(self, text: str) -> str:
        """
        Process text to handle problematic Unicode characters.
        
        Args:
            text (str): Input text
            
        Returns:
            str: Processed text with character replacements
        """
        if not text:
            return text
        
        # Character replacements for better compatibility
        replacements = {
            '⍺': 'α',  # Use standard Greek alpha
            '⍬': '∅',  # Empty set
            '⍳': 'ι',  # Greek iota
            '⍴': 'ρ',  # Greek rho
            '⍵': 'ω',  # Greek omega
        }
        
        processed_text = text
        for old_char, new_char in replacements.items():
            processed_text = processed_text.replace(old_char, new_char)
        
        return processed_text
    
    def create_paragraph_with_unicode_support(self, text: str, style: ParagraphStyle) -> Paragraph:
        """
        Create a paragraph with Unicode support.
        
        Args:
            text (str): Paragraph text
            style (ParagraphStyle): Paragraph style
            
        Returns:
            Paragraph: Created paragraph
        """
        processed_text = self.process_text_for_unicode(text)
        return Paragraph(processed_text, style)
    
    def create_styles(self) -> Dict[str, ParagraphStyle]:
        """
        Create standard styles for exam documents.
        
        Returns:
            Dict[str, ParagraphStyle]: Dictionary of styles
        """
        base_styles = getSampleStyleSheet()
        
        styles = {
            'question': ParagraphStyle(
                'QuestionStyle',
                parent=base_styles['Normal'],
                fontSize=11,
                spaceAfter=8,
                spaceBefore=8,
                leftIndent=0,
                fontName=self.font_name_bold,
                encoding='utf-8'
            ),
            'option': ParagraphStyle(
                'OptionStyle',
                parent=base_styles['Normal'],
                fontSize=10,
                fontName=self.font_name,
                encoding='utf-8'
            ),
            'unicode_text': ParagraphStyle(
                'UnicodeText',
                parent=base_styles['Normal'],
                fontSize=10,
                fontName=self.font_name,
                encoding='utf-8'
            ),
            'institute_header': ParagraphStyle(
                'InstituteHeader',
                fontSize=12,
                alignment=TA_CENTER,
                spaceAfter=5,
                fontName=self.font_name_bold,
                encoding='utf-8'
            ),
            'course_header': ParagraphStyle(
                'CourseHeader',
                fontSize=10,
                alignment=TA_CENTER,
                spaceAfter=8,
                fontName=self.font_name,
                encoding='utf-8'
            ),
            'instructions': ParagraphStyle(
                'Instructions',
                fontSize=9,
                alignment=TA_LEFT,
                spaceAfter=10,
                spaceBefore=5,
                fontName=self.font_name,
                encoding='utf-8'
            ),
            'answer_title': ParagraphStyle(
                'AnswerTitle',
                fontSize=11,
                alignment=TA_CENTER,
                spaceAfter=8,
                fontName=self.font_name_bold,
                encoding='utf-8'
            ),
            'compact_question': ParagraphStyle(
                'CompactQuestion',
                fontSize=11,
                fontName=self.font_name,
                leading=13,
                spaceAfter=4,
                encoding='utf-8'
            ),
            'compact_option': ParagraphStyle(
                'CompactOption',
                fontSize=10,
                fontName=self.font_name,
                leading=12,
                leftIndent=0.3,  # Will be converted to cm in usage
                encoding='utf-8'
            ),
            'question_number': ParagraphStyle(
                'QuestionNum',
                fontSize=9,
                fontName=self.font_name_bold,
                alignment=TA_CENTER,
                encoding='utf-8'
            ),
            'option_text': ParagraphStyle(
                'OptionText',
                fontSize=10,
                fontName=self.font_name,
                leading=12,
                encoding='utf-8'
            )
        }
        
        return styles