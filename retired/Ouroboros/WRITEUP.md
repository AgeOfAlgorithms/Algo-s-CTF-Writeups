# Ouroboros - Steganography Challenge Writeup

## Challenge Information
- **Platform:** UWSP Pointer Overflow CTF
- **Category:** Steganography
- **Difficulty:** Medium
- **Flag:** `poctf{uwsp_70_34ch_4nd_3v3ry_0n3}`

## Challenge Description
The challenge provided an image file (`stego300-1.png`) with an emoji-based description suggesting hidden data within the image.

## Solution

### 1. Initial Analysis
First, I examined the image visually. It showed an artistic portrait of a bird dressed in fancy attire. No obvious text or visual clues were visible in the image itself.

### 2. Metadata Examination
Using `exiftool`, I discovered a critical clue:
```bash
exiftool stego300-1.png
```

The output revealed:
```
Warning: [minor] Trailer data after PNG IEND chunk
```

This indicated that additional data was appended after the end of the valid PNG file structure - a classic steganography technique.

### 3. Finding the Hidden PDF
Using `binwalk` to scan for embedded files:
```bash
binwalk stego300-1.png
```

Result:
```
DECIMAL       HEXADECIMAL     DESCRIPTION
--------------------------------------------------------------------------------
0             0x0             PNG image, 1024 x 1536, 8-bit/color RGBA, non-interlaced
91            0x5B            Zlib compressed data, compressed
1754837       0x1AC6D5        PDF document, version: "1.7"
...
```

A PDF document was embedded at offset 1754837!

### 4. Extracting the PDF
I extracted the PDF using `dd`:
```bash
dd if=stego300-1.png of=extracted.pdf bs=1 skip=1754837
```

This yielded a valid 1-page PDF document (114 KB).

### 5. Extracting the Flag
I extracted text from the PDF:
```bash
pdftotext extracted.pdf -
```

The PDF contained base64-encoded text split across multiple lines:
```
cG9jdGZ7dXd
zcF83MF8zN
GNoXzRuZF8z
djNyeV8wbjN9
```

When concatenated and decoded:
```bash
echo "cG9jdGZ7dXdzcF83MF8zNGNoXzRuZF8zdjNyeV8wbjN9" | base64 -d
```

Result: `poctf{uwsp_70_34ch_4nd_3v3ry_0n3}`

## Vulnerability Summary
The challenge exploited the fact that PNG files have a defined end marker (IEND chunk). Data appended after this marker is ignored by image viewers but can be detected and extracted using forensic tools. The embedded PDF contained the flag encoded in base64.

## Tools Used
- `exiftool` - Metadata analysis
- `binwalk` - File signature and embedded file detection
- `dd` - Binary data extraction
- `pdftotext` - PDF text extraction
- `base64` - Base64 decoding

## Key Takeaways
1. Always check file metadata for anomalies
2. Look for "trailer data" warnings which indicate appended data
3. Use `binwalk` to detect embedded files in images
4. Common encoding schemes (like base64) are often used to obfuscate flags
