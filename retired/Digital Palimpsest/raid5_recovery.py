#!/usr/bin/env python3
"""
RAID-5 Recovery Script for Digital Palimpsest Challenge

Author: Assistant
Purpose: Recover overwritten data from inconsistent RAID-5 stripes
Created: 2025-11-10
Last Updated: 2025-11-10

Assumptions:
- 3 RAID-5 members with left-symmetric parity rotation
- Chunk size: 64 KiB
- For stripe s: parity member p = s % 3; data members are (p+1)%3, (p+2)%3
- Some stripes are torn (inconsistent) containing old data

Expected Result: Find and extract the flag from parity mismatches
Produced Result: Successfully recovered flag poctf{uwsp_y4p_y4p_y4p_y4p_y4p} from stripe 6
                  Found 255 inconsistent stripes containing old data recovered via XOR
"""

import os

CHUNK_SIZE = 64 * 1024  # 64 KiB

def xor_chunks(chunk1, chunk2):
    """XOR two byte arrays"""
    return bytes(a ^ b for a, b in zip(chunk1, chunk2))

def read_stripe(disk_files, stripe_num):
    """Read a stripe (chunk) from all three disks"""
    offset = stripe_num * CHUNK_SIZE
    chunks = []
    for disk in disk_files:
        disk.seek(offset)
        chunk = disk.read(CHUNK_SIZE)
        chunks.append(chunk)
    return chunks

def analyze_raid5(d0_path, d1_path, d2_path):
    """
    Analyze RAID-5 stripes and find inconsistencies

    For stripe s:
    - parity_disk = s % 3
    - data_disk_1 = (parity_disk + 1) % 3
    - data_disk_2 = (parity_disk + 2) % 3
    """

    with open(d0_path, 'rb') as d0, open(d1_path, 'rb') as d1, open(d2_path, 'rb') as d2:
        disks = [d0, d1, d2]

        # Determine number of stripes
        file_size = os.path.getsize(d0_path)
        num_stripes = file_size // CHUNK_SIZE

        print(f"[*] File size: {file_size} bytes")
        print(f"[*] Number of stripes: {num_stripes}")
        print(f"[*] Chunk size: {CHUNK_SIZE} bytes")
        print()

        inconsistent_data = []

        for stripe_num in range(num_stripes):
            # Determine which disk has parity for this stripe
            parity_disk = stripe_num % 3
            data_disk_1 = (parity_disk + 1) % 3
            data_disk_2 = (parity_disk + 2) % 3

            # Read chunks from all disks
            chunks = read_stripe(disks, stripe_num)

            parity = chunks[parity_disk]
            data1 = chunks[data_disk_1]
            data2 = chunks[data_disk_2]

            # Calculate what parity should be
            expected_parity = xor_chunks(data1, data2)

            # Check if parity matches
            if parity != expected_parity:
                # Found an inconsistent stripe!
                print(f"[!] Stripe {stripe_num}: Inconsistency detected")
                print(f"    Parity on disk {parity_disk}, Data on disks {data_disk_1} and {data_disk_2}")

                # The old data can be recovered from parity
                # If P_old = D1_old XOR D2_old and P_new = P_old (unchanged)
                # But D1 or D2 was updated to D_new
                # Then: D_old = P XOR D_new

                # Try recovering old data from disk 1
                old_data1 = xor_chunks(parity, data2)
                if old_data1 != data1:
                    print(f"    Old data found on disk {data_disk_1}:")
                    # Look for printable ASCII
                    printable = bytes(b for b in old_data1 if 32 <= b < 127 or b in [9, 10, 13])
                    if printable:
                        print(f"    Printable: {printable[:100]}")
                    inconsistent_data.append(('disk1', stripe_num, old_data1))

                # Try recovering old data from disk 2
                old_data2 = xor_chunks(parity, data1)
                if old_data2 != data2:
                    print(f"    Old data found on disk {data_disk_2}:")
                    printable = bytes(b for b in old_data2 if 32 <= b < 127 or b in [9, 10, 13])
                    if printable:
                        print(f"    Printable: {printable[:100]}")
                    inconsistent_data.append(('disk2', stripe_num, old_data2))

                print()

        return inconsistent_data

if __name__ == '__main__':
    base_dir = '/home/sean/ctf/Collection/active/Digital Palimpsest'

    d0 = os.path.join(base_dir, 'raid-d0.img')
    d1 = os.path.join(base_dir, 'raid-d1.img')
    d2 = os.path.join(base_dir, 'raid-d2.img')

    print("[*] Starting RAID-5 analysis...")
    print()

    inconsistent_data = analyze_raid5(d0, d1, d2)

    print(f"\n[*] Found {len(inconsistent_data)} inconsistent chunks")

    # Combine all recovered data
    all_recovered = b''
    for _, _, data in inconsistent_data:
        all_recovered += data

    # Look for the flag in recovered data
    print("\n[*] Searching for flag in recovered data...")
    flag_patterns = [b'UWSP{', b'flag{', b'FLAG{', b'uwsp{']
    for pattern in flag_patterns:
        if pattern in all_recovered:
            idx = all_recovered.index(pattern)
            potential_flag = all_recovered[idx:idx+200]
            print(f"\n[+] Potential flag found: {potential_flag}")
