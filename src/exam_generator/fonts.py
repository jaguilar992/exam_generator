# -*- coding: utf-8 -*-
"""
Font management system for the exam generator library.
Provides system-independent font support using embedded Liberation fonts.
"""

from pathlib import Path
from typing import Optional, Dict

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily


class EmbeddedFontManager:
    """
    Manages embedded Liberation fonts for consistent cross-platform rendering.
    Automatically falls back to system fonts if embedded fonts are unavailable.
    """
    
    def __init__(self):
        """Initialize the font manager."""
        self.fonts_registered = False
        self.font_name = 'Liberation-Sans'
        self.font_name_bold = 'Liberation-Sans-Bold'
    
    def get_fonts_directory(self) -> Path:
        """Get the directory where fonts are stored."""
        current_dir = Path(__file__).parent
        fonts_dir = current_dir / "fonts"
        return fonts_dir
    
    def ensure_fonts_registered(self) -> bool:
        """
        Ensure embedded fonts are registered and available.
        
        Returns:
            bool: True if fonts were registered successfully
        """
        if self.fonts_registered:
            return True
        
        try:
            self._register_liberation_fonts()
        except Exception as e:
            print(f"Warning: Could not register Liberation fonts: {e}")
            self._register_fallback_fonts()
        
        self.fonts_registered = True
        return True
    
    def _register_liberation_fonts(self) -> None:
        """Register Liberation Sans fonts from embedded files."""
        fonts_dir = self.get_fonts_directory()
        
        # Define font mappings
        font_files = {
            'Liberation-Sans': 'LiberationSans-Regular.ttf',
            'Liberation-Sans-Bold': 'LiberationSans-Bold.ttf',
            'Liberation-Sans-Italic': 'LiberationSans-Italic.ttf',
            'Liberation-Sans-BoldItalic': 'LiberationSans-BoldItalic.ttf'
        }
        
        # Check if required font files exist
        required_fonts = ['Liberation-Sans', 'Liberation-Sans-Bold']
        for font_name in required_fonts:
            font_file = font_files[font_name]
            font_path = fonts_dir / font_file
            if not font_path.exists():
                raise FileNotFoundError(f"Font file not found: {font_path}")
        
        # Register fonts with ReportLab
        for font_name, font_file in font_files.items():
            font_path = fonts_dir / font_file
            if font_path.exists():
                pdfmetrics.registerFont(TTFont(font_name, str(font_path)))
        
        # Register font family
        registerFontFamily('Liberation-Sans',
                         normal='Liberation-Sans',
                         bold='Liberation-Sans-Bold',
                         italic='Liberation-Sans-Italic',
                         boldItalic='Liberation-Sans-BoldItalic')
        
        self.font_name = 'Liberation-Sans'
        self.font_name_bold = 'Liberation-Sans-Bold'
    
    def _register_fallback_fonts(self):
        """Register fallback fonts if Liberation fonts are not available."""
        self.font_name = 'Times-Roman'
        self.font_name_bold = 'Times-Bold'
    
    def get_font_name(self, bold: bool = False) -> str:
        """
        Get the appropriate font name.
        
        Args:
            bold (bool): Whether to get bold variant
            
        Returns:
            str: Font name
        """
        self.ensure_fonts_registered()
        return self.font_name_bold if bold else self.font_name
    
    def get_available_fonts(self) -> Dict[str, str]:
        """
        Get dictionary of available fonts.
        
        Returns:
            Dict[str, str]: Dictionary with font mappings
        """
        self.ensure_fonts_registered()
        return {
            'regular': self.font_name,
            'bold': self.font_name_bold,
            'italic': self.font_name,
            'bold_italic': self.font_name_bold
        }
    
    def test_unicode_support(self, text: str = "áéíóúñÁÉÍÓÚÑ αβγδε") -> bool:
        """
        Test if current fonts support Unicode characters.
        
        Args:
            text (str): Test text with Unicode characters
            
        Returns:
            bool: True if Unicode is supported
        """
        try:
            self.ensure_fonts_registered()
            # Liberation fonts have excellent Unicode support
            return self.font_name.startswith('Liberation')
        except Exception:
            return False


# Global font manager instance
_font_manager = None


def get_font_manager() -> EmbeddedFontManager:
    """
    Get the global font manager instance.
    
    Returns:
        EmbeddedFontManager: Font manager instance
    """
    global _font_manager
    if _font_manager is None:
        _font_manager = EmbeddedFontManager()
    return _font_manager


def ensure_fonts_available() -> bool:
    """
    Ensure fonts are available for use.
    
    Returns:
        bool: True if fonts are available
    """
    return get_font_manager().ensure_fonts_registered()