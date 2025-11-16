# On Hinge and Pin - CTF Writeup

## Challenge Information
- **Platform**: UWSP Pointer Overflow CTF
- **Category**: Reverse Engineering
- **Difficulty**: Easy-Medium
- **Flag**: `poctf{uwsp_c4nc3l_c0u7ur3}`

## Initial Analysis

The challenge provided an Android APK file (`rev200-1.apk`) with the description: "A tiny Android app refuses to trust your device and hides a secret. Your job: recover the flag."

## Solution

### 1. APK Extraction

First, I extracted the APK contents (APK files are essentially ZIP archives):

```bash
unzip rev200-1.apk -d apk_extracted
```

This revealed an interesting file in the assets folder:
- `assets/enc_flag.bin` - An encrypted flag file

### 2. Decompiling the APK

I used JADX to decompile the APK and obtain the Java source code:

```bash
jadx -d decompiled rev200-1.apk
```

### 3. Analyzing the Code

I examined the decompiled source code and found three key files:

#### MainActivity.java
The main activity showed that:
- The app checks for root access using a `RootDetector` class
- If the device is rooted, it blocks access to the flag
- When a button is clicked, it calls `Crypto.loadAndDecrypt()` to decrypt and display the flag

#### Crypto.java
This was the critical file containing the decryption logic:

```java
private static final String KEY = "ONOFFONOFF";

public final String loadAndDecrypt(Context ctx, String assetName) {
    // Loads enc_flag.bin from assets
    byte[] data = ByteStreamsKt.readBytes(it);
    byte[] key = StringsKt.encodeToByteArray(KEY);
    byte[] out = new byte[data.length];

    // Simple XOR decryption
    for (int i = 0; i < length; i++) {
        out[i] = (byte) (data[i] ^ key[i % key.length]);
    }

    return new String(out, Charsets.UTF_8);
}
```

**Key findings:**
- The encryption key is hardcoded as `"ONOFFONOFF"`
- The algorithm is a simple XOR cipher with a repeating key
- The encrypted data is in `assets/enc_flag.bin`

### 4. Decryption

With the key and algorithm identified, I wrote a Python script to decrypt the flag:

```python
def decrypt_flag(encrypted_file, key):
    with open(encrypted_file, 'rb') as f:
        encrypted_data = f.read()

    key_bytes = key.encode('utf-8')
    decrypted = bytearray()

    for i in range(len(encrypted_data)):
        decrypted.append(encrypted_data[i] ^ key_bytes[i % len(key_bytes)])

    return decrypted.decode('utf-8')

KEY = "ONOFFONOFF"
flag = decrypt_flag("apk_extracted/assets/enc_flag.bin", KEY)
print(f"Decrypted flag: {flag}")
```

Running this script produced the flag: **poctf{uwsp_c4nc3l_c0u7ur3}**

## Vulnerabilities Exploited

1. **Hardcoded Encryption Key**: The XOR key was hardcoded in the application source code, making it trivial to extract through decompilation.

2. **Weak Encryption**: XOR cipher with a short repeating key is cryptographically weak and provides no real security.

3. **Client-Side Security**: Relying on client-side checks (root detection) and client-side encryption meant all security could be bypassed through static analysis without needing to run the app.

## Flag
```
poctf{uwsp_c4nc3l_c0u7ur3}
```
