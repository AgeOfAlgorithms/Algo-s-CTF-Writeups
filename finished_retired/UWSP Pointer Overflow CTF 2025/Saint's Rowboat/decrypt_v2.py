#!/usr/bin/env python3
"""
Author: Claude Code
Purpose: Decrypt secret.enc - trying alternative IV/key derivation methods
Created: 2025-11-10
Last Updated: 2025-11-10

Assumptions:
- Trying different interpretations of where IV comes from
- Key might be in OTP, IV might be derived

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

print("Testing alternative IV/key combinations...")
print("="*60)

attempts = []

# Scenario 1: secret.enc is pure ciphertext, IV derived from UID
# Try different key sources from OTP
for key_source in [otp_data[:16], otp_data[16:], hashlib.sha256(otp_data).digest()[:16]]:
    # Try different IV derivations from UID
    iv_options = [
        uid + b'\x00' * 4,  # UID zero-padded
        uid + otp_data[:4],  # UID + first 4 of OTP
        hashlib.sha256(uid).digest()[:16],  # SHA256(UID)
        hashlib.md5(uid).digest(),  # MD5(UID)
    ]

    for iv in iv_options:
        attempts.append((key_source, iv, encrypted_data))

# Scenario 2: First 16 of secret.enc is IV, last 16 is ciphertext (original assumption)
iv_from_enc = encrypted_data[:16]
ct_from_enc = encrypted_data[16:]

for key_source in [
    otp_data[:16],
    otp_data[16:],
    hashlib.sha256(otp_data).digest()[:16],
    hashlib.sha256(uid).digest()[:16],
    hashlib.sha256(uid + otp_data).digest()[:16],
]:
    attempts.append((key_source, iv_from_enc, ct_from_enc))

# Scenario 3: Last 16 of secret.enc is IV, first 16 is ciphertext
iv_from_enc2 = encrypted_data[16:]
ct_from_enc2 = encrypted_data[:16]

for key_source in [otp_data[:16], otp_data[16:]]:
    attempts.append((key_source, iv_from_enc2, ct_from_enc2))

# Scenario 4: OTP contains both key and IV
# [16 bytes IV][16 bytes key]
key_from_otp_end = otp_data[16:]
iv_from_otp_start = otp_data[:16]
attempts.append((key_from_otp_end, iv_from_otp_start, encrypted_data))

# [16 bytes key][16 bytes IV]
key_from_otp_start = otp_data[:16]
iv_from_otp_end = otp_data[16:]
attempts.append((key_from_otp_start, iv_from_otp_end, encrypted_data))

# Try all combinations
success_found = False
for i, (key, iv, ciphertext) in enumerate(attempts):
    try:
        cipher = AES.new(key, AES.MODE_CBC, iv)
        plaintext = cipher.decrypt(ciphertext)

        # Check if it looks like valid text
        if all(32 <= b < 127 or b in [9, 10, 13] for b in plaintext[:16]):  # Check first 16 bytes
            print(f"\n[POTENTIALLY VALID] Attempt {i+1}")
            print(f"Key: {key.hex()}")
            print(f"IV: {iv.hex()}")
            print(f"Plaintext: {plaintext}")
            print(f"Plaintext (hex): {plaintext.hex()}")

            # Check for flag format
            text = plaintext.decode('ascii', errors='ignore')
            if 'POCTF{' in text or 'flag{' in text.lower() or 'ctf{' in text.lower():
                print(f"\n*** FLAG FOUND: {text} ***")
                success_found = True
                break
    except Exception as e:
        pass

if not success_found:
    print("\n[INFO] No obvious flag found. Let me try XOR-based key derivation...")

    # Try XOR combinations between UID and OTP
    xor_keys = []

    # XOR UID with different parts of OTP
    for offset in range(0, 20, 4):  # Try different offsets
        xor_result = bytes([uid[i % 12] ^ otp_data[(offset + i) % 32] for i in range(16)])
        xor_keys.append(xor_result)

    for key in xor_keys:
        for iv in [encrypted_data[:16], otp_data[:16], uid + b'\x00' * 4]:
            try:
                cipher = AES.new(key, AES.MODE_CBC, iv)
                plaintext = cipher.decrypt(encrypted_data[16:] if len(iv) == 16 else encrypted_data)

                if all(32 <= b < 127 or b in [9, 10, 13] for b in plaintext[:min(16, len(plaintext))]):
                    print(f"\n[XOR METHOD FOUND SOMETHING]")
                    print(f"Key: {key.hex()}")
                    print(f"IV: {iv.hex()}")
                    print(f"Plaintext: {plaintext}")

                    text = plaintext.decode('ascii', errors='ignore')
                    if 'POCTF{' in text or 'flag' in text.lower():
                        print(f"\n*** FLAG FOUND: {text} ***")
                        success_found = True
                        break
            except:
                pass
        if success_found:
            break

print("\n" + "="*60)
print("Decryption complete")
print("="*60)
