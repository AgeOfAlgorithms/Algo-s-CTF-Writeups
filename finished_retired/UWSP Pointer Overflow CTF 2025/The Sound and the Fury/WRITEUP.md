# The Sound and the Fury - Writeup

## Challenge Information
- **Name:** The Sound and the Fury
- **Category:** Forensics
- **Difficulty:** Medium
- **Flag:** `poctf{uwsp_74773r_707_c4553r0l3}`

## Challenge Description
This challenge involves a Windows executable that fetches a flag from a remote server and loads it into memory. The goal is to use debugging or live memory forensics to extract the flag.

## Solution Overview
Instead of running the Windows executable and debugging it, we reverse engineered the protocol it uses to communicate with the server and replicated it in Python.

## Analysis Process

### Step 1: Initial Reconnaissance
We examined the provided file `for300-2.exe`:
```bash
file for300-2.exe
# PE32+ executable (console) x86-64 (stripped to external PDB), for MS Windows
```

### Step 2: String Analysis
Using the `strings` command on the executable revealed critical information:

**Error Messages:**
- `[SoundAndFury] GET nonce failed (after retry)`
- `[SoundAndFury] POST flag request failed`
- `[SoundAndFury] sealed_flag not found`
- `[SoundAndFury] Flag securely loaded into process memory.`

**Protocol Details:**
- The executable uses WinHTTP for network communication
- JSON payload format: `{"nonce":"%s","pk":"%s"}`
- Uses libsodium for cryptography (`crypto_box_seal_open`)

**Server Details (from wide strings):**
```
Host: for300-2.pointeroverflowctf.com
Endpoints:
  - GET /api/v1/nonce
  - POST /api/v1/flag
```

**Certificate Pinning:**
- SHA256 hash: `0ce37031d44ddf290572e2cb83b529d1f4cfd99648741b72cf64a54c7066ed6c`

### Step 3: Understanding the Protocol
Based on the strings analysis, we identified the following workflow:

1. **GET /api/v1/nonce** - Fetch a nonce from the server
2. **Generate Keypair** - Create a libsodium/NaCl keypair for sealed box encryption
3. **POST /api/v1/flag** - Send JSON with nonce and public key
4. **Decrypt** - Use sealed box decryption with private key to reveal the flag

### Step 4: Implementation
We created a Python script using PyNaCl (Python bindings for libsodium) that:

1. Generates a fresh Curve25519 keypair
2. Fetches the nonce from the server
3. Sends a POST request with the nonce and base64-encoded public key
4. Receives the encrypted flag (sealed box)
5. Decrypts the flag using `SealedBox.decrypt()`

### Step 5: Flag Retrieval
Running the script successfully retrieved the flag:
```
Flag: poctf{uwsp_74773r_707_c4553r0l3}
```

## Vulnerabilities Exploited

### Information Disclosure
The Windows executable contained all the information needed to understand and replicate the protocol:
- Server URLs in plaintext (wide strings)
- Error messages revealing the protocol flow
- Library names revealing the crypto implementation

### Protocol Design
The protocol doesn't require any client authentication or secrets embedded in the executable. Anyone who understands the protocol can request and decrypt the flag without running the actual executable.

## Key Techniques Used
1. **Static Analysis** - Examining the executable with `strings` and `file`
2. **Protocol Reverse Engineering** - Understanding the network communication flow
3. **Cryptographic Analysis** - Identifying libsodium sealed box encryption
4. **Python Scripting** - Implementing the client protocol with PyNaCl

## Tools Used
- `strings` - Extract readable strings from the binary
- `file` - Identify file type
- `curl` - Test HTTP endpoints
- Python 3 with libraries:
  - `requests` - HTTP client
  - `PyNaCl` - Cryptographic operations (sealed box)
  - `base64` - Encoding/decoding

## Alternative Approaches
1. **Dynamic Analysis** - Run the executable in a Windows VM with a debugger (x64dbg, WinDbg) and dump memory
2. **Memory Forensics** - Capture a memory dump while the program is waiting and analyze it with Volatility
3. **Network Interception** - Use Wireshark to capture the network traffic and examine the protocol

## Lessons Learned
- Static analysis can reveal complete protocol implementations without running the code
- Sealed box encryption provides anonymity (sender doesn't need to identify themselves)
- Client-side applications cannot hide secrets - all embedded information can be extracted
- Wide character strings in Windows executables require `-e l` flag with `strings`
