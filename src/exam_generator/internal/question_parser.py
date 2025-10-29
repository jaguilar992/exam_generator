# -*- coding: utf-8 -*-
"""
Question parser for reading question files.
"""

import re
import random
from typing import List, Dict, Any
from ..exceptions import InvalidQuestionFormatError


class QuestionParser:
    """
    Parser for question files in .ptf format.
    
    Supports parsing questions with multiple choice options and
    optional shuffling of answer choices.
    """
    
    def __init__(self, shuffle_options: bool = True):
        """
        Initialize question parser.
        
        Args:
            shuffle_options (bool): Whether to shuffle answer options
        """
        self.shuffle_options = shuffle_options
    
    def parse_from_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Parse questions from a file.
        
        Args:
            file_path (str): Path to the question file
            
        Returns:
            List[Dict[str, Any]]: List of parsed questions
            
        Raises:
            InvalidQuestionFormatError: If file format is invalid
            FileNotFoundError: If file doesn't exist
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"Question file not found: {file_path}")
        except Exception as e:
            raise InvalidQuestionFormatError(f"Error reading file {file_path}: {str(e)}")
        
        return self.parse_from_string(content)
    
    def parse_from_string(self, content: str) -> List[Dict[str, Any]]:
        """
        Parse questions from string content.
        
        Expected format:
        - Question text?
        Option 1 (correct answer - always first)
        Option 2
        Option 3
        Option 4
        
        Args:
            content (str): Question file content
            
        Returns:
            List[Dict[str, Any]]: List of parsed questions
            
        Raises:
            InvalidQuestionFormatError: If content format is invalid
        """
        if not content or not content.strip():
            raise InvalidQuestionFormatError("Question content is empty")
        
        questions = []
        
        # Split by questions (lines that start with -)
        question_blocks = re.split(r'^-\s+', content, flags=re.MULTILINE)[1:]
        
        if not question_blocks:
            raise InvalidQuestionFormatError("No questions found in content")
        
        for i, block in enumerate(question_blocks):
            try:
                question_data = self._parse_question_block(block, i + 1)
                questions.append(question_data)
            except Exception as e:
                raise InvalidQuestionFormatError(f"Error parsing question {i + 1}: {str(e)}")
        
        return questions
    
    def _parse_question_block(self, block: str, question_number: int) -> Dict[str, Any]:
        """
        Parse a single question block.
        
        Args:
            block (str): Question block content
            question_number (int): Question number for error reporting
            
        Returns:
            Dict[str, Any]: Parsed question data
            
        Raises:
            InvalidQuestionFormatError: If block format is invalid
        """
        lines = [line.strip() for line in block.strip().split('\n') if line.strip()]
        
        if not lines:
            raise InvalidQuestionFormatError(f"Question {question_number} is empty")
        
        question_text = lines[0]
        if not question_text:
            raise InvalidQuestionFormatError(f"Question {question_number} has no text")
        
        # Extract options (lines 1-4, or however many are available)
        options = lines[1:5] if len(lines) > 1 else []
        
        # Ensure we have at least 2 options for a meaningful question
        if len(options) < 2:
            raise InvalidQuestionFormatError(
                f"Question {question_number} must have at least 2 options, found {len(options)}"
            )
        
        # Pad with empty options if less than 4
        while len(options) < 4:
            options.append("")
        
        # The correct answer is always the first option initially (index 0)
        correct_answer_index = 0
        
        # Shuffle options if enabled
        if self.shuffle_options and len([opt for opt in options if opt]) > 1:
            correct_answer_index = self._shuffle_options(options)
        
        return {
            'question': question_text,
            'options': options,
            'correct_answer': correct_answer_index
        }
    
    def _shuffle_options(self, options: List[str]) -> int:
        """
        Shuffle the options and return the new index of the correct answer.
        
        Args:
            options (List[str]): List of options to shuffle in-place
            
        Returns:
            int: New index of the correct answer
        """
        # Create list of tuples (option, is_correct)
        options_with_flags = [(opt, i == 0) for i, opt in enumerate(options)]
        
        # Shuffle the list
        random.shuffle(options_with_flags)
        
        # Update the options list and find new correct answer index
        new_correct_index = 0
        for i, (option, is_correct) in enumerate(options_with_flags):
            options[i] = option
            if is_correct:
                new_correct_index = i
        
        return new_correct_index