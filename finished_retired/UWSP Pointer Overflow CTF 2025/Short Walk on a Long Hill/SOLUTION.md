# Solution: Short Walk on a Long Hill

**Status:** ✅ SOLVED  
**Flag:** `poctf{uwsp_7h3_l16h7_4nd_7h3_d4rk}`  
**Secret Exponent:** `x = 15607543889841794955`

## Challenge Overview

This was a Diffie-Hellman subgroup confinement attack challenge. The server provides an oracle that:
- Accepts any public value A (where 2 ≤ A < p)
- Computes K = A^x mod p (x is the secret exponent)
- Returns HMAC-SHA256(key=K_bytes, msg=nonce)

The goal was to recover x and use it to decrypt an AES-CTR encrypted flag.

## Key Insights

### 1. Subgroup Confinement Attack
Since the server doesn't validate that A is in the correct subgroup, we can send elements of small order to extract information about x modulo small primes.

### 2. Structure of p-1
The prime p was specially crafted such that p-1 factors completely into small primes:
```
p-1 = 2 × 3 × 5 × 7 × 11 × 13 × ... × 739 × 743
```

This has 132 distinct prime factors, all ≤ 743.

### 3. Oracle Uses HMAC, Not SHA256
**Critical detail:** The oracle returns `HMAC-SHA256(key=K_bytes, msg=nonce)`, not just `SHA256(K_bytes)`.  
K_bytes uses variable-length encoding (natural byte length of the integer).

## Attack Strategy

### Step 1: Extract Modular Constraints

For each small prime factor p_i of (p-1):

1. Compute element = g^((p-1)/p_i) mod p  
   This creates an element of order p_i

2. Send element to oracle, get back MAC

3. For k = 0 to p_i-1:
   - Compute K = element^k mod p
   - Test if HMAC-SHA256(K, nonce) matches the server MAC
   - If match, we know x ≡ k (mod p_i)

### Step 2: Apply Chinese Remainder Theorem

After extracting constraints for many primes, we have a system:
```
x ≡ r_1 (mod p_1)
x ≡ r_2 (mod p_2)
...
x ≡ r_n (mod p_n)
```

Using CRT, we combine these to get x modulo (p_1 × p_2 × ... × p_n).

We need enough constraints that the combined modulus exceeds the size of x.

### Step 3: Verify and Decrypt

1. Verify: Check that g^x ≡ B (mod p)
2. Derive AES key: SHA256(x.to_bytes(16, 'big') || b"short-walk")  
3. Decrypt ciphertext using AES-CTR

## Solution Execution

We extracted **62 constraints** from primes 2 through 293:
- x ≡ 1 (mod 2) → x is odd
- x ≡ 0 (mod 3)
- x ≡ 0 (mod 5)
- x ≡ 1 (mod 7)
- ... (58 more constraints)

Combined modulus: **400 bits**  
This was sufficient to uniquely determine x = 15607543889841794955

## Files

- `final_solution_crt.py` - Working Python exploit using CRT attack
- `flag.txt` - Contains the recovered secret and flag
- `README.md` - Original challenge description

## Lessons Learned

1. Always check if the MAC is HMAC vs plain hash - this cost significant debugging time
2. Subgroup confinement attacks are powerful when p-1 has many small factors
3. Chinese Remainder Theorem is the elegant way to combine partial information
4. Read the challenge description carefully - the HMAC detail was documented but easy to miss

---
*Solved: November 15, 2025*
