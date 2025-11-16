# Ink Between the Lines - UWSP Pointer Overflow CTF

**Category:** Steganography
**Difficulty:** Very Easy
**Flag:** `poctf{uwsp_sweetheart_is_thy_call}`

## Challenge Description

The challenge presents a poem that has been "secured and verified by digital means" - provided as a 7z archive containing two files.

## Solution Overview

This challenge uses **whitespace steganography** where hidden data is encoded in trailing tabs and spaces at the end of each line of text.

## Step 1: Extract the Archive

The challenge provides `Stego100-1.7z` which contains:
- `leaflet.txt` - A poem with hidden data
- `leaflet.sha256` - SHA256 hash for verification

```bash
7z x Stego100-1.7z
```

## Step 2: Analyze the Poem

The poem itself contains numerous clues about the steganography technique:

```
Ink between the lines.
The quiet parts carry weight.
Margins remember.
...
Tabs quarrel with spaces.
Count what you cannot see.
...
Read the endings.
...
```

Key phrases that hint at the solution:
- **"Ink between the lines"** - Hidden data in whitespace
- **"Tabs quarrel with spaces"** - Tabs and spaces encode the message
- **"Count what you cannot see"** - Whitespace characters are invisible
- **"Read the endings"** - Look at the end of each line
- **"Zoom, never copy"** - Must preserve exact whitespace (copying might lose it)
- **"Lossless eyes only"** - File integrity is important

## Step 3: Verify File Integrity

Verify the SHA256 hash matches to ensure the whitespace is intact:

```bash
sha256sum leaflet.txt
# Output: 631717644565747abeaf6c791953adc6bfd4121f19b3bb56e3c8394d2067f121
```

This matches the hash in `leaflet.sha256`, confirming the file is authentic.

## Step 4: Extract the Hidden Message

Created [`extract_whitespace.py`](extract_whitespace.py) to decode the hidden message.

The script:
1. Reads the file in binary mode to preserve exact whitespace
2. Extracts trailing whitespace from each line
3. Converts to binary using the encoding: **Tab = 1, Space = 0**
4. Decodes the binary as ASCII (8 bits per character)

### Whitespace Pattern

Each line has trailing tabs (T) and spaces (S):

```
Line  1: 'STTTSSTT' -> 01110011 -> 's'
Line  2: 'STTTSTTT' -> 01110111 -> 'w'
Line  3: 'STTSSTST' -> 01100101 -> 'e'
Line  4: 'STTSSTST' -> 01100101 -> 'e'
Line  5: 'STTTSTSS' -> 01110100 -> 't'
Line  6: 'STTSTSSS' -> 01101000 -> 'h'
Line  7: 'STTSSTST' -> 01100101 -> 'e'
Line  8: 'STTSSSST' -> 01100001 -> 'a'
Line  9: 'STTTSSTS' -> 01110010 -> 'r'
Line 10: 'STTTSTSS' -> 01110100 -> 't'
Line 11: 'SSTSSSSS' -> 00100000 -> ' '
Line 12: 'STTSTSST' -> 01101001 -> 'i'
Line 13: 'STTTSSTT' -> 01110011 -> 's'
Line 14: 'SSTSSSSS' -> 00100000 -> ' '
Line 15: 'STTTSTSS' -> 01110100 -> 't'
Line 16: 'STTSTSSS' -> 01101000 -> 'h'
Line 17: 'STTTTSST' -> 01111001 -> 'y'
Line 18: 'SSTSSSSS' -> 00100000 -> ' '
Line 19: 'STTSSSTT' -> 01100011 -> 'c'
Line 20: 'STTSSSST' -> 01100001 -> 'a'
Line 21: 'STTSTTSS' -> 01101100 -> 'l'
Line 22: 'STTSTTSS' -> 01101100 -> 'l'
```

**Decoded message:** `sweetheart is thy call`

## Step 5: Format the Flag

The decoded message is: **`sweetheart is thy call`**

According to the UWSP Pointer Overflow CTF rules:
- Format: `poctf{uwsp_...}`
- Character set: `4bcd3f6h1jklmn0pqr57uvwxyz` (l33tspeak)
- Spaces replaced by underscores
- Case insensitive

L33tspeak conversion mapping (from example `poctf{uwsp_7h15_15_4_54mpl3_fl46}`):
- `a` → `4`, `e` → `3`, `g` → `6`, `i` → `1`, `o` → `0`, `s` → `5`, `t` → `7`

Converting the decoded message:
- `sweetheart` → `5w337h34r7`
- `is` → `15`
- `thy` → `7hy`
- `call` → `c4ll`

**Flag:** `poctf{uwsp_5w337h34r7_15_7hy_c4ll}`

## Key Techniques

1. **Whitespace Steganography**: Data hidden in tabs and spaces
2. **Binary Encoding**: Tab=1, Space=0
3. **ASCII Decoding**: 8 bits per character
4. **File Integrity**: SHA256 verification ensures whitespace preservation

## Tools Used

- Python 3 for decoding
- `sha256sum` for verification
- Binary-safe file reading to preserve exact whitespace

## Lessons Learned

- Whitespace steganography is effective because whitespace is invisible in normal viewing
- The challenge poem itself contained all the hints needed to solve it
- File integrity verification (SHA256) is crucial when whitespace matters
- Tabs and spaces can encode binary data (Tab=1, Space=0)
