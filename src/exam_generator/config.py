# -*- coding: utf-8 -*-
"""
Configuration classes for ExamGenerator with Builder pattern.
"""

import datetime
import os
from typing import Optional
from .exceptions import ConfigurationError
from .i18n import Language, get_text_strings


class ExamConfig:
    """
    Configuration class for exam generation.
    
    This class holds all the configuration parameters needed to generate an exam,
    without any hardcoded values. All parameters must be provided by the user.
    """
    
    def __init__(
        self,
        institute_name: str,
        course_name: str,
        class_name: str,
        professor_name: str,
        student_name: Optional[str] = None,
        course_section: Optional[str] = None,
        exam_period: Optional[str] = None,
        total_points: int = 100,
        password: str = "default_password",
        logo_path: Optional[str] = None,
        year: Optional[int] = None,
        language: Language = Language.ENGLISH
    ):
        """
        Initialize exam configuration.
        
        Args:
            institute_name (str): Name of the educational institution
            course_name (str): Name of the course (e.g., "I de Bachillerato Técnico en Informática")
            class_name (str): Name of the specific class/subject
            professor_name (str): Name of the professor
            student_name (str, optional): Student name field content. If None, will be blank line
            course_section (str, optional): Course section. If None, will be blank line
            exam_period (str, optional): Exam period. If None, will use "I Parcial {year}"
            total_points (int): Total points for the exam (default: 100)
            password (str): Password for answer key encryption (default: "default_password")
            logo_path (str, optional): Path to institution logo image file
            year (int, optional): Year for the exam. If None, uses current year
            language (Language): Language for headers and instructions (default: English)
        
        Raises:
            ConfigurationError: If required parameters are missing or invalid
        """
        # Validate required parameters
        if not institute_name or not isinstance(institute_name, str):
            raise ConfigurationError("institute_name is required and must be a string")
        if not course_name or not isinstance(course_name, str):
            raise ConfigurationError("course_name is required and must be a string")
        if not class_name or not isinstance(class_name, str):
            raise ConfigurationError("class_name is required and must be a string")
        if not professor_name or not isinstance(professor_name, str):
            raise ConfigurationError("professor_name is required and must be a string")
        if not isinstance(total_points, int) or total_points <= 0:
            raise ConfigurationError("total_points must be a positive integer")
        if not password or not isinstance(password, str):
            raise ConfigurationError("password is required and must be a string")
        if not logo_path or not isinstance(logo_path, str):
            raise ConfigurationError("logo_path is required and must be a string")
        if not os.path.exists(logo_path):
            raise ConfigurationError(f"Logo file does not exist: {logo_path}")
        
        # Set core parameters
        self.institute_name = institute_name.strip()
        self.course = course_name.strip()
        self.language = language
        
        # Get text strings for the specified language
        text_strings = get_text_strings(language)
        
        self.class_name = f"{text_strings.get_label_with_colon('class_label')} {class_name.strip()}"
        self.professor_name = f"{text_strings.get_label_with_colon('professor_label')} {professor_name.strip()}"
        
        # Set optional parameters with defaults
        self.year = year if year is not None else datetime.datetime.now().year
        
        if student_name is not None:
            self.student_name = f"{text_strings.get_label_with_colon('student_label')} {student_name.strip()}"
        else:
            self.student_name = text_strings.get('student_name_blank')
        
        if course_section is not None:
            self.course_section = f"{text_strings.get_label_with_colon('course_label')} {course_section.strip()}"
        else:
            self.course_section = text_strings.get('course_section_blank')
        
        if exam_period is not None:
            self.exam_period = exam_period.strip()
        else:
            # Default exam period based on language
            if language == Language.SPANISH:
                self.exam_period = f"I Parcial {self.year}"
            else:
                self.exam_period = f"Midterm Exam {self.year}"
        
        self.total = total_points
        self.test_value = text_strings.get_points_text(self.total)
        self.password = password.strip()
        self.logo_path = logo_path.strip()
    
    def validate(self) -> None:
        """
        Validate the configuration parameters.
        
        Raises:
            ConfigurationError: If any parameter is invalid
        """
        if self.logo_path and not isinstance(self.logo_path, str):
            raise ConfigurationError("logo_path must be a string if provided")
        
        if self.year < 1900 or self.year > 2100:
            raise ConfigurationError("year must be between 1900 and 2100")
    
    def to_dict(self) -> dict:
        """
        Convert configuration to dictionary.
        
        Returns:
            dict: Configuration as dictionary
        """
        return {
            'institute_name': self.institute_name,
            'course': self.course,
            'class_name': self.class_name,
            'professor_name': self.professor_name,
            'student_name': self.student_name,
            'course_section': self.course_section,
            'exam_period': self.exam_period,
            'total': self.total,
            'test_value': self.test_value,
            'password': self.password,
            'logo_path': self.logo_path,
            'year': self.year,
            'language': self.language
        }
    
    @classmethod
    def from_dict(cls, config_dict: dict) -> 'ExamConfig':
        """
        Create ExamConfig from dictionary.
        
        Args:
            config_dict (dict): Configuration dictionary
            
        Returns:
            ExamConfig: New configuration instance
        """
        # Extract base parameters, removing prefixes for the constructor
        institute_name = config_dict['institute_name']
        course_name = config_dict['course']
        language = config_dict.get('language', Language.ENGLISH)
        
        # Get text strings for the language to properly remove prefixes
        text_strings = get_text_strings(language)
        
        # Remove prefixes from class_name and professor_name
        class_prefix = text_strings.get_label_with_colon('class_label') + " "
        professor_prefix = text_strings.get_label_with_colon('professor_label') + " "
        
        class_name = config_dict['class_name'].replace(class_prefix, "")
        professor_name = config_dict['professor_name'].replace(professor_prefix, "")
        
        # Handle student_name - extract actual name or None for blank
        student_name = None
        student_blank = text_strings.get('student_name_blank')
        if config_dict['student_name'] != student_blank:
            student_prefix = text_strings.get_label_with_colon('student_label') + " "
            student_name = config_dict['student_name'].replace(student_prefix, "")
        
        # Handle course_section - extract actual section or None for blank
        course_section = None
        course_blank = text_strings.get('course_section_blank')
        if config_dict['course_section'] != course_blank:
            course_prefix = text_strings.get_label_with_colon('course_label') + " "
            course_section = config_dict['course_section'].replace(course_prefix, "")
        
        return cls(
            institute_name=institute_name,
            course_name=course_name,
            class_name=class_name,
            professor_name=professor_name,
            student_name=student_name,
            course_section=course_section,
            exam_period=config_dict['exam_period'],
            total_points=config_dict['total'],
            password=config_dict['password'],
            logo_path=config_dict['logo_path'],
            year=config_dict['year'],
            language=language
        )


