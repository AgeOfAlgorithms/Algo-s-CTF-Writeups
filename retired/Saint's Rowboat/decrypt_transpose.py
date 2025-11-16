#!/usr/bin/env python3
"""
Author: Claude Code
Purpose: Try transpose-based key derivation
Created: 2025-11-10
Last Updated: 2025-11-10

Assumptions:
- "Rowboat" hint suggests row/column matrix operations
- Trying transposed OTP as key source

Expected Result: Decrypt the flag
Produced Result: (to be updated after execution)
"""

from Crypto.Cipher import AES

# Read the data files
with open('otp_dump.bin', 'rb') as f:
    otp_data = f.read()

with open('secret.enc', 'rb') as f:
    encrypted_data = f.read()

# Parse UID
uid_hex = "5a928ebd3f5729b548b77e73"
uid = bytes.fromhex(uid_hex)

print("Testing transpose-based key derivation...")
print("="*60)

# Extract IV and ciphertext
iv = encrypted_data[:16]
ciphertext = encrypted_data[16:]

# Transpose OTP (treating as 4x8 matrix)
matrix = []
for row in range(4):
    matrix.append(list(otp_data[row*8:(row+1)*8]))

transposed = [[matrix[row][col] for row in range(4)] for col in range(8)]
transposed_bytes = bytes([b for row in transposed for b in row])

print(f"\nOriginal OTP: {otp_data.hex()}")
print(f"Transposed OTP: {transposed_bytes.hex()}")

# Try transposed data as key
attempts = [
    ("Transposed first 16", transposed_bytes[:16]),
    ("Transposed last 16", transposed_bytes[16:]),
]

# Also try different transpose dimensions
# 8x4 transpose
matrix2 = []
for row in range(8):
    matrix2.append(list(otp_data[row*4:(row+1)*4]))

transposed2 = [[matrix2[row][col] for row in range(8)] for col in range(4)]
transposed_bytes2 = bytes([b for row in transposed2 for b in row])
attempts.append(("8x4 Transposed first 16", transposed_bytes2[:16]))
attempts.append(("8x4 Transposed last 16", transposed_bytes2[16:]))

# 2x16 transpose
matrix3 = []
for row in range(2):
    matrix3.append(list(otp_data[row*16:(row+1)*16]))

transposed3 = [[matrix3[row][col] for row in range(2)] for col in range(16)]
transposed_bytes3 = bytes([b for row in transposed3 for b in row])
attempts.append(("2x16 Transposed first 16", transposed_bytes3[:16]))
attempts.append(("2x16 Transposed last 16", transposed_bytes3[16:]))

# Try each transposed key
for method_name, key in attempts:
    try:
        cipher = AES.new(key, AES.MODE_CBC, iv)
        plaintext = cipher.decrypt(ciphertext)

        print(f"\n[ATTEMPT] Method: {method_name}")
        print(f"Key: {key.hex()}")
        print(f"Plaintext (hex): {plaintext.hex()}")

        # Check if it looks like valid text
        if all(32 <= b < 127 or b in [9, 10, 13] for b in plaintext):
            print(f"Plaintext (ASCII): {plaintext}")

            # Check for flag format
            text = plaintext.decode('ascii', errors='ignore')
            if 'POCTF{' in text or 'flag{' in text.lower() or 'ctf{' in text.lower():
                print(f"\n*** FLAG FOUND: {text} ***")
                break
        else:
            # Show partial decode
            decoded = plaintext.decode('ascii', errors='replace')
            print(f"Partial decode: {decoded}")

    except Exception as e:
        print(f"\n[ERROR] Method: {method_name} - {e}")

print("\n" + "="*60)
