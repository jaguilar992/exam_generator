from exam_generator import ExamGenerator, Language

config = ExamGenerator.builder()\
    .institute("Instituto de Ejemplo")\
    .class_subject("Matemáticas 101")\
    .professor("Dr. Juan Pérez")\
    .exam_period("Primer Semestre")\
    .total_points(50)\
    .logo("./logo.jpg")\
    .course("Curso de Prueba")\
    .language(Language.SPANISH)\
    .password("kakaroto1")\
    .build()
    
with ExamGenerator(config, shuffle_options=True) as gen:
    gen.load_questions_from_file("./capitals.ptf")
    student_pdf, answer_key_pdf = gen.generate_both(
        "exam_student.pdf",
        "exam_answer_key.pdf"
    )