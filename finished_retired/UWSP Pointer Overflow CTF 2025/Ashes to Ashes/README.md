## Challenge Name
Ashes to Ashes

## Platform
UWSP Pointer Overflow CTF 2025

## Category
Crypto

## Difficulty
easy

## Challenge Description
You’re given a strange 128-bit “sponge” hash that processes 16-byte blocks, alternating between left and right rotations by 13 bits each round. The service will give you a random ASCII prefix that both of your messages must start with. Your goal is to find two different hex-encoded messages that produce the same hash digest under this function and submit them together.

Because the round function is linear (XORs and rotations only), a simple two-block disturbance-and-correction pattern works. Pad the given prefix with zeros until its length is a multiple of 16 so your controlled data begins on a block boundary. Pick any two 16-byte blocks A1, A2 and a non-zero difference Δ. For the first message use A1, A2; for the second use B1 = A1 XOR Δ and B2 = A2 XOR rotate13(Δ) (the rotation direction depends on whether your first custom block index is even or odd). Both messages will then hash to the same final state.

Submit your two different hex strings—each at least 32 bytes beyond the prefix—along with the session ID from /prefix. If they collide, you’ll receive the flag.

Your Target: https://crypto100-4.pointeroverflowctf.com
/prefix
/submit -H "Content-Type: application/json" -d "{""session_id"":""$SID"",""m1_hex"":""$M1"",""m2_hex"":""$M2""}"

the hash function:
#!/usr/bin/env python3
# Ashes: intentionally broken "weird sponge" (128-bit, 16-byte rate, alt inverse rounds)

# ashes_hash.py
from typing import Iterable

C = bytes([0xA5]) * 16

def _to_u128(b: bytes) -> int:
    return int.from_bytes(b, "little")

def _from_u128(x: int) -> bytes:
    return x.to_bytes(16, "little")

def _rol13(x: int) -> int:
    return ((x << 13) | (x >> (128 - 13))) & ((1 << 128) - 1)

def _ror13(x: int) -> int:
    return ((x >> 13) | (x << (128 - 13))) & ((1 << 128) - 1)

def ashes_hash(msg: bytes) -> bytes:
    # process in 16-byte blocks; zero-pad last partial block
    if len(msg) % 16 != 0:
        pad_len = 16 - (len(msg) % 16)
        msg += b"\x00" * pad_len

    S = 0  # 128-bit IV = 0
    c = _to_u128(C)

    for i in range(0, len(msg), 16):
        m = _to_u128(msg[i:i+16])
        if ((i // 16) % 2) == 0:  # even
            S = _rol13(S ^ m) ^ c
        else:                      # odd
            S = _ror13(S ^ m) ^ c

    return _from_u128(S)
