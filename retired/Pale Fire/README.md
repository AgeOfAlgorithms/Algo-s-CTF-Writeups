## Challenge Name
Pale Fire

## Platform
UWSP Pointer Overflow CTF 2025

## Category
Crypto

## Difficulty
Medium

## Challenge Description
Two programs on the network perform a Diffie–Hellman handshake and then use the resulting shared secret to obfuscate a short message. The handshake uses a small, legacy prime; on modern machines a determined solver can recover a private exponent by computing a discrete log. Your job is to recover the hidden message. You are given the public DH parameters and one exchange; recover the message and submit it in the format poctf{…}.

The server will accept connections on the challenge port and emits a single handshake exchange then closes. Optionally, a PCAP of a sample run is also provided if you prefer offline analysis. Good luck.

I'm providing an abundance of redundant information here for your convenience, but really all you need is:
"p": "0x7fffffff",
"g": "0x3",
"A": "0x70b7c967",
"B": "0x0307f998",
"ciphertext": "0x51c11d7e4c03a84dcff76bcd1dccf649894a70ed1ce9"

[Health Check](https://crypto200-3.pointeroverflowctf.com/health)
[Params](https://crypto200-3.pointeroverflowctf.com/params)