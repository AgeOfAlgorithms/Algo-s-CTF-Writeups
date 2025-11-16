# Mason, Adytum - Writeup

## Challenge Information
- **Category:** Crypto
- **Difficulty:** Hard
- **Flag:** `poctf{uwsp_7w45_bu7_7h3_w1nd}`

## Challenge Description
The challenge provided three RSA public keys and three ciphertexts:
- All three public keys use the same public exponent `e = 3`
- All three ciphertexts are encryptions of the same message
- No padding was used during encryption

## Vulnerability
This setup is vulnerable to a **Håstad's Broadcast Attack** using the Chinese Remainder Theorem (CRT).

### Why This Attack Works

When RSA encryption is performed without padding and the same message `m` is encrypted with multiple different moduli using a small exponent `e`, the following conditions exist:

1. `c1 ≡ m³ (mod n1)`
2. `c2 ≡ m³ (mod n2)`
3. `c3 ≡ m³ (mod n3)`

If the plaintext `m` is small enough such that `m³ < n1 × n2 × n3`, then the Chinese Remainder Theorem can be used to find `m³` directly over the integers (not modulo anything), and a simple cube root operation recovers the original message.

## Exploitation

### Step 1: Extract and Examine Files
```bash
unzip crypto300-2.zip
```

This provided:
- `pub1.json`, `pub2.json`, `pub3.json` - Public keys with moduli `n` (hex) and exponent `e` (decimal)
- `c1.bin`, `c2.bin`, `c3.bin` - Ciphertexts as raw big-endian binary

### Step 2: Apply Chinese Remainder Theorem

The attack script ([crt_attack.py](crt_attack.py)) performs the following:

1. **Load public keys**: Parse JSON files and convert hex moduli to integers
2. **Load ciphertexts**: Read binary files as big-endian integers
3. **Apply CRT**: Solve the system of congruences to find `x` where:
   - `x ≡ c1 (mod n1)`
   - `x ≡ c2 (mod n2)`
   - `x ≡ c3 (mod n3)`
4. **Calculate cube root**: Since `x = m³`, compute `m = ∛x`
5. **Decode message**: Convert integer `m` to bytes and decode as ASCII

### Step 3: Key Implementation Details

**Chinese Remainder Theorem:**
```python
def chinese_remainder_theorem(remainders, moduli):
    total = 0
    prod = reduce(lambda a, b: a * b, moduli)

    for remainder, modulus in zip(remainders, moduli):
        p = prod // modulus
        total += remainder * modinv(p, modulus) * p

    return total % prod
```

**Integer Cube Root (using binary search):**
```python
def integer_cube_root(n):
    low, high = 0, n
    while low <= high:
        mid = (low + high) // 2
        cube = mid ** 3
        if cube == n:
            return mid
        elif cube < n:
            low = mid + 1
        else:
            high = mid - 1
    return high
```

## Results

Running the attack script:
```bash
python3 crt_attack.py
```

Output:
```
✓ Cube root verified!
Recovered plaintext (integer): 3031244604381979917917998076481278744042807733040435686360801287758973
Plaintext (hex): 706f6374667b757773705f377734355f6275375f3768335f77316e647d
Plaintext (ASCII): poctf{uwsp_7w45_bu7_7h3_w1nd}
🚩 FLAG FOUND: poctf{uwsp_7w45_bu7_7h3_w1nd}
```

## Mitigation
To prevent this attack:
1. **Use padding schemes**: OAEP (Optimal Asymmetric Encryption Padding) prevents this attack
2. **Use larger exponents**: e = 65537 is standard (though padding is still required)
3. **Never encrypt the same message**: Use randomized padding to ensure different ciphertexts
4. **Ensure m^e > n**: The message should be large enough that m^e doesn't fall below the modulus

## References
- [Håstad's Broadcast Attack](https://en.wikipedia.org/wiki/Coppersmith%27s_attack#H%C3%A5stad's_broadcast_attack)
- [Chinese Remainder Theorem](https://en.wikipedia.org/wiki/Chinese_remainder_theorem)
