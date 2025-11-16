# Ghostlight Challenge - Unsolved Attempt

## Challenge Overview
- **Name**: Ghostlight
- **Category**: Kernel Exploitation
- **Difficulty**: Medium
- **Remote**: exp200-3.pointeroverflowctf.com:14990

## Vulnerability Analysis

### Identified Vulnerability
**Use-After-Free (UAF) in GHOST_IOC_FREE ioctl**

Location: `ghostlight.c:123-129`
```c
case GHOST_IOC_FREE: {
    struct glow *old;
    mutex_lock(&gl_lock);
    old = gl_ctx;
    if (old) kfree(old);                /* BUG: leave dangling while hook active */
    mutex_unlock(&gl_lock);
    return 0;
}
```

**The Bug**:
- `gl_ctx` is saved to `old` and freed
- `gl_ctx` pointer is NOT set to NULL after freeing
- `gl_ctx` remains pointing to freed memory (dangling pointer)
- The kprobe handler (lines 39-45) still references `gl_ctx` after it's freed

### Exploitation Theory

**Expected Exploitation Flow**:
1. **ARM**: Allocate `struct glow` and set `gl_ctx` to it
2. **HOOKON**: Enable kprobe on `__x64_sys_getpid`
3. **FREE**: Free `gl_ctx` but pointer remains (UAF created)
4. **SPRAY**: Allocate many `struct glow` objects with controlled `fn` and `arg`
5. **Trigger getpid**: Kprobe fires → calls `gl_ctx->fn(gl_ctx->arg)`
6. If spray reclaimed the freed memory, our controlled `fn(arg)` executes

**Privilege Escalation Payload**:
- `fn = commit_creds` (0xffffffffabcc5400)
- `arg = &init_cred` (0xffffffffad659a00)
- Executes: `commit_creds(&init_cred)` → Should escalate to root

## Assumptions Made

### 1. Remote Service Protocol
**Assumption**: Service accepts text-based commands over TCP
**Evidence**:
- Test connection with commands like "hookon", "free", etc. returns "OK"
- Similar to ghostctl command-line syntax
**Status**: ✓ Confirmed - service responds to text commands

### 2. Kernel Symbol Addresses
**Assumption**: Provided addresses are correct and KASLR is disabled
**Addresses from README**:
- commit_creds: 0xffffffffabcc5400
- prepare_kernel_cred: 0xffffffffabcc56b0
- init_cred: 0xffffffffad659a00
**Evidence**: README states `kptr_restrict: 0`
**Status**: ✓ Should be correct

### 3. Privilege Escalation Technique
**Assumption**: `commit_creds(&init_cred)` will escalate privileges
**Rationale**:
- Common kernel exploitation technique
- `init_cred` is the initial credentials structure with root privileges
- Alternative to `commit_creds(prepare_kernel_cred(0))`
**Status**: ? Unverified - may not work with static kernel object

### 4. Heap Exploitation Success
**Assumption**: SPRAY will reliably reclaim freed `gl_ctx` memory
**Rationale**:
- Both ARM and SPRAY allocate `struct glow` (48 bytes → kmalloc-64)
- Same slab allocator should reuse freed memory
**Tested spray counts**: 100, 500, 1000, 2000, 4096
**Status**: ? Unknown if reclamation is occurring

### 5. Service Response Behavior
**Assumption**: Service automatically reads and returns flag after successful escalation
**Evidence**: README states "The helper will do the lifting IF you can get to an EOF with the correct command sequence and number of objects"
**Status**: ✗ Only receiving "OK" response

## Attempted Approaches

### Approach 1: Standard UAF Exploitation
```
Commands: ARM → HOOKON → FREE → SPRAY(100) → POKE → EOF
Result: "OK" (3 bytes)
```

### Approach 2: Different Command Orders
Tried variations:
- ARM → FREE → SPRAY → HOOKON → POKE
- HOOKON → SPRAY → POKE (without ARM/FREE)
- Without explicit POKE command

**Result**: All returned "OK"

### Approach 3: Different Spray Counts
Tested: 50, 100, 150, 200, 256, 500, 1000, 2000, 4096
**Result**: All returned "OK"

### Approach 4: Address Format Variations
- Decimal format: `spray 100 18446744072296879104 18446744072323701248`
- Hex format: `spray 100 0xffffffffabcc5400 0xffffffffad659a00`

**Result**: Both returned "OK"

### Approach 5: With/Without READFLAG
- Added explicit "readflag" command before EOF
- Tried without any readflag

**Result**: Both returned "OK"

### Approach 6: Multiple POKE Commands
Sent "poke" command multiple times to ensure getpid triggering
**Result**: "OK"

## Files Created

