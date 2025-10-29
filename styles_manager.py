from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
import os
import platform

class StylesManager:
    def __init__(self):
        self._register_fonts()
    
    def _register_fonts(self):
        """Registra fuentes con soporte completo UTF-8 y Unicode"""
        try:
            fonts_registered = False
            system = platform.system()
            
            # macOS - buscar fuentes con mejor soporte Unicode
            if system == "Darwin":
                # Lista de fuentes macOS con buen soporte Unicode (incluye símbolos griegos)
                macos_fonts = [
                    # Arial Unicode MS (muy completa)
                    ('/Library/Fonts/Arial Unicode.ttf', 'Arial-Unicode-UTF8', 'Arial-Unicode-UTF8-Bold'),
                    ('/System/Library/Fonts/Arial Unicode.ttc', 'Arial-Unicode-UTF8', 'Arial-Unicode-UTF8-Bold'),
                    
                    # Helvetica Neue (buena para símbolos)
                    ('/System/Library/Fonts/Helvetica.ttc', 'Helvetica-UTF8', 'Helvetica-UTF8-Bold'),
                    ('/System/Library/Fonts/Helvetica Neue.ttc', 'Helvetica-UTF8', 'Helvetica-UTF8-Bold'),
                    
                    # Times New Roman (excelente soporte Unicode)
                    ('/System/Library/Fonts/Times.ttc', 'Times-UTF8', 'Times-UTF8-Bold'),
                    ('/Library/Fonts/Times New Roman.ttf', 'Times-UTF8', 'Times-UTF8-Bold'),
                    
                    # Arial estándar
                    ('/System/Library/Fonts/Arial.ttf', 'Arial-UTF8', 'Arial-UTF8-Bold'),
                ]
                
                for font_path, regular_name, bold_name in macos_fonts:
                    if os.path.exists(font_path):
                        try:
                            pdfmetrics.registerFont(TTFont(regular_name, font_path))
                            
                            # Buscar versión bold
                            bold_path = font_path.replace('.ttf', ' Bold.ttf').replace('.ttc', ' Bold.ttc')
                            if os.path.exists(bold_path):
                                pdfmetrics.registerFont(TTFont(bold_name, bold_path))
                            else:
                                # Usar la misma fuente para bold si no existe versión bold
                                pdfmetrics.registerFont(TTFont(bold_name, font_path))
                            
                            self.font_name = regular_name
                            self.font_name_bold = bold_name
                            fonts_registered = True
                            break
                            
                        except Exception as e:
                            continue
            
            # Linux - DejaVu y otras fuentes con buen soporte Unicode
            elif system == "Linux":
                linux_fonts = [
                    # DejaVu (excelente soporte Unicode)
                    ('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 'DejaVu-UTF8', 
                     '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 'DejaVu-UTF8-Bold'),
                    
                    # Liberation (compatible con Arial)
                    ('/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf', 'Liberation-UTF8',
                     '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf', 'Liberation-UTF8-Bold'),
                    
                    # Ubuntu fonts
                    ('/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf', 'Ubuntu-UTF8',
                     '/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf', 'Ubuntu-UTF8-Bold'),
                ]
                
                for regular_path, regular_name, bold_path, bold_name in linux_fonts:
                    if os.path.exists(regular_path):
                        try:
                            pdfmetrics.registerFont(TTFont(regular_name, regular_path))
                            
                            if os.path.exists(bold_path):
                                pdfmetrics.registerFont(TTFont(bold_name, bold_path))
                            else:
                                pdfmetrics.registerFont(TTFont(bold_name, regular_path))
                            
                            self.font_name = regular_name
                            self.font_name_bold = bold_name
                            fonts_registered = True
                            break
                            
                        except Exception as e:
                            continue
            
            # Windows
            elif system == "Windows":
                windows_fonts = [
                    # Arial Unicode MS (muy completa)
                    (r'C:\Windows\Fonts\ARIALUNI.TTF', 'Arial-Unicode-UTF8', 'Arial-Unicode-UTF8-Bold'),
                    
                    # Times New Roman
                    (r'C:\Windows\Fonts\times.ttf', 'Times-UTF8', r'C:\Windows\Fonts\timesbd.ttf', 'Times-UTF8-Bold'),
                    
                    # Arial
                    (r'C:\Windows\Fonts\arial.ttf', 'Arial-UTF8', r'C:\Windows\Fonts\arialbd.ttf', 'Arial-UTF8-Bold'),
                ]
                
                for item in windows_fonts:
                    if len(item) == 3:  # Arial Unicode MS (un archivo)
                        regular_path, regular_name, bold_name = item
                        bold_path = regular_path
                    else:  # Fuentes con archivos separados
                        regular_path, regular_name, bold_path, bold_name = item
                    
                    if os.path.exists(regular_path):
                        try:
                            pdfmetrics.registerFont(TTFont(regular_name, regular_path))
                            
                            if os.path.exists(bold_path):
                                pdfmetrics.registerFont(TTFont(bold_name, bold_path))
                            else:
                                pdfmetrics.registerFont(TTFont(bold_name, regular_path))
                            
                            self.font_name = regular_name
                            self.font_name_bold = bold_name
                            fonts_registered = True
                            break
                            
                        except Exception as e:
                            continue
            
            if not fonts_registered:
                # Fallback mejorado - Times-Roman tiene mejor soporte Unicode que Helvetica
                self.font_name = 'Times-Roman'
                self.font_name_bold = 'Times-Bold'
                
        except Exception as e:
            # Fallback ultra-seguro
            self.font_name = 'Times-Roman'
            self.font_name_bold = 'Times-Bold'
    
    def get_best_font_for_text(self, text):
        """Determina la mejor fuente para el texto dado, considerando caracteres especiales"""
        # Verificar si el texto contiene caracteres que requieren Symbol font
        greek_chars = set('αβγδεζηθικλμνξοπρστυφχψωΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩ⍺')
        
        if any(char in greek_chars for char in text):
            # Para caracteres griegos, intentar usar Symbol si está disponible
            try:
                # Verificar si Symbol está disponible
                from reportlab.pdfbase import pdfmetrics
                available_fonts = pdfmetrics.getRegisteredFontNames()
                if 'Symbol' in available_fonts:
                    return 'Symbol'
            except:
                pass
        
        return self.font_name
    

    def process_text_for_unicode(self, text):
        """Procesa el texto para manejar caracteres Unicode especiales"""
        if not text:
            return text
        
        # Mapeo de caracteres problemáticos a sus equivalentes
        char_replacements = {
            '⍺': 'α',  # Usar alpha griego estándar en lugar del símbolo especial
            '⍬': '∅',  # Conjunto vacío
            '⍳': 'ι',  # Iota
            '⍴': 'ρ',  # Rho
            '⍵': 'ω',  # Omega
        }
        
        processed_text = text
        for old_char, new_char in char_replacements.items():
            processed_text = processed_text.replace(old_char, new_char)
        
        return processed_text
    
    def create_paragraph_with_unicode_support(self, text, style):
        """Crea un párrafo con soporte mejorado para Unicode"""
        # Procesar el texto para caracteres problemáticos
        processed_text = self.process_text_for_unicode(text)
        
        # Crear el párrafo
        return Paragraph(processed_text, style)
    
    def create_styles(self):
        """Define los estilos para el documento"""
        styles = getSampleStyleSheet()
        
        # Estilo para preguntas con soporte Unicode mejorado
        question_style = ParagraphStyle(
            'QuestionStyle',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=8,
            spaceBefore=8,
            leftIndent=0,
            fontName=self.font_name_bold,
            encoding='utf-8'  # Especificar encoding UTF-8
        )
        
        # Estilo para opciones con soporte Unicode
        option_style = ParagraphStyle(
            'OptionStyle',
            parent=styles['Normal'],
            fontSize=10,
            fontName=self.font_name,
            encoding='utf-8'
        )
        
        # Estilo para texto general con Unicode
        unicode_text_style = ParagraphStyle(
            'UnicodeText',
            parent=styles['Normal'],
            fontSize=10,
            fontName=self.font_name,
            encoding='utf-8'
        )
        
        return {
            'question': question_style,
            'option': option_style,
            'unicode_text': unicode_text_style
        }