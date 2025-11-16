# Saint's Rowboat - UNSOLVED

## Challenge Information
- **Platform**: UWSP Pointer Overflow CTF
- **Category**: Reverse Engineering
- **Difficulty**: Hard
- **Points**: 400

## Challenge Description
A smuggler's dock gate is controlled by a tiny microcontroller. Someone flipped read-out protection on and called it "secure." You managed to shake loose two things without lifting RDP: the device's 96-bit UID and a 32-byte blob from an OTP row. There's also a tiny ciphertext captured from the control logic. Your job: recover what you need to decrypt secret.enc. The plaintext is your flag.

## Files Provided
1. `openocd_log.txt` - OpenOCD debug log
2. `otp_dump.bin` - 32-byte OTP dump (One-Time Programmable memory)
3. `secret.enc` - 32-byte encrypted file
4. `stm32_uid.txt` - 96-bit Unique Device Identifier

## Key Information from Analysis
- **Device**: STM32F407 (Rev Z) microcontroller
- **UID** (96 bits): `5a928ebd 3f5729b5 48b77e73`
- **OTP dump** (32 bytes): `5f08228c29eba8c448c2869bce79f60fccce3d88b0357af697b2cf43f5823228`
- **Encrypted data** (32 bytes): `395fdae58a60af5a9ab6ed5325238531e6544eec404c70e39db60299b7109608`
- **Encryption method**: AES-128-CBC with 16-byte IV (per OpenOCD log)

## Assumptions Made

### 1. File Structure Assumptions
- **Assumption**: secret.enc contains [16 bytes IV][16 bytes ciphertext]
- **Alternative tried**: Entire 32 bytes is ciphertext, IV derived separately
- **Alternative tried**: [16 bytes ciphertext][16 bytes IV]

### 2. Key Derivation Assumptions
Tried the following key derivation methods:

#### Direct Extraction
- First 16 bytes of OTP as key
- Last 16 bytes of OTP as key
- UID extended to 16 bytes (various padding methods)

#### Hash-Based Key Derivation Functions
- SHA256(UID)[:16]
- SHA256(OTP)[:16]
- SHA256(UID || OTP)[:16]
- SHA256(OTP || UID)[:16]
- MD5(UID)
- MD5(OTP)
- PBKDF2(UID, OTP_salt, iterations=1/100/1000/10000/100000)
- PBKDF2(OTP, UID_salt, iterations=1/100/1000/10000/100000)
- HKDF(UID, OTP_salt)
- HKDF(OTP, UID_salt)

#### XOR-Based Derivation
- UID XOR OTP[:12], extended to 16 bytes (various methods)
- UID XOR OTP[16:28], extended to 16 bytes
- OTP[i:i+16] XOR UID_cyclic for all offsets i
- Byte-by-byte XOR with UID repeated/extended

#### Arithmetic Operations on 32-bit Words
- ADD: (OTP_word[i] + UID_word[i%3]) & 0xFFFFFFFF
- SUB: (OTP_word[i] - UID_word[i%3]) & 0xFFFFFFFF
- MUL: (OTP_word[i] * UID_word[i%3]) & 0xFFFFFFFF
- XOR: OTP_word[i] ^ UID_word[i%3]
- Bit rotation (ROL/ROR) with various shift amounts

#### Matrix Transformations
- Transpose OTP as 4x8 matrix
- Transpose OTP as 8x4 matrix
- Transpose OTP as 2x16 matrix
- Column-major vs row-major reading

#### Row Transposition Cipher
- Applied row transposition with keywords: "SAINT", "SAINTS", "SAINTROW", "SAINTSROW", "ROWBOAT", "ROW", "BOAT"
- Both encryption and decryption directions

#### Byte Order Manipulations
- Reversed OTP (entire array)
- Little-endian to big-endian conversion of 32-bit words
- Reversed UID

