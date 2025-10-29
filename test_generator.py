import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Spacer
from reportlab.lib.units import cm



from question_parser import QuestionParser
from styles_manager import StylesManager
from pdf_builder import PDFBuilder
from test_config import TestConfig

class TestGenerator:
    def __init__(self, input_file, output_file, class_name=None, professor_name=None, institute_name=None, password=None, shuffle_options=True):
        self.input_file = input_file
        self.output_file = output_file
        self.shuffle_options = shuffle_options
        self.page_width, self.page_height = letter
        self.margin = 0.7 * cm
        self.content_width = self.page_width - 2 * self.margin
        
        # Inicializar componentes
        self.config = TestConfig(class_name, professor_name, institute_name, password)
        self.question_parser = QuestionParser(shuffle_options)
        self.styles_manager = StylesManager()
        self.pdf_builder = PDFBuilder(self.content_width)
    
    def encode_answers_to_hex(self, correct_answers):
        """
        Codifica un array de respuestas correctas (0-3) en una cadena hexadecimal
        Cada respuesta se codifica con 2 bits: 00=0, 01=1, 10=2, 11=3
        4 respuestas por byte (8 bits)
        """
        hex_string = ""
        
        # Procesar las respuestas en grupos de 4
        for i in range(0, len(correct_answers), 4):
            # Tomar hasta 4 respuestas del grupo actual
            group = correct_answers[i:i+4]
            
            # Rellenar con 0s si el grupo no tiene 4 elementos
            while len(group) < 4:
                group.append(0)
            
            # Convertir cada respuesta (0-3) a 2 bits y combinar en un byte
            byte_value = 0
            for j, answer in enumerate(group):
                # Cada respuesta ocupa 2 bits, desplazada según su posición
                byte_value |= (answer & 0x03) << (6 - j * 2)
            
            # Convertir el byte a hexadecimal (2 dígitos)
            hex_string += f"{byte_value:02X}"
        
        return hex_string
    

    
    def _prepare_qr_data(self, questions):
        """Prepara los datos del QR sin encriptación"""
        # Extraer respuestas correctas y generar código QR
        correct_answers = [q['correct_answer'] for q in questions]
        hex_code = self.encode_answers_to_hex(correct_answers)
    
        
        # Crear datos compactos para el QR usando formato simple
        # Formato: Q#P#A# donde Q=preguntas, P=puntos, A=respuestas_hex
        qr_data = f"Q{len(questions)}P{self.config.total}A{hex_code}"
        
        return qr_data
    
    def generate_pdf(self):
        """Genera el PDF con el test"""
        questions = self.question_parser.parse_questions(self.input_file)
        styles = self.styles_manager.create_styles()
        
        # Preparar datos del QR (reutilizar el mismo QR)
        if not hasattr(self, '_qr_data'):
            self._qr_data = self._prepare_qr_data(questions)
        
        # Generar QR con los datos encriptados (reutilizar si ya existe)
        if not hasattr(self, '_qr_path'):
            self._qr_path = self.pdf_builder.generate_qr_code(self._qr_data, "test_qr.png")
        
        doc = SimpleDocTemplate(
            self.output_file,
            pagesize=letter,
            rightMargin=self.margin,
            leftMargin=self.margin,
            topMargin=self.margin,
            bottomMargin=self.margin
        )
        
        story = []
        
        # Header compacto con QR
        story.extend(self.pdf_builder.create_header(self.config, styles, self._qr_path))
        
        # Título
        story.append(Spacer(1, 0.15*cm))
        
        # Preguntas
        for i, question in enumerate(questions, 1):
            story.append(self.pdf_builder.create_question_table(question, i, styles))
        
        doc.build(story)
        print(f"Test generado: {self.output_file}")
    
    def generate_answer_key_pdf(self, output_file, password):
        """Genera el PDF con las respuestas marcadas y protegido con contraseña"""
        questions = self.question_parser.parse_questions(self.input_file)
        styles = self.styles_manager.create_styles()
        
        # Reutilizar los mismos datos del QR preparados anteriormente
        if not hasattr(self, '_qr_data'):
            self._qr_data = self._prepare_qr_data(questions)
        
        # Reutilizar el mismo QR generado anteriormente
        if not hasattr(self, '_qr_path'):
            self._qr_path = self.pdf_builder.generate_qr_code(self._qr_data, "test_qr.png")
        
        # Crear configuración especial para la pauta (con "PAUTA" en el nombre del alumno)
        pauta_config = TestConfig(self.config.class_name.replace("Clase: ", ""), 
                                 self.config.professor_name.replace("Profesor: ", ""), 
                                 self.config.institute_name,
                                 self.config.password)
        pauta_config.student_name = "Alumno: PAUTA - HOJA DE RESPUESTAS"
        
        # Crear documento con encriptación
        doc = SimpleDocTemplate(
            output_file,
            pagesize=letter,
            rightMargin=self.margin,
            leftMargin=self.margin,
            topMargin=self.margin,
            bottomMargin=self.margin
        )
        
        # Configurar encriptación del documento
        def on_first_page(canvas, doc):
            canvas.setEncrypt(self.config.password)
            
        def on_later_pages(canvas, doc):
            canvas.setEncrypt(self.config.password)
        
        story = []
        
        # Header con configuración de pauta
        story.extend(self.pdf_builder.create_header(pauta_config, styles, self._qr_path))
        
        # Título
        story.append(Spacer(1, 0.15*cm))
        
        # Preguntas con respuestas marcadas
        for i, question in enumerate(questions, 1):
            story.append(self.pdf_builder.create_question_table_with_answer(question, i, styles))
        
        doc.build(story, onFirstPage=on_first_page, onLaterPages=on_later_pages)
        print(f"Pauta de respuestas generada: {output_file} (protegida con contraseña)")

# Función principal
def main():
    input_file = "capitals.ptf"
    output_file = "test_capitales.pdf"
    
    # Valores pre-filled para clase y profesor
    class_name = "Geografía Mundial"
    professor_name = "Juan Carlos Méndez"
    
    # Crear generador con shuffle habilitado (por defecto)
    generator = TestGenerator(input_file, output_file, class_name, professor_name, shuffle_options=True)
    generator.generate_pdf()

if __name__ == "__main__":
    main()