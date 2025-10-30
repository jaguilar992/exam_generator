# -*- coding: utf-8 -*-
"""
Encryption utilities for answer key protection.
"""

from ..exceptions import EncryptionError
from string import ascii_letters, digits

# Custom alphabet for encoding
ALPHABET = digits + ascii_letters

class AnswerKeyEncryption:
    """
    Handles encryption and decryption of answer keys using a Vigenère-like cipher.
    """
    
    def __init__(self):
        """Initialize the encryption handler."""
        self.alphabet = ALPHABET
        self.alphabet_index = {ch: i for i, ch in enumerate(self.alphabet)}
        self.alphabet_size = len(self.alphabet)
    
    def encrypt(self, plaintext: str, password: str) -> str:
        """
        Encrypt plaintext using Vigenère-like cipher.
        
        Args:
            plaintext (str): Text to encrypt
            password (str): Encryption password
            
        Returns:
            str: Encrypted text
            
        Raises:
            EncryptionError: If encryption fails
        """
        if not plaintext:
            raise EncryptionError("Cannot encrypt empty text")
        if not password:
            raise EncryptionError("Password cannot be empty")
        
        try:
            return self._vigenere_encrypt(plaintext, password)
        except Exception as e:
            raise EncryptionError(f"Encryption failed: {str(e)}")
    
    def decrypt(self, ciphertext: str, password: str) -> str:
        """
        Decrypt ciphertext using Vigenère-like cipher.
        
        Args:
            ciphertext (str): Text to decrypt
            password (str): Decryption password
            
        Returns:
            str: Decrypted text
            
        Raises:
            EncryptionError: If decryption fails
        """
        if not ciphertext:
            raise EncryptionError("Cannot decrypt empty text")
        if not password:
            raise EncryptionError("Password cannot be empty")
        
        try:
            return self._vigenere_decrypt(ciphertext, password)
        except Exception as e:
            raise EncryptionError(f"Decryption failed: {str(e)}")
    
    def _vigenere_encrypt(self, plaintext: str, key: str) -> str:
        """
        Internal Vigenère encryption implementation.
        
        Args:
            plaintext (str): Text to encrypt
            key (str): Encryption key
            
        Returns:
            str: Encrypted text
        """
        key_indices = [self.alphabet_index[c] for c in key if c in self.alphabet_index]
        if not key_indices:
            raise EncryptionError("Key contains no valid characters")
        
        result = []
        key_position = 0
        
        for char in plaintext:
            if char not in self.alphabet_index:
                # Leave characters not in alphabet unchanged
                result.append(char)
                continue
            
            plain_index = self.alphabet_index[char]
            key_index = key_indices[key_position % len(key_indices)]
            cipher_index = (plain_index + key_index) % self.alphabet_size
            result.append(self.alphabet[cipher_index])
            key_position += 1
        
        return "".join(result)
    
    def _vigenere_decrypt(self, ciphertext: str, key: str) -> str:
        """
        Internal Vigenère decryption implementation.
        
        Args:
            ciphertext (str): Text to decrypt
            key (str): Decryption key
            
        Returns:
            str: Decrypted text
        """
        key_indices = [self.alphabet_index[c] for c in key if c in self.alphabet_index]
        if not key_indices:
            raise EncryptionError("Key contains no valid characters")
        
        result = []
        key_position = 0
        
        for char in ciphertext:
            if char not in self.alphabet_index:
                # Leave characters not in alphabet unchanged
                result.append(char)
                continue
            
            cipher_index = self.alphabet_index[char]
            key_index = key_indices[key_position % len(key_indices)]
            plain_index = (cipher_index - key_index) % self.alphabet_size
            result.append(self.alphabet[plain_index])
            key_position += 1
        
        return "".join(result)


def encrypt_answer_data(questions_data: str, password: str) -> str:
    """
    Convenience function to encrypt answer data.
    
    Args:
        questions_data (str): Answer data to encrypt
        password (str): Encryption password
        
    Returns:
        str: Encrypted data
    """
    encryptor = AnswerKeyEncryption()
    return encryptor.encrypt(questions_data, password)


def decrypt_answer_data(encrypted_data: str, password: str) -> str:
    """
    Convenience function to decrypt answer data.
    
    Args:
        encrypted_data (str): Encrypted data
        password (str): Decryption password
        
    Returns:
        str: Decrypted data
    """
    encryptor = AnswerKeyEncryption()
    return encryptor.decrypt(encrypted_data, password)


def parse_decrypted_qr_data(decrypted_data: str) -> dict:
    """
    Parse decrypted QR data into structured information.
    
    Args:
        decrypted_data (str): Decrypted QR data in format "Q{num}_P{points}_{answers}"
        
    Returns:
        dict: Parsed data containing 'num_questions', 'total_points', 'answers'
        
    Raises:
        ValueError: If data format is invalid
    """
    try:
        # Expected format: Q25_P100_ABCDABCD...
        if not decrypted_data.startswith('Q'):
            raise ValueError("Invalid QR data format")
        
        parts = decrypted_data.split('_')
        if len(parts) != 3:
            raise ValueError("Invalid QR data format - expected 3 parts")
        
        # Parse number of questions
        q_part = parts[0]  # Q25
        if not q_part.startswith('Q'):
            raise ValueError("Invalid questions part")
        num_questions = int(q_part[1:])
        
        # Parse total points
        p_part = parts[1]  # P100
        if not p_part.startswith('P'):
            raise ValueError("Invalid points part")
        total_points = int(p_part[1:])
        
        # Parse answers
        answers_string = parts[2]  # ABCDABCD...
        if len(answers_string) != num_questions:
            raise ValueError(f"Expected {num_questions} answers, got {len(answers_string)}")
        
        # Convert answer letters to indices
        answers = []
        for letter in answers_string:
            if letter not in 'ABCD':
                raise ValueError(f"Invalid answer letter: {letter}")
            answers.append(ord(letter) - ord('A'))  # A=0, B=1, C=2, D=3
        
        return {
            'num_questions': num_questions,
            'total_points': total_points,
            'answers': answers,
            'answer_letters': answers_string
        }
        
    except (ValueError, IndexError) as e:
        raise ValueError(f"Failed to parse QR data: {str(e)}")


def decrypt_qr_code(encrypted_qr_data: str, password: str) -> dict:
    """
    Complete function to decrypt and parse QR code data.
    
    Args:
        encrypted_qr_data (str): Encrypted QR code data
        password (str): Password used for encryption
        
    Returns:
        dict: Parsed answer key data
        
    Raises:
        EncryptionError: If decryption fails
        ValueError: If data format is invalid
    """
    # Decrypt the data
    decrypted_data = decrypt_answer_data(encrypted_qr_data, password)
    
    # Parse the decrypted data
    return parse_decrypted_qr_data(decrypted_data)