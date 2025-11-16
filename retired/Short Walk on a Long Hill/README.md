## Challenge Name
Short Walk on a Long Hill

## Platform
UWSP Pointer Overflow CTF 2025

## Category
Crypto

## Difficulty
medium

## Challenge Description
You’ve intercepted a Diffie–Hellman “HSM” that behaves… generously. It accepts any public value you send and replies with a MAC that “proves” the shared secret. The vendor swears the parameters are fine because (p) is large and “we use SHA-256.”

Goal: Recover the flag. Hints: If a responder never validates that your public value lives in the correct subgroup, you may be able to “walk” their long secret exponent in short cycles. Sometimes a long hill is climbed by lots of tiny steps.

POST /oracle
Content-Type: application/json
Request: { "A": "<decimal string for your public value>" }
Rules:
- A must be an integer 2 <= A < p
- The server computes K = A^x mod p (x is static)
- Returns HMAC-SHA256(key=K_bytes, msg=nonce) as hex

Response:
{ "mac": "<hex string>" }

GET /nonce -> returns raw 32-byte nonce
GET /params-> returns p and B as JSON
GET /ciphertext -> returns c

Your target: crypto200-2.pointeroverflowctf.com:11697

The flag is the AES-CTR plaintext. Derive the AES key as SHA256(x.to_bytes(16,'big') || b"short-walk"), split the server blob into iv, ct = blob[:16], blob[16:], then decrypt with AES-CTR using nonce=iv[:8] and initial_value=int.from_bytes(iv[8:], 'big').
