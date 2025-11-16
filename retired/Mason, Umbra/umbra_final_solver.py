#!/usr/bin/env python3
"""
Mason, Umbra - Final Solver
Solve the shift cipher and format the flag correctly
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

def leet_decode(text):
    """Reverse leet speak conversion"""
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

def format_flag_properly(text):
    """Format the decrypted text as a proper flag"""
    # Convert to lowercase for consistency
    lower_text = text.lower()

    # Fix the flag structure
    if 'poctf{' in lower_text:
        # Extract the content between braces
        parts = lower_text.split('poctf{')
        if len(parts) > 1:
            content = parts[1].split('}')[0] if '}' in parts[1] else parts[1]

            # Process the content: "u wsp_4l ch3m157 5_f1 r 3"
            # This should become: "uwsp_al chemist s_fi r e"
            # Then leet decode: "uwsp_al chemist s_fi r e" -\u003e "uwsp_al chemist s_fi re"

            # Fix the spacing: "u wsp_4l" -> "uwsp_4l"
            content = content.replace("u wsp", "uwsp")

            # Apply leet decoding
            decoded_content = leet_decode(content)

            # Construct final flag
            final_flag = f"poctf{{{decoded_content}}}"
            return final_flag

    return None

def main():
    ciphertext = "ZyMDP{E GCZ_4V mR3W157 5_P1 b 3}"

    print("Mason, Umbra - Final Solver")
    print("=" * 50)
    print(f"Ciphertext: {ciphertext}")
    print("=" * 50)

    # We've determined shift 10 is correct
    shifted_result = caesar_decrypt(ciphertext, 10)
    print(f"Shift 10 result: {shifted_result}")

    # Convert to intermediate format: poctf{u wsp_4l ch3m157 5_f1 r 3}
    intermediate = shifted_result.lower()
    print(f"Lowercase intermediate: {intermediate}")

    # Format properly
    final_flag = format_flag_properly(shifted_result)
    print(f"Final flag: {final_flag}")

    # Verify the flag structure
    if final_flag:
        # Check flag format: poctf{uwsp_...}
        flag_content = final_flag[6:-1]  # Remove "poctf{" and "}"

        print(f"\nFlag content: {flag_content}")
        print(f"Flag structure analysis:")
        print(f"  - Starts correctly with poctf{{")
        print(f"  - Has uwsp_ prefix: {'uwsp_' in flag_content}")
        print(f"  - Valid characters: {all(c in '4bcd3f6h1jklmn0pqr57uvwxyz_' for c in flag_content)}")

        # Alternative possibilities for the final word
        print(f"\nPossible interpretations:")
        content_parts = flag_content.replace("uwsp_", "").split("_")
        for i, part in enumerate(content_parts):
            decoded_part = leet_decode(part)
            print(f"  Part {i}: '{part}' -> '{decoded_part}'")

if __name__ == "__main__":
    main()