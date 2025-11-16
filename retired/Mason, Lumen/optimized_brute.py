#!/usr/bin/env python3
"""
Optimized brute force solution for Mason, Lumen ARX stream cipher challenge.

Key space: 24-bit key = 6 hex chars = 16,777,216 possibilities
This version includes optimizations and early termination if a flag is found.
"""

import sys
sys.path.insert(0, '.')
from encrypt import keystream_bytes
import string

def is_likely_flag(text):
    """More aggressive filtering for likely flags."""
    if not text or len(text) == 0:
        return False

    # Must be printable ASCII
    try:
        decoded = text.decode('ascii')
    except UnicodeDecodeError:
        return False

    # Check for flag-like structures
    flag_starts = ['flag{', 'FLAG{', 'uwsp{', 'UWSP{', 'ctf{', 'CTF{']
    has_flag_start = any(decoded.startswith(start) for start in flag_starts)

    if has_flag_start:
        return True

    # Check if contains flag pattern {..}
    if decoded.count('{') >= 1 and decoded.count('}') >= 1:
        return True

    # Check for common CTF flag endings
    flag_endings = ['}', 'flag', 'ctf']
    if any(decoded.endswith(ending) for ending in flag_endings):
        return True

    return False

def optimized_brute_force():
    """Brute force with optimizations."""
    # Load files
    with open('nonce.txt', 'r') as f:
        nonce_hex = f.read().strip()

    with open('ciphetext.bin', 'rb') as f:
        ciphertext = f.read()

    print(f"Nonce: {nonce_hex}")
    print(f"Ciphertext: {ciphertext.hex()}")
    print(f"Ciphertext length: {len(ciphertext)} bytes")
    print(f"Total key space: {2**24:,} keys")

    nonce = int(nonce_hex, 16)
    total_keys = 2**24
    found_flag = None

    # Pre-calculate some values for optimization
    key_characters = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789{}_')

    print("Starting brute force...")

    # Try all possible 24-bit keys
    for key in range(total_keys):
        # Generate keystream and decrypt
        keystream = keystream_bytes(key, nonce, len(ciphertext))
        plaintext = bytes([c ^ k for c, k in zip(ciphertext, keystream)])

        # Quick check for printable characters
        try:
            decoded = plaintext.decode('ascii')
            if all(c in key_characters for c in decoded):
                if is_likely_flag(plaintext):
                    print(f"\n🚩 FLAG FOUND! 🚩")
                    print(f"Key: 0x{key:06x}")
                    print(f"Flag: {decoded}")
                    found_flag = (key, decoded)
                    break
        except:
            continue

        # Progress indicator every 500k keys
        if key % 500000 == 0 and key != 0:
            print(f"Progress: {key:,} / {total_keys:,} keys tested ({(key/total_keys)*100:.1f}%)")
            sys.stdout.flush()

    if not found_flag:
        print("\nNo flag found in brute force search!")
        print("This might mean:")
        print("1. The flag validation logic is too restrictive")
        print("2. The flag uses non-standard format")
        print("Let's try a more comprehensive search...")

        # Second pass with looser criteria
        print("\nRunning comprehensive search...")
        for key in range(total_keys):
            keystream = keystream_bytes(key, nonce, len(ciphertext))
            plaintext = bytes([c ^ k for c, k in zip(ciphertext, keystream)])

            try:
                decoded = plaintext.decode('ascii')
                # Just check if it's printable and looks reasonable
                if len(decoded.split()) <= 10 and any(char.isalpha() for char in decoded):
                    print(f"Key 0x{key:06x}: '{decoded}'")
            except:
                continue
    else:
        return found_flag

if __name__ == "__main__":
    result = optimized_brute_force()
    if result:
        key, flag = result
        print(f"\n✅ SUCCESS: Flag found with key 0x{key:06x}")
        print(f"✅ FLAG: {flag}")
    else:
        print("\n❌ No valid flag found")