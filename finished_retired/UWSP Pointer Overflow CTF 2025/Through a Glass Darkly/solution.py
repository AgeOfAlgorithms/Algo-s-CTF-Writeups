"""
Final Flag Decoder for Through a Glass Darkly CTF Challenge
Author: Claude
Purpose: Decode the flag with correct data offset
Created: 2025-11-10
Updated: 2025-11-10 (corrected encoded data starting point)
Expected result: Get the actual flag
Produced result: TBD
"""

import ctypes

# CORRECTED: Data from WASM at file offset 0x1a7 (memory offset 1056)
reference_string = b"through_a_glass_darkly"  # 22 characters
encoded_data = bytes([
    0x43, 0x55, 0x84, 0x24, 0xf7, 0x5c, 0x90, 0xe9,  # Started with 0x43, not 0x55!
    0xa8, 0xcd, 0x26, 0xbc, 0x07, 0x4a, 0x0e, 0xa8,
    0xe5, 0x5a, 0x48, 0xe2, 0xba, 0x77, 0x7d, 0x6e,
    0x11, 0x86, 0xbe
])  # 27 bytes

print("Decoding flag with CORRECTED encoded data...")
print("=" * 60)

flag = ""

for b in range(27):  # Now 27 characters!
    # select: if (b < 22) then b else (b - 22)
    ref_index = b if b < 22 else (b - 22)
    ref_byte = reference_string[ref_index]

    # c = ref_byte XOR (b * 73 + 19)
    c = ref_byte ^ ((b * 73 + 19) & 0xFF)

    # d = (b & 255) % 7
    d = (b & 0xFF) % 7

    # Rotation
    shift_left = (d + 1) & 7
    shift_right = d ^ 7
    rotation = ((c << shift_left) | ((c & 0xFF) >> shift_right)) & 0xFFFFFFFF

    # Decode
    mult_result = ctypes.c_int32(b * -17).value
    temp = (encoded_data[b] + mult_result + 123) & 0xFFFFFFFF
    flag_char = (temp ^ rotation) & 0xFF

    flag += chr(flag_char)

    if 32 <= flag_char <= 126:
        char_display = f"'{chr(flag_char)}'"
    else:
        char_display = f"[0x{flag_char:02x}]"

    print(f"b={b:2d}: enc=0x{encoded_data[b]:02x} -> {char_display}")

print("=" * 60)
print(f"\nDecoded flag: {flag}")
print()

if all(32 <= ord(c) <= 126 for c in flag):
    print("✓ All printable ASCII characters!")
else:
    print("✗ Contains non-printable characters")
    non_printable = [(i, ord(c)) for i, c in enumerate(flag) if not (32 <= ord(c) <= 126)]
    print(f"Non-printable at positions: {non_printable}")
