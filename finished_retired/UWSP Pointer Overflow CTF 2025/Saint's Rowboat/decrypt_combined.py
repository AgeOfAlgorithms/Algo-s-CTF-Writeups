#!/usr/bin/env python3
"""
Author: Claude Code
Purpose: Combine UID with transposed OTP for key derivation
Created: 2025-11-10
Last Updated: 2025-11-10

Assumptions:
- Need to combine both UID and OTP (transposed)
- Trying various combination methods

Expected Result: Decrypt the flag
Produced Result: (to be updated after execution)
"""

from Crypto.Cipher import AES
import hashlib

# Read the data files
with open('otp_dump.bin', 'rb') as f:
    otp_data = f.read()

with open('secret.enc', 'rb') as f:
    encrypted_data = f.read()

# Parse UID
uid_hex = "5a928ebd3f5729b548b77e73"
uid = bytes.fromhex(uid_hex)

print("Testing combined UID + transposed OTP...")
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

print(f"UID: {uid.hex()}")
print(f"Transposed OTP: {transposed_bytes.hex()}")

attempts = []

# Method 1: XOR UID with first 12 bytes of transposed OTP, extend to 16
xor_key1 = bytes([uid[i] ^ transposed_bytes[i] for i in range(12)])
xor_key1_ext = xor_key1 + transposed_bytes[12:16]
attempts.append(("XOR(UID, Transposed[:12]) + Transposed[12:16]", xor_key1_ext))

# Method 2: XOR UID with last 12 bytes of first 16 of transposed
xor_key2 = bytes([uid[i] ^ transposed_bytes[4+i] for i in range(12)])
xor_key2_ext = transposed_bytes[:4] + xor_key2
attempts.append(("Transposed[:4] + XOR(UID, Transposed[4:16])", xor_key2_ext))

# Method 3: SHA256(UID || transposed)
key3 = hashlib.sha256(uid + transposed_bytes).digest()[:16]
attempts.append(("SHA256(UID || Transposed)[:16]", key3))

# Method 4: SHA256(transposed || UID)
key4 = hashlib.sha256(transposed_bytes + uid).digest()[:16]
attempts.append(("SHA256(Transposed || UID)[:16]", key4))

# Method 5: XOR UID with second half of transposed
xor_key5 = bytes([uid[i] ^ transposed_bytes[16+i] for i in range(12)])
xor_key5_ext = xor_key5 + transposed_bytes[28:32]
attempts.append(("XOR(UID, Transposed[16:28]) + Transposed[28:32]", xor_key5_ext))

# Method 6: Try different transpositions with UID
# 8x4 transpose
matrix2 = []
for row in range(8):
    matrix2.append(list(otp_data[row*4:(row+1)*4]))

transposed2 = [[matrix2[row][col] for row in range(8)] for col in range(4)]
transposed_bytes2 = bytes([b for row in transposed2 for b in row])

xor_key6 = bytes([uid[i] ^ transposed_bytes2[i] for i in range(12)])
xor_key6_ext = xor_key6 + transposed_bytes2[12:16]
attempts.append(("XOR(UID, 8x4_Transposed[:12]) + rest", xor_key6_ext))

# Method 7: Interleave UID and transposed
# Take alternating bytes?
interleaved = bytes([uid[i//2] if i % 2 == 0 and i//2 < 12 else transposed_bytes[i//2 if i % 2 == 0 else i//2] for i in range(16)])
attempts.append(("Interleaved UID and Transposed", interleaved))

# Try each key
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
