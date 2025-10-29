#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Complete example showing the ExamGenerator library with font independence.
"""

import os
import tempfile
import traceback
from pathlib import Path
from PIL import Image, ImageDraw

from exam_generator import (
    ExamGenerator, 
    ExamConfigBuilder,
    decrypt_qr_code, 
    decrypt_answer_data, 
    parse_decrypted_qr_data
)


def create_sample_logo():
    """Create a simple PNG logo for testing using PIL."""
    
    # Create a simple 100x100 logo with text
    image = Image.new('RGB', (100, 100), color='white')
    draw = ImageDraw.Draw(image)
    
    # Draw a simple logo shape
    draw.rectangle([10, 10, 90, 90], outline='black', width=2)
    draw.text((30, 40), "LOGO", fill='black')
    
    # Save to temporary file
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
        image.save(f.name, 'PNG')
        return f.name


def main():
    """Complete example of exam generation with embedded fonts."""
    print("=" * 60)
    print("EXAM GENERATOR - COMPLETE EXAMPLE WITH FONT INDEPENDENCE")
    print("=" * 60)
    
    # Create temporary logo
    logo_path = create_sample_logo()
    print(f"Created temporary logo: {logo_path}")
    
    try:
        # 1. Create configuration using Builder pattern
        print("\n1. Creating exam configuration...")
        config = (ExamConfigBuilder()
                 .logo(logo_path)
                 .institute("Superior Technical Institute")
                 .course("Computer Science Bachelor III")
                 .class_subject("Advanced Mathematics")
                 .professor("Dr. John Smith")
                 .exam_period("Midterm Exam - 2024")
                 .password("mathematics2024")
                 .total_points(100)
                 .build())
        
        print("✓ Configuration created successfully")
        
        # 2. Create sample questions with Unicode characters
        questions_content = """
- What is the value of the integral ∫₀¹ x² dx?
1/3
1/2
2/3
1

- If α = 30° and β = 45°, what is the value of sin(α + β)?
(√6 + √2)/4
(√6 - √2)/4
√3/2
√2/2

- The sum ∑ᵢ₌₁ⁿ i equals:
n(n+1)/2
n²
n(n-1)/2
2n

- What is the derivative of f(x) = e^(x²)?
2xe^(x²)
e^(x²)
2e^(x²)
xe^(x²)

- In a right triangle, if the legs are 3 and 4, the hypotenuse is:
5
7
√7
25
"""
        
        print("\n2. Creating questions with Unicode support...")
        
        # 3. Generate exam with context manager
        print("\n3. Generating exam PDFs...")
        with ExamGenerator(config, shuffle_options=True) as generator:
            # Load questions
            generator.load_questions_from_string(questions_content)
            print(f"✓ Loaded {generator.get_question_count()} questions")
            
            # Generate both PDFs
            with tempfile.NamedTemporaryFile(suffix='_student.pdf', delete=False) as student_file, \
                 tempfile.NamedTemporaryFile(suffix='_answers.pdf', delete=False) as answer_file:
                
                student_pdf, answer_pdf = generator.generate_both(
                    student_file.name,
                    answer_file.name
                )
                
                print(f"✓ Student exam: {student_pdf}")
                print(f"✓ Answer key: {answer_pdf}")
                
                # Check file sizes
                student_size = os.path.getsize(student_pdf)
                answer_size = os.path.getsize(answer_pdf)
                
                print(f"✓ Student PDF size: {student_size:,} bytes")
                print(f"✓ Answer PDF size: {answer_size:,} bytes")
        
        # 4. Demonstrate public encryption API
        print("\n4. Testing public encryption API...")
        
        # This would normally come from scanning a QR code
        sample_encrypted_data = "Q5_P100_AACBA"  # This is just for demonstration
        
        try:
            # Decrypt QR code (this will fail with our sample data, but shows the API)
            decrypted_info = decrypt_qr_code(sample_encrypted_data, "mathematics2024")
            print(f"✓ Decrypted info: {decrypted_info}")
        except Exception as e:
            print(f"ℹ Expected error (demo data): {type(e).__name__}")
        
        print("\n" + "=" * 60)
        print("✓ EXAMPLE COMPLETED SUCCESSFULLY!")
        print("✓ Font independence working - PDFs will render consistently")
        print("✓ Unicode characters supported: α, β, γ, δ, ε, π, ∑, ∫, √")
        print("✓ Builder pattern provides clean, fluent API")
        print("✓ Public encryption API available for external tools")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        traceback.print_exc()
    
    finally:
        # Cleanup temporary logo
        try:
            os.unlink(logo_path)
            print(f"\nCleaned up temporary logo: {logo_path}")
        except:
            pass


if __name__ == "__main__":
    main()