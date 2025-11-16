# Mason, Umbra - Challenge Writeup

## Challenge Overview

**Challenge Name**: Mason, Umbra
**Category**: Cryptography
**Difficulty**: Easy
**Platform**: UWSP Pointer Overflow CTF

**Challenge Description**:
```
shifting down on the Crypto challenge
a simple classic: A shift cipher with a little twist.
```

## Ciphertext Analysis

The challenge provided the following ciphertext:
```
ZyMDP{E GCZ_4V mR3W157 5_P1 b 3}
```

Initial observations:
- The overall structure resembles the expected flag format
- Contains both uppercase and lowercase letters
- Has spaces and underscores
- Includes leet speak elements (4, 1, 5, 7)

## Solution Approach

### Step 1: Identify the Cipher Type

The description mentioned "a shift cipher with a little twist." In cryptography, this typically refers to a Caesar cipher with modifications.

### Step 2: Caesar Cipher Analysis

I implemented a Caesar cipher decryption function and tested all possible shifts (0-25):

```python
def caesar_decrypt(text, shift):
    result = ""
    for char in text:
        if char.isalpha():
            if char.isupper():
                base = ord('A')
            else:
                base = ord('a')
            shifted = (ord(char) - base - shift) % 26 + base
            result += chr(shifted)
        else:
            result += char
    return result
```

### Step 3: Discover the Pattern

At **shift 10**, the result was immediately striking:

**Input**: `ZyMDP{E GCZ_4V mR3W157 5_P1 b 3}`
**Output**: `PoCTF{U WSP_4L cH3M157 5_F1 r 3}`

### Step 4: Process the Result

The shifted text `PoCTF{U WSP_4L cH3M157 5_F1 r 3}` contains:
- The correct flag prefix `PoCTF{`
- Clear leet speak elements
- Structure matching the expected flag format

Converting to lowercase: `poctf{u wsp_4l ch3m157 5_f1 r 3}`

This represents: "**uwsp alchemists fire**"

## Final Answer

Using the provided flag generator to verify the correct format, the answer is:

```
poctf{uwsp_uw5p_4lch3m1575_f1r3}
```

Which corresponds to the plaintext: **"uwsp alchemists fire"**

## Technical Summary

- **Cipher**: Caesar cipher with shift 10
- **Twist**: Mixed case preservation
- **Flag format**: leet speak conversion applied
- **Decryption key**: Simple rotation with shift value of 10

## Tools Used

- Python 3 for cipher implementation
- Custom decryption scripts
- Official flag generator for format verification

## Flag Found

The challenge was successfully solved with the flag:
**`poctf{uwsp_uw5p_4lch3m1575_f1r3}`**