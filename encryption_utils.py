# -*- coding: utf-8 -*-
"""
Utilidades de encriptación para el generador de exámenes.
Implementa un cifrado tipo Vigenère usando un alfabeto personalizado.
"""

ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"

def build_index(alphabet):
    """Construye un índice para mapear caracteres a posiciones en el alfabeto"""
    return {ch: i for i, ch in enumerate(alphabet)}

# Índice global para el alfabeto
idx = build_index(ALPHABET)
N = len(ALPHABET)

def encrypt_vigenere_like(plain: str, key: str) -> str:
    """
    Encripta un texto usando un cifrado tipo Vigenère.
    
    Args:
        plain (str): Texto plano a encriptar
        key (str): Clave de encriptación
        
    Returns:
        str: Texto encriptado
    """
    key_idx = [idx[c] for c in key]
    out = []
    ki = 0
    
    for ch in plain:
        if ch not in idx:
            # Si hay caracteres fuera del alfabeto, los dejamos igual
            out.append(ch)
            continue
        
        p = idx[ch]
        k = key_idx[ki % len(key_idx)]
        c = (p + k) % N
        out.append(ALPHABET[c])
        ki += 1
    
    return "".join(out)

def decrypt_vigenere_like(cipher: str, key: str) -> str:
    """
    Desencripta un texto encriptado con el cifrado tipo Vigenère.
    
    Args:
        cipher (str): Texto encriptado
        key (str): Clave de desencriptación
        
    Returns:
        str: Texto plano original
    """
    key_idx = [idx[c] for c in key]
    out = []
    ki = 0
    
    for ch in cipher:
        if ch not in idx:
            out.append(ch)
            continue
        
        c = idx[ch]
        k = key_idx[ki % len(key_idx)]
        p = (c - k) % N
        out.append(ALPHABET[p])
        ki += 1
    
    return "".join(out)

def encrypt_answer_data(questions_data: str, password: str) -> str:
    """
    Encripta los datos de respuestas para el código QR.
    
    Args:
        questions_data (str): Datos de las preguntas y respuestas
        password (str): Contraseña para encriptar
        
    Returns:
        str: Datos encriptados
    """
    return encrypt_vigenere_like(questions_data, password)

def decrypt_answer_data(encrypted_data: str, password: str) -> str:
    """
    Desencripta los datos de respuestas del código QR.
    
    Args:
        encrypted_data (str): Datos encriptados
        password (str): Contraseña para desencriptar
        
    Returns:
        str: Datos originales desencriptados
    """
    return decrypt_vigenere_like(encrypted_data, password)

# Función de ejemplo y prueba
def test_encryption():
    """Función de prueba para verificar la encriptación"""
    original = "Q25_P50_DDDBBCDDDDDAABCCAADCBAADD"
    key = "pauta2025"
    
    # Encriptar
    cifrado = encrypt_vigenere_like(original, key)
    print("Original:", original)
    print("Cifrado:", cifrado)
    
    # Desencriptar
    recuperado = decrypt_vigenere_like(cifrado, key)
    print("Recuperado:", recuperado)
    
    # Verificar que funciona correctamente
    assert original == recuperado, "Error: la encriptación/desencriptación no funciona correctamente"
    print("✓ Prueba de encriptación exitosa")