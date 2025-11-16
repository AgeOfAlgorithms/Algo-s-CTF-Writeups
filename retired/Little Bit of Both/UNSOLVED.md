# Little Bit of Both - Unsolved Challenge Analysis

## Challenge Information
- **Platform**: UWSP Pointer Overflow CTF
- **Category**: Exploit
- **Difficulty**: Easy
- **Target**: exp100-3.pointeroverflowctf.com:14667
- **Flag Location**: flag/flag.txt

## Challenge Description
Classic Morris Worm fingerd buffer overflow exploit. The binary has:
- Executable stack (-zexecstack)
- No stack canaries (-fno-stack-protector)
- No PIE (-no-pie)
- `gets()` vulnerability on line 60 of source code

## Assumptions Made and Attempts

### 1. Buffer Overflow Offset Calculation
**Assumption**: The return address can be overwritten at offset 552 bytes from the buffer start.
- Buffer is at `rbp-0x220` (544 bytes)
- Return address is at `rbp+8`
- Total offset: 0x220 + 8 = 0x228 = 552 bytes

**Verification**: Confirmed via disassembly and GDB analysis.
**Status**: ✓ Correct

### 2. Stack Address Prediction
**Assumption**: Stack addresses would be predictable/fixed since binary has no PIE.
- Local GDB analysis showed buffer at `0x7fffffffd330`
- Tried addresses in range `0x7fffffffd000` to `0x7fffffffe000`
- Attempted 256+ different addresses with NOP sled

**Result**: Failed - No working address found
**Possible Issues**:
- Remote server may have ASLR enabled
- Environment variables differ significantly from local
- Stack layout differs due to system configuration

### 3. Shellcode Execution
**Assumption**: Standard x64 shellcode (shellcraft.amd64.linux.sh()) would work.
- Used 48-byte shellcode to spawn /bin/sh
- Preceded with 300-400 byte NOP sled
- Shellcode tested and confirmed working locally

**Status**: Shellcode itself appears valid
**Possible Issues**:
- May not be reaching shellcode due to crash before return
- Stack alignment issues
- Shellcode may need modification for remote environment

### 4. Exploit Techniques Attempted

#### A. Direct Stack Shellcode Injection
- Payload: NOP sled + shellcode + padding + return address
- Tried multiple return addresses in buffer range
- **Result**: Failed

#### B. Direct Flag Reading Shellcode
- Created custom shellcode to open() and read() flag file directly
- Avoided need for interactive shell
- **Result**: Failed - no output received

#### C. Brute Force Address Guessing
- Systematically tried 256 different stack addresses
- Range: 0x7fffffffd000 - 0x7fffffffe000 (step 0x10)
- **Result**: Timed out after 151 attempts, no success

### 5. Alternative Approaches Considered

#### Ret2libc
**Assumption**: Could return to system() in libc.
**Issue**:
- Binary doesn't have system() in PLT
- Would need libc address leak
- Libc addresses contain null bytes (though gets() can handle them)
**Status**: Not viable without information leak

####  Environment Variable Shellcode
**Assumption**: Could place shellcode in environment variable at predictable address.
**Issue**: Cannot control remote environment via network connection
**Status**: Not applicable for remote exploit

### 6. Analysis of Challenge Title
**"Little Bit of Both"** - Possible interpretations:
1. Both shellcode AND ROP techniques needed?
2. Both 32-bit and 64-bit exploitation?
3. Both classic and modern techniques?
4. Wordplay on "bits" (binary digits)?

**Status**: Unclear - may be missing the intended hint

## Key Questions / Unknowns

1. **ASLR Status**: Is ASLR enabled on the remote server?
   - If yes, need information leak or different approach
   - If no, why aren't predicted addresses working?

2. **Environment Differences**: What differs between local and remote?
   - Environment variables (HOME, PATH, etc.)
   - Stack layout due to loader differences
   - Kernel/system configuration

3. **Missing Technique**: Is there a specific Morris Worm technique not being used?
   - Original worm used environment variables
   - Original worm may have had different payload structure

4. **Challenge Design Intent**: What does "Little Bit of Both" actually mean?
   - Could this be hinting at a hybrid exploit approach?
   - Is there something about the binary name "exp100-3" that's significant?

## Files Created
- `morris_worm_exploit.py` - Initial exploit attempt
- `exploit.py` - Address-trying exploit
- `robust_exploit.py` - Multi-address attempt
- `ret2libc_exploit.py` - Analysis of ROP approach
- `direct_flag_exploit.py` - Custom shellcode for direct flag reading
- `corrected_exploit.py` - GDB-informed address targeting
- `brute_force_exploit.py` - Systematic address brute force
- `find_offset.py` - Offset calculation verification

## Next Steps for Future Attempts

1. **Test Locally First**: Verify exploit works 100% on local binary before remote attempts
2. **Information Gathering**:
   - Check if there's a way to leak stack addresses
   - Investigate if challenge provides any hints or auxiliary files
   - Research if others have solved similar challenges

3. **Alternative Exploitation Vectors**:
   - Investigate the `execv()` call in the binary
   - Look for format string vulnerabilities
   - Check if input parsing logic has exploitable flaws

4. **Ask for Clarification**: The challenge may require interaction with challenge authors or have missing information

## Technical Notes
- Binary confirmed to have executable stack and no protections
- Offset calculation verified multiple times
- Local GDB showed stack at ~0x7fffffffd330
- No ROP gadgets readily available for complex chains
- PLT/GOT doesn't contain useful functions for ret2plt

## Conclusion
Despite multiple exploitation attempts and techniques, unable to successfully exploit the remote service. The most likely issue is the inability to predict the correct stack address on the remote system, possibly due to ASLR or significant environment differences. The challenge title "Little Bit of Both" may contain a hint about the required approach that has not been deciphered.
