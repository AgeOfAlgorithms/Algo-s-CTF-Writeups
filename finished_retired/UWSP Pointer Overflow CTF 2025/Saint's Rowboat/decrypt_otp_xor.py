#!/usr/bin/env python3
"""
Author: Claude Code
Purpose: Try using UID as one-time pad to decrypt key from OTP
Created: 2025-11-10
Last Updated: 2025-11-10

Assumptions:
- OTP might contain the key encrypted with UID
- UID acts as a one-time pad (XOR mask)

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

print("Testing OTP XOR UID as key derivation...")
print("="*60)

# Extract IV and ciphertext
iv = encrypted_data[:16]
ciphertext = encrypted_data[16:]

attempts = []

# Method 1: XOR first 16 bytes of OTP with UID (extended)
uid_extended = uid + uid[:4]  # 12 + 4 = 16 bytes
key1 = bytes([otp_data[i] ^ uid_extended[i] for i in range(16)])
attempts.append(("OTP[:16] XOR UID_extended", key1))

# Method 2: XOR last 16 bytes of OTP with UID (extended)
key2 = bytes([otp_data[16+i] ^ uid_extended[i] for i in range(16)])
attempts.append(("OTP[16:] XOR UID_extended", key2))

# Method 3: Extend UID differently (repeat pattern)
uid_pattern = (uid * 2)[:16]  # Repeat UID pattern to get 16 bytes
key3 = bytes([otp_data[i] ^ uid_pattern[i] for i in range(16)])
attempts.append(("OTP[:16] XOR UID_pattern", key3))

key4 = bytes([otp_data[16+i] ^ uid_pattern[i] for i in range(16)])
attempts.append(("OTP[16:] XOR UID_pattern", key4))

# Method 4: Try XORing with UID in different positions
for offset in range(0, 17):  # Try different offsets
    key = bytes([otp_data[offset+i] ^ uid[i % 12] for i in range(16)])
    attempts.append((f"OTP[{offset}:{offset+16}] XOR UID_cyclic", key))

# Try each key
for method_name, key in attempts:
    try:
        cipher = AES.new(key, AES.MODE_CBC, iv)
        plaintext = cipher.decrypt(ciphertext)

        # Only print if it looks promising
        if all(32 <= b < 127 or b in [9, 10, 13] for b in plaintext):
            print(f"\n[POTENTIALLY VALID] Method: {method_name}")
            print(f"Key: {key.hex()}")
            print(f"Plaintext (ASCII): {plaintext}")

            # Check for flag format
            text = plaintext.decode('ascii', errors='ignore')
            if 'POCTF{' in text or 'flag{' in text.lower() or 'ctf{' in text.lower():
                print(f"\n*** FLAG FOUND: {text} ***")
                break

    except Exception as e:
        pass

print("\n" + "="*60)
print("Testing complete")
print("="*60)
