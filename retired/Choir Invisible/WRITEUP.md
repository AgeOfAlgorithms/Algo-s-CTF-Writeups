# Choir Invisible - Writeup

**Challenge:** Choir Invisible
**Platform:** UWSP Pointer Overflow CTF
**Category:** Exploit
**Difficulty:** Medium
**Flag:** `poctf{uwsp_50_f3w_15_5un5h1n3}`

## Challenge Description

This service simulates an in-kernel heap object with a leading function pointer that has a use-after-free bug exploitable remotely via a tiny TCP protocol.

## Vulnerability Analysis

### The Bug

The vulnerability exists in the `op_free()` function ([exp300-1.c:55-64](exp300-1.c#L55-L64)):

```c
static void op_free(int fd, const uint8_t* d, uint32_t n){
    if (n != 4){ respond(fd, 1, "bad args", 8); return; }
    uint32_t idx = *(uint32_t*)d;
    if (idx >= 128 || !slots[idx]){ respond(fd, 2, "bad idx", 7); return; }
    choir_t* c = slots[idx];
    free(c->buf);
    free(c);
    // BUG: leave dangling pointer in slots[idx]
    respond(fd, 0, NULL, 0);
}
```

**The bug:** After freeing the `choir_t` structure, the pointer in `slots[idx]` is not cleared, creating a **use-after-free** vulnerability.

### Structure Layout

The `choir_t` structure ([exp300-1.c:15-19](exp300-1.c#L15-L19)):

```c
typedef struct choir {
    void (*cb)(struct choir*);  // Function pointer at offset 0
    char *buf;                  // Pointer at offset 8
    size_t len;                 // Size at offset 16
} choir_t;
```

On a 64-bit system, this structure is **24 bytes** total.

### Key Functions

1. **`give_root()`** ([exp300-1.c:29](exp300-1.c#L29)): Sets `is_root = 1`, allowing us to read the flag
2. **`choir_sing()`** ([exp300-1.c:28](exp300-1.c#L28)): Default callback (does nothing)
3. **`op_leak()`** ([exp300-1.c:113-116](exp300-1.c#L113-L116)): Conveniently leaks addresses of both functions
4. **`op_trigger()`** ([exp300-1.c:78-86](exp300-1.c#L78-L86)): Calls the callback function pointer

## Exploitation Strategy

1. **LEAK (op 6):** Get the address of `give_root` function
2. **CREATE (op 1):** Create a choir object at index 0
3. **FREE (op 2):** Free the object at index 0, creating the UAF condition
4. **SPRAY (op 5):** Flood the heap with 24-byte chunks containing:
   - First 8 bytes: address of `give_root` (overwrites the `cb` function pointer)
   - Remaining bytes: dummy data
5. **TRIGGER (op 4):** Invoke the callback at index 0
   - The freed memory has been reclaimed by our spray
   - The function pointer now points to `give_root`
   - This sets `is_root = 1`
6. **READFLAG (op 7):** Read `/flag.txt` now that we have "root"

## Exploit Implementation

The exploit follows the strategy above:

```python
# 1. Get address leak
give_root, choir_sing = op_leak(sock)

# 2. Create object at index 0
op_create(sock, 0)

# 3. Free object (UAF)
op_free(sock, 0)

# 4. Spray heap with 24-byte chunks
chunk_size = 24
spray_count = 1000
payload = struct.pack("<QQQ", give_root, 0x4141414141414141, 0x100)
op_spray(sock, chunk_size, spray_count, payload)

# 5. Trigger callback (calls give_root)
op_trigger(sock, 0)

# 6. Read flag
flag = op_readflag(sock)
```

## Why This Works

When we free the `choir_t` object:
- The 24-byte chunk is returned to the heap
- The pointer in `slots[0]` still points to that freed memory (UAF)

When we spray 1000 chunks of size 24:
- One of these chunks will likely occupy the same memory location
- Our payload overwrites the old `choir_t` structure
- The first 8 bytes (the `cb` function pointer) now point to `give_root`

When we trigger index 0:
- The code dereferences `slots[0]->cb`
- This reads from our spray payload
- It calls `give_root` instead of `choir_sing`
- `is_root` is set to 1

Finally, `READFLAG` succeeds because `is_root == 1`.

## Key Takeaways

- **Use-after-free** vulnerabilities occur when pointers aren't cleared after freeing
- Heap spraying can be used to reclaim freed memory with controlled data
- Function pointers are a common target for UAF exploits
- The `LEAK` operation made this challenge more accessible by providing addresses directly

## Files

- [exploit.py](exploit.py) - Final working exploit
- [exp300-1.c](exp300-1.c) - Challenge source code
- [exp300-1_client.py](exp300-1_client.py) - Reference client
