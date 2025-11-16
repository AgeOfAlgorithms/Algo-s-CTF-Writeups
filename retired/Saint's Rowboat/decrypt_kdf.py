#!/usr/bin/env python3
"""
Author: Claude Code
Purpose: Try standard KDF functions (PBKDF2, HKDF) for key derivation
Created: 2025-11-10
Last Updated: 2025-11-10

Assumptions:
- Trying PBKDF2, HKDF, and other standard KDFs
- Also trying byte order manipulations

Expected Result: Decrypt the flag
Produced Result: (to be updated after execution)
"""

from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2, HKDF
from Crypto.Hash import SHA256, SHA1, MD5
import hashlib

# Read the data files
with open('otp_dump.bin', 'rb') as f:
    otp_data = f.read()

with open('secret.enc', 'rb') as f:
    encrypted_data = f.read()

# Parse UID
uid_hex = "5a928ebd3f5729b548b77e73"
uid = bytes.fromhex(uid_hex)

print("Testing KDF-based key derivation...")
print("="*60)

# Extract IV and ciphertext (assuming first 16 bytes are IV)
iv = encrypted_data[:16]
ciphertext = encrypted_data[16:]

attempts = []

# PBKDF2 attempts with various parameters
for iterations in [1000, 10000, 100000, 1, 100]:
    # Using UID as password, OTP as salt
    try:
        key = PBKDF2(uid, otp_data, dkLen=16, count=iterations, hmac_hash_module=SHA256)
        attempts.append((f"PBKDF2(UID, OTP_salt, iter={iterations}, SHA256)", key, iv, ciphertext))
    except:
        pass

    # Using OTP as password, UID as salt
    try:
        key = PBKDF2(otp_data, uid, dkLen=16, count=iterations, hmac_hash_module=SHA256)
        attempts.append((f"PBKDF2(OTP, UID_salt, iter={iterations}, SHA256)", key, iv, ciphertext))
    except:
        pass

# HKDF attempts
try:
    # Using UID as input key material, OTP as salt
    key = HKDF(uid, 16, otp_data, SHA256)
    attempts.append(("HKDF(UID_ikm, OTP_salt, SHA256)", key, iv, ciphertext))
except:
    pass

try:
    # Using OTP as input key material, UID as salt
    key = HKDF(otp_data, 16, uid, SHA256)
    attempts.append(("HKDF(OTP_ikm, UID_salt, SHA256)", key, iv, ciphertext))
except:
    pass

# Try byte-reversed OTP
otp_reversed = otp_data[::-1]
attempts.append(("OTP reversed (first 16)", otp_reversed[:16], iv, ciphertext))
attempts.append(("OTP reversed (last 16)", otp_reversed[16:], iv, ciphertext))

# Try treating OTP as little-endian 32-bit words and swap to big-endian
import struct
otp_words = struct.unpack('<8I', otp_data)  # 8 little-endian 32-bit ints
otp_swapped = struct.pack('>8I', *otp_words)  # Convert to big-endian
attempts.append(("OTP endian-swapped (first 16)", otp_swapped[:16], iv, ciphertext))
attempts.append(("OTP endian-swapped (last 16)", otp_swapped[16:], iv, ciphertext))

# Try different interpretations of secret.enc structure
# What if the whole thing is ciphertext and IV comes from elsewhere?
for key_candidate in [otp_data[:16], otp_data[16:]]:
    for iv_candidate in [
        uid + b'\x00' * 4,
        hashlib.sha256(uid).digest()[:16],
        otp_data[:16],
        otp_data[16:],
    ]:
        attempts.append(("Alternative IV interpretation", key_candidate, iv_candidate, encrypted_data))

# Try each combination
success_found = False
for method_name, key, test_iv, test_ct in attempts:
    try:
        cipher = AES.new(key, AES.MODE_CBC, test_iv)
        plaintext = cipher.decrypt(test_ct)

        # Check if it looks like valid text
        if all(32 <= b < 127 or b in [9, 10, 13] for b in plaintext[:min(16, len(plaintext))]):
            print(f"\n[POTENTIALLY VALID] Method: {method_name}")
            print(f"Key: {key.hex()}")
            print(f"IV: {test_iv.hex()}")
            print(f"Plaintext: {plaintext}")

            # Check for flag format
            text = plaintext.decode('ascii', errors='ignore')
            if 'POCTF{' in text or 'flag{' in text.lower() or 'ctf{' in text.lower():
                print(f"\n*** FLAG FOUND: {text} ***")
                success_found = True
                break
    except Exception as e:
        pass

    if success_found:
        break

if not success_found:
    print("\n[INFO] No flag found with standard KDF methods.")

print("\n" + "="*60)
print("Decryption attempts complete")
print("="*60)
