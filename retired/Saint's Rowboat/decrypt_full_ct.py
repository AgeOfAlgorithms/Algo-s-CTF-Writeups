#!/usr/bin/env python3
"""
Author: Claude Code
Purpose: Try interpreting entire secret.enc as ciphertext, derive both key and IV
Created: 2025-11-10
Last Updated: 2025-11-10

Assumptions:
- Entire 32 bytes of secret.enc might be ciphertext
- Both key and IV derived from UID/OTP

Expected Result: Decrypt the flag
Produced Result: (to be updated after execution)
"""

from Crypto.Cipher import AES
import hashlib

# Read the data files
with open('otp_dump.bin', 'rb') as f:
    otp_data = f.read()

with open('secret.enc', 'rb') as f:
    encrypted_data = f.read()  # All 32 bytes as ciphertext

# Parse UID
uid_hex = "5a928ebd3f5729b548b77e73"
uid = bytes.fromhex(uid_hex)

print("Testing with entire secret.enc as ciphertext...")
print("="*60)

# Build key/IV pairs
pairs = []

# Pair 1: First half of OTP as key, second half as IV
pairs.append(("OTP[:16] key, OTP[16:] IV", otp_data[:16], otp_data[16:]))

# Pair 2: Second half as key, first half as IV
pairs.append(("OTP[16:] key, OTP[:16] IV", otp_data[16:], otp_data[:16]))

# Pair 3: First half as key, UID as IV (extended)
uid_iv = uid + uid[:4]
pairs.append(("OTP[:16] key, UID IV", otp_data[:16], uid_iv))

# Pair 4: Second half as key, UID as IV
pairs.append(("OTP[16:] key, UID IV", otp_data[16:], uid_iv))

# Pair 5: Hash-based
key_hash = hashlib.sha256(otp_data).digest()[:16]
iv_hash = hashlib.sha256(uid).digest()[:16]
pairs.append(("SHA256(OTP) key, SHA256(UID) IV", key_hash, iv_hash))

# Pair 6: Swap
pairs.append(("SHA256(UID) key, SHA256(OTP) IV", iv_hash, key_hash))

# Pair 7: XOR-based
xor_key = bytes([otp_data[i] ^ uid[i % 12] for i in range(16)])
xor_iv = bytes([otp_data[16+i] ^ uid[i % 12] for i in range(16)])
pairs.append(("XOR key, XOR IV", xor_key, xor_iv))

# Pair 8: MD5-based
key_md5 = hashlib.md5(otp_data).digest()
iv_md5 = hashlib.md5(uid).digest()
pairs.append(("MD5(OTP) key, MD5(UID) IV", key_md5, iv_md5))

# Pair 9: Combined hash
combined = uid + otp_data
key_comb = hashlib.sha256(combined).digest()[:16]
iv_comb = hashlib.sha256(combined).digest()[16:32]
pairs.append(("SHA256(UID||OTP)[:16] key, [16:32] IV", key_comb, iv_comb))

# Pair 10: Zero IV with various keys
for key_name, key_val in [
    ("OTP[:16]", otp_data[:16]),
    ("OTP[16:]", otp_data[16:]),
    ("SHA256(OTP)[:16]", hashlib.sha256(otp_data).digest()[:16]),
]:
    pairs.append((f"{key_name} key, Zero IV", key_val, b'\x00' * 16))

# Try each pair
for name, key, iv in pairs:
    try:
        cipher = AES.new(key, AES.MODE_CBC, iv)
        plaintext = cipher.decrypt(encrypted_data)

        # Check if it looks like valid text (check more bytes since we have 32)
        if all(32 <= b < 127 or b in [9, 10, 13, 0] for b in plaintext[:24]):
            print(f"\n[POTENTIALLY VALID] {name}")
            print(f"Key: {key.hex()}")
            print(f"IV: {iv.hex()}")
            print(f"Plaintext: {plaintext}")

            # Check for flag format
            text = plaintext.decode('ascii', errors='ignore').rstrip('\x00')
            if 'POCTF{' in text or 'flag{' in text.lower() or 'ctf{' in text.lower():
                print(f"\n*** FLAG FOUND: {text} ***")
                break

    except Exception as e:
        pass

print("\n" + "="*60)
