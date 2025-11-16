# This is Not the Way - Writeup

## Challenge Information
- **Platform**: UWSP Pointer Overflow CTF
- **Category**: Cryptography
- **Difficulty**: Hard
- **Target**: https://crypto400.pointeroverflowctf.com

## Challenge Description
An RSA implementation with a suspiciously small private exponent. Given only the public key and ciphertext, we need to recover the plaintext flag using a classic Wiener's attack.

## Vulnerability Analysis

The vulnerability in this challenge is the **use of a small private exponent (d)** in RSA encryption.

### Why Small d is Dangerous

In RSA:
- Public key: (n, e) where n = p × q
- Private key: d where e × d ≡ 1 (mod φ(n))
- φ(n) = (p-1)(q-1)

When d is small (specifically when d < N^(1/4)), **Wiener's attack** can efficiently recover the private key using continued fraction expansion.

### Theory Behind Wiener's Attack

From the RSA equation: e × d ≡ 1 (mod φ(n))

This means: e × d = 1 + k × φ(n) for some integer k

Rearranging: e/n ≈ k/d (since φ(n) ≈ n)

Wiener's attack uses continued fraction expansion of e/n to find convergents (k/d) that reveal the actual private key.

## Exploitation Steps

### 1. Retrieve Public Key and Ciphertext

```bash
curl https://crypto400.pointeroverflowctf.com/pubkey
curl https://crypto400.pointeroverflowctf.com/ciphertext
```

Retrieved:
- n (1024-bit modulus)
- e (public exponent, unusually large)
- c (ciphertext, base64-encoded)

### 2. Implement Wiener's Attack

The attack algorithm:
1. Compute continued fraction expansion of e/n
2. For each convergent k/d:
   - Calculate φ(n) = (e×d - 1) / k
   - Derive p and q from: p + q = n - φ(n) + 1 and p × q = n
   - Verify if p × q = n
3. If valid factorization found, d is the private key

### 3. Decrypt the Ciphertext

Once d is recovered:
- m = c^d mod n
- Convert m to bytes to get the plaintext flag

## Solution Script

See [wiener_attack.py](wiener_attack.py) for the complete implementation.

## Results

The attack successfully recovered:
- **Private exponent d**: 995191913291720747743128311991170033204089781785
- **Prime factors**:
  - p = 1292842...762099 (308 digits)
  - q = 9285339...543959 (307 digits)

**Flag**: `poctf{uwsp_1v3_b33n_c4ll3d_w0r53}`

## Key Takeaways

1. **Never use small private exponents** in RSA - always ensure d > N^(1/4)
2. **Wiener's attack is practical** - it's a polynomial-time attack when d is small
3. The convergent at which the attack succeeds reveals k and d directly
4. Modern RSA implementations should use d ≈ φ(n) in size to avoid this vulnerability

## References
- M. J. Wiener, "Cryptanalysis of Short RSA Secret Exponents," IEEE Transactions on Information Theory, 1990
- Boneh, D. "Twenty Years of Attacks on the RSA Cryptosystem," Notices of the AMS, 1999
