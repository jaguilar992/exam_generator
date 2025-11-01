# -*- coding: utf-8 -*-
"""
Main ExamGenerator class - the public API for the library.
"""

import atexit
import os
import tempfile
from typing import List, Dict, Any, Optional

import qrcode
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate

from .config import ExamConfig, ExamConfigBuilder
from .exceptions import ExamGeneratorError, FileGenerationError
from .i18n import get_text_strings
from .internal.question_parser import QuestionParser
from .internal.encryption import encrypt_answer_data
from .internal.pdf_builder import PDFBuilder


class ExamGenerator:
    """
    Main class for generating professional multiple-choice exam PDFs.
    
    This is the primary interface for the exam generator library.
    All functionality is accessed through this class.
    """
    
    @staticmethod
    def builder() -> ExamConfigBuilder:
        """
        Create a new ExamConfigBuilder for fluent configuration.
        
        Returns:
            ExamConfigBuilder: Builder instance for creating configuration
        """
        return ExamConfigBuilder()
    
    def __init__(
        self,
        config: ExamConfig,
        shuffle_options: bool = True,
        max_questions: int = 25
    ):
        """
        Initialize the exam generator.
        
        Args:
            config (ExamConfig): Exam configuration
            shuffle_options (bool): Whether to shuffle answer options
            max_questions (int): Maximum number of questions to include
        
        Raises:
            ExamGeneratorError: If configuration is invalid
        """
        if not isinstance(config, ExamConfig):
            raise ExamGeneratorError("config must be an instance of ExamConfig")
        
        self.config = config
        self.shuffle_options = shuffle_options
        self.max_questions = max(1, min(max_questions, 50))  # Reasonable limits
        
        # Initialize internal components
        self.question_parser = QuestionParser(shuffle_options)
        self.pdf_builder = None  # Initialized when needed
        
        # Cache for parsed questions to ensure consistency
        self._parsed_questions = None
        self._qr_data = None
        self._qr_image_path = None
        self._temp_files = []  # Track all temporary files for cleanup
        
        # Register cleanup on exit
        atexit.register(self.cleanup)
    
    def load_questions_from_file(self, file_path: str) -> 'ExamGenerator':
        """
        Load questions from a file.
        
        Args:
            file_path (str): Path to question file
            
        Returns:
            ExamGenerator: Self for method chaining
            
        Raises:
            ExamGeneratorError: If file cannot be read or parsed
        """
        try:
            questions = self.question_parser.parse_from_file(file_path)
            self._set_questions(questions)
            return self
        except Exception as e:
            raise ExamGeneratorError(f"Failed to load questions from {file_path}: {str(e)}")
    
    def load_questions_from_string(self, content: str) -> 'ExamGenerator':
        """
        Load questions from string content.
        
        Args:
            content (str): Question content in .ptf format
            
        Returns:
            ExamGenerator: Self for method chaining
            
        Raises:
            ExamGeneratorError: If content cannot be parsed
        """
        try:
            questions = self.question_parser.parse_from_string(content)
            self._set_questions(questions)
            return self
        except Exception as e:
            raise ExamGeneratorError(f"Failed to parse questions: {str(e)}")
    
    def set_questions(self, questions: List[Dict[str, Any]]) -> 'ExamGenerator':
        """
        Set questions directly.
        
        Args:
            questions (List[Dict[str, Any]]): List of question dictionaries
                Each question should have: 'question', 'options', 'correct_answer'
            
        Returns:
            ExamGenerator: Self for method chaining
            
        Raises:
            ExamGeneratorError: If questions format is invalid
        """
        try:
            self._validate_questions(questions)
            self._set_questions(questions)
            return self
        except Exception as e:
            raise ExamGeneratorError(f"Invalid questions format: {str(e)}")
    
    def generate_student_exam(self, output_path: str) -> str:
        """
        Generate the student exam PDF.
        
        Args:
            output_path (str): Path for output PDF file
            
        Returns:
            str: Path to generated PDF
            
        Raises:
            FileGenerationError: If PDF generation fails
        """
        if not self._parsed_questions:
            raise ExamGeneratorError("No questions loaded. Call load_questions_* first.")
        
        try:
            self._ensure_pdf_builder()
            
            doc = SimpleDocTemplate(
                output_path,
                pagesize=letter,
                rightMargin=self.pdf_builder.margin,
                leftMargin=self.pdf_builder.margin,
                topMargin=self.pdf_builder.margin,
                bottomMargin=self.pdf_builder.margin
            )
            
            story = self.pdf_builder.build_student_exam_story(
                self._parsed_questions,
                self.config,
                self._get_qr_image_path()
            )
            
            doc.build(story)
            return output_path
            
        except Exception as e:
            raise FileGenerationError(f"Failed to generate student exam: {str(e)}")
    
    def generate_answer_key(self, output_path: str) -> str:
        """
        Generate the password-protected answer key PDF.
        
        Args:
            output_path (str): Path for output PDF file
            
        Returns:
            str: Path to generated PDF
            
        Raises:
            FileGenerationError: If PDF generation fails
        """
        if not self._parsed_questions:
            raise ExamGeneratorError("No questions loaded. Call load_questions_* first.")
        
        try:
            self._ensure_pdf_builder()
            
            # Create answer key config
            answer_key_config = self._create_answer_key_config()
            
            doc = SimpleDocTemplate(
                output_path,
                pagesize=letter,
                rightMargin=self.pdf_builder.margin,
                leftMargin=self.pdf_builder.margin,
                topMargin=self.pdf_builder.margin,
                bottomMargin=self.pdf_builder.margin
            )
            
            story = self.pdf_builder.build_answer_key_story(
                self._parsed_questions,
                answer_key_config,
                self._get_qr_image_path()
            )
            
            # Set up PDF encryption
            def apply_encryption(canvas, doc):
                canvas.setEncrypt(self.config.password)
            
            doc.build(story, onFirstPage=apply_encryption, onLaterPages=apply_encryption)
            return output_path
            
        except Exception as e:
            raise FileGenerationError(f"Failed to generate answer key: {str(e)}")
    
    def generate_both(self, student_path: str, answer_key_path: str) -> tuple[str, str]:
        """
        Generate both student exam and answer key PDFs.
        
        Args:
            student_path (str): Path for student exam PDF
            answer_key_path (str): Path for answer key PDF
            
        Returns:
            tuple[str, str]: Paths to generated PDFs (student, answer_key)
        """
        student_file = self.generate_student_exam(student_path)
        answer_key_file = self.generate_answer_key(answer_key_path)
        return student_file, answer_key_file
    
    def get_question_count(self) -> int:
        """
        Get the number of loaded questions.
        
        Returns:
            int: Number of questions
        """
        return len(self._parsed_questions) if self._parsed_questions else 0
    
    def get_questions_preview(self) -> List[Dict[str, Any]]:
        """
        Get a preview of loaded questions (without answers).
        
        Returns:
            List[Dict[str, Any]]: List of questions for preview
        """
        if not self._parsed_questions:
            return []
        
        return [
            {
                'question': q['question'],
                'options': q['options']
            }
            for q in self._parsed_questions
        ]
    
    def cleanup(self) -> None:
        """Clean up all temporary files."""
        # Clean up QR image
        if self._qr_image_path and os.path.exists(self._qr_image_path):
            try:
                os.remove(self._qr_image_path)
                self._qr_image_path = None
            except Exception:
                pass  # Ignore cleanup errors
        
        # Clean up all tracked temporary files
        for temp_file in self._temp_files[:]:  # Copy list to avoid modification during iteration
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                    self._temp_files.remove(temp_file)
                except Exception:
                    pass  # Ignore cleanup errors
    
    def _track_temp_file(self, file_path: str) -> str:
        """Track a temporary file for cleanup."""
        if file_path not in self._temp_files:
            self._temp_files.append(file_path)
        return file_path
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup."""
        self.cleanup()
    
    def _set_questions(self, questions: List[Dict[str, Any]]) -> None:
        """Set and limit questions."""
        limited_questions = questions[:self.max_questions]
        self._parsed_questions = limited_questions
        
        # Clear cached data since questions changed
        self._qr_data = None
        if self._qr_image_path:
            self.cleanup()
    
    def _validate_questions(self, questions: List[Dict[str, Any]]) -> None:
        """Validate questions format."""
        if not isinstance(questions, list):
            raise ValueError("Questions must be a list")
        
        if not questions:
            raise ValueError("Questions list cannot be empty")
        
        for i, question in enumerate(questions):
            if not isinstance(question, dict):
                raise ValueError(f"Question {i+1} must be a dictionary")
            
            required_keys = ['question', 'options', 'correct_answer']
            for key in required_keys:
                if key not in question:
                    raise ValueError(f"Question {i+1} missing required key: {key}")
            
            if not isinstance(question['options'], list):
                raise ValueError(f"Question {i+1} options must be a list")
            
            if len(question['options']) < 2:
                raise ValueError(f"Question {i+1} must have at least 2 options")
            
            correct_idx = question['correct_answer']
            if not isinstance(correct_idx, int) or not (0 <= correct_idx < len(question['options'])):
                raise ValueError(f"Question {i+1} has invalid correct_answer index")
    
    def _ensure_pdf_builder(self) -> None:
        """Initialize PDF builder if needed."""
        if self.pdf_builder is None:
            page_width, page_height = letter
            margin = 0.7 * cm  # 0.7 cm margins
            content_width = page_width - 2 * margin
            self.pdf_builder = PDFBuilder(content_width, margin)
    
    def _get_qr_data(self) -> str:
        """Get or generate QR data."""
        if self._qr_data is None:
            correct_answers = [q['correct_answer'] for q in self._parsed_questions]
            answer_letters = ''.join([chr(65 + answer) for answer in correct_answers])
            
            plain_data = f"Q{len(self._parsed_questions)}_P{self.config.total}_{answer_letters}"
            self._qr_data = encrypt_answer_data(plain_data, self.config.password)
        
        return self._qr_data
    
    def _get_qr_image_path(self) -> Optional[str]:
        """Get or generate QR code image."""
        if self._qr_image_path is None:
            qr_data = self._get_qr_data()
            
            # Generate QR code image
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=3,
                border=1,
            )
            qr.add_data(qr_data)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                img.save(tmp.name)
                self._qr_image_path = self._track_temp_file(tmp.name)
        
        return self._qr_image_path
    
    def _create_answer_key_config(self) -> ExamConfig:
        """Create configuration for answer key."""
        # Create a copy with modified student name for answer key
        config_dict = self.config.to_dict()
        # Use localized answer key student name
        text_strings = get_text_strings(config_dict.get('language'))
        config_dict['student_name'] = text_strings.get('answer_key_student_name')
        return ExamConfig.from_dict(config_dict)