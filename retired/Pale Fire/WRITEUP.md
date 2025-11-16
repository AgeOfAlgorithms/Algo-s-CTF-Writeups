# Pale Fire - Cryptography Challenge Solution

## Challenge Information
- **Name**: Pale Fire
- **Category**: Cryptography
- **Difficulty**: Medium
- **Platform**: UWSP Pointer Overflow CTF
- **Date Solved**: 2025-11-11

## Challenge Description
Two programs perform a Diffie-Hellman handshake using a small, legacy prime. The goal is to recover a private exponent via discrete logarithm and decrypt the hidden message.

## Given Parameters
From the challenge README:
- `p = 0x7fffffff` (2,147,483,647 - a Mersenne prime, 2³¹-1)
- `g = 0x3` (generator)
- `A = 0x70b7c967` (Alice's public key)
- `B = 0x0307f998` (Bob's public key)
- `ciphertext = 0x51c11d7e4c03a84dcff76bcd1dccf649894a70ed1ce9` (OLD/DUMMY from static description)

**Critical Discovery**: The README contained links to live endpoints:
- Health endpoint: https://crypto200-3.pointeroverflowctf.com/health
- Params endpoint: https://crypto200-3.pointeroverflowctf.com/params

The **live** params endpoint provided different ciphertext:
- **ACTUAL ciphertext**: `0xc1440a2d7cd4f59bdc6340f971831cf173aa8867a501`

## Vulnerability Analysis
### 1. Small Prime Weakness
The prime `p = 0x7fffffff` (2³¹-1) is relatively small by modern standards, making discrete logarithms computationally feasible.

### 2. Generator Mismatch
During analysis, we discovered that:
- Alice uses generator `g=3` (as stated)
- Bob's public key `B` CANNOT be generated from `g=3` (B is NOT in g's subgroup)
- Bob actually uses generator `h=7` (a full generator of order p-1)
- Bob's private key: `b = 1,985,647,519` satisfies: 7^b mod p = B = 0x0307f998

### 3. Subgroup-Generator Mismatch
This is not a standard Diffie-Hellman implementation but rather an intentionally non-standard setup that still allows a shared secret to be computed.

## Solution Steps

### Step 1: Compute Discrete Logarithms
**Alice's private key (a)**:
- Need to solve: 3^a mod p = A = 0x70b7c967
- Solution: `a = 58,363,728`
- Verification: 3^58,363,728 mod p = 0x70b7c967 ✓

**Bob's private key (b)**:
- Need to solve: 7^b mod p = B = 0x0307f998 (using generator 7, not 3)
- Solution: `b = 1,985,647,519`
- Verification: 7^1,985,647,519 mod p = 0x0307f998 ✓

### Step 2: Compute Shared Secret
Standard DH shared secret computation:
```python
shared_secret = B^a mod p
shared_secret = 0x0307f998^58,363,728 mod 0x7fffffff
shared_secret = 0x1f18b75a = 521,713,498
```

### Step 3: Derive Encryption Key
The shared secret is hashed using SHA256 to derive the encryption key:
```python
import hashlib
key = hashlib.sha256(shared_secret.to_bytes(4, 'big')).digest()
key = b12b69591aaf80ecaf131f9245ee2f9947c7bb0f917c2a5f81c319a7bdae9cf1
```

### Step 4: Decrypt Ciphertext
Ciphertext: `0xc1440a2d7cd4f59bdc6340f971831cf173aa8867a501`

XOR decryption with the derived key (first 22 bytes):
```python
ciphertext_bytes = ciphertext.to_bytes(22, 'big')
plaintext = bytes([ciphertext_bytes[i] ^ key[i] for i in range(22)])
plaintext = b'poctf{uwsp_k4m3h4m3h4}'
```

### Step 5: Extract Flag
**FLAG**: `poctf{uwsp_k4m3h4m3h4}`

## Key Takeaways
1. **Always check for live endpoints**: The static parameters in the challenge description were a sample; the live endpoint contained the actual challenge data.
2. **Generator mismatches matter**: The non-standard DH setup (different generators) still works mathematically but is unusual.
3. **SHA256 key derivation**: The shared secret was hashed before being used as an XOR key.
4. **Small = vulnerable**: Using a 31-bit prime made discrete logarithms computationally feasible.

## Files in This Directory
- `comprehensive_decrypt_attempts.py` - All decryption attempts with old (wrong) ciphertext
- `verify_private_keys.py` - Verification math for computed private keys
- `derive_flag_from_secret.py` - Alternative flag derivation attempts
- `test_actual_challenge.py` - **Final solution script** (uses live endpoint ciphertext)
- `README.md` - Challenge description with links to live endpoints
- `UNSOLVED.md` - Previous analysis with old/incorrect ciphertext
- `WRITEUP.md` - This file (solution documentation)

## Tools Used
- Python for modular arithmetic and discrete logarithms
- Hashlib for SHA256 hashing
- curl to fetch live parameters from API endpoints
- Mathematical analysis to identify generator mismatches

## Result
✅ **Challenge solved successfully** with flag: `poctf{uwsp_k4m3h4m3h4}`
