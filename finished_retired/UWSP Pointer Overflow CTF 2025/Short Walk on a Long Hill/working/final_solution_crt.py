#!/usr/bin/env python3
"""
Extended CRT Solution - Extract many more constraints
"""

import requests
import json
import hashlib
import hmac
import sympy
from Crypto.Cipher import AES
from Crypto.Util import Counter

SERVER_URL = "http://crypto200-2.pointeroverflowctf.com:11697"

def long_to_bytes_var(n):
    byte_len = (n.bit_length() + 7) // 8
    return n.to_bytes(byte_len, 'big') if byte_len > 0 else b'\x00'

def get_server_params():
    response = requests.get(f"{SERVER_URL}/params")
    params = response.json()
    p = int(params['p'])
    g = int(params['g'])
    B = int(params['B'])
    
    nonce_resp = requests.get(f"{SERVER_URL}/nonce")
    nonce = nonce_resp.content
    
    return p, g, B, nonce

def extract_constraint_for_prime(p, g, nonce, prime_factor):
    cofactor = (p - 1) // prime_factor
    element = pow(g, cofactor, p)

    if element == 1:
        for base in range(2, 100):
            element = pow(base, cofactor, p)
            if element != 1 and pow(element, prime_factor, p) == 1:
                break
        else:
            return None

    headers = {"Content-Type": "application/json"}
    data = {"A": str(element)}

    try:
        response = requests.post(f"{SERVER_URL}/oracle", headers=headers, data=json.dumps(data))
        target_mac = response.json()['mac']
    except:
        return None

    for k in range(prime_factor):
        K = pow(element, k, p)
        K_bytes = long_to_bytes_var(K)
        test_mac = hmac.new(K_bytes, nonce, hashlib.sha256).hexdigest()

        if test_mac == target_mac:
            return k

    return None

def main():
    print("="*60)
    print("EXTENDED CRT ATTACK - Extracting Many Constraints")
    print("="*60)

    p, g, B, nonce = get_server_params()
    print(f"\np bit length: {p.bit_length()}")
    
    factors = sympy.factorint(p - 1)
    print(f"p-1 has {len(factors)} distinct prime factors")
    
    # Extract from ALL primes up to 200 (and beyond if needed)
    all_primes = sorted([prime for prime in factors.keys()])
    print(f"Largest prime factor: {max(all_primes)}")
    print()
    
    constraints = []
    combined_modulus = 1
    
    # We need combined_modulus to exceed p-1 to uniquely determine x
    target_bits = p.bit_length()
    
    print(f"Target: combined modulus should have ~{target_bits} bits")
    print()
    
    for i, prime in enumerate(all_primes):
        if prime > 300:  # Skip very large primes for now
            continue
            
        print(f"[{i+1}/{len(all_primes)}] Prime {prime}...", end=" ", flush=True)
        
        remainder = extract_constraint_for_prime(p, g, nonce, prime)
        
        if remainder is not None:
            constraints.append((remainder, prime))
            combined_modulus *= prime
            print(f"✓ x ≡ {remainder} (mod {prime}) | Combined modulus: {combined_modulus.bit_length()} bits")
            
            # Check if we have enough
            if combined_modulus.bit_length() >= target_bits:
                print(f"\n✓ Combined modulus is large enough!")
                break
        else:
            print(f"✗ Failed")
    
    print(f"\n[*] Extracted {len(constraints)} constraints")
    print(f"[*] Combined modulus: {combined_modulus.bit_length()} bits")
    
    if len(constraints) < 3:
        print("Need more constraints!")
        return
    
    # Solve with CRT
    print("\n[*] Applying CRT...")
    remainders = [r for r, m in constraints]
    moduli = [m for r, m in constraints]
    
    try:
        x_solution, _ = sympy.ntheory.modular.crt(moduli, remainders)
        print(f"[*] CRT solution: x = {x_solution}")
        
        # Verify
        print(f"\n[*] Verifying...")
        test_B = pow(g, x_solution, p)
        
        if test_B == B:
            print(f"✓✓✓ VERIFICATION PASSED!")
            
            # Decrypt
            print(f"\n[*] Decrypting flag...")
            cipher_resp = requests.get(f"{SERVER_URL}/ciphertext")
            ciphertext = cipher_resp.content

            key = hashlib.sha256(x_solution.to_bytes(16, 'big') + b"short-walk").digest()
            iv = ciphertext[:16]
            ct = ciphertext[16:]

            nonce_ctr = iv[:8]
            initial_value = int.from_bytes(iv[8:], 'big')
            ctr = Counter.new(64, prefix=nonce_ctr, initial_value=initial_value)
            cipher = AES.new(key, AES.MODE_CTR, counter=ctr)
            plaintext = cipher.decrypt(ct)

            print(f"\n{'='*60}")
            print(f"FLAG: {plaintext.decode('utf-8', errors='ignore')}")
            print(f"{'='*60}")

            with open('flag.txt', 'w') as f:
                f.write(f"x = {x_solution}\n")
                f.write(f"Flag: {plaintext.decode('utf-8', errors='ignore')}\n")
                
        else:
            print(f"✗ Verification failed - need more constraints")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
