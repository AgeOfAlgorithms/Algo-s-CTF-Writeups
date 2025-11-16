#!/usr/bin/env python3
"""
encrypt.py -- reference ARX toy keystream and encrypt/decrypt helper.

Usage:
  python3 encrypt.py encrypt <key24_hex> <nonce_hex> <infile> <outfile>
  python3 encrypt.py decrypt <key24_hex> <nonce_hex> <infile> <outfile>

Key: 24-bit hex (6 hex chars), nonce: 32-bit hex (8 hex chars).
This file also exposes `keystream_bytes(key24, nonce, length)` for quick testing.
"""
import sys
from typing import Tuple

def rol32(x: int, r: int) -> int:
    return ((x << r) & 0xFFFFFFFF) | (x >> (32 - r))

def keystream_bytes(key24: int, nonce: int, length: int) -> bytes:
    """
    Small ARX-based keystream:
      - Expand key24 to a 32-bit mixing word (deterministic simple spread)
      - state = nonce ^ key32
      - each byte:
          state = (state + key32) & 0xFFFFFFFF
          state = rol32(state, 7)
          k = (state & 0xFF) ^ ((state >> 8) & 0xFF)
          append k
          state ^= counter
    Designed to be simple and reversible given key+nonce.
    """
    key32 = (key24 & 0xFFFFFF) | ((key24 & 0xFFFFFF) << 24) & 0xFFFFFFFF
    state = (nonce ^ key32) & 0xFFFFFFFF
    out = bytearray()
    for i in range(length):
        state = (state + key32) & 0xFFFFFFFF
        state = rol32(state, 7)
        k = ((state & 0xFF) ^ ((state >> 8) & 0xFF)) & 0xFF
        out.append(k)
        state = (state ^ (i & 0xFFFFFFFF)) & 0xFFFFFFFF
    return bytes(out)

def crypt_file(key24_hex: str, nonce_hex: str, infile: str, outfile: str):
    key24 = int(key24_hex, 16) & 0xFFFFFF
    nonce = int(nonce_hex, 16) & 0xFFFFFFFF
    with open(infile, "rb") as f:
        pt = f.read()
    ks = keystream_bytes(key24, nonce, len(pt))
    ct = bytes([a ^ b for a, b in zip(pt, ks)])
    with open(outfile, "wb") as f:
        f.write(ct)

def main():
    if len(sys.argv) != 6:
        print("Usage: encrypt.py <encrypt|decrypt> <key24_hex> <nonce_hex> <infile> <outfile>")
        sys.exit(1)
    mode, keyhex, nonhex, infile, outfile = sys.argv[1:6]
    crypt_file(keyhex, nonhex, infile, outfile)

if __name__ == '__main__':
    main()