### 3. IV Derivation Assumptions
Tried the following IV sources:
- First 16 bytes of secret.enc
- Last 16 bytes of secret.enc
- First 16 bytes of OTP
- Last 16 bytes of OTP
- UID extended to 16 bytes (zero padding, repetition)
- SHA256(UID)[:16]
- MD5(UID)
- Zero IV (all zeros)

### 4. Title Interpretation Assumptions
"Saint's Rowboat" was interpreted as:
- Reference to "Row" transposition cipher
- "SAINT" as a keyword for transposition
- Matrix row operations
- Bit rotation ("ROW" = rotate word?)
- Possible acronym

## Attempts Summary

Total distinct approaches tried: **~1000+ combinations**

### Scripts Created
1. `decrypt_secret.py` - Initial basic key derivation attempts (9 methods)
2. `decrypt_v2.py` - Alternative IV/key combinations (dozens of attempts)
3. `decrypt_kdf.py` - PBKDF2 and HKDF attempts with various parameters
4. `analyze_data.py` - Data structure analysis and pattern recognition
5. `decrypt_transpose.py` - Matrix transpose operations (3 dimensions)
6. `decrypt_row_transpose.py` - Row transposition cipher with keywords
7. `decrypt_combined.py` - UID + transposed OTP combinations
8. `decrypt_otp_xor.py` - XOR-based key derivation (17 offsets)
9. `decrypt_arithmetic.py` - 32-bit word arithmetic operations
10. `decrypt_comprehensive.py` - Systematic testing of 702 combinations
11. `decrypt_full_ct.py` - Full ciphertext interpretation with key/IV pairs
12. `decrypt_exhaustive.py` - Sliding window search through all data

## What Didn't Work
- None of the attempted combinations produced valid ASCII plaintext
- No flag format (POCTF{...}) was found in any output
- Exhaustive sliding window search of all 16-byte substrings failed
- Row transposition cipher with various keywords failed

## Possible Missing Elements

### 1. Additional Information Needed
- Is there a specific STM32F407 Rev Z vulnerability we need to know about?
- Is there additional context from the CTF platform or challenge description?
- Are there other files or hints that weren't included in the zip?

### 2. Encryption Method
- Could the encryption method be something other than AES-128-CBC?
- Could there be a custom/proprietary encryption scheme?
- Is the OpenOCD log misleading about the encryption method?

### 3. Key Derivation
- Is there a specific STM32 HAL function or library that implements a standard KDF we're not aware of?
- Could there be a custom key derivation function specific to this challenge?
- Does the "rowboat" hint refer to a specific algorithm we haven't found?

### 4. Data Interpretation
- Are we interpreting the byte order correctly (little-endian vs big-endian)?
- Is the UID shown in the correct format in the log?
- Could the OTP dump be encoded/encrypted itself?

## Next Steps for Solving

1. **Research specific vulnerabilities**: Look for STM32F407 Rev Z specific security issues
2. **Review CTF platform**: Check if there are additional hints or clarifications
3. **Community resources**: Look for writeups from this specific CTF
4. **Alternative crypto schemes**: Consider non-AES encryption methods
5. **Reverse engineering tools**: Use IDA/Ghidra if there's embedded firmware we haven't seen
6. **Ask for hints**: If allowed, request a hint from CTF organizers

## Tools and Resources Used
- Python 3 with PyCryptodome library
- hashlib for various hash functions
- struct for binary data parsing
- Web searches for:
  - STM32 OTP key derivation
  - Row transposition cipher
  - UWSP Pointer Overflow CTF writeups
  - Embedded system key storage practices

## Conclusion
After extensive attempts covering basic key derivation, advanced KDFs, matrix operations, cipher techniques, and exhaustive brute-force searching, the flag remains undiscovered. The challenge likely requires either:
1. Additional information not present in the provided files
2. A specific cryptographic technique or vulnerability we haven't identified
3. A creative interpretation of the "Saint's Rowboat" hint that we've missed
4. Knowledge of a specific STM32 implementation detail

The fundamental assumption that the key can be derived from the UID and OTP using standard cryptographic primitives may be incorrect.
