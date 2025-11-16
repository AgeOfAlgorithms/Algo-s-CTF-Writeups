# Paper Tigers - CTF Writeup

## Challenge Information
- **Name:** Paper Tigers
- **Category:** Exploit (Binary Exploitation)
- **Difficulty:** Easy
- **Platform:** UWSP Pointer Overflow CTF
- **Target:** exp100-1.pointeroverflowctf.com:14660

## Challenge Description
Classic buffer overflow challenge with ret2libc exploitation. The binary has no PIE, no stack canaries, and conveniently leaks both a libc address (puts) and a stack address.

## Vulnerability Analysis

### Source Code Review
The vulnerable program ([exploit100-1.c](exploit100-1.c)) has the following key features:

1. **Information Leaks** - The `leak_addresses()` function helpfully provides:
   - Address of `puts()` in libc
   - A stack address

2. **Buffer Overflow** - The `vuln()` function has a classic overflow:
   ```c
   char buf[128];
   char inputbuf[512];
   ssize_t n = read(STDIN_FILENO, inputbuf, sizeof(inputbuf));
   // ...
   memcpy(buf, inputbuf, (size_t)n);  // Copies up to 512 bytes into 128-byte buffer!
   ```

3. **Compilation flags** - The binary was compiled with:
   - `-no-pie`: No Position Independent Executable
   - `-fno-stack-protector`: No stack canaries
   - `-O0`: No optimizations

### Finding the Offset

The critical step was determining the exact offset from the buffer to the return address. Initial attempts used 136 bytes (128-byte buffer + 8-byte saved RBP), but this was incorrect.

Using GDB to disassemble the `vuln()` function revealed:
```asm
lea    -0x90(%rbp),%rax    # buf is at RBP-0x90 (RBP-144)
```

The buffer is at RBP-144, not RBP-128. This means:
- Buffer: 128 bytes (at RBP-144 to RBP-16)
- Gap: 16 bytes (at RBP-16 to RBP)
- Saved RBP: 8 bytes (at RBP)
- Return address: at RBP+8

**Total offset: 152 bytes** (144 bytes to reach saved RBP + 8 bytes for saved RBP)

## Exploitation

### Attack Strategy
1. Connect to the target and parse the leaked addresses
2. Calculate libc base address using the leaked puts address
3. Find gadgets in libc:
   - `pop rdi; ret` - to set up function argument
   - `ret` - for stack alignment (required for x64 system() calls)
4. Build ROP chain to call `system("/bin/sh")`
5. Send commands to the spawned shell to read the flag

### Payload Structure
```python
payload = b'A' * 152          # Fill to return address
payload += p64(ret_addr)      # Stack alignment gadget
payload += p64(pop_rdi_addr)  # pop rdi; ret
payload += p64(binsh_addr)    # Address of "/bin/sh" string
payload += p64(system_addr)   # Call system()
```

### Exploit Code
The final working exploit is in [correct_offset_exploit.py](correct_offset_exploit.py).

Key steps:
1. Load libc and extract symbol offsets
2. Find ROP gadgets using pwntools' ROP module
3. Connect and parse leaked addresses
4. Calculate libc base: `libc_base = leaked_puts - puts_offset`
5. Calculate actual addresses of gadgets and functions
6. Build and send payload
7. Send shell commands to cat the flag

## Flag
```
poctf{uwsp_7h15_fl46_15_n07_4_clu3}
```

## Key Takeaways
1. Always verify buffer offsets with disassembly - don't assume based on source code variable sizes
2. The compiler may add padding between local variables
3. Stack alignment is important for x64 system() calls (hence the extra `ret` gadget)
4. Information leaks make ASLR bypass trivial
5. Classic ret2libc is still effective when modern mitigations are disabled
