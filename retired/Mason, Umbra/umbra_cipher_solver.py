#!/usr/bin/env python3
"""
Mason, Umbra - Shift Cipher Solver
Ciphertext: ZyMDP{E GCZ_4V mR3W157 5_P1 b 3}
"""

def caesar_decrypt(text, shift):
    """Standard Caesar cipher decryption"""
    result = ""
    for char in text:
        if char.isalpha():
            # Determine ASCII offset based on case
            if char.isupper():
                base = ord('A')
            else:
                base = ord('a')
            # Shift character
            shifted = (ord(char) - base - shift) % 26 + base
            result += chr(shifted)
        else:
            # Keep non-alphabetic characters unchanged
            result += char
    return result

def reverse_mixed_case_caesar(text, shift):
    """Try Caesar but with mixed case reversal"""
    result = ""
    for char in text:
        if char.isalpha():
            if char.isupper():
                # Uppercase shifted normally
                shifted = (ord(char) - ord('A') - shift) % 26 + ord('A')
            else:
                # Lowercase shifted in reverse or different pattern
                shifted = (ord(char) - ord('a') + shift) % 26 + ord('a')
            result += chr(shifted)
        else:
            result += char
    return result

def vowel_consonant_shift(text, vowel_shift, consonant_shift):
    """Shift vowels and consonants by different amounts"""
    vowels = "aeiouAEIOU"
    result = ""
    for char in text:
        if char.isalpha():
            if char in vowels:
                base = ord('A') if char.isupper() else ord('a')
                shifted = (ord(char) - base - vowel_shift) % 26 + base
            else:
                base = ord('A') if char.isupper() else ord('a')
                shifted = (ord(char) - base - consonant_shift) % 26 + base
            result += chr(shifted)
        else:
            result += char
    return result

def position_based_shift(text, base_shift=1):
    """Shift based on position in text"""
    result = ""
    for i, char in enumerate(text):
        if char.isalpha():
            shift = (i * base_shift) % 26
            if char.isupper():
                base = ord('A')
            else:
                base = ord('a')
            shifted = (ord(char) - base - shift) % 26 + base
            result += chr(shifted)
        else:
            result += char
    return result

def print_decryption_results(ciphertext, decrypt_func, func_name, *args):
    """Helper to print decryption results"""
    print(f"\n{func_name}:")
    result = decrypt_func(ciphertext, *args)
    print(f"Result: {result}")

    # Check if it looks like a flag format
    if text_looks_like_flag(result):
        print("🎯 POTENTIAL FLAG FOUND!")
        return result
    return None

def text_looks_like_flag(text):
    """Check if text matches expected flag patterns"""
    # Expected patterns for poctf
    flag_indicators = [
        "poctf{", "uwsp_", "flag{", "ctf{",
        "{", "}",  # Basic flag structure
    ]

    # Count alphanumeric characters vs length
    alphanumeric = sum(1 for c in text if c.isalnum() or c in "_ -.")

    # Check for basic structure
    has_braces = '{' in text and '}' in text
    has_alphanumeric_words = any(word.isalnum() for word in text.split())

    return has_braces and has_alphanumeric_words

def main():
    ciphertext = "ZyMDP{E GCZ_4V mR3W157 5_P1 b 3}"

    print("Mason, Umbra - Shift Cipher Solver")
    print("=" * 50)
    print(f"Ciphertext: {ciphertext}")
    print("=" * 50)

    potential_flag = None

    # Test standard Caesar cipher with all possible shifts
    print("\n📍 Testing Standard Caesar Cipher (shifts 0-25):")
    for shift in range(26):
        result = caesar_decrypt(ciphertext, shift)
        if text_looks_like_flag(result):
            print(f"Shift {shift}: {result}")
            if potential_flag is None:
                potential_flag = result

    # Test other approaches
    if not potential_flag:
        for shift in range(26):
            result = reverse_mixed_case_caesar(ciphertext, shift)
            if text_looks_like_flag(result):
                print(f"\n🎯 Reverse Mixed Case (shift {shift}):")
                print(f"Result: {result}")
                potential_flag = result
                break

    if not potential_flag:
        # Test vowel/consonant different shifts
        print("\n📍 Testing Vowel/Consonant Different Shifts:")
        for vshift in range(8):  # Limited range
            for cshift in range(8):
                result = vowel_consonant_shift(ciphertext, vshift, cshift)
                if text_looks_like_flag(result):
                    print(f"Vowel shift {vshift}, Consonant shift {cshift}:")
                    print(f"Result: {result}")
                    potential_flag = result
                    break
            if potential_flag:
                break

    # Test position-based shifts
    if not potential_flag:
        print("\n📍 Testing Position-based Shifts:")
        for base in range(1, 5):
            result = position_based_shift(ciphertext, base)
            if text_looks_like_flag(result):
                print(f"Position-based (base {base}): {result}")
                potential_flag = result
                break

    # Manual inspection of all Caesar shifts
    print("\n📍 Manual inspection:")
    print("Examining all Caesar shifts for interesting patterns:")

    for shift in range(26):
        result = caesar_decrypt(ciphertext, shift)
        # Look for words that might make sense
        if any(word in result.lower() for word in ["uwsp", "flag", "ctf", "password", "key"]):
            print(f"Shift {shift}: {result}")
        elif len([c for c in result if c.isalpha()]) > 10 and shift < 5:  # Show first few for comparison
            print(f"Shift {shift}: {result}")

    if potential_flag:
        print(f"\n🎯 Most likely result: {potential_flag}")
        return potential_flag

    return None

if __name__ == "__main__":
    main()