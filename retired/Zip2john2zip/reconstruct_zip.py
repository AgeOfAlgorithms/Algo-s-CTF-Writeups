#!/usr/bin/env python3
"""
Reconstruct ZIP file from pkzip2 hash
Author: CTF Solver
Purpose: Reverse the zip2john process to recreate the ZIP archive
Created: 2025-11-09
Expected: Create a valid encrypted ZIP file from the hash data
Last updated: 2025-11-09
"""

import struct
import binascii
from datetime import datetime

def parse_pkzip2_hash(hash_line):
    """Parse a pkzip2 hash and extract components"""
    parts = hash_line.strip().split(':')
    filename_path = parts[0]  # e.g., "flag.zip/flag.txt"
    hash_data = parts[1]

    # Extract ZIP filename and internal filename
    zip_filename, internal_filename = filename_path.split('/')

    # Remove $pkzip2$ markers
    hash_data = hash_data.replace('$pkzip2$', '')
    fields = hash_data.split('*')

    return {
        'zip_filename': zip_filename,
        'internal_filename': internal_filename,
        'hash_count': int(fields[0]),
        'checksum_bytes': int(fields[1]),
        'magic_type': int(fields[2]),
        'unknown1': int(fields[3]),
        'compressed_len': int(fields[4], 16),
        'uncompressed_len': int(fields[5], 16),
        'crc32': fields[6],
        'compression_type': int(fields[7]),
        'data_len': int(fields[8], 16),
        'unknown2': int(fields[9]),
        'unknown3': int(fields[10], 16),
        'checksum': fields[11],
        'timestamp_checksum': fields[12],
        'encrypted_data': fields[13]
    }

def create_zip_file(data, output_filename):
    """Create a ZIP file from the parsed hash data"""

    filename = data['internal_filename'].encode('utf-8')
    encrypted_data = binascii.unhexlify(data['encrypted_data'])
    crc32 = int(data['crc32'], 16)
    compressed_size = data['compressed_len']
    uncompressed_size = data['uncompressed_len']

    # Use current time for modification timestamp
    now = datetime.now()
    mod_time = (now.hour << 11) | (now.minute << 5) | (now.second // 2)
    mod_date = ((now.year - 1980) << 9) | (now.month << 5) | now.day

    # Build local file header
    local_header = b''
    local_header += struct.pack('<I', 0x04034b50)  # Local file header signature
    local_header += struct.pack('<H', 20)          # Version needed to extract (2.0)
    local_header += struct.pack('<H', 0x0001)      # General purpose bit flag (bit 0 = encrypted)
    local_header += struct.pack('<H', 0)           # Compression method (0 = stored)
    local_header += struct.pack('<H', mod_time)    # File modification time
    local_header += struct.pack('<H', mod_date)    # File modification date
    local_header += struct.pack('<I', crc32)       # CRC-32
    local_header += struct.pack('<I', compressed_size)   # Compressed size
    local_header += struct.pack('<I', uncompressed_size) # Uncompressed size
    local_header += struct.pack('<H', len(filename))     # Filename length
    local_header += struct.pack('<H', 0)           # Extra field length
    local_header += filename                       # Filename

    # Save offset for central directory
    local_header_offset = 0

    # Combine local header with encrypted data
    local_file_data = local_header + encrypted_data

    # Build central directory header
    central_header = b''
    central_header += struct.pack('<I', 0x02014b50)  # Central directory signature
    central_header += struct.pack('<H', 20)          # Version made by
    central_header += struct.pack('<H', 20)          # Version needed to extract
    central_header += struct.pack('<H', 0x0001)      # General purpose bit flag (encrypted)
    central_header += struct.pack('<H', 0)           # Compression method
    central_header += struct.pack('<H', mod_time)    # Modification time
    central_header += struct.pack('<H', mod_date)    # Modification date
    central_header += struct.pack('<I', crc32)       # CRC-32
    central_header += struct.pack('<I', compressed_size)   # Compressed size
    central_header += struct.pack('<I', uncompressed_size) # Uncompressed size
    central_header += struct.pack('<H', len(filename))     # Filename length
    central_header += struct.pack('<H', 0)           # Extra field length
    central_header += struct.pack('<H', 0)           # File comment length
    central_header += struct.pack('<H', 0)           # Disk number start
    central_header += struct.pack('<H', 0)           # Internal file attributes
    central_header += struct.pack('<I', 0x20)        # External file attributes
    central_header += struct.pack('<I', local_header_offset)  # Relative offset of local header
    central_header += filename                       # Filename

    central_directory_offset = len(local_file_data)
    central_directory_size = len(central_header)

    # Build end of central directory record
    eocd = b''
    eocd += struct.pack('<I', 0x06054b50)  # End of central directory signature
    eocd += struct.pack('<H', 0)           # Number of this disk
    eocd += struct.pack('<H', 0)           # Disk where central directory starts
    eocd += struct.pack('<H', 1)           # Number of central directory records on this disk
    eocd += struct.pack('<H', 1)           # Total number of central directory records
    eocd += struct.pack('<I', central_directory_size)     # Size of central directory
    eocd += struct.pack('<I', central_directory_offset)   # Offset of start of central directory
    eocd += struct.pack('<H', 0)           # ZIP file comment length

    # Combine all parts
    zip_data = local_file_data + central_header + eocd

    # Write to file
    with open(output_filename, 'wb') as f:
        f.write(zip_data)

    print(f"Created ZIP file: {output_filename}")
    print(f"  Internal filename: {data['internal_filename']}")
    print(f"  Compressed size: {compressed_size} bytes")
    print(f"  Uncompressed size: {uncompressed_size} bytes")
    print(f"  CRC32: 0x{data['crc32']}")
    print(f"  Compression: {'stored' if data['compression_type'] == 0 else 'deflated'}")
    print(f"  Encrypted: Yes")

if __name__ == "__main__":
    with open('hash.txt', 'r') as f:
        hash_line = f.read().strip()

    data = parse_pkzip2_hash(hash_line)
    create_zip_file(data, data['zip_filename'])
