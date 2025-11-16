#!/usr/bin/env python3
"""
Wiener's Attack on RSA with Small Private Exponent

Author: Claude
Purpose: Exploit RSA vulnerability when d < N^(1/4) using continued fractions
Challenge: This is Not the Way (UWSP Pointer Overflow CTF)
Created: 2025-11-09
Last Updated: 2025-11-09

Assumptions:
- Private exponent d is small enough for Wiener's attack to work
- Server provides valid RSA public key (n, e) and ciphertext
- The attack uses continued fraction expansion of e/n

Expected Result: Recover private key d and decrypt ciphertext to get flag
Produced Result: SUCCESS - Recovered d=995191913291720747743128311991170033204089781785
                FLAG: poctf{uwsp_1v3_b33n_c4ll3d_w0r53}
"""

import base64
from fractions import Fraction
from math import isqrt

def continued_fractions(e, n):
    """
    Generate convergents of the continued fraction expansion of e/n

    Args:
        e: Public exponent
        n: Modulus

    Yields:
        Tuples (k, d) representing convergents
    """
    convergents = []
    quotients = []

    # Generate continued fraction expansion
    a, b = e, n
    while b:
        q = a // b
        quotients.append(q)
        a, b = b, a - q * b

    # Generate convergents from quotients
    for i in range(len(quotients)):
        if i == 0:
            convergents.append((quotients[0], 1))
        elif i == 1:
            convergents.append((quotients[1] * quotients[0] + 1, quotients[1]))
        else:
            num = quotients[i] * convergents[i-1][0] + convergents[i-2][0]
            den = quotients[i] * convergents[i-1][1] + convergents[i-2][1]
            convergents.append((num, den))

    return convergents

def wiener_attack(e, n):
    """
    Perform Wiener's attack to recover private key d

    Args:
        e: Public exponent
        n: Modulus

    Returns:
        Private exponent d if found, None otherwise
    """
    convergents = continued_fractions(e, n)

    for k, d in convergents:
        # Skip invalid cases
        if k == 0 or d == 0:
            continue

        # Check if this convergent gives us valid p and q
        # From ed - 1 = k * phi(n), we have phi(n) = (ed - 1) / k
        if (e * d - 1) % k != 0:
            continue

        phi = (e * d - 1) // k

        # Solve for p and q: p + q = n - phi + 1, p * q = n
        # This gives us: x^2 - (n - phi + 1)x + n = 0
        s = n - phi + 1
        discriminant = s * s - 4 * n

        if discriminant < 0:
            continue

        sqrt_discriminant = isqrt(discriminant)
        if sqrt_discriminant * sqrt_discriminant != discriminant:
            continue

        p = (s + sqrt_discriminant) // 2
        q = (s - sqrt_discriminant) // 2

        # Verify we found the correct factorization
        if p * q == n:
            print(f"[+] Found valid convergent: k={k}, d={d}")
            print(f"[+] Factored n: p={p}, q={q}")
            return d

    return None

def decrypt_rsa(c, d, n):
    """
    Decrypt RSA ciphertext using private exponent

    Args:
        c: Ciphertext (integer)
        d: Private exponent
        n: Modulus

    Returns:
        Plaintext as bytes
    """
    m = pow(c, d, n)

    # Convert integer to bytes
    byte_length = (m.bit_length() + 7) // 8
    plaintext = m.to_bytes(byte_length, byteorder='big')

    return plaintext

def main():
    # Public key data from server
    n_hex = "aaf30f8b829e0b5bb203a19c935fed0df9aea4639842fabf6798bd3231c5107cc5a1299a57b51be9f875ac4751eaa20c43daaa4f7b4a326deb4361a867b907809f6e1d92cf2bb429194df8fcc3f9410acb4e0c60eeb8a505e3c3a8943ff48a36e4de4ff1d50fde8ccaf38183ea9cd9192f9562fbf0072740cffde27e607ebf55"
    e_hex = "6837148823c3bfda827b7ca6e7b545888e0d5c28c3128d12b671a163913d04ef7320e4e8d3447e49b2a7ffe0f7420090ce742e8ee95021e8b7c2da6290e5cfb8d411d61078cc960dcf9e09b75db4034e88d238083260c690e126f47a10f978f20d6ec7e1a1c2571b104b2c9ed5e3bd4928699dfbadeb1af58416c630c969a6c5"

    # Ciphertext from server
    c_b64 = "Z5PJFcMDIt4+VjqhnTTSU83YPJsbbUG8iIgQSzqxviBphzcDNSEt4JadnMUEc4bII1THA8xNOV/MeoIjfkLFaZi3m6wlvh1wsTkGgX6TuhIqagug2Z2buO5JQDO4yhy95YO/2/6QHpyQnITmaIvQQOpBfOhbKQVoQ9W47n3affI="

    # Parse values
    n = int(n_hex, 16)
    e = int(e_hex, 16)
    c_bytes = base64.b64decode(c_b64)
    c = int.from_bytes(c_bytes, byteorder='big')

    print(f"[*] n = {n}")
    print(f"[*] e = {e}")
    print(f"[*] c = {c}")
    print(f"\n[*] Launching Wiener's attack...")

    # Perform Wiener's attack
    d = wiener_attack(e, n)

    if d is None:
        print("[-] Wiener's attack failed!")
        return

    print(f"\n[+] Recovered private exponent: d = {d}")

    # Decrypt ciphertext
    print(f"\n[*] Decrypting ciphertext...")
    plaintext = decrypt_rsa(c, d, n)

    print(f"[+] Plaintext (bytes): {plaintext}")
    print(f"[+] Plaintext (UTF-8): {plaintext.decode('utf-8', errors='ignore')}")
    print(f"\n[+] FLAG: {plaintext.decode('utf-8', errors='ignore')}")

if __name__ == "__main__":
    main()
