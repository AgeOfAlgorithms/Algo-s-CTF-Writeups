# Ashes to Ashes - Hash Collision Attack

## Challenge Overview
The "Ashes to Ashes" challenge from UWSP Pointer Overflow CTF was a cryptography challenge involving a custom 128-bit "sponge" hash function. The challenge provided a vulnerable hash function that processes 16-byte blocks with alternating left and right rotations by 13 bits each round.

**Challenge Details:**
- **Category:** Cryptography
- **Difficulty:** Easy
- **Flag:** `poctf{uwsp_54v3_y0ur_f0rk_7h3r35_p13}`
- **Target:** https://crypto100-4.pointeroverflowctf.com

## Vulnerability Analysis

### The Hash Function
The `ashes_hash` function is a custom sponge construction with the following properties:
1. **128-bit internal state (S)**
2. **16-byte block size**
3. **Alternating round operations:** Left rotation (13 bits) for even blocks, right rotation (13 bits) for odd blocks
4. **Only XOR and rotation operations** - making it completely linear

The critical vulnerability is that **the hash function uses only linear operations** (XORs and rotations), which makes it susceptible to differential cryptanalysis.

### The Attack
Due to the linearity, we can predict how differences propagate through the compression function:
- If we introduce a difference Δ in one block, we can cancel it out in the next block
- The rotation direction depends on the block index parity
- We can create two different messages that produce the same hash output

## Exploitation Strategy

The challenge description provided the exact attack method:

1. **Get a random prefix** from the service via POST to `/prefix`
2. **Pad the prefix** to a 16-byte boundary with zeros
3. **Choose 16-byte blocks A1, A2** and a non-zero difference Δ
4. **Create two messages:**
   - Message 1: `prefix + A1 + A2`
   - Message 2: `prefix + B1 + B2` where:
     - `B1 = A1 XOR Δ`
     - `B2 = A2 XOR rotate(Δ)` (direction depends on block index%2)
5. **Submit both messages** to `/submit` endpoint

## Implementation Details

### Local Testing
The exploit was first tested locally to verify the collision works:
```
Local collision check: d3fbbcefc977bfffb417d01c5d321b20 == d3fbbcefc977bfffb417d01c5d321b20 -> True
```

### Target Service Communication
- **Prefix endpoint:** `POST /prefix` (not GET as initially attempted)
- **Submit endpoint:** `POST /submit` with JSON payload containing:
  - `session_id`: From the prefix response
  - `m1_hex`: First message in hex
  - `m2_hex`: Second message in hex

### Message Requirements
Each message must be at least 32 bytes beyond the prefix (as per challenge requirements).

## Exploit Results

The exploit successfully:
1. Retrieved a random prefix: `"s565nudvreuailn3"`
2. Created a collision pair that both hash to: `d3fbbcefc977bfffb417d01c5d321b20`
3. Submitted the collision to the service
4. Received the flag: `poctf{uwsp_54v3_y0ur_f0rk_7h3r35_p13}`

## Key Takeaways

1. **Linear hash functions are vulnerable** to differential attacks
2. **Rotation-based designs** need careful analysis of how differences propagate
3. **CTF challenges often provide hints** - the challenge description gave the exact attack method
4. **Always check HTTP methods** - the prefix endpoint required POST, not GET

## Files Created
- `exploit_ashes.py`: Complete exploit implementation
- `WRITEUP.md`: This documentation

The exploit demonstrates a practical application of differential cryptanalysis against a real (though intentionally weak) hash function, showing how mathematical analysis can break cryptographic primitives when linearity is present.