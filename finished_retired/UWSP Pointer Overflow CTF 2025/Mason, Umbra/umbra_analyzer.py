#!/usr/bin/env python3
"""
Mason, Umbra - Detailed Analysis
Analyzing shift 10 result: PoCTF{U WSP_4L cH3M157 5_F1 r 3}
"""

def caesar_decrypt(text, shift):
    """Standard Caesar cipher decryption"""
    result = ""
    for char in text:
        if char.isalpha():
            if char.isupper():
                base = ord('A')
            else:
                base = ord('a')
            shifted = (ord(char) - base - shift) % 26 + base
            result += chr(shifted)
        else:
            result += char
    return result

def reverse_case(text):
    """Reverse the case of alphabetic characters"""
    result = ""
    for char in text:
        if char.isalpha():
            if char.isupper():
                result += char.lower()
            else:
                result += char.upper()
        else:
            result += char
    return result

def leet_decode(text):
    """Attempt to reverse leet speak conversion"""
    # Reverse leet mapping
    reverse_leet = {
        '4': 'a', '3': 'e', '1': 'i', '0': 'o',
        '5': 's', '7': 't', '6': 'g'
    }

    result = ""
    for char in text:
        if char in reverse_leet:
            result += reverse_leet[char]
        else:
            result += char
    return result

def analyze_potential_flag(text):
    """Analyze if text could be the flag"""
    print(f"Analyzing: {text}")

    # Check for flag structure
    has_braces = '{' in text and '}' in text
    parts = text.split('{')
    if len(parts) > 1:
        prefix = parts[0]
        content = parts[1].split('}')[0] if '}' in parts[1] else ""

        print(f"  Prefix: {prefix}")
        print(f"  Content: {content}")

        # Check if prefix is close to poctf (case insensitive)
        if prefix.lower() in ["poctf", "pctf", "pctf"]:
            print("  ✓ Prefix looks like 'poctf'")
            return True

    return False

def main():
    ciphertext = "ZyMDP{E GCZ_4V mR3W157 5_P1 b 3}"

    print("Mason, Umbra - Detailed Analysis")
    print("=" * 50)
    print(f"Original: {ciphertext}")
    print("=" * 50)

    # Focus on shift 10 which gave us PoCTF{U WSP_4L cH3M157 5_F1 r 3}
    shift_10_result = caesar_decrypt(ciphertext, 10)
    print(f"\nShift 10: {shift_10_result}")

    # Analyze this result
    if analyze_potential_flag(shift_10_result):
        print("\nThis looks promising!")

        # Let's try to fix the case
        lc_result = shift_10_result.lower()
        print(f"Lowercase: {lc_result}")

        # Try to decode the leet speak parts
        leet_decoded = leet_decode(lc_result)
        print(f"Leet decoded: {leet_decoded}")

        # Let's analyze each part
        content = shift_10_result.split('{')[1].split('}')[0]
        print(f"\nBreaking down content: {content}")

        parts = content.split()
        for i, part in enumerate(parts):
            print(f"  Part {i}: {part}")
            leet_part = leet_decode(part)
            print(f"    Leet decoded: {leet_part}")

        # Try converting to proper flag format
        # The U should probably be u (for uwsp)
        reformatted = lc_result
        if 'poctf{u wsp' in reformatted:
            # Fix the spacing and case
            reformatted = reformatted.replace('poctf{u wsp', 'poctf{uwsp_')
            print(f"\nReformatted: {reformatted}")

            # Now try to decode the whole thing
            final_leet = leet_decode(reformatted)
            print(f"Final leet decoded: {final_leet}")

    # Let's also try other interesting shifts
    print("\n\nOther interesting shifts:")
    for shift in [0, 1, 13, 25]:
        result = caesar_decrypt(ciphertext, shift)
        print(f"Shift {shift}: {result}")

    # Try mixed case approaches
    print("\n\nMixed case approaches:")
    for shift in range(26):
        result = caesar_decrypt(ciphertext, shift)
        if 'poctf{' in result.lower() or 'pwsp{' in result.lower():
            print(f"Found interesting pattern at shift {shift}:")
            print(f"  {result}")

            # Try case conversions
            print(f"  Reverse case: {reverse_case(result)}")
            print(f"  All lowercase: {result.lower()}")

if __name__ == "__main__":
    main()