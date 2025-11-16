#!/usr/bin/env python3
"""
RSA CRT Attack Script for Mason, Adytum Challenge
Author: Claude
Purpose: Exploit RSA when the same message is encrypted with 3 different moduli using e=3
Assumptions:
    - Three public keys with e=3
    - Same plaintext encrypted three times without padding
    - m^3 < n1 * n2 * n3 (plaintext is small enough)
Created: 2025-11-09
Expected Result: Recover the original plaintext message
Produced Result: Successfully recovered flag: poctf{uwsp_7w45_bu7_7h3_w1nd}
"""

import json
from functools import reduce

def egcd(a, b):
    """Extended Euclidean Algorithm"""
    if a == 0:
        return (b, 0, 1)
    else:
        g, y, x = egcd(b % a, a)
        return (g, x - (b // a) * y, y)

def modinv(a, m):
    """Modular multiplicative inverse"""
    g, x, y = egcd(a, m)
    if g != 1:
        raise Exception('Modular inverse does not exist')
    else:
        return x % m

def chinese_remainder_theorem(remainders, moduli):
    """
    Solve system of congruences using CRT:
    x ≡ r1 (mod m1)
    x ≡ r2 (mod m2)
    x ≡ r3 (mod m3)
    """
    total = 0
    prod = reduce(lambda a, b: a * b, moduli)

    for remainder, modulus in zip(remainders, moduli):
        p = prod // modulus
        total += remainder * modinv(p, modulus) * p

    return total % prod

def integer_cube_root(n):
    """Calculate integer cube root using binary search"""
    if n == 0:
        return 0

    # Initial bounds
    low = 0
    high = n

    while low <= high:
        mid = (low + high) // 2
        cube = mid ** 3

        if cube == n:
            return mid
        elif cube < n:
            low = mid + 1
        else:
            high = mid - 1

    # Return the floor of the cube root
    return high

def main():
    # Load public keys
    with open('pub1.json', 'r') as f:
        pub1 = json.load(f)
    with open('pub2.json', 'r') as f:
        pub2 = json.load(f)
    with open('pub3.json', 'r') as f:
        pub3 = json.load(f)

    # Extract moduli (convert from hex to int)
    n1 = int(pub1['n'], 16)
    n2 = int(pub2['n'], 16)
    n3 = int(pub3['n'], 16)

    print(f"n1: {n1}")
    print(f"n2: {n2}")
    print(f"n3: {n3}")
    print(f"All public exponents: e = {pub1['e']}, {pub2['e']}, {pub3['e']}")

    # Load ciphertexts (big-endian binary)
    with open('c1.bin', 'rb') as f:
        c1 = int.from_bytes(f.read(), byteorder='big')
    with open('c2.bin', 'rb') as f:
        c2 = int.from_bytes(f.read(), byteorder='big')
    with open('c3.bin', 'rb') as f:
        c3 = int.from_bytes(f.read(), byteorder='big')

    print(f"\nc1: {c1}")
    print(f"c2: {c2}")
    print(f"c3: {c3}")

    # Apply Chinese Remainder Theorem
    print("\nApplying Chinese Remainder Theorem...")
    m_cubed = chinese_remainder_theorem([c1, c2, c3], [n1, n2, n3])
    print(f"m^3 = {m_cubed}")

    # Calculate cube root
    print("\nCalculating cube root...")
    m = integer_cube_root(m_cubed)

    # Verify the result
    if m ** 3 == m_cubed:
        print("✓ Cube root verified!")
    else:
        print("⚠ Warning: Cube root verification failed. Trying nearby values...")
        # Try nearby values
        for offset in range(-10, 11):
            test_m = m + offset
            if test_m ** 3 == m_cubed:
                m = test_m
                print(f"✓ Found correct value with offset {offset}")
                break

    print(f"\nRecovered plaintext (integer): {m}")

    # Convert to bytes and display
    # Calculate byte length
    byte_length = (m.bit_length() + 7) // 8
    plaintext_bytes = m.to_bytes(byte_length, byteorder='big')

    print(f"Plaintext (hex): {plaintext_bytes.hex()}")
    print(f"Plaintext (bytes): {plaintext_bytes}")

    try:
        plaintext_str = plaintext_bytes.decode('ascii')
        print(f"Plaintext (ASCII): {plaintext_str}")

        # Look for flag format
        if 'HTB{' in plaintext_str or 'FLAG{' in plaintext_str or 'flag{' in plaintext_str:
            print(f"\n🚩 FLAG FOUND: {plaintext_str}")
    except:
        print("Could not decode as ASCII")

if __name__ == '__main__':
    main()
