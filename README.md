# ExamGenerator

A Python library for generating professional multiple-choice exam PDFs with advanced features like QR-coded answer keys, password protection, and Unicode support.

## Features

- **Professional PDF Layout**: Clean, standardized exam format with institutional headers
- **Answer Sheet Generation**: Bubble-style answer sheets for optical scanning
- **QR Code Integration**: Encrypted answer keys embedded in QR codes
- **Password Protection**: Secure answer key PDFs with password encryption
- **Unicode Support**: Full support for special characters and international text
- **System-Independent Fonts**: Uses embedded Liberation fonts for consistent rendering across platforms
- **Internationalization**: Built-in support for English and Spanish headers and instructions
- **Flexible Question Input**: Support for file-based or programmatic question input
- **Option Shuffling**: Automatic randomization of answer choices
- **Two-Column Layout**: Efficient use of page space

## Installation

### From Source

```bash
git clone <repository-url>
cd exam-generator
pip install -e .
```

### Dependencies

The library requires:
- `reportlab>=4.0.0` - PDF generation
- `pillow>=10.0.0` - Image processing  
- `qrcode>=7.0.0` - QR code generation

### Font System

The library uses embedded **Liberation Sans** fonts to ensure consistent rendering across all platforms, regardless of system-installed fonts. The fonts are automatically downloaded and managed by the library.

#### Automatic Font Setup

On first use, the library will automatically download the required fonts:

```python
from exam_generator.fonts import ensure_fonts_available

# This is called automatically, but you can call it explicitly
ensure_fonts_available()
```

#### Font Features

- **System Independence**: No dependency on system fonts
- **Unicode Support**: Full support for international characters and mathematical symbols
- **Professional Quality**: Liberation Sans fonts are metric-compatible with Arial
- **Automatic Fallback**: Graceful degradation if fonts are unavailable

#### Manual Font Installation

To manually download fonts (optional):

```bash
cd exam-generator
python setup_fonts.py
```

This creates a `src/exam_generator/fonts/` directory with the required font files.

## Quick Start

```python
from exam_generator import ExamGenerator, Language

# Configure using Builder pattern (recommended)
config = (ExamGenerator.builder()
         .institute("Technical Superior Institute")
         .course("Computer Science Bachelor III")
         .class_subject("World Geography")
         .professor("John Smith")
         .password("exam2024")
         .logo("path/to/logo.png")  # Required!
         .language(Language.ENGLISH)  # English (default) or Spanish
         .total_points(100)
         .build())

# Create generator
with ExamGenerator(config, shuffle_options=True) as generator:
    # Load questions from file
    generator.load_questions_from_file("questions.ptf")
    
    # Generate both student exam and answer key
    student_pdf, answer_key_pdf = generator.generate_both(
        "exam_student.pdf",
        "exam_answer_key.pdf"
    )
    
    print(f"Generated: {student_pdf} and {answer_key_pdf}")
```

## Question File Format

Questions should be in `.ptf` format:

```
- What is the capital of Germany?
Berlin
Munich  
Frankfurt
Hamburg

- What is the capital of France?
Paris
Lyon
Nice
Marseille
```

**Format Rules:**
- Each question starts with `- ` (dash and space)
- First line after dash is the question text
- Next 2-4 lines are the answer options
- **The first option is always the correct answer**
- Empty lines are ignored

## Internationalization Support

The library supports English and Spanish headers and instructions. By default, all text appears in English, but you can easily switch to Spanish or create custom text strings.

### Supported Languages

- **English** (default): All headers, instructions, and labels in English
- **Spanish**: All headers, instructions, and labels in Spanish

### Setting Language

```python
from exam_generator import ExamGenerator, Language

# English exam (default)
config = (ExamGenerator.builder()
         .institute("Technical Institute")
         .course("Computer Science")
         .class_subject("Programming")
         .professor("Dr. Smith")
         .password("exam2024")
         .logo("logo.png")
         .language(Language.ENGLISH)  # Explicit English
         .build())

# Spanish exam
config = (ExamGenerator.builder()
         .institute("Instituto Técnico")
         .course("Ciencias de la Computación")
         .class_subject("Programación")
         .professor("Dr. González")
         .password("examen2024")
         .logo("logo.png")
         .language(Language.SPANISH)  # Spanish headers
         .build())
```

