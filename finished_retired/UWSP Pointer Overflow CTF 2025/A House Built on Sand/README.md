## Challenge Name
A House Built on Sand

## Platform
UWSP Pointer Overflow CTF 2025

## Category
Crypto

## Difficulty
medium-hard

## Challenge Description
You are given many ECDSA signatures produced with the SAME private key on secp256k1. The signer’s RNG was flawed: each per-signature nonce k was biased (very close to a hidden base value), which makes the private key recoverable.

Details:
curve: secp256k1
pubkey_hex: 041cabd688f57365a9f2d6b7cd0f23e76199d7155244bc90af09c6bcce0817101c9e9664b0c52b60e771892cbaa1867880e66a1dd4811576ce9ff1de13ad2b0223
and of course you'll need the [signatures](crypto300-1.csv)

Once you have the private key, you can use it as the symmetric key to decrypt this [archive](crypto300-1.7z).

Update:
z is already provided in the CSV. Treat each z as a big-endian integer (ECDSA uses z mod n internally). You do not need the original messages.
There exists a fixed secret base 𝑘0 such that every nonce 𝑘 satisfies: ∣𝑘−𝑘0∣≤2^12−1(about 2^12)
Decryption; 7z x crypto300-1.7z -p<hex_private_key>
