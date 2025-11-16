# Two Wrongs Make a Right - Writeup

**Challenge**: Crypto 200-1
**CTF**: UWSP Pointer Overflow CTF 2025
**Category**: Cryptography
**Difficulty**: Medium
**Points**: 200

## Challenge Description

Two ciphertexts were produced with CTR mode using the same nonce and same key (keystream reuse). Recover both plaintexts. You are given two ciphertexts (hex) and the nonce. The key is unknown. You have received a leak of the C1 plaintext.

## Vulnerability

AES-CTR mode **nonce reuse** - when two messages are encrypted with the same nonce and key, they share the same keystream, allowing recovery of plaintexts through XOR operations.

## Solution

### 1. Understanding the Attack

In CTR mode:
- `C1 = P1 ⊕ KS`
- `C2 = P2 ⊕ KS`

Where `KS` is the keystream. If the same nonce/key is reused:
- `C1 ⊕ C2 = (P1 ⊕ KS) ⊕ (P2 ⊕ KS) = P1 ⊕ P2`

Therefore:
- `P2 = P1 ⊕ (C1 ⊕ C2)`

### 2. Critical Discovery

The **key mistake** in previous attempts was using an incomplete P1 plaintext. The P1 in the local README file was 522 bytes, but the ciphertexts were 592 bytes.

The correct P1 (from the CTF challenge description) includes email addresses in angle brackets:
```
From: Tamsin <tamsin@pointeroverflowctf.com>
To: Mason <mason@pointeroverflowctf.com>
```

This makes P1 **exactly 592 bytes** - matching the ciphertext length perfectly.

### 3. Implementation

```python
import binascii

def xor_bytes(b1, b2):
    return bytes(x ^ y for x, y in zip(b1, b2))

# Load ciphertexts
c1_bytes = binascii.unhexlify(c1_hex)
c2_bytes = binascii.unhexlify(c2_hex)

# Exact P1 from challenge description (592 bytes)
p1 = """From: Tamsin <tamsin@pointeroverflowctf.com>
To: Mason <mason@pointeroverflowctf.com>
Date: Sat, 11 Oct 2025 10:02:05 -0500
Subject: System checks and handoff plan

Hey—quick handoff notes before I go off-grid:
 • Rotate the service tokens on barad-dur first, then traefik.
 • The staging login banner still shows "2024"; fix that.
 • If anyone pings you about CRYP 200-1, tell them it's *not* a padding-oracle.
 • Also: the validator only accepts lowercase flags.

Final reminder: never ship secrets in plaintext. Use proper key management and never reuse a CTR nonce again.

—T
"""

p1_bytes = p1.encode('utf-8')

# Apply attack
c1_xor_c2 = xor_bytes(c1_bytes, c2_bytes)
p2_bytes = xor_bytes(p1_bytes, c1_xor_c2)

# Decode P2
p2_text = p2_bytes.decode('utf-8')
```

### 4. Recovered Plaintext (P2)

```
# chatlog.txt (redacted)
[10:01:07] analyst: the bias lattice looks fine, we just need better side info
[10:01:16] you: wrong challenge—this one is CTR, not ECDSA
[10:01:33] analyst: oh right, the two-wrongs-make-a-right one?
[10:02:00] you: yep; XOR the ciphertexts to get P1⊕P2, then crib-drag common English
[10:02:25] system: helpful hint — look for an English header like "Subject:"
[10:02:59] you: and the flag… yeah it's in here somewhere: poctf{uwsp_7h15_fl46_15_4ll_5w34r_w0rd5}
[10:03:21] analyst: lowercase, braces, underscores… classic
```

## Flag

```
poctf{uwsp_7h15_fl46_15_4ll_5w34r_w0rd5}
```

Translation: "this flag is all swear words" (in leet speak)

## Lessons Learned

1. **Always verify plaintext length** - The P1 length must exactly match the ciphertext length
2. **Check the official source** - The challenge description on the CTF platform had the complete P1, while the local README had an abbreviated version
3. **CTR mode security** - Never reuse a nonce with the same key in CTR mode, as it completely breaks confidentiality

## Tools Used

- Python 3
- Standard cryptographic libraries (binascii)

## References

- [CTR Mode](https://en.wikipedia.org/wiki/Block_cipher_mode_of_operation#Counter_(CTR))
- [Many-time pad attack](https://crypto.stackexchange.com/questions/2249/how-does-one-attack-a-two-time-pad-i-e-one-time-pad-with-key-reuse)
