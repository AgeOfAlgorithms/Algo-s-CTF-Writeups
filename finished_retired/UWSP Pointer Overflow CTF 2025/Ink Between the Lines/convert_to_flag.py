#!/usr/bin/env python3
"""
Convert decoded message to proper flag format
Based on rules: poctf{uwsp_...} with character set 4bcd3f6h1jklmn0pqr57uvwxyz
"""

message = "sweetheart is thy call"

# L33tspeak conversion based on allowed character set
# Character set: 4bcd3f6h1jklmn0pqr57uvwxyz
# Mapping: a->4, e->3, g->6, i->1, o->0, s->5, t->7
# (from example: poctf{uwsp_7h15_15_4_54mpl3_fl46})

def convert_to_leet(text):
    """Convert text to l33tspeak using allowed character set"""
    leet_map = {
        'a': '4',
        'e': '3',
        'g': '6',
        'i': '1',
        'o': '0',
        's': '5',
        't': '7',
    }

    result = ""
    for char in text.lower():
        if char in leet_map:
            result += leet_map[char]
        elif char == ' ':
            result += '_'
        else:
            result += char

    return result

leet_message = convert_to_leet(message)

print(f"Original message: {message}")
print(f"L33t conversion:  {leet_message}")
print(f"\nFlag: poctf{{uwsp_{leet_message}}}")

# Verify all characters are in allowed set
allowed_chars = set('4bcd3f6h1jklmn0pqr57uvwxyz_')
flag_body = leet_message

print(f"\nVerification:")
print(f"All chars in allowed set: {all(c in allowed_chars for c in flag_body)}")

invalid_chars = set(c for c in flag_body if c not in allowed_chars)
if invalid_chars:
    print(f"Invalid characters: {invalid_chars}")
else:
    print("✓ All characters valid!")
