from test_generator import TestGenerator

def main():
    input_file = "capitals.ptf"
    output_file = "test_capitales.pdf"
    answer_key_file = "test_capitales_PAUTA.pdf"
    password = "pauta2025"  # Contraseña para el PDF de respuestas
    
    # Valores pre-filled para clase, profesor e instituto
    class_name = "Geografía Mundial"
    professor_name = "Juan Carlos Méndez"
    institute_name = "Instituto Técnico Superior"
    
    # Crear generador con shuffle habilitado (por defecto)
    generator = TestGenerator(input_file, output_file, class_name, professor_name, institute_name, password, shuffle_options=True)
    
    # Generar PDF normal (para estudiantes)
    generator.generate_pdf()
    
    # Generar PDF con respuestas marcadas y protegido con contraseña (para profesor)
    generator.generate_answer_key_pdf(answer_key_file, password)

if __name__ == "__main__":
    main()