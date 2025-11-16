#!/usr/bin/env python3
"""
Author: Claude Code
Purpose: Exhaustive brute-force - try every 16-byte substring as key
Created: 2025-11-10
Last Updated: 2025-11-10

Assumptions:
- Key is somewhere in the combined UID+OTP data
- Trying all possible 16-byte windows

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

print("Exhaustive brute-force of all 16-byte windows...")
print("="*60)

# Combine all data sources
combined_data = uid + otp_data  # 12 + 32 = 44 bytes total

# Also try reversed versions
combined_reversed = combined_data[::-1]
uid_reversed = uid[::-1]
otp_reversed = otp_data[::-1]

all_data_sources = [
    ("UID+OTP", combined_data),
    ("OTP+UID", otp_data + uid),
    ("UID+OTP reversed", combined_reversed),
    ("OTP alone", otp_data),
    ("OTP reversed", otp_reversed),
]

# IV candidates
iv_candidates = [
    ("secret.enc[:16]", encrypted_data[:16]),
    ("secret.enc[16:]", encrypted_data[16:]),
    ("Zero IV", b'\x00' * 16),
]

# Ciphertext candidates
ct_candidates = [
    ("secret.enc[16:]", encrypted_data[16:]),
    ("full secret.enc", encrypted_data),
]

print(f"\nTrying all 16-byte windows from multiple data sources...")

found = False
for data_name, data in all_data_sources:
    if found:
        break

    # Try every possible 16-byte window
    for i in range(len(data) - 15):
        key = data[i:i+16]

        for iv_name, iv in iv_candidates:
            for ct_name, ct in ct_candidates:
                try:
                    cipher = AES.new(key, AES.MODE_CBC, iv)
                    plaintext = cipher.decrypt(ct)

                    # Check if it looks like valid ASCII
                    if len(plaintext) >= 10 and all(32 <= b < 127 or b in [9, 10, 13, 0] for b in plaintext[:min(20, len(plaintext))]):
                        print(f"\n[VALID ASCII FOUND]")
                        print(f"Data source: {data_name}")
                        print(f"Key offset: {i}")
                        print(f"Key: {key.hex()}")
                        print(f"IV: {iv_name}")
                        print(f"CT: {ct_name}")
                        print(f"Plaintext: {plaintext}")

                        # Check for flag
                        text = plaintext.decode('ascii', errors='ignore').rstrip('\x00')
                        if 'POCTF{' in text or 'flag{' in text.lower() or 'ctf{' in text.lower():
                            print(f"\n*** FLAG FOUND: {text} ***")
                            found = True
                            break
                except:
                    pass

                if found:
                    break
            if found:
                break

if not found:
    print("\n[INFO] No flag found in exhaustive search.")

print("\n" + "="*60)