class ExamConfigBuilder:
    """
    Builder pattern for creating ExamConfig instances.
    
    Provides a fluent interface for setting configuration parameters.
    """
    
    def __init__(self):
        """Initialize builder with default values."""
        self._institute_name: Optional[str] = None
        self._course_name: Optional[str] = None
        self._class_name: Optional[str] = None
        self._professor_name: Optional[str] = None
        self._student_name: Optional[str] = None
        self._course_section: Optional[str] = None
        self._exam_period: Optional[str] = None
        self._total_points: int = 100
        self._password: Optional[str] = None
        self._logo_path: Optional[str] = None
        self._year: Optional[int] = None
        self._language: Language = Language.ENGLISH
    
    def institute(self, name: str) -> 'ExamConfigBuilder':
        """
        Set the institution name.
        
        Args:
            name (str): Institution name
            
        Returns:
            ExamConfigBuilder: Self for chaining
        """
        self._institute_name = name
        return self
    
    def course(self, name: str) -> 'ExamConfigBuilder':
        """
        Set the course name.
        
        Args:
            name (str): Course name
            
        Returns:
            ExamConfigBuilder: Self for chaining
        """
        self._course_name = name
        return self
    
    def class_subject(self, name: str) -> 'ExamConfigBuilder':
        """
        Set the class/subject name.
        
        Args:
            name (str): Class or subject name
            
        Returns:
            ExamConfigBuilder: Self for chaining
        """
        self._class_name = name
        return self
    
    def professor(self, name: str) -> 'ExamConfigBuilder':
        """
        Set the professor name.
        
        Args:
            name (str): Professor name
            
        Returns:
            ExamConfigBuilder: Self for chaining
        """
        self._professor_name = name
        return self
    
    def student(self, name: str) -> 'ExamConfigBuilder':
        """
        Set the student name (optional).
        
        Args:
            name (str): Student name
            
        Returns:
            ExamConfigBuilder: Self for chaining
        """
        self._student_name = name
        return self
    
    def section(self, section: str) -> 'ExamConfigBuilder':
        """
        Set the course section (optional).
        
        Args:
            section (str): Course section
            
        Returns:
            ExamConfigBuilder: Self for chaining
        """
        self._course_section = section
        return self
    
    def exam_period(self, period: str) -> 'ExamConfigBuilder':
        """
        Set the exam period (optional).
        
        Args:
            period (str): Exam period description
            
        Returns:
            ExamConfigBuilder: Self for chaining
        """
        self._exam_period = period
        return self
    
    def total_points(self, points: int) -> 'ExamConfigBuilder':
        """
        Set the total points for the exam.
        
        Args:
            points (int): Total points
            
        Returns:
            ExamConfigBuilder: Self for chaining
        """
        self._total_points = points
        return self
    
    def password(self, password: str) -> 'ExamConfigBuilder':
        """
        Set the password for answer key encryption.
        
        Args:
            password (str): Encryption password
            
        Returns:
            ExamConfigBuilder: Self for chaining
        """
        self._password = password
        return self
    
    def logo(self, logo_path: str) -> 'ExamConfigBuilder':
        """
        Set the path to the institution logo.
        
        Args:
            logo_path (str): Path to logo image file
            
        Returns:
            ExamConfigBuilder: Self for chaining
        """
        self._logo_path = logo_path
        return self
    
    def year(self, year: int) -> 'ExamConfigBuilder':
        """
        Set the exam year.
        
        Args:
            year (int): Exam year
            
        Returns:
            ExamConfigBuilder: Self for chaining
        """
        self._year = year
        return self
    
    def language(self, language: Language) -> 'ExamConfigBuilder':
        """
        Set the language for headers and instructions.
        
        Args:
            language (Language): Language to use (English or Spanish)
            
        Returns:
            ExamConfigBuilder: Self for chaining
        """
        self._language = language
        return self
    
    def build(self) -> ExamConfig:
        """
        Build the ExamConfig instance.
        
        Returns:
            ExamConfig: Configured exam configuration
            
        Raises:
            ConfigurationError: If required parameters are missing
        """
        # Check required parameters
        if not self._institute_name:
            raise ConfigurationError("Institute name is required. Use .institute(name)")
        if not self._course_name:
            raise ConfigurationError("Course name is required. Use .course(name)")
        if not self._class_name:
            raise ConfigurationError("Class name is required. Use .class_subject(name)")
        if not self._professor_name:
            raise ConfigurationError("Professor name is required. Use .professor(name)")
        if not self._password:
            raise ConfigurationError("Password is required. Use .password(password)")
        if not self._logo_path:
            raise ConfigurationError("Logo path is required. Use .logo(path)")
        
        return ExamConfig(
            institute_name=self._institute_name,
            course_name=self._course_name,
            class_name=self._class_name,
            professor_name=self._professor_name,
            student_name=self._student_name,
            course_section=self._course_section,
            exam_period=self._exam_period,
            total_points=self._total_points,
            password=self._password,
            logo_path=self._logo_path,
            year=self._year,
            language=self._language
        )