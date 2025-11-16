#!/usr/bin/env python3
"""
Author: Claude Code
Purpose: Try arithmetic operations between UID and OTP words
Created: 2025-11-10
Last Updated: 2025-11-10

Assumptions:
- STM32 uses 32-bit words
- Try ADD, SUB, XOR, etc. at word level

Expected Result: Decrypt the flag
Produced Result: (to be updated after execution)
"""

from Crypto.Cipher import AES
import struct

# Read the data files
with open('otp_dump.bin', 'rb') as f:
    otp_data = f.read()

with open('secret.enc', 'rb') as f:
    encrypted_data = f.read()

# Parse UID (little-endian 32-bit words as STM32 uses)
uid_hex = "5a928ebd3f5729b548b77e73"
uid = bytes.fromhex(uid_hex)

print("Testing arithmetic operations on UID and OTP words...")
print("="*60)

# Extract IV and ciphertext
iv = encrypted_data[:16]
ciphertext = encrypted_data[16:]

# Parse as 32-bit words (little-endian)
uid_words = struct.unpack('<3I', uid)
otp_words = struct.unpack('<8I', otp_data)

print(f"\nUID words (LE): {[hex(w) for w in uid_words]}")
print(f"OTP words (LE): {[hex(w) for w in otp_words]}")

attempts = []

# Method 1: ADD UID words to first 3 OTP words, then use first 4 words as key
key_words = [(otp_words[i] + uid_words[i % 3]) & 0xFFFFFFFF for i in range(4)]
key1 = struct.pack('<4I', *key_words)
attempts.append(("ADD: (OTP[i] + UID[i%3]) for first 4 words", key1))

# Method 2: SUB UID words from first 3 OTP words
key_words2 = [(otp_words[i] - uid_words[i % 3]) & 0xFFFFFFFF for i in range(4)]
key2 = struct.pack('<4I', *key_words2)
attempts.append(("SUB: (OTP[i] - UID[i%3]) for first 4 words", key2))

# Method 3: XOR UID words with first 3 OTP words
key_words3 = [otp_words[i] ^ uid_words[i % 3] for i in range(4)]
key3 = struct.pack('<4I', *key_words3)
attempts.append(("XOR: (OTP[i] ^ UID[i%3]) for first 4 words", key3))

# Method 4: Multiply and take modulo
key_words4 = [(otp_words[i] * uid_words[i % 3]) & 0xFFFFFFFF for i in range(4)]
key4 = struct.pack('<4I', *key_words4)
attempts.append(("MUL: (OTP[i] * UID[i%3]) for first 4 words", key4))

# Try with last 4 OTP words too
key_words5 = [(otp_words[4+i] + uid_words[i % 3]) & 0xFFFFFFFF for i in range(4)]
key5 = struct.pack('<4I', *key_words5)
attempts.append(("ADD: (OTP[4+i] + UID[i%3]) for last 4 words", key5))

key_words6 = [(otp_words[4+i] - uid_words[i % 3]) & 0xFFFFFFFF for i in range(4)]
key6 = struct.pack('<4I', *key_words6)
attempts.append(("SUB: (OTP[4+i] - UID[i%3]) for last 4 words", key6))

key_words7 = [otp_words[4+i] ^ uid_words[i % 3] for i in range(4)]
key7 = struct.pack('<4I', *key_words7)
attempts.append(("XOR: (OTP[4+i] ^ UID[i%3]) for last 4 words", key7))

# Method: Rotate UID words
def rotate_left(val, shift):
    return ((val << shift) | (val >> (32 - shift))) & 0xFFFFFFFF

def rotate_right(val, shift):
    return ((val >> shift) | (val << (32 - shift))) & 0xFFFFFFFF

# Try rotating each UID word by various amounts
for shift in [1, 4, 8, 16]:
    rotated_uid = [rotate_left(w, shift) for w in uid_words]
    key_words_rot = [otp_words[i] ^ rotated_uid[i % 3] for i in range(4)]
    key_rot = struct.pack('<4I', *key_words_rot)
    attempts.append((f"XOR with UID ROL {shift}", key_rot))

# Try each key
for method_name, key in attempts:
    try:
        cipher = AES.new(key, AES.MODE_CBC, iv)
        plaintext = cipher.decrypt(ciphertext)

        # Only show if looks valid
        if all(32 <= b < 127 or b in [9, 10, 13] for b in plaintext):
            print(f"\n[POTENTIALLY VALID] Method: {method_name}")
            print(f"Key: {key.hex()}")
            print(f"Plaintext: {plaintext}")

            # Check for flag format
            text = plaintext.decode('ascii', errors='ignore')
            if 'POCTF{' in text or 'flag{' in text.lower() or 'ctf{' in text.lower():
                print(f"\n*** FLAG FOUND: {text} ***")
                break
    except Exception as e:
        pass

print("\n" + "="*60)
