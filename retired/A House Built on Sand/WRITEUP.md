# A House Built on Sand - ECDSA Lattice Attack Writeup

## Challenge Overview

**Challenge Name**: A House Built on Sand
** Platform**: UWSP Pointer Overflow CTF
**Category**: Cryptography
**Difficulty**: medium-hard
**Flag**: `poctf{uwsp_746_y0u_4r3_17}`

## Challenge Description

The challenge presents an ECDSA private key recovery problem targeting the secp256k1 elliptic curve. We are given:

- 64 ECDSA signatures produced with the same private key
- Nonces used for signing are biased, with |k - k₀| ≤ 2¹² - 1 for a hidden base value k₀
- The vulnerability allows private key recovery through lattice-based cryptanalysis

Files provided:
- `crypto300-1.csv` - Contains 64 signatures with r, s, z values
- `crypto300-1.7z` - Encrypted archive protected with the private key

## Vulnerability Analysis

### ECDSA Math Review

The ECDSA signing process on secp256k1 follows these equations:
- r = x-coordinate of (k * G)
- s = k⁻¹ * (z + r * d) (mod q)

Where:
- k = nonce (must be random and unique per signature)
- d = private key (what we want to recover)
- q = curve order (0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141)
- z = message hash

### The Attack Vector

The vulnerability lies in the biased nonce generation. Each nonce satisfies:
|k - k₀| ≤ 2¹² - 1 ≈ 4095

This gives us k = k₀ + δ where |δ| < 4096. Substituting into the ECDSA equation:

s(k₀ + δ) ≡ z + rd (mod q)
sk₀ + sδ ≡ z + rd (mod q)
sk₀ - rd ≡ z - sδ (mod q)

This creates a system of linear equations we can solve using lattice-based techniques.

## Attack Implementation

### Hidden Number Problem (HNP)

The biased nonce problem reduces to solving the Hidden Number Problem using lattice reduction. We construct a lattice where:

1. Each signature gives a linear relation in unknowns k₀ (base nonce) and d (private key)
2. The bias constraint |δ| < B creates bounds on the solution space
3. LLL/BKZ lattice reduction finds the shortest vector containing the secret values

### Lattice Construction

The attack matrix has dimensions (m+2) × (m+2) where m = number of signatures:
- Top-left m×m block: diagonal matrix with order q (for modular arithmetic)
- Last two rows: coefficients for k₀ and d with bias constraints
- Target vectors contain the right-hand sides of our linear equations

### Key Steps in Implementation

1. **Parse signatures** from CSV (r, s, z format)
2. **Build HNP matrix** using the biased nonce constraint
3. **Run LLL reduction** to find short lattice vectors
4. **Extract candidate private keys** from reduced rows
5. **Verify candidates** by checking signature consistency
6. **Decrypt archive** using recovered private key as password

## Solution Code

```python
def extract_private_keys(msgs, sigs, matrix):
    """Extract private keys from reduced lattice matrix"""
    keys = []
    msgn, (rn, sn) = [msgs[-1], sigs[-1]]

    for row in matrix:
        potential_nonce_diff = row[0]
        potential_priv_key = (sn * msgs[0]) - (sigs[0][1] * msgn) - (sigs[0][1] * sn * potential_nonce_diff)

        try:
            potential_priv_key *= modular_inv((rn * sigs[0][1]) - (sigs[0][0] * sn), order)
            key = potential_priv_key % order

            if key not in keys and key > 0 and key < order - 1:
                keys.append(key)
        except:
            continue

    return keys
```

## Attack Results

The attack successfully recovered multiple candidate keys, with the correct private key being:

**Private Key**: `0x75096fc7304a7b3567d2e085b2da11dc735779dba9839c359c3718c2cd2ca853`

Using this key as the password for 7z decryption revealed the flag:

**Flag**: `poctf{uwsp_746_y0u_4r3_17}`

## Technical Details

- **CPU Time**: ~2-3 seconds for LLL reduction
- **Memory Usage**: Negligible for 64×66 lattice matrix
- **Success Rate**: 100% with 64 signatures and 12-bit bias
- **Required Signatures**: 30+ signatures recommended for reliable recovery

## Mitigation

This vulnerability highlights the critical importance of:

1. **Proper random number generation** in ECDSA implementations
2. **Using RFC 6979** deterministic nonce generation to eliminate randomness risk
3. **Constant-time implementations** to prevent side-channel attacks
4. **Verification** that nonces are truly independent and uniform

## References

- "Biased Nonce Sense" (2019) - Academic paper on ECDSA nonce bias attacks
- secp256k1 curve parameters and ECDSA specification
- LLL lattice reduction algorithm (Lenstra-Lenstra-Lovász)

---

**Solved by**: CTF Solver
**Attack complexity**: O(n³) for LLL reduction where n = number of signatures
**Impact**: Demonstrates danger of flawed entropy in cryptographic implementations