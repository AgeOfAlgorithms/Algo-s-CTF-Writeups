#!/usr/bin/env python3
"""
Author: Claude Code
Purpose: Analyze the data structure and patterns
Created: 2025-11-10
Last Updated: 2025-11-10

Let me examine the data more carefully for patterns
"""

import struct

# Parse data
uid_hex = "5a928ebd3f5729b548b77e73"
uid = bytes.fromhex(uid_hex)

with open('otp_dump.bin', 'rb') as f:
    otp_data = f.read()

with open('secret.enc', 'rb') as f:
    encrypted_data = f.read()

print("="*60)
print("DATA ANALYSIS")
print("="*60)

print(f"\nUID (12 bytes): {uid.hex()}")
print(f"  As 3 x 32-bit words (little-endian):")
uid_words_le = struct.unpack('<3I', uid)
for i, word in enumerate(uid_words_le):
    print(f"    Word {i}: 0x{word:08x} ({word})")

print(f"\n  As 3 x 32-bit words (big-endian):")
uid_words_be = struct.unpack('>3I', uid)
for i, word in enumerate(uid_words_be):
    print(f"    Word {i}: 0x{word:08x} ({word})")

print(f"\nOTP (32 bytes): {otp_data.hex()}")
print(f"  First half (16 bytes): {otp_data[:16].hex()}")
print(f"  Second half (16 bytes): {otp_data[16:].hex()}")

print(f"\n  As 8 x 32-bit words (little-endian):")
otp_words_le = struct.unpack('<8I', otp_data)
for i, word in enumerate(otp_words_le):
    print(f"    Word {i}: 0x{word:08x} ({word})")

print(f"\n  As 8 x 32-bit words (big-endian):")
otp_words_be = struct.unpack('>8I', otp_data)
for i, word in enumerate(otp_words_be):
    print(f"    Word {i}: 0x{word:08x} ({word})")

print(f"\nSecret.enc (32 bytes): {encrypted_data.hex()}")
print(f"  Assumed IV (16 bytes): {encrypted_data[:16].hex()}")
print(f"  Assumed CT (16 bytes): {encrypted_data[16:].hex()}")

# Check for obvious patterns
print("\n" + "="*60)
print("PATTERN ANALYSIS")
print("="*60)

# Check if OTP XOR UID gives something interesting
print("\nXOR patterns:")
print("  UID[0:12] XOR OTP[0:12]:")
xor_result = bytes([uid[i] ^ otp_data[i] for i in range(12)])
print(f"    {xor_result.hex()}")

print("  UID[0:12] XOR OTP[16:28]:")
xor_result2 = bytes([uid[i] ^ otp_data[16+i] for i in range(12)])
print(f"    {xor_result2.hex()}")

# Try interpreting as matrix
print("\nMatrix interpretation (4 rows x 8 cols):")
for row in range(4):
    row_data = otp_data[row*8:(row+1)*8]
    print(f"  Row {row}: {row_data.hex()}")

print("\nMatrix interpretation (8 rows x 4 cols):")
for row in range(8):
    row_data = otp_data[row*4:(row+1)*4]
    print(f"  Row {row}: {row_data.hex()}")

print("\nMatrix interpretation (2 rows x 16 cols):")
for row in range(2):
    row_data = otp_data[row*16:(row+1)*16]
    print(f"  Row {row}: {row_data.hex()}")

# Check for transpose operations
print("\n" + "="*60)
print("TRANSPOSE OPERATIONS (treating as 4x8 matrix of bytes)")
print("="*60)

# Treat OTP as 4 rows x 8 columns
matrix = []
for row in range(4):
    matrix.append(list(otp_data[row*8:(row+1)*8]))

# Transpose
transposed = [[matrix[row][col] for row in range(4)] for col in range(8)]
transposed_bytes = bytes([b for row in transposed for b in row])
print(f"Transposed (column-major): {transposed_bytes.hex()}")
print(f"  First 16 bytes: {transposed_bytes[:16].hex()}")
print(f"  Last 16 bytes: {transposed_bytes[16:].hex()}")
