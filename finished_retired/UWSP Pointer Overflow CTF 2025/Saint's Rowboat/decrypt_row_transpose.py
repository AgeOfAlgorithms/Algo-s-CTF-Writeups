#!/usr/bin/env python3
"""
Author: Claude Code
Purpose: Apply Row Transposition Cipher with keyword "SAINT" to derive key
Created: 2025-11-10
Last Updated: 2025-11-10

Assumptions:
- "Saint's Rowboat" hints at Row Transposition Cipher
- "SAINT" or related words might be the keyword

Expected Result: Decrypt the flag
Produced Result: (to be updated after execution)
"""

from Crypto.Cipher import AES

def row_transposition_decrypt(ciphertext_bytes, keyword):
    """Apply row transposition decryption with a keyword"""
    keyword_upper = keyword.upper()
    key_len = len(keyword_upper)

    # Create column order based on alphabetical sort of keyword
    sorted_keyword = sorted(enumerate(keyword_upper), key=lambda x: x[1])
    column_order = [i for i, _ in sorted_keyword]

    # Calculate number of rows
    num_rows = (len(ciphertext_bytes) + key_len - 1) // key_len

    # Create matrix
    matrix = [[None for _ in range(key_len)] for _ in range(num_rows)]

    # Fill matrix column by column in the order determined by keyword
    idx = 0
    for col_priority in range(key_len):
        # Find which column to fill
        col = column_order.index(col_priority)
        for row in range(num_rows):
            if idx < len(ciphertext_bytes):
                matrix[row][col] = ciphertext_bytes[idx]
                idx += 1
            else:
                matrix[row][col] = 0  # Padding

    # Read row by row
    result = bytes([cell for row in matrix for cell in row if cell is not None])
    return result[:len(ciphertext_bytes)]  # Trim to original length

# Read the data files
with open('otp_dump.bin', 'rb') as f:
    otp_data = f.read()

with open('secret.enc', 'rb') as f:
    encrypted_data = f.read()

# Parse UID
uid_hex = "5a928ebd3f5729b548b77e73"
uid = bytes.fromhex(uid_hex)

print("Testing Row Transposition Cipher...")
print("="*60)

# Extract IV and ciphertext
iv = encrypted_data[:16]
ciphertext = encrypted_data[16:]

# Try different keywords
keywords = [
    "SAINT",
    "SAINTS",
    "SAINTROW",
    "SAINTSROW",
    "ROWBOAT",
    "ROW",
    "BOAT",
]

attempts = []

for keyword in keywords:
    # Apply row transposition to OTP
    transposed = row_transposition_decrypt(otp_data, keyword)

    # Try first and last 16 bytes as key
    attempts.append((f"Row Transpose with '{keyword}' (first 16)", transposed[:16]))
    attempts.append((f"Row Transpose with '{keyword}' (last 16)", transposed[16:]))

# Also try reverse (encryption instead of decryption)
for keyword in keywords:
    keyword_upper = keyword.upper()
    key_len = len(keyword_upper)

    # Create column order based on alphabetical sort of keyword
    sorted_keyword = sorted(enumerate(keyword_upper), key=lambda x: x[1])

    # Fill row by row, read column by column in keyword order
    num_rows = (len(otp_data) + key_len - 1) // key_len
    matrix = []
    for i in range(num_rows):
        matrix.append(list(otp_data[i*key_len:(i+1)*key_len]))

    # Pad last row if needed
    while len(matrix[-1]) < key_len:
        matrix[-1].append(0)

    # Read columns in sorted order
    result = bytes()
    for _, char in sorted_keyword:
        col_idx = keyword_upper.index(char)
        for row in matrix:
            result += bytes([row[col_idx]])

    attempts.append((f"Row Transpose ENC with '{keyword}' (first 16)", result[:16]))
    attempts.append((f"Row Transpose ENC with '{keyword}' (last 16)", result[16:]))

# Try each key
for method_name, key in attempts:
    try:
        cipher = AES.new(key, AES.MODE_CBC, iv)
        plaintext = cipher.decrypt(ciphertext)

        # Check if it looks like valid text
        if all(32 <= b < 127 or b in [9, 10, 13] for b in plaintext):
            print(f"\n[POTENTIALLY VALID] Method: {method_name}")
            print(f"Key: {key.hex()}")
            print(f"Plaintext: {plaintext}")

            # Check for flag format
            text = plaintext.decode('ascii', errors='ignore')
            if 'POCTF{' in text or 'flag{' in text.lower() or 'ctf{' in text.lower():
                print(f"\n*** FLAG FOUND: {text} ***")
                break
    except Exception as e:
        pass

print("\n" + "="*60)
