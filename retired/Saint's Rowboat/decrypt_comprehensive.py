#!/usr/bin/env python3
"""
Author: Claude Code
Purpose: Comprehensive brute-force of all key/IV combinations
Created: 2025-11-10
Last Updated: 2025-11-10

Assumptions:
- Testing all reasonable combinations systematically

Expected Result: Decrypt the flag
Produced Result: (to be updated after execution)
"""

from Crypto.Cipher import AES
import hashlib
import itertools

# Read the data files
with open('otp_dump.bin', 'rb') as f:
    otp_data = f.read()

with open('secret.enc', 'rb') as f:
    encrypted_data = f.read()

# Parse UID
uid_hex = "5a928ebd3f5729b548b77e73"
uid = bytes.fromhex(uid_hex)

print("Comprehensive key/IV testing...")
print("="*60)

# Build all possible key candidates (16 bytes each)
key_candidates = []

# Direct extractions from OTP
key_candidates.append(("OTP[:16]", otp_data[:16]))
key_candidates.append(("OTP[16:]", otp_data[16:]))

# UID-based
uid_ext1 = uid + uid[:4]
uid_ext2 = uid + b'\x00' * 4
key_candidates.append(("UID + first 4 repeated", uid_ext1))
key_candidates.append(("UID + zero pad", uid_ext2))

# XOR combinations
for i in range(0, 17):
    xor_key = bytes([otp_data[i+j] ^ uid[j % 12] for j in range(16)])
    key_candidates.append((f"OTP[{i}:{i+16}] XOR UID", xor_key))

# Hashes
key_candidates.append(("SHA256(UID)[:16]", hashlib.sha256(uid).digest()[:16]))
key_candidates.append(("SHA256(OTP)[:16]", hashlib.sha256(otp_data).digest()[:16]))
key_candidates.append(("SHA256(UID||OTP)[:16]", hashlib.sha256(uid + otp_data).digest()[:16]))
key_candidates.append(("MD5(UID)", hashlib.md5(uid).digest()))
key_candidates.append(("MD5(OTP)", hashlib.md5(otp_data).digest()))

# Build all possible IV candidates (16 bytes each)
iv_candidates = []

# Direct extractions
iv_candidates.append(("secret.enc[:16]", encrypted_data[:16]))
iv_candidates.append(("secret.enc[16:]", encrypted_data[16:]))
iv_candidates.append(("OTP[:16]", otp_data[:16]))
iv_candidates.append(("OTP[16:]", otp_data[16:]))
iv_candidates.append(("UID extended", uid_ext1))
iv_candidates.append(("UID zero-pad", uid_ext2))
iv_candidates.append(("Zero IV", b'\x00' * 16))

# Hashes
iv_candidates.append(("SHA256(UID)[:16]", hashlib.sha256(uid).digest()[:16]))
iv_candidates.append(("MD5(UID)", hashlib.md5(uid).digest()))

# Build ciphertext candidates
ct_candidates = []
ct_candidates.append(("secret.enc[16:]", encrypted_data[16:]))
ct_candidates.append(("entire secret.enc", encrypted_data))
ct_candidates.append(("secret.enc[:16]", encrypted_data[:16]))

# Try all combinations
print(f"\nTrying {len(key_candidates)} keys x {len(iv_candidates)} IVs x {len(ct_candidates)} ciphertexts")
print(f"Total combinations: {len(key_candidates) * len(iv_candidates) * len(ct_candidates)}")
print("(Only showing promising results...)\n")

found = False
for (key_name, key), (iv_name, iv), (ct_name, ct) in itertools.product(key_candidates, iv_candidates, ct_candidates):
    try:
        cipher = AES.new(key, AES.MODE_CBC, iv)
        plaintext = cipher.decrypt(ct)

        # Check if it looks like valid text
        if len(plaintext) >= 8 and all(32 <= b < 127 or b in [9, 10, 13] for b in plaintext[:min(len(plaintext), 16)]):
            print(f"\n[POTENTIALLY VALID]")
            print(f"Key: {key_name} = {key.hex()}")
            print(f"IV: {iv_name} = {iv.hex()}")
            print(f"CT: {ct_name}")
            print(f"Plaintext: {plaintext}")

            # Check for flag format
            try:
                text = plaintext.decode('ascii', errors='ignore')
                if 'POCTF{' in text or 'flag{' in text.lower() or 'ctf{' in text.lower():
                    print(f"\n*** FLAG FOUND: {text} ***")
                    found = True
                    break
            except:
                pass

    except Exception as e:
        pass

    if found:
        break

if not found:
    print("\n[INFO] No flag found after comprehensive search.")

print("\n" + "="*60)
