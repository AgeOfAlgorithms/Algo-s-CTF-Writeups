#!/usr/bin/env python3
"""
Parse pkzip2 hash and extract components
Author: CTF Solver
Purpose: Extract encrypted data and metadata from zip2john hash
Created: 2025-11-09
Expected: Parse hash successfully and display components
"""

def parse_pkzip2_hash(hash_line):
    """Parse a pkzip2 hash and extract components"""
    # Split the line
    parts = hash_line.strip().split(':')
    filename = parts[0]
    hash_data = parts[1]

    print(f"Filename: {filename}")
    print(f"Hash: {hash_data}\n")

    # Remove $pkzip2$ markers
    hash_data = hash_data.replace('$pkzip2$', '')

    # Split by asterisks
    fields = hash_data.split('*')

    print("Hash Fields:")
    for i, field in enumerate(fields):
        print(f"  [{i}]: {field}")

    # Parse according to format: C*B*[MT*?*CL*UL*CR*CT*DL*?*?*CS*TC*DA]
    hash_count = int(fields[0])
    checksum_bytes = int(fields[1])
    magic_type = int(fields[2])
    unknown1 = int(fields[3])
    compressed_len = int(fields[4], 16)  # hex
    uncompressed_len = int(fields[5], 16)  # hex
    crc32 = fields[6]
    compression_type = int(fields[7])
    data_len = int(fields[8], 16)  # hex
    unknown2 = int(fields[9])
    unknown3 = int(fields[10], 16)  # hex
    checksum = fields[11]
    timestamp_checksum = fields[12]
    encrypted_data = fields[13]

    print(f"\nParsed Data:")
    print(f"  Hash Count: {hash_count}")
    print(f"  Checksum Bytes: {checksum_bytes}")
    print(f"  Magic Type: {magic_type}")
    print(f"  Unknown1: {unknown1}")
    print(f"  Compressed Length: {compressed_len} bytes (0x{fields[4]})")
    print(f"  Uncompressed Length: {uncompressed_len} bytes (0x{fields[5]})")
    print(f"  CRC32: 0x{crc32}")
    print(f"  Compression Type: {compression_type} {'(stored)' if compression_type == 0 else '(deflated)'}")
    print(f"  Data Length: {data_len} bytes (0x{fields[8]})")
    print(f"  Unknown2: {unknown2}")
    print(f"  Unknown3: {unknown3} (0x{fields[10]})")
    print(f"  Checksum: 0x{checksum}")
    print(f"  Timestamp Checksum: 0x{timestamp_checksum}")
    print(f"  Encrypted Data: {encrypted_data}")
    print(f"  Encrypted Data Length: {len(encrypted_data)//2} bytes")

    return {
        'filename': filename,
        'hash_count': hash_count,
        'checksum_bytes': checksum_bytes,
        'magic_type': magic_type,
        'compressed_len': compressed_len,
        'uncompressed_len': uncompressed_len,
        'crc32': crc32,
        'compression_type': compression_type,
        'data_len': data_len,
        'checksum': checksum,
        'timestamp_checksum': timestamp_checksum,
        'encrypted_data': encrypted_data
    }

if __name__ == "__main__":
    with open('hash.txt', 'r') as f:
        hash_line = f.read().strip()

    data = parse_pkzip2_hash(hash_line)