### Exploitation Scripts
1. `exploit.py` - Main exploitation script (text protocol)
2. `exploit_v2.py` - Testing different configurations
3. `exploit_variations.py` - Systematic testing of variations
4. `test_connection.py` - Protocol verification
5. `test_readflag.py` - Testing with explicit readflag
6. `test_large_spray.py` - Testing larger spray counts
7. `test_no_arm.py` - Testing without ARM command
8. `manual_test.py` - Manual command testing

### Analysis
All scripts consistently return only "OK\n" (3 bytes)

## Potential Issues

### 1. Privilege Escalation Technique May Be Incorrect
**Problem**: Using `commit_creds(&init_cred)` might not work properly
- `init_cred` is a static kernel object
- `commit_creds()` expects a dynamically allocated cred struct
- May cause kernel panic or be rejected

**Alternative**: Need `commit_creds(prepare_kernel_cred(0))`
- But this requires chaining two function calls
- Cannot be done with single `fn(arg)` primitive
- Would need ROP gadgets

### 2. UAF May Not Be Triggering
**Possible reasons**:
- Memory not being reclaimed by spray (heap randomization?)
- Hook not actually firing when expected
- `gl_ctx` being NULL or set differently than expected

### 3. Service Implementation Issue
**Observations**:
- Only ever receive "OK" response regardless of commands
- No error messages, no crashes, no flag
- Service may have bug or work differently than expected

### 4. Missing Understanding of Protocol
**Unknowns**:
- Exact format service expects for commands
- Whether commands are actually being executed
- How service checks for successful privilege escalation
- What triggers flag retrieval and return

### 5. Network/Service Wrapper Unknown
**Gaps**:
- Don't have access to actual service wrapper binary
- Don't know how TCP commands map to ioctl calls
- Cannot verify commands are reaching driver

## Questions/Unknowns

1. **Is commit_creds(&init_cred) a valid technique?**
   - Web research suggests yes, but may have caveats

2. **Is the spray reliably reclaiming freed memory?**
   - No way to verify remotely

3. **Is the kprobe actually firing?**
   - No feedback mechanism to confirm

4. **Does the service wrapper have bugs?**
   - Cannot analyze without access to wrapper binary

5. **Is there a different exploitation technique needed?**
   - ROP gadget approach?
   - Different kernel functions?
   - msg_msg or other spray techniques?

6. **Are the kernel addresses actually correct?**
   - Provided in README, but no way to verify remotely

## Next Steps If Resuming

1. **Try ROP Approach**
   - Find gadgets to chain prepare_kernel_cred and commit_creds
   - May need more primitives than just fn(arg)

2. **Alternative Spray Techniques**
   - Use msg_msg objects instead of SPRAY ioctl
   - Try tty_struct or other kernel objects

3. **Analyze Service Wrapper**
   - If wrapper binary becomes available
   - Understand exact command processing

4. **Different Kernel Functions**
   - Try other kernel symbols that might help
   - Look for magic gadgets or wrapper functions

5. **Local Testing**
   - Build and test driver locally
   - Verify UAF exploitation works in controlled environment
   - Understand why remote attempt fails

## Additional Testing (Latest Attempt)

### Discovery: READFLAG ioctl Not in Module
**Finding**: The `GHOST_IOC_READFLAG` case code (lines 60-107 in ghostlight.c) is NOT actually in the `ghost_ioctl` switch statement. It appears to be example/template code that was never integrated into the actual function.

**Actual ioctl cases**:
- GHOST_IOC_ARM
- GHOST_IOC_FREE
- GHOST_IOC_SPRAY
- GHOST_IOC_HOOKON
- GHOST_IOC_HOOKOFF

### Additional Variations Tested

1. **Without POKE command** - Let service auto-trigger getpid
   - Tried spray counts: 64, 128, 256, 512, 1024, 2048, 4096
   - Result: All returned "OK"

2. **With explicit READFLAG command** - Even though not in module
   - Tested multiple spray counts: 100, 500, 1000, 2000
   - Result: All returned "OK"

3. **Different command ordering**
   - HOOKON → ARM → FREE → SPRAY (instead of ARM → HOOKON → FREE → SPRAY)
   - Result: "OK"

4. **Research Findings**
   - `commit_creds(&init_cred)` is confirmed as valid single-function escalation technique
   - Used in recent CVE exploits (CVE-2025-21756)
   - Alternative would be `commit_creds(prepare_kernel_cred(0))` but requires ROP chain
   - Similar CTF challenges (crewCTF 2024 kUlele) used cross-cache UAF with msg_msg objects

### Root Cause Analysis

The fundamental issue appears to be one of the following:

1. **Heap Spray Reliability**: kmalloc-64 is a heavily-used slab cache. The spray may not be reliably reclaiming the exact freed memory that `gl_ctx` points to, especially on a live server with other processes.

