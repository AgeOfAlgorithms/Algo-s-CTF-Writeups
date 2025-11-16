# Through a Glass Darkly - CTF Writeup

## Challenge Information
- **Platform:** UWSP Pointer Overflow CTF
- **Category:** Reverse Engineering
- **Difficulty:** Medium
- **Target:** http://rev300-1.pointeroverflowctf.com/

## Challenge Description
The challenge presents a web page with a simple input field that verifies a flag. The verification logic is implemented in WebAssembly, requiring reverse engineering of the binary to extract the flag.

## Solution

### 1. Initial Analysis
Upon visiting the target URL, we find a minimal web interface with:
- An input field for entering a flag
- A "Check" button that validates the input
- The verification is performed client-side using WebAssembly

### 2. Downloading Assets
We downloaded two key files:
- `verifier.js` - Emscripten-generated JavaScript wrapper
- `verifier.wasm` - WebAssembly binary containing the verification logic (450 bytes)

### 3. Decompiling the WebAssembly
Using `wabt` tools (`wasm-decompile` and `wasm2wat`), we decompiled the WASM module to understand its structure:

**Key findings:**
- The WASM module contains two data sections:
  - Offset 1024: `"through_a_glass_darkly"` (reference string)
  - Offset 1056: 27 encoded bytes starting with `0x43 0x55...`

- The verification function checks if the input is exactly 27 characters long
- For each character position, a complex algorithm is applied

### 4. Reverse Engineering the Algorithm
The verification algorithm for each position `b` (0 to 26):

```python
# Get reference byte (cycles through "through_a_glass_darkly")
ref_index = b if b < 22 else (b - 22)
ref_byte = reference_string[ref_index]

# Calculate intermediate value c
c = ref_byte ^ ((b * 73 + 19) & 0xFF)

# Calculate rotation amount
d = (b & 0xFF) % 7
shift_left = (d + 1) & 7
shift_right = d ^ 7

# Perform bit rotation
rotation = ((c << shift_left) | ((c & 0xFF) >> shift_right))

# Decode the flag character
mult_result = (b * -17)  # Signed 32-bit integer
temp = (encoded_data[b] + mult_result + 123) & 0xFFFFFFFF
flag_char = (temp ^ rotation) & 0xFF
```

The algorithm involves:
- Position-dependent XOR operations
- Bit rotation based on position modulo 7
- Signed integer multiplication
- Multiple layers of obfuscation

### 5. Key Insight: Data Offset
Initially, we extracted the wrong bytes because we used file offset 0x1a8 instead of 0x1a7. The correct encoded data starts with `0x43` ('C'), not `0x55` ('U'). This was discovered by:
- Searching for the pattern in the actual file
- Verifying against the WAT decompilation which showed the data starting with "CU"

### 6. Decoding the Flag
After implementing the reverse algorithm with the correct data offset, we successfully decoded:

**Flag:** `poctf{uwsp_715_0nly_4_64m3}`

The flag reads as "poctf{uwsp 715 only for game}" with leetspeak substitutions.

### 7. Verification
We verified the flag by:
1. Testing it through our Python implementation of the verify function
2. Submitting it to the actual web challenge, which returned "Correct!"

## Tools Used
- **wabt** (WebAssembly Binary Toolkit): `wasm-decompile`, `wasm2wat`
- **Python 3** with `ctypes` for proper signed integer handling
- **xxd** for hex dump analysis
- **Browser developer tools** for initial inspection

## Lessons Learned
1. **Offset precision matters** - File offsets vs memory offsets can cause subtle bugs
2. **WASM decompilers are essential** - Manual bytecode analysis would have been much harder
3. **Bit operations need careful handling** - Rotation and shift operations must account for integer sizes
4. **Signed vs unsigned arithmetic** - The `b * -17` operation required proper handling as signed 32-bit

## Flag
`poctf{uwsp_715_0nly_4_64m3}`
