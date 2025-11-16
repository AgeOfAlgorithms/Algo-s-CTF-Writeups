# The Long Way Home - Unsolved Challenge Documentation

## Challenge Information
- **Name**: The Long Way Home
- **Platform**: UWSP Pointer Overflow CTF
- **Category**: Exploit (medium-hard)
- **Target**: exp300-2.pointeroverflowctf.com:7092

## Vulnerability Identified

**Off-by-one heap overflow** in the `read_line` function:
```c
malloc(size)  // Allocates exactly 'size' bytes
read_line(notes[i], size + 1)  // Reads up to 'size' characters + null terminator
```

When writing exactly `size` characters, the null terminator at position `size` overflows by one byte into the next heap chunk.

## Goal
Change the filepath from "not_the_flag.txt" to "flag.txt" to read the flag via execl("/usr/bin/cat", "cat", filepath, NULL).

## Key Observations

1. **String structure insight**: "not_the_flag.txt" contains "flag.txt" at offset 8:
   - Position 0-7: "not_the_"
   - Position 8-16: "flag.txt"

2. **filepath behavior**:
   - `filepath = strdup("not_the_flag.txt")` allocates 18 bytes on heap
   - The filepath variable itself is on the stack (can't be reached by heap overflow)
   - Only the string it points to is on the heap

3. **Server personalities**: Remote server has multiple "personalities" (Waifu, Marv) mentioned in challenge description

4. **Challenge hint**: "work out the right angle" - suggests simpler solution than expected

##  Assumptions Made and Approaches Tried

### Assumption 1: Direct Heap Layout Manipulation
**Assumption**: Create notes in specific orders to place a note adjacent to filepath string, then overflow into it.

**Attempts**:
- Created notes before setting filename
- Created notes after setting filename
- Deleted notes to create holes, then set filename
- Tried sizes: 1-50, with various combinations

**Result**: Failed - filepath always remained "not_the_flag.txt"

**Potential Error**: May not have found the correct size or order combination

### Assumption 2: Heap Metadata Corruption
**Assumption**: Use off-by-one to corrupt heap chunk metadata (size/flags) to cause overlapping chunks.

**Attempts**:
- Created multiple notes of size 32
- Deleted middle notes to fragment heap
- Tried to trigger chunk consolidation

**Result**: Failed - no observable effect on filepath

**Potential Error**: Modern glibc protections may prevent simple metadata corruption, or technique too complex for "easier than it seems" challenge

### Assumption 3: Memory Reuse Strategy
**Assumption**: Make filepath and a note point to the same memory by freeing and reallocating.

**Attempts**:
- Set filename multiple times (leaks old filepath strings)
- Created notes of size 17-18 (same as filepath size)
- Wrote "flag.txt" to notes hoping for memory reuse

**Result**: Failed - no memory overlap observed

**Potential Error**: Malloc doesn't reuse freed filepath memory for notes due to different size classes or allocation patterns

### Assumption 4: filepath Pointer Corruption
**Assumption**: Make filepath pointer point to offset +8 of the string (where "flag.txt" starts).

**Result**: Not feasible - filepath pointer is a stack variable, unreachable by heap overflow

### Assumption 5: Direct String Modification
**Assumption**: Overflow to modify bytes within filepath string itself.

**Limitation**: Can only null-terminate at specific positions, cannot insert "flag.txt"

### Assumption 6: Brute Force Size Combinations
**Assumption**: There exists a "magic" size/order combination that works.

**Attempts**:
- Tested sizes 1-50 with various operation orders
- Tested note -> filename -> note combinations
- Tested note -> delete -> filename -> note combinations

**Result**: No combination found in tested range

**Potential Error**: May need larger sizes, specific metadata-aligned sizes, or more complex operation sequences

### Assumption 7: "Right Angle" Hint Interpretation
**Interpretations Considered**:
- "Right angle" = 90 degrees = specific numeric value?
- "Right approach" vs "wrong approach"
- Mathematical relationship between sizes
- Binary/hex value patterns
- Different attack vector entirely

**Result**: No clear interpretation led to success

## Unexplored Approaches

1. **Advanced Heap Techniques**:
   - Tcache poisoning
   - Fastbin dup
   - Unsafe unlink (if applicable)

2. **Size Alignment**:
   - Testing sizes that align with glibc chunk size classes (16, 32, 64, etc.)
   - Testing sizes related to filepath length (17, 18, 19)

3. **Multiple Overflow Strategy**:
   - Creating multiple notes that each overflow slightly
   - Cascading effects

4. **Race Conditions** (if server is multi-threaded)

5. **Integer Overflow in size calculations** (already checked, seems protected)

6. **Environment/System-specific Behavior**:
   - Different behavior between local binary and remote server
   - Server-specific file setup

## Tools & Scripts Created

1. `analysis.md` - Initial vulnerability analysis
2. `heap_overflow_exploit.py` - Basic exploit attempt
3. `heap_manipulation_test.py` - Testing different heap layouts
4. `refined_exploit.py` - Refined approach with heap holes
5. `systematic_test.py` - Systematic size testing
6. `angle_approach.py` - Various "angle" interpretations
7. `simple_remote_test.py` - Basic remote testing
8. `pointer_manipulation.py` - Overlap technique testing
9. `brute_force_sizes.py` - Comprehensive size brute forcing
10. `multiple_filename_test.py` - Multiple filename calls
11. `overlap_memory.py` - Memory reuse attempt

## Ghidra Analysis Findings

Using Ghidra MCP to decompile and analyze the binary, I discovered:

1. **Decompiled Off-by-One Loop**:
```c
do {
  iVar3 = getc(stdin);
  if ((iVar3 == 10) || (iVar3 == -1)) break;
  iVar2 = iVar2 + 1;
  *pcVar7 = (char)iVar3;
  pcVar7 = pcVar7 + 1;
} while (iVar2 != iVar1 + 1);  // iVar1 = size, so reads up to size+1 chars
pcVar4[iVar2] = '\0';  // Null byte written at position 'size'
```

2. **String in Binary**: "not_the_flag.txt" is at 0x001020df in `.rodata`:
```
001020df  6e 6f 74 5f 74 68 65 5f  66 6c 61 67 2e 74 78 74
          n  o  t  _  t  h  e  _   f  l  a  g  .  t  x  t
```
   - Bytes 0-7: "not_the_"
   - Bytes 8-16: "flag.txt" ← The "right angle" likely refers to viewing this substring!

3. **Memory Leak**: Each call to option 3 does `local_e8 = strdup("not_the_flag.txt")` without freeing the previous pointer, creating a heap leak.

4. **Stack vs Heap**: The `local_e8` (filepath) variable is on the stack, but it points to heap memory. Heap overflow can modify the heap string, but not the stack pointer itself.

## Additional Scripts Created (Ghidra Analysis Phase)

12. `ghidra_insight_exploit.py` - Exploit based on strdup memory reuse
13. `offset_pointer_exploit.py` - Attempt to leverage +8 offset insight
14. `heap_metadata_corruption.py` - Systematic heap metadata corruption tests

## Questions Remaining

1. What does "work out the right angle" specifically refer to?
   - **Likely Answer**: The substring "flag.txt" at offset 8 within "not_the_flag.txt"
   - **Unknown**: How to exploit this insight with only a null-byte overflow

2. Is there a specific heap layout that's achievable but not yet discovered?
   - Testing showed no obvious layout works with sizes 1-50
   - May require understanding of exact glibc malloc chunk sizes and alignment

3. Is the solution related to the server's "multiple personalities"?
   - Different messages (Waifu/Marv) but no apparent functional difference

4. Does the solution require understanding of specific glibc malloc implementation details?
   - Likely yes - may involve tcache, fastbins, or specific chunk size classes

5. Is there a completely different vulnerability not yet identified?
   - Unlikely - off-by-one seems to be the intended vulnerability
   - Memory leak from repeated filename calls might be relevant

## Recommendations for Next Attempt

1. **Manual GDB Analysis**: Step through program with GDB to observe actual heap layout and addresses
2. **Study Malloc Implementation**: Research exact glibc malloc behavior for size 18 allocations
3. **Test Larger Sizes**: Try sizes beyond 50, especially metadata-aligned values
4. **Alternative Vulnerabilities**: Look for other bugs besides off-by-one
5. **Seek Hints**: Look for similar challenges or official hints if available
6. **Different Tools**: Try heap visualization tools like pwndbg's heap commands

## Conclusion

Despite extensive testing and multiple exploitation strategies, the challenge remains unsolved. The hint that it's "much easier than it might seem" suggests a simpler approach exists that has been overlooked. The core challenge is finding a way to change the filepath string from "not_the_flag.txt" to "flag.txt" using only a single null-byte heap overflow.