### What Gets Translated

When you set the language, the following elements are automatically localized:

| Element | English | Spanish |
|---------|---------|---------|
| Student field | "Student:" | "Alumno:" |
| Course field | "Course:" | "Curso:" |
| Class field | "Class:" | "Clase:" |
| Professor field | "Professor:" | "Profesor:" |
| Date field | "Date:" | "Fecha:" |
| List number field | "#List:" | "#Lista:" |
| Grade box | "Grade" | "Calificación" |
| Points value | "Value: X pts" | "Valor: X pts" |
| Instructions title | "INSTRUCTIONS:" | "INSTRUCCIONES:" |
| Answer sheet title | "ANSWER SHEET" | "HOJA DE RESPUESTAS" |
| Answer key label | "ANSWER KEY - ANSWER SHEET" | "PAUTA - HOJA DE RESPUESTAS" |

### Instructions Text

The instructions text is also fully localized:

**English:**
> "Read each question carefully and select the correct answer by completely filling in the corresponding circle. Use only pencil No. 2 or blue or black pen."

**Spanish:**
> "Lea cuidadosamente cada pregunta y seleccione la respuesta correcta rellenando completamente el círculo correspondiente. Use únicamente lápiz No. 2 o bolígrafo azul o negro."

### Global Language Setting

You can also set a global default language for all exams:

```python
from exam_generator import set_global_language, Language

# Set Spanish as global default
set_global_language(Language.SPANISH)

# Now all exams will default to Spanish unless explicitly overridden
config = ExamGenerator.builder()  # Will use Spanish
    # ... other configuration

# Override for specific exam
config = ExamGenerator.builder().language(Language.ENGLISH)  # Force English
    # ... other configuration
```

### Custom Text Strings

For advanced use cases, you can access the text strings directly:

```python
from exam_generator import get_text_strings, Language

# Get English text strings
english_texts = get_text_strings(Language.ENGLISH)
print(english_texts.get('student_label'))  # "Student"

# Get Spanish text strings
spanish_texts = get_text_strings(Language.SPANISH)
print(spanish_texts.get('student_label'))  # "Alumno"

# Format points text
points_text = english_texts.get_points_text(100)  # "Value: 100 pts"
```

## Configuration Options

### Builder Pattern (Recommended)

```python
config = (ExamGenerator.builder()
         .institute("Your Institution")        # Required
         .course("Course Name")                # Required  
         .class_subject("Subject Name")        # Required
         .professor("Professor Name")          # Required
         .password("your_password")            # Required
         .logo("/path/to/logo.png")           # Required
         .student("Student Name")              # Optional
         .section("Section A")                 # Optional
         .exam_period("Final Exam 2024")      # Optional
         .total_points(100)                    # Optional, defaults to 100
         .year(2024)                          # Optional, defaults to current year
         .language(Language.SPANISH)          # Optional, defaults to English
         .build())
```

### Traditional Configuration (Still Supported)

```python
from exam_generator import ExamConfig

config = ExamConfig(
    institute_name="Your Institution",        # Required
    course_name="Course Name",                # Required  
    class_name="Subject Name",                # Required
    professor_name="Professor Name",          # Required
    password="your_password",                 # Required
    logo_path="/path/to/logo.png",           # Required
    student_name="Student Name",              # Optional
    course_section="Section A",               # Optional
    exam_period="Final Exam 2024",           # Optional
    total_points=100,                         # Optional, defaults to 100
    year=2024,                               # Optional, defaults to current year
    language=Language.SPANISH                # Optional, defaults to English
)
```

### ExamGenerator Options

