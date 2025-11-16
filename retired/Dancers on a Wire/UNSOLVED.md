# Dancers on a Wire - Unsolved Analysis

## Challenge Status: BLOCKED

### What I've Accomplished
1. ✅ Identified vulnerability: Stack buffer overflow (96 bytes buffer, 400 bytes read)
2. ✅ Found syscall gadget at offset 0x1247
3. ✅ Understood seccomp restrictions (only read, write, exit, exit_group, rt_sigreturn allowed)
4. ✅ Identified flag is pre-opened on FD 3
5. ✅ Built theoretical SROP chain to read(3, bss, 0x100) then write(1, bss, 0x100)
6. ✅ Created multiple exploit attempts
7. ✅ Connected to remote server successfully
8. ✅ Confirmed exploit reaches "round 2" (partial success)

### Critical Blocker: The `xor eax, eax` Problem

**Location:** Main function at offset 0x1139

**Disassembly:**
```assembly
1130:	call   read@plt        # Second read(0, buf, 400)
                               # Returns with rax = bytes_read
1135:	add    rsp,0x60
1139:	xor    eax,eax         # ← ZEROS RAX!
113b:	pop    rbx
113c:	ret                    # rax is 0, not 15
```

**Impact:**
Even if we send exactly 15 bytes in the second read to set rax=15, the `xor eax, eax` instruction (from `return 0;` in the source) zeros it before returning. When control reaches our syscall gadget, rax=0 (read syscall) instead of rax=15 (rt_sigreturn), preventing SROP chain from triggering.

### Attempted Solutions (All Failed)

1. **Send 15 bytes in second read**
   - ❌ Result: rax=15, then xor zeros it to rax=0

2. **Skip xor by returning to different address**
   - ❌ Tried: Return to 0x113b (pop rbx; ret)
   - ❌ Problem: Control flow already passed through xor

3. **Use first read for rax=15**
   - ❌ Problem: Second read and subsequent code overwrites rax

4. **Call do_syscall(15, ...) directly**
   - ❌ Problem: No `pop rdi; ret` gadget to set first argument to 15

5. **Brute force PIE bases**
   - ❌ Tried: 0x400000, 0x555555554000, 0x555555555000, 0x0
   - ❌ All fail at same point (can't trigger rt_sigreturn)

6. **Multiple exploit iterations**
   - ❌ All crash after sending second payload
   - ❌ Connection closes, suggesting program crash/exit

### Observations

**Partial Success:**
- Exploit successfully overflows return address
- First SROP payload is properly placed on stack
- Second read correctly receives 15 bytes
- But program crashes instead of executing SROP chain

**Available Gadgets:**
- `syscall; ret` at 0x1247 ✅
- `pop rbx; ret` at 0x113b ✅
- `pop rsi; ret` at 0x1145 ✅
- `pop rbp; ret` at 0x1213 ✅
- `pop rdi; ret` - NOT FOUND ❌

**Do_syscall Function:**
```assembly
1230:	mov    rax,rdi    # Sets rax from first argument
1233:	...               # Shuffles other arguments
1247:	syscall
1249:	ret
```
Could be used to set rax=15 IF we had pop rdi gadget.

### Assumptions Made (Possibly Incorrect)

1. **Remote binary matches local binary**
   - Assumption: Remote has `xor eax, eax` at 0x1139
   - Possible: Remote compiled differently without this instruction?

2. **PIE base address**
   - Tried: 0x400000 (no PIE), 0x555555554000 (standard PIE)
   - Possible: Different base address or ASLR behavior?

3. **SROP is the only/best approach**
   - Assumption: Pure SROP chain is intended solution
   - Possible: Hybrid approach with ROP needed?

4. **Flag is exactly at FD 3**
   - Based on wrapper source code
   - Should be correct ✅

5. **Seccomp blocks other syscalls**
   - Based on source and binary analysis
   - Should be correct ✅

### Questions

1. **Is remote binary different?**
   - Compiled without `xor eax, eax`?
   - Different optimization level?

2. **Am I missing a technique?**
   - Is there a way to set rax=15 I haven't found?
   - Is there a different SROP chaining method?

3. **Should I use libc gadgets?**
   - Are there useful gadgets in the provided libc_remote.so.6?
   - Do I need to leak addresses first?

4. **Is there an info leak step first?**
   - Do I need to leak PIE base before exploitation?
   - Can I leak with the overflow somehow?

### Files Created
- solve.py, solve_v2.py, solve_final.py - Main exploit attempts
- debug_exploit.py - Verbose version for debugging
- eureka_exploit.py - Attempted workaround
- rop_approach.py - Alternative ROP approach
- PROGRESS.md, SUMMARY.md - Documentation

### Next Steps Needed
1. Confirm whether remote binary has `xor eax, eax`
2. Find alternative way to set rax=15
3. Or: Determine correct exploitation technique if not pure SROP
4. Or: Get hint about what I'm missing

### Request
Need guidance on:
- Is the remote binary compiled differently?
- What technique bypasses the `xor eax, eax` instruction?
- Am I on the right track with SROP?
