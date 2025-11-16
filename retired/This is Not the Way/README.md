## Challenge Name
This is Not the Way

## Platform
UWSP Pointer Overflow CTF 2025

## Category
crypto 

## Difficulty
hard

## Challenge Description
Somewhere between “secure enough” and “ship it” lives an RSA key with a suspiciously small private exponent. You are given only the public key and a ciphertext. This challenges has been nerfed down to a classic small-d continued fractions (Wiener) trick. Recover the plaintext — that plaintext is the flag.

Your Target: https://crypto400.pointeroverflowctf.com
GET /pubkey → JSON with "n" (hex), "e" (hex), and "k" (bytes length).
GET /ciphertext → JSON {"c_b64": ""}.
