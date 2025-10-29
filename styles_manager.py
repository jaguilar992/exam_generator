from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

class StylesManager:
    def __init__(self):
        self._register_fonts()
    
    def _register_fonts(self):
        """Registra fuentes con soporte UTF-8"""
        try:
            fonts_registered = False
            
            # Intentar Arial primero (macOS)
            if os.path.exists('/System/Library/Fonts/Arial.ttf'):
                pdfmetrics.registerFont(TTFont('Arial-UTF8', '/System/Library/Fonts/Arial.ttf'))
                if os.path.exists('/System/Library/Fonts/Arial Bold.ttf'):
                    pdfmetrics.registerFont(TTFont('Arial-UTF8-Bold', '/System/Library/Fonts/Arial Bold.ttf'))
                else:
                    pdfmetrics.registerFont(TTFont('Arial-UTF8-Bold', '/System/Library/Fonts/Arial.ttf'))
                fonts_registered = True
                self.font_name = 'Arial-UTF8'
                self.font_name_bold = 'Arial-UTF8-Bold'
            
            # Si no está Arial, usar DejaVu (Linux)
            elif os.path.exists('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'):
                pdfmetrics.registerFont(TTFont('DejaVu-UTF8', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
                if os.path.exists('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'):
                    pdfmetrics.registerFont(TTFont('DejaVu-UTF8-Bold', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))
                else:
                    pdfmetrics.registerFont(TTFont('DejaVu-UTF8-Bold', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
                fonts_registered = True
                self.font_name = 'DejaVu-UTF8'
                self.font_name_bold = 'DejaVu-UTF8-Bold'
            
            if not fonts_registered:
                # Fallback a Times-Roman que tiene mejor soporte UTF-8 que Helvetica
                self.font_name = 'Times-Roman'
                self.font_name_bold = 'Times-Bold'
                
        except Exception as e:
            print(f"Error registrando fuentes: {e}")
            # Fallback seguro
            self.font_name = 'Times-Roman'
            self.font_name_bold = 'Times-Bold'
    
    def create_styles(self):
        """Define los estilos para el documento"""
        styles = getSampleStyleSheet()
        
        # Estilo para preguntas
        question_style = ParagraphStyle(
            'QuestionStyle',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=8,
            spaceBefore=8,
            leftIndent=0,
            fontName=self.font_name_bold
        )
        

        
        return {
            'question': question_style
        }