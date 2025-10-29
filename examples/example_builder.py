#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
New Builder Pattern Examples for ExamGenerator Library.
"""

import sys
import os
import traceback
from pathlib import Path

# Add src to path for development
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from exam_generator import (
    ExamGenerator,
    encrypt_answer_data, 
    decrypt_answer_data, 
    decrypt_qr_code,
    parse_decrypted_qr_data
)

def example_builder_pattern():
    """Demonstrate the new Builder pattern."""
    print("🏗️  New Builder Pattern Example")
    print("-" * 40)
    
    # Create a test logo
    logo_path = "test_logo.png"
    create_dummy_logo(logo_path)
    
    try:
        # NEW: Use Builder pattern (fluent interface)
        config = (ExamGenerator.builder()
                 .institute("Technical Superior Institute")
                 .course("Computer Science Bachelor III")
                 .class_subject("World Geography")
                 .professor("John Smith")
                 .password("geography2024")
                 .logo(logo_path)  # Now required!
                 .total_points(100)
                 .build())
        
        print("✅ Configuration built with Builder pattern")
        
        # Use the generator
        with ExamGenerator(config) as generator:
            questions = create_sample_questions()
            generator.set_questions(questions)
            
            student_file, answer_file = generator.generate_both(
                "builder_student.pdf",
                "builder_answers.pdf"
            )
            
            print(f"✅ Generated: {student_file}")
            print(f"✅ Generated: {answer_file}")
            
    finally:
        if os.path.exists(logo_path):
            os.remove(logo_path)


def example_encryption_api():
    """Demonstrate the public encryption API."""
    print("\n🔐 Public Encryption API Example")
    print("-" * 40)
    
    # Sample data
    original_data = "Q5_P100_ABCDA"
    password = "test123"
    
    # Encrypt
    encrypted = encrypt_answer_data(original_data, password)
    print(f"✅ Encrypted: {original_data} -> {encrypted}")
    
    # Decrypt  
    decrypted = decrypt_answer_data(encrypted, password)
    print(f"✅ Decrypted: {decrypted}")
    
    # Parse decrypted QR data
    parsed = parse_decrypted_qr_data(decrypted)
    print(f"✅ Parsed QR data:")
    print(f"   Questions: {parsed['num_questions']}")
    print(f"   Points: {parsed['total_points']}")
    print(f"   Answers: {parsed['answer_letters']}")
    print(f"   Indices: {parsed['answers']}")
    
    # Complete QR decryption in one call
    complete_info = decrypt_qr_code(encrypted, password)
    print(f"✅ Complete QR decrypt: {complete_info}")


def create_sample_questions():
    """Sample questions for testing."""
    return [
        {
            'question': 'What is the capital of Spain?',
            'options': ['Madrid', 'Barcelona', 'Valencia', 'Seville'],
            'correct_answer': 0
        },
        {
            'question': 'What is the capital of France?',
            'options': ['Paris', 'Lyon', 'Marseille', 'Nice'],
            'correct_answer': 0
        },
        {
            'question': 'What is the capital of Italy?',
            'options': ['Rome', 'Milan', 'Naples', 'Florence'],
            'correct_answer': 0
        },
        {
            'question': 'What is the capital of Germany?',
            'options': ['Berlin', 'Munich', 'Frankfurt', 'Hamburg'],
            'correct_answer': 0
        },
        {
            'question': 'What is the capital of Portugal?',
            'options': ['Lisbon', 'Porto', 'Faro', 'Coimbra'],
            'correct_answer': 0
        }
    ]


def create_dummy_logo(filename):
    """Create a simple test logo."""
    # Create minimal PNG file
    with open(filename, 'wb') as f:
        # Minimal 1x1 white PNG
        f.write(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\x12IDATx\x9cc```bPPP\x00\x02D\x00\x00\x00\x0e\x00\x01\xdb\xd8\x0b\x98\x00\x00\x00\x00IEND\xaeB`\x82')


def main():
    """Run new examples."""
    print("🚀 ExamGenerator - New Builder Pattern & Encryption API")
    print("=" * 60)
    
    try:
        # Builder pattern example
        example_builder_pattern()
        
        # Encryption API example
        example_encryption_api()
        
        print("\n" + "=" * 60)
        print("🎉 All new features working correctly!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())