```python
generator = ExamGenerator(
    config=config,
    shuffle_options=True,    # Randomize answer order
    max_questions=25         # Limit number of questions
)
```

## API Reference

### ExamGenerator Class

#### Methods

**`load_questions_from_file(file_path: str) -> ExamGenerator`**
- Load questions from a .ptf file
- Returns self for method chaining

**`load_questions_from_string(content: str) -> ExamGenerator`**  
- Load questions from string content
- Returns self for method chaining

**`set_questions(questions: List[Dict]) -> ExamGenerator`**
- Set questions programmatically
- Each question dict needs: `'question'`, `'options'`, `'correct_answer'`
- Returns self for method chaining

**`generate_student_exam(output_path: str) -> str`**
- Generate student exam PDF
- Returns path to created file

**`generate_answer_key(output_path: str) -> str`**
- Generate password-protected answer key PDF  
- Returns path to created file

**`generate_both(student_path: str, answer_key_path: str) -> tuple[str, str]`**
- Generate both PDFs at once
- Returns tuple of (student_pdf_path, answer_key_pdf_path)

**`get_question_count() -> int`**
- Get number of loaded questions

**`get_questions_preview() -> List[Dict]`**
- Get preview of questions (without answers)

**`cleanup()`**
- Clean up temporary files

#### Context Manager Support

```python
with ExamGenerator(config) as generator:
    # Use generator
    pass
# Automatic cleanup when exiting context
```

## Advanced Usage

### Programmatic Question Creation

```python
questions = [
    {
        'question': 'What is 2 + 2?',
        'options': ['4', '3', '5', '6'],
        'correct_answer': 0  # Index of correct option
    },
    {
        'question': 'What is the largest planet?', 
        'options': ['Jupiter', 'Saturn', 'Earth', 'Mars'],
        'correct_answer': 0
    }
]

generator.set_questions(questions)
```

### Custom Logo Integration

```python
config = ExamConfig(
    # ... other parameters ...
    logo_path="/path/to/institution_logo.png"
)
```

The logo will be automatically converted to grayscale and resized appropriately.

### QR Code Answer Keys

The generated QR codes contain encrypted answer data in the format:
```
Q{num_questions}_P{points}_{answer_letters}
```

For example: `Q25_P100_DDDBBCDDDDDAABCCAADCBAADD` (encrypted with the configured password)

### QR Code Decryption (Public API)

The library exposes encryption utilities for external use:

```python
from exam_generator import decrypt_qr_code, decrypt_answer_data, parse_decrypted_qr_data

# Decrypt QR code data (complete solution)
qr_data = "encrypted_qr_string_here"
password = "your_password"
decrypted_info = decrypt_qr_code(qr_data, password)
print(f"Questions: {decrypted_info['num_questions']}")
print(f"Answers: {decrypted_info['answer_letters']}")

# Or decrypt step by step
decrypted_text = decrypt_answer_data(qr_data, password)
parsed_data = parse_decrypted_qr_data(decrypted_text)
```

## Error Handling

The library provides specific exception types:

```python
from exam_generator.exceptions import (
    ExamGeneratorError,           # Base exception
    InvalidQuestionFormatError,   # Question parsing errors
    ConfigurationError,           # Configuration errors  
    FileGenerationError,          # PDF generation errors
    EncryptionError              # Encryption errors
)

try:
    generator.load_questions_from_file("questions.ptf")
except InvalidQuestionFormatError as e:
    print(f"Question format error: {e}")
except FileNotFoundError as e:
    print(f"File not found: {e}")
```

## Project Structure

```
exam_generator/
├── src/exam_generator/          # Main library package
│   ├── fonts/                   # Embedded Liberation fonts
│   ├── internal/                # Internal implementation modules
│   ├── __init__.py             # Public API exports
│   ├── core.py                 # ExamGenerator main class
│   ├── config.py               # Configuration and Builder
│   ├── encryption.py           # Public encryption utilities
│   └── fonts.py                # Font management system
├── examples/                    # Usage examples and tests
│   ├── example_builder.py       # Basic Builder pattern example
│   ├── complete_example.py      # Comprehensive example
│   ├── test_embedded_fonts.py   # Font system tests
│   └── test_font_independence.py # Font independence tests
├── legacy/                      # Original project files (archived)
├── capitals.ptf                 # Sample question file
├── requirements.txt             # Dependencies
├── setup.py                     # Package configuration
└── README.md                    # This file
```

