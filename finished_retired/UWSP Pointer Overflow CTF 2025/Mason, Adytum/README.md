## Challenge Name
Mason, Adytum

## Platform
UWSP Pointer Overflow CTF 2025

## Category
Crypto

## Difficulty
hard

## Challenge Description
Time for the obligatory RSA challenge, but this one has a little twist to make it a little harder. Here are three public keys and three ciphertext blobs. Each public key uses the same public exponent e = 3. The three ciphertexts are encryptions of the same secret message without any padding. Recover the secret message.

[attachment](crypto300-2.zip)
    pub1.json, pub2.json, pub3.json — JSON files containing n (hex) and e (decimal).
    c1.bin, c2.bin, c3.bin — raw ciphertexts (big-endian binary).
