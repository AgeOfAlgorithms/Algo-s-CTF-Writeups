# Mason, Meridian - CTF Writeup

## Challenge Information
- **Platform:** UWSP Pointer Overflow CTF
- **Category:** Exploit
- **Difficulty:** Easy
- **Flag:** `poctf{uwsp_n3v3r_w1ll_1_w4nd3r}`

## Challenge Description
The challenge presents a "TLS heartbeat simulator" and references famous named vulnerabilities like DirtyCOW, Spectre, ShellShock, and Heartbleed. The challenge name "Mason, Meridian" is likely a creative reference to the Heartbleed vulnerability.

## Vulnerability Discovery

### Source Code Analysis
The provided source code reveals a classic Heartbleed vulnerability implementation. The key structure is:

```c
struct {
    char data[64];    // User input buffer
    char pad[32];     // Contains "LEAK->"
    char flag[128];   // Contains the flag from /flag
} frame;
```

### The Vulnerability
The critical bug is in the `serve()` function:

```c
scanf(" %d:%63s", &len, frame.data);
write(STDOUT_FILENO, frame.data, (size_t)len);
```

The program:
1. Reads up to 63 bytes into `frame.data`
2. Writes `len` bytes starting from `frame.data`
3. **Does not validate that `len` matches the actual data size**

### Memory Layout
When the struct is allocated in memory:
- Bytes 0-63: `data` (user input)
- Bytes 64-95: `pad` (contains "LEAK->")
- Bytes 96-223: `flag` (contains the actual flag)

## Exploitation

### Attack Vector
By specifying a `len` value larger than the actual data provided (e.g., 200 bytes while only sending 4 bytes), the program will write beyond the `data` buffer, leaking adjacent memory including the `flag` field.

### Exploit Steps
1. Connect to the server at `exp100-2.pointeroverflowctf.com:14662`
2. Send payload: `200:AAAA` (request 200 bytes, send only 4 bytes)
3. Server writes 200 bytes starting from `frame.data`, which includes:
   - The 4 'A' characters
   - Null padding
   - The "LEAK->" marker
   - **The flag content**
4. Parse the response to extract the flag

### Exploit Code
See [heartbleed_exploit.py](heartbleed_exploit.py) for the full implementation.

## Key Takeaways
This challenge demonstrates the **Heartbleed vulnerability (CVE-2014-0160)**, one of the most famous security bugs in history. The vulnerability allowed attackers to read sensitive memory from servers due to missing bounds checking in the OpenSSL heartbeat extension.

The fix is simple: validate that the requested length doesn't exceed the actual data length before writing to the output buffer.
