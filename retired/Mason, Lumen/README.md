## Challenge Name
Mason, Lumen

## Platform
UWSP Pointer Overflow CTF 2025

## Category
Crypto

## Difficulty
easy

## Challenge Description
We found an old utility used by the lab to encrypt small messages. It uses a tiny custom ARX-based stream keystream with a 24-bit key.

Your goal is to recover the plaintext flag from the provided ciphertext.

Files:
- encrypt.py (reference implementation of the keystream/encrypt)
- ciphertext.bin (ciphertext you must decrypt)
- nonce.txt (nonce used to generate the keystream)

Notes:
- Key is 24 bits (i.e., 6 hex chars).
- Nonce is 32 bits (8 hex chars) and is provided in nonce.txt.

[attachment](Crypto100-2)
