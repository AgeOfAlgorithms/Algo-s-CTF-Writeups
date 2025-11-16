# zip2john2zip - BuckeyeCTF 2025

**Category:** Forensics
**Difficulty:** Medium
**Flag:** `bctf{not_all_hashes_are_hashed_equally}`

## Challenge Description

We were given only a zip2john hash output without the original ZIP file. The challenge asked us to crack the password, but noted that since we don't have the archive, we "can't steal all our flags."

## Solution Overview

The challenge name "zip2john2zip" hints at the solution: reversing the zip2john process to reconstruct the ZIP file from the hash.

## Step 1: Understanding the pkzip2 Hash Format

The provided hash was:
```
flag.zip/flag.txt:$pkzip2$1*1*2*0*34*28*64ac0ae2*0*26*0*34*64ac*a388*2c386d49756e1d70ab5f2d8b7ccf1703b28d2775e84d89ccf4bf26d0e735e9a817b0032b5071540889c34b9331b694d6042c30a0*$/pkzip2$:flag.txt:flag.zip::flag.zip
```

Research revealed that the pkzip2 hash format contains:
- **Hash Count** and **Checksum Bytes**
- **Magic Type**: File type indicator
- **Compressed/Uncompressed Lengths**: Size information
- **CRC32**: Checksum of the plaintext
- **Compression Type**: 0 = stored (no compression)
- **Data Length**: Length of encrypted data
- **Checksum and Timestamp Checksum**: Validation data
- **Encrypted Data**: The actual encrypted file content

Key insight: Unlike cryptographic hashes, zip2john output contains the **actual encrypted data** and all metadata needed to reconstruct the ZIP file!

## Step 2: Parsing the Hash

Created [`parse_hash.py`](parse_hash.py) to extract components:
- Internal filename: `flag.txt`
- Compressed size: 52 bytes
- Uncompressed size: 40 bytes
- CRC32: `0x64ac0ae2`
- Compression: stored (no compression)
- Encrypted data: 52 bytes of ciphertext

## Step 3: Reconstructing the ZIP File

Created [`reconstruct_zip.py`](reconstruct_zip.py) to build a valid ZIP archive from the hash data:

1. Built a **Local File Header** with:
   - ZIP signature (`0x04034b50`)
   - Version, flags (encryption bit set)
   - Compression method, timestamps
   - CRC32, sizes, filename

2. Appended the **encrypted data** from the hash

3. Built a **Central Directory Header** with file metadata

4. Added **End of Central Directory Record**

This successfully created a valid password-protected ZIP file: `flag.zip`

## Step 4: Cracking the Password

Attempted multiple approaches:
1. **John the Ripper**: System version didn't support PKZIP format (gave "No password hashes loaded" error)
2. **Common passwords**: Tried 32 common passwords - all failed
3. **RockYou wordlist**: Success!

Created [`crack_zip.py`](crack_zip.py) and tested passwords from rockyou.txt:
- **Password found:** `factfinder`
- **Position in wordlist:** 955,101 out of ~14 million
- **Time to crack:** ~120 seconds

The password was successfully found and `flag.txt` was extracted.

## Step 5: Retrieving the Flag

The extracted `flag.txt` contained:
```
bctf{not_all_hashes_are_hashed_equally}
```

## Key Takeaways

1. **zip2john output isn't a hash** in the cryptographic sense - it contains the encrypted data and metadata
2. **ZIP file reconstruction is possible** from zip2john output because it preserves all necessary information
3. **Old ZIP encryption (ZipCrypto)** is vulnerable to both password cracking and known-plaintext attacks
4. The flag message perfectly captures the challenge: "not all hashes are hashed equally" - some "hashes" (like zip2john output) contain much more than just a one-way transformation

## Tools & Scripts Created

- [`parse_hash.py`](parse_hash.py): Parse pkzip2 hash format
- [`reconstruct_zip.py`](reconstruct_zip.py): Rebuild ZIP file from hash
- [`crack_zip.py`](crack_zip.py): Password cracking with wordlists

## References

- [ZIP File Format Structure](https://users.cs.jmu.edu/buchhofp/forensics/formats/pkzip.html)
- [bkcrack - Known Plaintext Attack on ZipCrypto](https://github.com/kimci86/bkcrack)
- [John the Ripper zip2john Format](https://github.com/openwall/john/blob/bleeding-jumbo/src/zip2john.c)