## Examples

> 📁 **More examples available in the `examples/` directory**

### Basic Example with Builder Pattern

```python
from exam_generator import ExamGenerator

# Simple configuration using Builder
config = (ExamGenerator.builder()
         .institute("My School")
         .course("Mathematics Course")
         .class_subject("Algebra I")
         .professor("Dr. Smith")
         .password("math2024")
         .logo("school_logo.png")
         .build())

# Generate exam
with ExamGenerator(config) as generator:
    generator.load_questions_from_file("math_questions.ptf")
    student_pdf, answer_pdf = generator.generate_both(
        "math_exam.pdf", 
        "math_answers.pdf"
    )
```

### Advanced Example with Builder Pattern

```python
from exam_generator import ExamGenerator

# Detailed configuration using Builder
config = (ExamGenerator.builder()
         .institute("Advanced Technical Institute")
         .course("Computer Science Degree Program")
         .class_subject("Data Structures and Algorithms")
         .professor("Dr. María González")
         .section("Section B - Evening")
         .exam_period("Midterm Examination - Fall 2024")
         .total_points(150)
         .password("cs_midterm_2024!")
         .logo("./assets/institute_logo.png")
         .year(2024)
         .build())

# Create generator with custom settings
with ExamGenerator(config, shuffle_options=True, max_questions=30) as gen:
    # Load and validate questions
    gen.load_questions_from_file("algorithms_questions.ptf")
    
    print(f"Loaded {gen.get_question_count()} questions")
    
    # Generate files
    student_file, answer_file = gen.generate_both(
        "algorithms_midterm_student.pdf",
        "algorithms_midterm_answers.pdf"
    )
    
    print(f"Student exam: {student_file}")
    print(f"Answer key: {answer_file}")

### Internationalization Example

```python
from exam_generator import ExamGenerator, Language

# Create Spanish exam
spanish_config = (ExamGenerator.builder()
                 .institute("Instituto Técnico Superior")
                 .course("Licenciatura en Ingeniería")
                 .class_subject("Matemáticas Avanzadas")
                 .professor("Dr. María González")
                 .section("Sección A - Turno Noche")
                 .exam_period("Examen Parcial - Otoño 2024")
                 .password("matematicas2024")
                 .logo("logo_instituto.png")
                 .language(Language.SPANISH)  # Spanish headers and instructions
                 .total_points(100)
                 .build())

# Spanish questions content
questions_spanish = """
- ¿Cuál es la derivada de f(x) = x²?
2x
x²
x
1

- ¿Cuánto es la integral ∫ 2x dx?
x² + C
2x² + C
x + C
2 + C
"""

with ExamGenerator(spanish_config) as generator:
    generator.load_questions_from_string(questions_spanish)
    student_pdf, answer_pdf = generator.generate_both(
        "examen_estudiantes.pdf",    # Spanish filenames too!
        "examen_respuestas.pdf"
    )
    print(f"Examen generado: {student_pdf}")
```

### QR Code Decryption Example

```python
from exam_generator import decrypt_qr_code

# Decrypt QR code from exam (external usage)
encrypted_qr = "h8Kx3mP9..." # QR code data
password = "cs_midterm_2024!"

try:
    answer_data = decrypt_qr_code(encrypted_qr, password)
    print(f"Exam has {answer_data['num_questions']} questions")
    print(f"Answer key: {answer_data['answer_letters']}")
    print(f"Answer indices: {answer_data['answers']}")
except Exception as e:
    print(f"Failed to decrypt: {e}")
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

For questions, issues, or contributions, please visit the project repository.