#!/usr/bin/env python3
"""
Author: Claude Code
Purpose: Decrypt secret.enc using STM32 UID and OTP dump
Created: 2025-11-10
Last Updated: 2025-11-10

Assumptions:
- AES-128-CBC encryption is used
- The key is derived from the 96-bit UID and/or 32-byte OTP dump
- secret.enc contains: [16-byte IV][16-byte ciphertext]

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

# Parse UID from the log/txt file (96 bits = 12 bytes)
uid_hex = "5a928ebd3f5729b548b77e73"
uid = bytes.fromhex(uid_hex)

print(f"UID (12 bytes): {uid.hex()}")
print(f"OTP dump (32 bytes): {otp_data.hex()}")
print(f"Encrypted data (32 bytes): {encrypted_data.hex()}")

# Extract IV and ciphertext from secret.enc
iv = encrypted_data[:16]
ciphertext = encrypted_data[16:]

print(f"\nIV (16 bytes): {iv.hex()}")
print(f"Ciphertext (16 bytes): {ciphertext.hex()}")

# Try different key derivation methods
print("\n" + "="*60)
print("Attempting various key derivation methods...")
print("="*60)

attempts = []

# Method 1: First 16 bytes of OTP as key
key1 = otp_data[:16]
attempts.append(("First 16 bytes of OTP", key1))

# Method 2: Last 16 bytes of OTP as key
key2 = otp_data[16:]
attempts.append(("Last 16 bytes of OTP", key2))

# Method 3: XOR UID with first 12 bytes of OTP, then pad/extend
# This is common in embedded systems
otp_part = otp_data[:12]
xor_result = bytes([uid[i] ^ otp_part[i] for i in range(12)])
# Need to extend to 16 bytes - try padding with last 4 bytes of OTP
key3 = xor_result + otp_data[12:16]
attempts.append(("XOR(UID, OTP[:12]) + OTP[12:16]", key3))

# Method 4: SHA256(UID)[:16]
key4 = hashlib.sha256(uid).digest()[:16]
attempts.append(("SHA256(UID)[:16]", key4))

# Method 5: SHA256(UID || OTP)[:16]
key5 = hashlib.sha256(uid + otp_data).digest()[:16]
attempts.append(("SHA256(UID || OTP)[:16]", key5))

# Method 6: SHA256(OTP)[:16]
key6 = hashlib.sha256(otp_data).digest()[:16]
attempts.append(("SHA256(OTP)[:16]", key6))

# Method 7: UID padded to 16 bytes with zeros
key7 = uid + b'\x00' * 4
attempts.append(("UID + zero padding", key7))

# Method 8: UID padded with first 4 bytes of OTP
key8 = uid + otp_data[:4]
attempts.append(("UID + OTP[:4]", key8))

# Method 9: XOR UID with OTP and pad with zeros
xor_result2 = bytes([uid[i] ^ otp_data[i] for i in range(12)])
key9 = xor_result2 + b'\x00' * 4
attempts.append(("XOR(UID, OTP[:12]) + zero pad", key9))

# Try each key
for method_name, key in attempts:
    try:
        cipher = AES.new(key, AES.MODE_CBC, iv)
        plaintext = cipher.decrypt(ciphertext)

        # Check if it looks like valid text (printable ASCII or flag format)
        if all(32 <= b < 127 or b in [9, 10, 13] for b in plaintext):
            print(f"\n[SUCCESS] Method: {method_name}")
            print(f"Key: {key.hex()}")
            print(f"Plaintext: {plaintext}")
            print(f"Plaintext (hex): {plaintext.hex()}")

            # Check if it's a flag format
            if b'flag{' in plaintext.lower() or b'ctf{' in plaintext.lower() or b'POCTF{' in plaintext:
                print(f"\n*** FLAG FOUND: {plaintext.decode('ascii', errors='ignore')} ***")
                break
        else:
            # Still show attempts that might be close
            print(f"\n[ATTEMPT] Method: {method_name}")
            print(f"Key: {key.hex()}")
            print(f"Plaintext (hex): {plaintext.hex()}")
            # Try to show partial ASCII
            try:
                decoded = plaintext.decode('ascii', errors='replace')
                if 'flag' in decoded.lower() or 'poctf' in decoded.lower():
                    print(f"Partial text: {decoded}")
            except:
                pass
    except Exception as e:
        print(f"\n[ERROR] Method: {method_name} - {e}")

print("\n" + "="*60)
print("Decryption attempts complete")
print("="*60)
