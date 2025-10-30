# -*- coding: utf-8 -*-
"""
ExamGenerator - A Python library for generating professional multiple-choice exam PDFs.

This library provides an easy-to-use interface for creating formatted exams with:
- Multiple choice questions with customizable options
- Professional PDF layout with headers and answer sheets
- QR codes with encrypted answer keys
- Password-protected answer key generation
- Unicode and special character support
- Builder pattern for easy configuration
- Public encryption/decryption utilities
"""

from .core import ExamGenerator
from .config import ExamConfig, ExamConfigBuilder
from .exceptions import (
    ExamGeneratorError, 
    InvalidQuestionFormatError,
    ConfigurationError,
    FileGenerationError,
    EncryptionError
)
from .encryption import (
    encrypt_answer_data,
    decrypt_answer_data,
    parse_decrypted_qr_data,
    decrypt_qr_code,
    AnswerKeyEncryption
)

__version__ = "1.0.1"
__author__ = "Antonio Aguilar"
__email__ = "jaguilar992@gmail.com"

__all__ = [
    # Core classes
    "ExamGenerator", 
    "ExamConfig",
    "ExamConfigBuilder",
    
    # Exceptions
    "ExamGeneratorError", 
    "InvalidQuestionFormatError",
    "ConfigurationError",
    "FileGenerationError", 
    "EncryptionError",
    
    # Encryption utilities (public API)
    "encrypt_answer_data",
    "decrypt_answer_data", 
    "parse_decrypted_qr_data",
    "decrypt_qr_code",
    "AnswerKeyEncryption"
]