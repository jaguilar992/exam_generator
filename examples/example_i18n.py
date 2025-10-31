#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example demonstrating internationalization support (English and Spanish headers).
"""

import sys
import os
import tempfile
from pathlib import Path
from PIL import Image, ImageDraw

# Add src to path for development
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from exam_generator import (
    ExamGenerator,
    Language,
    get_text_strings,
    set_global_language
)


def create_sample_logo():
    """Create a simple PNG logo for testing."""
    image = Image.new('RGB', (100, 100), color='white')
    draw = ImageDraw.Draw(image)
    
    # Draw a simple logo shape
    draw.rectangle([10, 10, 90, 90], outline='black', width=2)
    draw.text((30, 40), "LOGO", fill='black')
    
    # Save to temporary file
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
        image.save(f.name, 'PNG')
        return f.name


def create_sample_questions():
    """Create sample questions for the exam."""
    questions_content = """
- What is the capital of Spain?
Madrid
Barcelona
Valencia
Seville

- What is the largest planet in our solar system?
Jupiter
Saturn
Earth
Mars

- Which programming language is known for its use in data science?
Python
JavaScript
C++
Ruby

- What is 15 + 27?
42
41
43
40

- Which ocean is the largest?
Pacific
Atlantic
Indian
Arctic
"""
    return questions_content


def demonstrate_english_exam():
    """Demonstrate exam generation in English."""
    print("\n" + "="*60)
    print("GENERATING EXAM IN ENGLISH")
    print("="*60)
    
    logo_path = create_sample_logo()
    
    try:
        # Create configuration in English (default)
        config = (ExamGenerator.builder()
                 .institute("Advanced Technical Institute")
                 .course("Computer Science Bachelor Program")
                 .class_subject("Introduction to Programming")
                 .professor("Dr. John Smith")
                 .exam_period("Midterm Exam - Fall 2024")
                 .password("programming2024")
                 .logo(logo_path)
                 .language(Language.ENGLISH)  # Explicitly set to English
                 .total_points(100)
                 .build())
        
        print(f"✓ Configuration created in English")
        
        # Show text strings being used
        text_strings = get_text_strings(Language.ENGLISH)
        print(f"✓ Instructions title: {text_strings.get('instructions_title')}")
        print(f"✓ Answer sheet title: {text_strings.get('answer_sheet_title')}")
        print(f"✓ Student label: {text_strings.get('student_label')}")
        print(f"✓ Grade label: {text_strings.get('grade_label')}")
        
        # Generate exam
        with ExamGenerator(config, shuffle_options=False) as generator:
            questions = create_sample_questions()
            generator.load_questions_from_string(questions)
            
            with tempfile.NamedTemporaryFile(suffix='_english_student.pdf', delete=False) as student_file, \
                 tempfile.NamedTemporaryFile(suffix='_english_answers.pdf', delete=False) as answer_file:
                
                student_pdf, answer_pdf = generator.generate_both(
                    student_file.name,
                    answer_file.name
                )
                
                print(f"✓ English student exam: {student_pdf}")
                print(f"✓ English answer key: {answer_pdf}")
                
                return student_pdf, answer_pdf
                
    finally:
        if os.path.exists(logo_path):
            os.remove(logo_path)


def demonstrate_spanish_exam():
    """Demonstrate exam generation in Spanish."""
    print("\n" + "="*60)
    print("GENERATING EXAM IN SPANISH")
    print("="*60)
    
    logo_path = create_sample_logo()
    
    try:
        # Create configuration in Spanish
        config = (ExamGenerator.builder()
                 .institute("Instituto Técnico Superior")
                 .course("Licenciatura en Ciencias de la Computación")
                 .class_subject("Introducción a la Programación")
                 .professor("Dr. María González")
                 .exam_period("Examen Parcial - Otoño 2024")
                 .password("programacion2024")
                 .logo(logo_path)
                 .language(Language.SPANISH)  # Set to Spanish
                 .total_points(100)
                 .build())
        
        print(f"✓ Configuration created in Spanish")
        
        # Show text strings being used
        text_strings = get_text_strings(Language.SPANISH)
        print(f"✓ Instructions title: {text_strings.get('instructions_title')}")
        print(f"✓ Answer sheet title: {text_strings.get('answer_sheet_title')}")
        print(f"✓ Student label: {text_strings.get('student_label')}")
        print(f"✓ Grade label: {text_strings.get('grade_label')}")
        
        # Generate exam
        with ExamGenerator(config, shuffle_options=False) as generator:
            # Use Spanish questions
            questions_spanish = """
- ¿Cuál es la capital de España?
Madrid
Barcelona
Valencia
Sevilla

- ¿Cuál es el planeta más grande de nuestro sistema solar?
Júpiter
Saturno
Tierra
Marte

- ¿Qué lenguaje de programación es conocido por su uso en ciencia de datos?
Python
JavaScript
C++
Ruby

- ¿Cuánto es 15 + 27?
42
41
43
40

- ¿Cuál es el océano más grande?
Pacífico
Atlántico
Índico
Ártico
"""
            
            generator.load_questions_from_string(questions_spanish)
            
            with tempfile.NamedTemporaryFile(suffix='_spanish_student.pdf', delete=False) as student_file, \
                 tempfile.NamedTemporaryFile(suffix='_spanish_answers.pdf', delete=False) as answer_file:
                
                student_pdf, answer_pdf = generator.generate_both(
                    student_file.name,
                    answer_file.name
                )
                
                print(f"✓ Spanish student exam: {student_pdf}")
                print(f"✓ Spanish answer key: {answer_pdf}")
                
                return student_pdf, answer_pdf
                
    finally:
        if os.path.exists(logo_path):
            os.remove(logo_path)


def demonstrate_global_language_setting():
    """Demonstrate setting global language."""
    print("\n" + "="*60)
    print("DEMONSTRATING GLOBAL LANGUAGE SETTING")
    print("="*60)
    
    # Set global language to Spanish
    set_global_language(Language.SPANISH)
    
    # Now all text strings will default to Spanish
    text_strings = get_text_strings()
    print(f"✓ Global language set to Spanish")
    print(f"✓ Default instructions title: {text_strings.get('instructions_title')}")
    print(f"✓ Default answer sheet title: {text_strings.get('answer_sheet_title')}")
    
    # Reset to English
    set_global_language(Language.ENGLISH)
    text_strings = get_text_strings()
    print(f"✓ Global language reset to English")
    print(f"✓ Default instructions title: {text_strings.get('instructions_title')}")
    print(f"✓ Default answer sheet title: {text_strings.get('answer_sheet_title')}")


def main():
    """Run internationalization demonstration."""
    print("🌍 EXAM GENERATOR - INTERNATIONALIZATION DEMO")
    print("Demonstrating English and Spanish header support")
    
    try:
        # Demonstrate English exam
        english_files = demonstrate_english_exam()
        
        # Demonstrate Spanish exam  
        spanish_files = demonstrate_spanish_exam()
        
        # Demonstrate global language setting
        demonstrate_global_language_setting()
        
        print("\n" + "="*60)
        print("🎉 INTERNATIONALIZATION DEMO COMPLETE!")
        print("="*60)
        print("✅ English exam generated with English headers")
        print("✅ Spanish exam generated with Spanish headers")
        print("✅ Both exams have proper localized text for:")
        print("   - Student/Alumno labels")
        print("   - Date/Fecha labels")
        print("   - Instructions/Instrucciones text")
        print("   - Answer Sheet/Hoja de Respuestas titles")
        print("   - Grade/Calificación labels")
        print("✅ Global language setting works correctly")
        print("="*60)
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())