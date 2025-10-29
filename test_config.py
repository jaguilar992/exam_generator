import datetime

class TestConfig:
    def __init__(self, class_name=None, professor_name=None, institute_name=None, password=None):
        # Header information
        self.logo_path = "logo.png"
        self.institute_name = institute_name if institute_name else "Instituto Técnico Superior"
        self.course = "I de Bachillerato Técnico en Informática"
        self.class_name = f"Clase: {class_name}" if class_name else "Clase: ___________________"
        self.student_name = "Alumno: _________________________________________________________________"
        self.professor_name = f"Profesor: {professor_name}" if professor_name else "Profesor: ___________________"
        self.course_section = "Curso: ___________________"
        self.year = datetime.datetime.now().year
        self.exam_period = "I Parcial " + str(self.year)
        self.total = 50
        self.test_value = f"Valor: {self.total} pts"
        self.password = password if password else "pauta2025"  # Contraseña por defecto