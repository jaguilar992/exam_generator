# -*- coding: utf-8 -*-
"""
Internationalization support for ExamGenerator.
Provides text strings in English and Spanish.
"""

from enum import Enum
from typing import Dict, Any


class Language(Enum):
    """Supported languages."""
    ENGLISH = "en"
    SPANISH = "es"


class TextStrings:
    """Text strings for internationalization support."""
    
    # Default language is English
    DEFAULT_LANGUAGE = Language.ENGLISH
    
    # Text definitions
    TEXTS = {
        Language.ENGLISH: {
            # Header texts
            "student_label": "Student",
            "course_label": "Course", 
            "class_label": "Section",
            "professor_label": "Instructor",
            "date_label": "Date",
            "list_number_label": "Student #",
            "value_label": "Points",
            "points_suffix": "pts",
            "grade_label": "Score",
            
            # Instructions
            "instructions_title": "INSTRUCTIONS",
            "instructions_text": (
                "Read each question carefully and select the correct answer by completely "
                "filling in the corresponding circle. Use only a No. 2 pencil or blue or black ink pen."
            ),
            
            # Answer sheet
            "answer_sheet_title": "ANSWER SHEET",
            
            # Answer key specific
            "answer_key_student_name": "ANSWER KEY",
            
            # Default form fields
            "student_name_blank": "Student Name: ___________________________________________________________",
            "course_section_blank": "Course/Section: ___________________",
            "date_blank": "Date: ________________",
            "list_number_blank": "Student #: ________________"
        },
        
        Language.SPANISH: {
            # Header texts
            "student_label": "Estudiante",
            "course_label": "Asignatura",
            "class_label": "Sección", 
            "professor_label": "Docente",
            "date_label": "Fecha",
            "list_number_label": "N° Lista",
            "value_label": "Puntos",
            "points_suffix": "pts",
            "grade_label": "Nota",
            
            # Instructions
            "instructions_title": "INSTRUCCIONES",
            "instructions_text": (
                "Lea cuidadosamente cada pregunta y seleccione la respuesta correcta "
                "rellenando completamente el círculo correspondiente. Use únicamente lápiz "
                "No. 2 o bolígrafo de tinta azul o negra."
            ),
            
            # Answer sheet
            "answer_sheet_title": "HOJA DE RESPUESTAS",
            
            # Answer key specific  
            "answer_key_student_name": "CLAVE DE RESPUESTAS",
            
            # Default form fields
            "student_name_blank": "Nombre del Estudiante: __________________________________________________",
            "course_section_blank": "Asignatura/Sección: ___________________", 
            "date_blank": "Fecha: ________________",
            "list_number_blank": "N° Lista: ________________"
        }
    }
    
    def __init__(self, language: Language = None):
        """
        Initialize text strings with specified language.
        
        Args:
            language (Language): Language to use. Defaults to English.
        """
        self.language = language or self.DEFAULT_LANGUAGE
        self._strings = self.TEXTS[self.language]
    
    def get(self, key: str, **kwargs) -> str:
        """
        Get localized text for the specified key.
        
        Args:
            key (str): Text key
            **kwargs: Format parameters for the text
            
        Returns:
            str: Localized text
        """
        text = self._strings.get(key, f"[MISSING: {key}]")
        
        # Apply formatting if kwargs provided
        if kwargs and isinstance(text, str):
            try:
                return text.format(**kwargs)
            except (KeyError, ValueError):
                return text
        
        return text
    
    def get_language(self) -> Language:
        """Get current language."""
        return self.language
    
    def set_language(self, language: Language):
        """
        Set the language for text strings.
        
        Args:
            language (Language): Language to set
        """
        if language in self.TEXTS:
            self.language = language
            self._strings = self.TEXTS[language]
        else:
            raise ValueError(f"Unsupported language: {language}")
    
    # Convenience methods for common text patterns
    def get_label_with_colon(self, key: str) -> str:
        """Get label with colon suffix."""
        return f"{self.get(key)}:"
    
    def get_field_with_blank_line(self, label_key: str, line_length: int = 65) -> str:
        """Get field label with blank line for filling."""
        label = self.get_label_with_colon(label_key)
        line = "_" * line_length
        return f"{label} {line}"
    
    def get_points_text(self, points: int) -> str:
        """Get formatted points text."""
        return f"{self.get('value_label')}: {points} {self.get('points_suffix')}"


# Global instance for easy access
_global_strings = None


def get_text_strings(language: Language = None) -> TextStrings:
    """
    Get global text strings instance.
    
    Args:
        language (Language): Language to use. If None, uses current global language.
        
    Returns:
        TextStrings: Text strings instance
    """
    global _global_strings
    
    if _global_strings is None:
        _global_strings = TextStrings(language or Language.ENGLISH)
    elif language is not None and language != _global_strings.get_language():
        _global_strings.set_language(language)
    
    return _global_strings


def set_global_language(language: Language):
    """
    Set the global language for all text strings.
    
    Args:
        language (Language): Language to set globally
    """
    global _global_strings
    if _global_strings is None:
        _global_strings = TextStrings(language)
    else:
        _global_strings.set_language(language)


# Convenience functions for common use cases
def t(key: str, language: Language = None, **kwargs) -> str:
    """
    Quick translation function.
    
    Args:
        key (str): Text key
        language (Language): Language override
        **kwargs: Format parameters
        
    Returns:
        str: Localized text
    """
    strings = get_text_strings(language)
    return strings.get(key, **kwargs)


def get_instructions_text(language: Language = None) -> str:
    """Get full formatted instructions text."""
    strings = get_text_strings(language)
    title = strings.get('instructions_title')
    text = strings.get('instructions_text')
    return f"<b>{title}:</b> {text}"


def get_answer_sheet_title(language: Language = None) -> str:
    """Get formatted answer sheet title."""
    strings = get_text_strings(language)
    return f"<b>{strings.get('answer_sheet_title')}</b>"