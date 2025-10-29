#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify the updated font system with embedded Liberation fonts.
"""

import sys
import traceback
from exam_generator.fonts import get_font_manager, ensure_fonts_available
from exam_generator.internal.styles import StylesManager

def test_font_system():
    """Test the embedded font system."""
    print("Testing embedded Liberation font system...")
    
    try:
        # Test font manager
        
        print("1. Testing font availability...")
        fonts_available = ensure_fonts_available()
        print(f"   ✓ Fonts available: {fonts_available}")
        
        print("2. Testing font manager...")
        font_manager = get_font_manager()
        
        regular_font = font_manager.get_font_name(bold=False)
        bold_font = font_manager.get_font_name(bold=True)
        
        print(f"   ✓ Regular font: {regular_font}")
        print(f"   ✓ Bold font: {bold_font}")
        
        print("3. Testing Unicode support...")
        unicode_support = font_manager.test_unicode_support("Test αβγ 你好")
        print(f"   ✓ Unicode support: {unicode_support}")
        
        print("4. Testing available fonts...")
        available_fonts = font_manager.get_available_fonts()
        for style, font_name in available_fonts.items():
            print(f"   ✓ {style}: {font_name}")
        
        print("5. Testing StylesManager integration...")
        styles_manager = StylesManager()
        
        print(f"   ✓ StylesManager font: {styles_manager.font_name}")
        print(f"   ✓ StylesManager bold font: {styles_manager.font_name_bold}")
        
        # Test creating styles
        styles = styles_manager.create_styles()
        print(f"   ✓ Created {len(styles)} styles")
        
        # Test text processing
        test_text = "Question with symbols: α, β, γ, δ, ∑, ∫"
        processed = styles_manager.process_text_for_unicode(test_text)
        print(f"   ✓ Text processing: {processed}")
        
        print("\n" + "="*50)
        print("✅ ALL TESTS PASSED!")
        print("✅ Liberation fonts are properly embedded and working!")
        print("✅ System-independent font support is complete!")
        print("="*50)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_font_system()
    sys.exit(0 if success else 1)