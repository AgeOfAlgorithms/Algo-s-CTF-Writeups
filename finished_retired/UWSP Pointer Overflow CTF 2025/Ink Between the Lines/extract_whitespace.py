#!/usr/bin/env python3
"""
Whitespace Steganography Decoder
Author: CTF Solver
Purpose: Extract hidden message from tabs and spaces in leaflet.txt
Created: 2025-11-09
Expected: Decode the flag hidden in trailing whitespace
Last updated: 2025-11-09
Result: Attempting to decode...
"""

def extract_whitespace_stego(filename):
    """Extract hidden data from trailing whitespace (tabs/spaces)"""

    print(f"[*] Reading file: {filename}")

    with open(filename, 'rb') as f:
        content = f.read()

    # Decode as text
    text = content.decode('utf-8')
    lines = text.split('\n')

    print(f"[*] Found {len(lines)} lines")

    # Extract trailing whitespace from each line
    binary_string = ""

    for i, line in enumerate(lines, 1):
        # Get only the trailing whitespace
        trailing_ws = ""
        for char in reversed(line):
            if char in [' ', '\t']:
                trailing_ws = char + trailing_ws
            else:
                break

        if trailing_ws:
            # Convert to binary: tab = 1, space = 0 (or reverse)
            binary_tab = ''.join('1' if c == '\t' else '0' for c in trailing_ws)
            binary_space = ''.join('0' if c == '\t' else '1' for c in trailing_ws)

            print(f"Line {i:2d}: '{trailing_ws.replace(' ', 'S').replace(chr(9), 'T')}' -> Tab=1: {binary_tab}, Space=1: {binary_space}")

            binary_string += binary_tab

    print(f"\n[*] Total binary (Tab=1): {binary_string}")
    print(f"[*] Length: {len(binary_string)} bits")

    # Try to decode as ASCII (8 bits per character)
    if len(binary_string) % 8 == 0:
        print("\n[*] Decoding as ASCII (Tab=1, Space=0):")
        try:
            message = ""
            for i in range(0, len(binary_string), 8):
                byte = binary_string[i:i+8]
                char = chr(int(byte, 2))
                message += char
                print(f"  {byte} -> {int(byte, 2):3d} -> '{char}'")
            print(f"\n[+] Decoded message (Tab=1): {message}")
        except Exception as e:
            print(f"[-] Error decoding: {e}")

    # Try reverse encoding (Space=1, Tab=0)
    binary_string_rev = ""
    for line in lines:
        trailing_ws = ""
        for char in reversed(line):
            if char in [' ', '\t']:
                trailing_ws = char + trailing_ws
            else:
                break

        if trailing_ws:
            binary_space = ''.join('1' if c == ' ' else '0' for c in trailing_ws)
            binary_string_rev += binary_space

    if len(binary_string_rev) % 8 == 0:
        print("\n[*] Decoding as ASCII (Space=1, Tab=0):")
        try:
            message = ""
            for i in range(0, len(binary_string_rev), 8):
                byte = binary_string_rev[i:i+8]
                char = chr(int(byte, 2))
                message += char
            print(f"\n[+] Decoded message (Space=1): {message}")
        except Exception as e:
            print(f"[-] Error decoding: {e}")

if __name__ == "__main__":
    extract_whitespace_stego("leaflet.txt")
