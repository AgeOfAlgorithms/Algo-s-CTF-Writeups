#!/usr/bin/env python3
"""
Pale Fire - Test with Actual Challenge Ciphertext
Author: Claude
Purpose: Test decryption with the ACTUAL ciphertext from params endpoint
Created: 2025-11-11
"""

import hashlib

# Challenge parameters (same as before)
p = 0x7fffffff
g = 0x3
A = 0x70b7c967
B = 0x0307f998

# Recovered private keys
a = 58363728
b = 1985647519

# NEW CIPHERTEXT from params endpoint (not the README static one!)
ciphertext = 0xc1440a2d7cd4f59bdc6340f971831cf173aa8867a501

def try_decrypt(key_bytes, method_name):
    """Try to decrypt ciphertext with given key bytes"""
    ct_bytes = ciphertext.to_bytes(22, 'big')

    if len(key_bytes) < len(ct_bytes):
        key_repeated = (key_bytes * ((len(ct_bytes) // len(key_bytes)) + 1))[:len(ct_bytes)]
    else:
        key_repeated = key_bytes[:len(ct_bytes)]

    plaintext = bytes([ct_bytes[i] ^ key_repeated[i] for i in range(len(ct_bytes))])

    try:
        decoded = plaintext.decode('ascii')
        if 'poctf' in decoded.lower() or ('{' in decoded and '}' in decoded):
            print(f"\n{'='*60}")
            print(f"*** POSSIBLE FLAG FOUND with {method_name} ***")
            print(f"Plaintext: {decoded}")
            print(f"{'='*60}\n")
            return decoded
    except:
        # Try to print partial printables if decode fails
        printable = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in plaintext)
        # If significant portion is printable, show it
        if sum(1 for b in plaintext if 32 <= b <= 126) >= 15:
            print(f"\n[{method_name}] Partial readable: {printable}")

    return None

print("="*70)
print("Testing with ACTUAL ciphertext from params endpoint")
print("="*70)
print(f"Ciphertext: {hex(ciphertext)}")

candidate_secrets = {
    "B^a mod p (standard)": pow(B, a, p),
    "A^b mod p (cross-gen)": pow(A, b, p),
    "g^(ab mod (p-1))": pow(g, (a*b) % (p-1), p),
    "7^(ab mod (p-1))": pow(7, (a*b) % (p-1), p),
    "A XOR B": A ^ B,
    "(A+B) mod p": (A+B) % p,
    "(A*B) mod p": (A*B) % p,
}

print("\n" + "-"*70)
print("Testing standard XOR approach:")
print("-"*70)

for name, value in candidate_secrets.items():
    secret_bytes = value.to_bytes((value.bit_length() + 7) // 8, 'big')
    result = try_decrypt(secret_bytes, f"{name} (direct)")
    if result:
        print(f"\n{'!'*70}")
        print(f"SUCCESS! Flag found: {result}")
        print(f"{'!'*70}")
        exit(0)

# Try with different hash functions
print("\n" + "-"*70)
print("Testing with hash derivations:")
print("-"*70)

for name, value in candidate_secrets.items():
    secret_bytes = value.to_bytes((value.bit_length() + 7) // 8, 'big')

    # SHA256
    result = try_decrypt(hashlib.sha256(secret_bytes).digest(), f"{name} (SHA256)")
    if result: exit(0)

    # MD5
    result = try_decrypt(hashlib.md5(secret_bytes).digest(), f"{name} (MD5)")
    if result: exit(0)

    # SHA1
    result = try_decrypt(hashlib.sha1(secret_bytes).digest(), f"{name} (SHA1)")
    if result: exit(0)

# Try literal string keys
print("\n" + "-"*70)
print("Testing common string keys:")
print("-"*70)

simple_keys = ["palefire", "Pale Fire", "nabokov", "999",
               "key", "password", "secret", "diffie-hellman", "dh"]

for key_str in simple_keys:
    key_bytes = key_str.encode('ascii')
    try_decrypt(key_bytes, f"simple key '{key_str}'")

    # Also try with hash
    try_decrypt(hashlib.sha256(key_bytes).digest(), f"SHA256('{key_str}')")

# Single byte XOR
print("\n" + "-"*70)
print("Testing single-byte XOR:")
print("-"*70)

for key_byte in range(256):
    ct_bytes = ciphertext.to_bytes(22, 'big')
    plaintext = bytes([b ^ key_byte for b in ct_bytes])

    printable = sum(1 for b in plaintext if 32 <= b <= 126)

    if printable >= 20:  # If almost entirely printable
        try:
            decoded = plaintext.decode('ascii')
            if 'poctf' in decoded.lower():
                print(f"\n{'!'*70}")
                print(f"SUCCESS! Single-byte XOR key: {key_byte} (0x{key_byte:02x})")
                print(f"Flag: {decoded}")
                print(f"{'!'*70}")
                exit(0)
        except:
            printable_text = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in plaintext)
            if 'poctf' in printable_text.lower():
                print(f"Potential partial match key={key_byte}: {printable_text}")

print("\n" + "="*70)
print("No flag found with initial tests")
print("Consider: Stream cipher, custom XOR, or connections to actual service")
print("="*70)
