# -*- coding: utf-8 -*-
"""
Custom exceptions for the ExamGenerator library.
"""


class ExamGeneratorError(Exception):
    """Base exception class for ExamGenerator errors."""
    pass


class InvalidQuestionFormatError(ExamGeneratorError):
    """Raised when question file format is invalid."""
    pass


class ConfigurationError(ExamGeneratorError):
    """Raised when configuration parameters are invalid."""
    pass


class FileGenerationError(ExamGeneratorError):
    """Raised when PDF file generation fails."""
    pass


class EncryptionError(ExamGeneratorError):
    """Raised when encryption/decryption operations fail."""
    pass