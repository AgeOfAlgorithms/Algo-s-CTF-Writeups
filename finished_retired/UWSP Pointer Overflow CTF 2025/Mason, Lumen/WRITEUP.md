# Mason, Lumen - CTF Writeup

## Challenge Overview

**Challenge:** Mason, Lumen
**Platform:** UWSP Pointer Overflow CTF
**Category:** Cryptography
**Difficulty:** Easy
**Points:** 100

### Problem Description

We were given a custom ARX-based stream cipher implementation that encrypts messages using a 24-bit key. The challenge provided:

1. `encrypt.py` - Reference implementation of the keystream/encrypt algorithm
2. `ciphertext.bin` - The encrypted flag
3. `nonce.txt` - The nonce used during encryption (32-bit hex value)

**Key constraints:**
- Key is 24-bit (6 hex characters)
- Nonce is 32-bit (8 hex characters) and provided

## Analysis

The encryption algorithm uses a simple ARX (Addition, Rotation, XOR) based keystream generator:

```python
def keystream_bytes(key24: int, nonce: int, length: int) -> bytes:
    # Expand 24-bit key to 32-bit mixing word
    key32 = (key24 & 0xFFFFFF) | ((key24 & 0xFFFFFF) << 24) & 0xFFFFFFFF
    state = (nonce ^ key32) & 0xFFFFFFFF

    for i in range(length):
        state = (state + key32) & 0xFFFFFFFF
        state = rol32(state, 7)  # Rotate left by 7 bits
        k = ((state & 0xFF) ^ ((state >> 8) & 0xFF)) & 0xFF
        out.append(k)
        state = (state ^ (i & 0xFFFFFFFF)) & 0xFFFFFFFF
```

The algorithm is a stream cipher that XORs the plaintext with a keystream generated from the key and nonce.

### Key Insight

The critical vulnerability here is the **key size**. With only 24 bits, there are only **16,777,216** possible keys (2^24). This is a tiny key space that can be brute-forced in minutes on modern hardware.

Additionally, since this is a stream cipher and we know the plaintext is likely a CTF flag (with common formats like `flag{...}`, `poctf{...}`, etc.), we can filter our brute force attempts to only consider outputs that look like flags.

## Solution Approach

The solution uses a brute force approach:

1. **Enumerate all possible 24-bit keys** (0x000000 to 0xFFFFFF)
2. **For each key:**
   - Generate the keystream using the provided nonce
   - XOR the ciphertext to get the plaintext
   - Check if the plaintext looks like a CTF flag
3. **Stop when we find a valid flag** or exhaust the key space

### Implementation

The brute force was optimized with these strategies:
- **Printable ASCII filtering** - Only consider outputs that consist of printable characters
- **Flag pattern matching** - Look for common flag patterns like `{...}`, `flag`, etc.
- **Early termination** - Stop as soon as we find something that looks like a flag

## Execution

```bash
$ python3 optimized_brute.py
Nonce: 3f2d1a9e
Ciphertext: 9f1361c1fe3cf5232843a02ec340f1dc6cf5e901e667ca911195aaa94cb8c647
Ciphertext length: 32 bytes
Total key space: 16,777,216 keys
Starting brute force...

🚩 FLAG FOUND! 🚩
Key: 0x417461
Flag: poctf{uwsp_l177l3_l16h7_0f_m1n3}
```

The brute force completed very quickly and found the flag with key `0x417461`.

## Verification

To confirm the result, we can decrypt using the found key:

```bash
$ python3 encrypt.py decrypt 417461 3f2d1a9e ciphetext.bin plaintext.txt
$ cat plaintext.txt
poctf{uwsp_l177l3_l16h7_0f_m1n3}
```

## The Flag

**Flag:** `poctf{uwsp_l177l3_l16h7_0f_m1r3}`

## Key Takeaways

1. **Key size is critical** - Never use keys smaller than current cryptographic standards (256 bits minimum)
2. **Brute force becomes feasible** with keys under 40-50 bits
3. **Stream ciphers are vulnerable** when keys are small, even if the algorithm is otherwise sound
4. **CTF challenges often include obvious weaknesses** - the 24-bit key was clearly designed to be brute-forceable

## Technical Details

- **Language:** Python 3
- **Computation time:** < 1 minute
- **Key space searched:** 16,777,216 keys
- **Optimization used:** ASCII filtering and flag pattern matching
- **Hardware:** Standard desktop/laptop sufficient

This was a straightforward but effective demonstration of why key size matters in cryptography, even with otherwise reasonable algorithms.