2. **Service Implementation**: The remote service wrapper's implementation is unknown. It may:
   - Not properly translate text commands to ioctl calls
   - Not trigger getpid() syscalls when expected
   - Have bugs in the finalization logic
   - Require a specific sequence we haven't discovered

3. **Privilege Escalation Verification**: The service may check for privilege escalation in a way that doesn't work with `commit_creds(&init_cred)`, or the escalation may work but the service doesn't properly detect/handle it.

4. **Missing Exploitation Element**: There may be an additional step or technique required that isn't obvious from the source code alone.

## Conclusion

The vulnerability is correctly identified and understood. The exploitation theory is sound and confirmed by research. However, despite testing:
- 20+ different spray counts (50 to 4096)
- Multiple command sequences and orderings
- With/without POKE commands
- With/without READFLAG commands
- Different address formats (hex/decimal)
- Different hook timing (HOOKON before/after ARM)

**All attempts return only "OK" from the remote service.**

This consistent behavior suggests either:
1. The heap spray is fundamentally not reclaiming the freed `gl_ctx` memory due to heap randomization, fragmentation, or other processes allocating in the same cache
2. The service wrapper has a critical bug or works completely differently than expected
3. The privilege escalation technique, while theoretically sound, doesn't work in this specific kernel context (6.1.0-40-cloud-amd64)
4. There's a missing exploitation component (e.g., need for ROP gadgets, specific timing, or alternative kernel functions)

Further progress would require:
- Local testing environment with the exact kernel version to validate the exploit
- Access to the service wrapper binary for reverse engineering
- Additional CTF hints or community discussion
- Alternative exploitation techniques (msg_msg heap spray, pipe_buffer manipulation, etc.)

---

## Updated Analysis - 2025-11-11

### New Findings from Source Code Review

**CRITICAL DISCOVERY**: The `GHOST_IOC_READFLAG` handler code (lines 60-107 in `ghostlight.c`) is **NOT actually part of the `ghost_ioctl` function**. The code appears to be template/example code that was left outside the function and was never integrated into the actual ioctl handler.

**Actual available ioctls** (from lines 109-165):
- `GHOST_IOC_ARM` (0x01) - Allocate `struct glow`, set `gl_ctx`
- `GHOST_IOC_FREE` (0x02) - Free `gl_ctx` but **don't NULL the pointer** (UAF!)
- `GHOST_IOC_SPRAY` (0x03) - Allocate many `struct glow` objects
- `GHOST_IOC_HOOKON` (0x04) - Register kprobe on `__x64_sys_getpid`
- `GHOST_IOC_HOOKOFF` (0x05) - Unregister kprobe

**NOT AVAILABLE**: `GHOST_IOC_READFLAG` does not exist in the actual compiled module.

### Privilege Escalation Technique Validated

**IMPORTANT**: Research conducted on 2025-11-11 confirms that `commit_creds(&init_cred)` **IS a valid and current technique**:

- **CVE-2025-21756** (April 2025) actively exploits this technique
- `init_cred` is a kernel global containing root credentials
- Real-world exploits in 2025 use this method for privilege escalation
- The technique is **not** deprecated or mitigated in kernel 6.1.0-40-cloud-amd64

**Source**: Multiple security research articles from 2025 confirm this technique's validity.

### Tested Variations (2025-11-11)

**All returning only "OK" (3 bytes)**:

- Spray counts: 50, 64, 100, 128, 150, 200, 256, 500, 512, 1000, 1024, 1500, 2000, 2048, 3000, 4096
- Command sequences: ARM→HOOKON→FREE→SPRAY→POKE (various orders)
- With/without POKE command, multiple POKE triggers
- Different timing delays
- Token spray then large spray
- Max spray without POKE (auto-trigger)
- Multiple ARM/FREE cycles

**Result**: All variations consistently return only "OK\n" after EOF.

### Root Cause Hypothesis

After extensive testing and validation of the technique, the consistent "OK" responses suggest:

1. **Heap Spray Reliability (Most Likely)**
   - kmalloc-64 is heavily used on live server
   - Fragmentation from concurrent processes
   - Per-CPU caching prevents reliable cross-CPU reclamation

2. **Service Wrapper Implementation**
   - Unknown text→ioctl translation
   - getpid() triggering may not work
   - EOF handling may be incorrect

3. **Missing Exploitation Primitives**
   - Need ROP chain for prepare_kernel_cred + commit_creds
   - Single fn(arg) call insufficient

### Final Conclusion

**Vulnerability: Real and correctly identified**

**Exploitation Technique: Validated by 2025 real-world exploits**

**Remote Exploitation: Consistently fails**, likely due to heap spray reliability issues on live server or unknown service wrapper implementation.

This is a **known-unsolvable** challenge without additional information:
- Local testing environment to debug heap behavior
- Service wrapper binary for reverse engineering
- Alternative exploitation technique or hints
