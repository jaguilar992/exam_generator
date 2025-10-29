# ExamGenerator Examples

This folder contains usage examples for the ExamGenerator library.

## Example Files

### `example_builder.py`
Basic example showing the use of the Builder pattern to configure and generate exams.
- Configuration using `ExamConfigBuilder`
- Generation of student and answer PDFs
- Usage of public encryption API

### `complete_example.py`
Complete and detailed example demonstrating all library features.
- Advanced configuration with Builder pattern
- Support for Unicode characters and mathematical symbols
- PDF generation with embedded fonts
- Public encryption API demonstration
- Temporary file handling

### `test_embedded_fonts.py`
Test script to verify the embedded fonts system.
- Testing of `EmbeddedFontManager`
- Liberation Sans fonts verification
- Unicode support testing
- Integration with `StylesManager`

### `test_font_independence.py`
Complete test script for the font independence system.
- Font download and configuration testing
- Test PDF generation
- Consistent rendering verification

## How to Run the Examples

From the project root directory:

```bash
# Basic example
python examples/example_builder.py

# Complete example 
python examples/complete_example.py

# Embedded fonts test
python examples/test_embedded_fonts.py

# Font independence test
python examples/test_font_independence.py
```

## Notes

- All examples require a PNG logo file to function
- Examples create temporary files that are automatically cleaned up
- Test scripts verify that the font system works correctly