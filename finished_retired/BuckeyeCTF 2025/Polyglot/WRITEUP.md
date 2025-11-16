# Polyglot Challenge Writeup

## Challenge Information
- **Name:** Monoglot, Diglot, Triglot, etc.
- **Platform:** BuckeyeCTF 2025
- **Category:** polyglot
- **Difficulty:** multiple

## Challenge Description
Craft a single executable that does the same operations on as many architectures as possible (each additional one reveals a flag).

**Goal:**
- Syscall number: 237
- Arg1: 38085 (0x94c5)
- Arg2: pointer to the string "Battelle"

**Supported Architectures:**
1. arm_le
2. arm_be
3. arm_thumb_le
4. aarch64_le
5. mips_le
6. mips_be
7. x86
8. x86_64
9. riscv64
10. powerpc32

## Solution

### Achieved: 2/10 Architectures (x86 and x86_64)

I successfully created a **Diglot** - a polyglot shellcode that works on both x86 (32-bit) and x86_64 architectures.

### Technique: REX Prefix Exploitation

The key technique used was exploiting how x86-64 repurposes the single-byte `inc` opcode (`0x40`) as a REX prefix:

**Dispatcher Logic:**
```assembly
xor eax, eax    ; Clear eax, set ZF=1 (31 c0)
0x40            ; x86: inc eax (ZF=0), x86_64: REX prefix (ZF stays 1)
jz x64_code     ; Jump if Zero
; x86 code here
x64_code:
; x86_64 code here
```

**Execution Flow:**

*On x86 (32-bit):*
1. `xor eax, eax` → eax=0, ZF=1
2. `inc eax` → eax=1, ZF=0
3. `jz` → doesn't jump (ZF=0)
4. Executes x86 code

*On x86_64:*
1. `xor eax, eax` → eax=0, ZF=1
2. REX prefix → ignored, ZF=1, eax=0
3. `jz` → jumps (ZF=1)
4. Executes x86_64 code

### Implementation Details

**x86 Payload:**
- Push "Battelle\x00" string onto stack (in reverse order)
- Set registers: ecx=pointer to string, ebx=38085, eax=237
- Execute syscall via `int 0x80`

**x86_64 Payload:**
- Push "Battelle\x00" string onto stack
- Set registers: rsi=pointer to string, rdi=38085, rax=237
- Execute syscall via `syscall` instruction

**Critical Bug Fixed:**
Initially used 0x94d5 for arg1, but the correct hex value is 0x94c5 (38085 decimal).

**Jump Offset Calculation:**
Keystone assembler interprets jump targets as addresses and subtracts the instruction size.
To jump +30 bytes, must pass 32 to the assembler (32 - 2 = 30).

### Final Shellcode

```
Length: 79 bytes
Hex: 31c040741e6a0068656c6c65684261747489e1bbc5940000b8ed000000cd8031c0cd806a0048b842617474656c6c65504889e648c7c7c594000048c7c0ed0000000f054831ff48c7c03c0000000f05
```

## Flags Obtained

1. **Monoglot flag:** `bctf{a_good_start_4fc9c43c0d95}`
2. **Diglot flag:** `bctf{now_you_are_bilingual_d9731b3bf6bf}`

## Challenges Encountered

### Multi-Architecture Complexity

Attempting to extend to 3+ architectures proved extremely challenging because:

1. **Conflicting Instruction Encodings:** The same bytes are interpreted completely differently:
   - x86 dispatcher: `xor eax, eax; inc eax; jz`
   - ARM interpretation: `strbvc ip, [r0], #-0x31` (memory write that crashes)

2. **Alignment Issues:** ARM/MIPS use fixed 4-byte instructions, x86 uses variable-length

3. **Endianness:** Need separate handling for LE vs BE variants

4. **Limited Magic Sequences:** Finding bytes that work as:
   - Functional dispatcher on x86/x86_64
   - Harmless/NOP on ARM
   - Branch instruction on MIPS
   - Valid on RISC-V and PowerPC

### Research Findings

Multi-architecture polyglots (5+ architectures) typically use:
- Sophisticated dispatchers with "magic blocks"
- Bytes like `EB XX 00 32` that interpret differently
- Staged execution with architecture-specific jumps
- Tools like xarch_shellcode for automated generation

## Tools Used

- **Keystone Engine:** Multi-architecture assembler
- **Capstone:** Multi-architecture disassembler (for analysis)
- **pwntools:** CTF framework
- **Python 3:** Scripting and automation

## References

- [DEFCON 2018] Doublethink – 8-Architecture Assembly Polyglot
- Midnightsun CTF 2019 Polyshell Writeup
- xarch_shellcode GitHub repository
- x86/x86-64 polyglot techniques (Stack Overflow)

## Conclusion

Successfully created a 2-architecture polyglot (Diglot) using REX prefix exploitation. Achieving 3+ architectures would require significantly more sophisticated dispatcher techniques and possibly automated tools. The challenge demonstrates the extreme complexity of creating true multi-architecture polyglots.
