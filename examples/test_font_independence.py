#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify font independence functionality.
"""

import os
import sys
import tempfile
import traceback
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from exam_generator import ExamGenerator, ExamConfigBuilder
from exam_generator.fonts import ensure_fonts_available, get_font_manager
from exam_generator.internal.styles import StylesManager

def test_font_independence():
    """Test the font independence system."""
    print("Testing font independence system...")
    
    # Download fonts if needed
    try:
        ensure_fonts_available()
        print("✓ Fonts are available")
    except Exception as e:
        print(f"✗ Font setup failed: {e}")
        return False
    
    # Test font manager
    try:
        font_manager = get_font_manager()
        
        regular_font = font_manager.get_font_name(bold=False)
        bold_font = font_manager.get_font_name(bold=True)
        
        print(f"✓ Regular font: {regular_font}")
        print(f"✓ Bold font: {bold_font}")
        
        # Test Unicode support
        test_result = font_manager.test_unicode_support("Test αβγ 你好")
        print(f"✓ Unicode test result: {test_result}")
        
    except Exception as e:
        print(f"✗ Font manager test failed: {e}")
        return False
    
    # Test styles manager
    try:
        styles_manager = StylesManager()
        
        print(f"✓ StylesManager initialized with font: {styles_manager.font_name}")
        
        # Create styles
        styles = styles_manager.create_styles()
        print(f"✓ Created {len(styles)} styles")
        
        # Test text processing
        test_text = "Question with symbols: α, β, γ, δ"
        processed = styles_manager.process_text_for_unicode(test_text)
        print(f"✓ Text processing: {processed}")
        
    except Exception as e:
        print(f"✗ StylesManager test failed: {e}")
        return False
    
    # Test exam generation with embedded fonts
    try:
        # Create a temporary logo
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as logo_file:
            # Create a simple 1x1 pixel PNG
            logo_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\x0cIDATx\x9cc\xf8\x00\x00\x00\x01\x00\x01\x00\x00\x00\x00\x7f\x1d\xf6\x00\x00\x00\x00IEND\xaeB`\x82'
            logo_file.write(logo_data)
            logo_path = logo_file.name
        
        try:
            # Create exam config with embedded fonts
            config = (ExamConfigBuilder()
                     .logo(logo_path)
                     .institute("Test Institute")
                     .course("Test Course")
                     .class_subject("Test Subject")
                     .professor("Test Professor")
                     .exam_period("Exam with Embedded Fonts - Test Date")
                     .password("test2024")
                     .build())
            
            # Create exam generator
            generator = ExamGenerator(config)
            
            # Test questions with Unicode
            questions_content = """
- What is the symbol for alpha?
α
β
γ
δ

- Question with mathematics: ∑ x²
Sum
Integral
Derivative
Limit
"""
            
            # Generate exam
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as output_file:
                generator.generate_exam(questions_content, output_file.name)
                print(f"✓ Exam generated successfully: {output_file.name}")
                
                # Check file size
                file_size = os.path.getsize(output_file.name)
                print(f"✓ PDF file size: {file_size} bytes")
                
                return True
                
        finally:
            # Cleanup temporary files
            try:
                os.unlink(logo_path)
                if 'output_file' in locals():
                    os.unlink(output_file.name)
            except:
                pass
                
    except Exception as e:
        print(f"✗ Exam generation test failed: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("TESTING FONT INDEPENDENCE SYSTEM")
    print("=" * 50)
    
    success = test_font_independence()
    
    print("=" * 50)
    if success:
        print("✓ ALL TESTS PASSED - Font independence working!")
    else:
        print("✗ TESTS FAILED - Check error messages above")
    print("=" * 50)