import re
import random

class QuestionParser:
    def __init__(self, shuffle_options=True):
        self.shuffle_options = shuffle_options
    
    def parse_questions(self, input_file):
        """Parsea el archivo de preguntas y opciones"""
        questions = []
        
        with open(input_file, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Dividir por preguntas (líneas que empiezan con -)
        question_blocks = re.split(r'^-\s+', content, flags=re.MULTILINE)[1:]
        
        for block in question_blocks:
            lines = [line.strip() for line in block.strip().split('\n') if line.strip()]
            if lines:
                question_text = lines[0]
                options = lines[1:5] if len(lines) > 1 else []
                
                # La respuesta correcta siempre es la primera opción (índice 0)
                correct_answer_index = 0
                
                # Shuffle las opciones si está habilitado
                if self.shuffle_options and len(options) > 1:
                    # Crear lista de tuplas (opción, es_correcta)
                    options_with_flags = [(opt, i == 0) for i, opt in enumerate(options)]
                    random.shuffle(options_with_flags)
                    
                    # Separar las opciones shuffleadas y encontrar la nueva posición de la correcta
                    shuffled_options = []
                    for i, (option, is_correct) in enumerate(options_with_flags):
                        shuffled_options.append(option)
                        if is_correct:
                            correct_answer_index = i
                    
                    options = shuffled_options
                
                questions.append({
                    'question': question_text,
                    'options': options,
                    'correct_answer': correct_answer_index
                })
        return questions