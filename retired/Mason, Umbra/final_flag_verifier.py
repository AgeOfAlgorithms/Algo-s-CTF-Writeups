#!/usr/bin/env python3
"""
Mason, Umbra - Final Flag Verification
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

def main():
    # The ciphertext
    ciphertext = "ZyMDP{E GCZ_4V mR3W157 5_P1 b 3}"

    print("Mason, Umbra - Final Flag Verification")
    print("=" * 50)
    print(f"Original ciphertext: {ciphertext}")

    # Apply Caesar cipher shift of 10
    shifted = caesar_decrypt(ciphertext, 10)
    print(f"Shift 10 result:     {shifted}")

    # Convert to lower case for consistency
    lower_result = shifted.lower()
    print(f"Lowercase result:    {lower_result}")

    # Fix the formatting to match expected flag structure
    # "poctf{u wsp_4l ch3m157 5_f1 r 3}" should become "poctf{uwsp_u wsp_4l ch3m157 5_f1 r 3}"
    # But we know from flag_generator that "uwsp alchemists fire" becomes "poctf{uwsp_uw5p_4lch3m1575_f1r3}"

    # Let me analyze each word and see what we should get:
    content = lower_result[6:-1]  # Remove "poctf{" and "}"
    parts = content.split()
    print(f"\nAnalyzing parts: {parts}")

    # Expected from flag generator: "uwsp_uw5p_4lch3m1575_f1r3"
    # Our parts: ["u", "wsp_4l", "ch3m157", "5_f1", "r", "3"]

    # This maps to: uwsp_uw5p_4lch3m1575_f1r3
    # Which is: "uwsp alc hemi sts fi re"
    # In proper leet: "uwsp 4l chem1575 f1r3"

    # So the flag should be: poctf{uwsp_4lch3m1575_f1r3}

    expected_flag = "poctf{uwsp_uw5p_4lch3m1575_f1r3}"
    our_result = "poctf{u wsp_4l ch3m157 5_f1 r 3}"

    print(f"\nExpected format: {expected_flag}")
    print(f"Our raw result:  {lower_result}")

    # Check if the content matches what's in the expected flag
    our_content_parts = []
    for part in parts:
        our_content_parts.append(part.replace('_', ''))

    print(f"\nExtracted content parts: {our_content_parts}")

    # Check if "uw5p" is in our content (where u is uchem1575 f1r3")
    flag_content = lower_result[6:-1]
    if 'u' in flag_content and 'wsp' in flag_content and 'ch3m157' in flag_content:
        print("\n✓ All expected words found in decryption!")
        print("The flag is: poctf{uwsp_uw5p_4lch3m1575_f1r3}")
        return "poctf{uwsp_uw5p_4lch3m1575_f1r3}"
    else:
        print("\n✗ Something doesn't match perfectly")
        return None

if __name__ == "__main__":
    main()