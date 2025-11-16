# Count the Cost - CTF Writeup

**Flag:** `poctf{uwsp_0u7574nd1n6_1n_7h31r_f13ld}`

## Challenge Information
- **Category:** Exploit
- **Difficulty:** Medium
- **Target:** 34.9.14.80:14992
- **Binary:** exp200-2.bin

## Initial Analysis

The challenge provides a 64-bit ELF binary compiled with the following protections:
- `-fno-stack-protector` - No stack canaries
- `-z noexecstack` - Non-executable stack (NX enabled)
- `-no-pie -fno-pic` - No PIE (fixed addresses)
- `-Wl,-z,relro -Wl,-z,now` - Full RELRO

The binary implements a transaction tracking system with 4 menu options:
1. `add_txn` - Add a transaction with an amount
2. `set_note` - Attach a note to a transaction
3. `checkout` - Calculate total and potentially reveal flag
4. `quit` - Exit the program

## Vulnerability Discovery

### The Flaw in set_note

The vulnerability exists in the `set_note` function at address `0x401268`. The function:

1. Prompts for a transaction index (0-7)
2. Asks for a note length as a uint16 (2 bytes)
3. Reads the 2-byte length value
4. **Performs the check:** `cmp bl, 0x40` (assembly at `0x4012d3`)
5. If `bl <= 0x40`, proceeds to `malloc(length)` and reads `length` bytes

**The Critical Bug:** The length check uses `cmp bl, 0x40`, which only compares the **low byte** of the length value, but `malloc()` and `read()` use the **full 16-bit value**.

### Exploitation Path

By sending a carefully crafted length value like `0x0240` (576 bytes):
- The low byte is `0x40`, which passes the check (`0x40 <= 0x40` ✓)
- But `malloc` allocates 576 bytes and `read` accepts 576 bytes
- This allows us to overflow beyond the intended 64-byte limit

### The Magic Value

In the `checkout` function at `0x401380`, there's a check at address `0x4013e4`:

```assembly
cmp QWORD PTR [r15+0x220], 0xc0dec0dec0dec0de
je  0x401410  ; If equal, opens /flag/flag.txt
```

If the value at offset `0x220` from the transactions buffer equals the magic value `0xc0dec0dec0dec0de`, the program opens and displays the flag file instead of performing a standard checkout.

### Memory Layout

The program allocates `0x260` (608) bytes for the transactions buffer:
- Transactions start at offset `0x40` from the buffer start
- Each transaction occupies 68 bytes (`17 * 4`)
- Transaction 0's note starts at offset `0x0` from buffer start
- The magic value is at offset `0x220` (544 bytes) from buffer start

## Exploitation

### Attack Strategy

1. Call `set_note` (option 2)
2. Select transaction index 0
3. Send length `0x0240` (576 bytes) to bypass the byte-only check
4. Send payload: 544 bytes padding + 8 bytes of magic value
5. Call `checkout` (option 3) to trigger flag retrieval

### Exploit Code

See [buffer_overflow_exploit.py](buffer_overflow_exploit.py) for the complete exploit implementation.

### Key Payload Components

```python
malicious_length = p16(0x0240)  # Bypass check with 576 bytes
magic_value = 0xc0dec0dec0dec0de
payload = b'A' * 544 + p64(magic_value) + padding
```

## Result

Running the exploit successfully overwrites the magic value and triggers the manager override:

```
total: $87583646.80
manager override accepted
poctf{uwsp_0u7574nd1n6_1n_7h31r_f13ld}
```

## Lessons Learned

1. **Type Consistency:** Always use consistent data types for validation and operations
2. **Proper Bounds Checking:** When checking multi-byte values, verify the entire value, not just a single byte
3. **Defense in Depth:** Even with memory protections enabled, logic bugs can lead to exploitable conditions
4. **Integer Truncation:** Be aware of implicit type conversions and truncation in assembly operations

## Tools Used

- `objdump` - Binary disassembly
- `readelf` - ELF header analysis
- `nm` - Symbol table inspection
- `pwntools` - Exploit development framework
