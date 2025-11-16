#!/usr/bin/env python3
"""
Author: Claude
Purpose: Replicate the for300-2.exe protocol to retrieve and decrypt the flag
Assumptions:
  - Server uses libsodium sealed box encryption
  - Public key needs to be base64 encoded
  - Nonce is fetched from /api/v1/nonce
  - Flag is retrieved from /api/v1/flag
Created: 2025-11-10
Updated: 2025-11-10
Expected Result: Decrypted flag printed to stdout
Produced Result: poctf{uwsp_74773r_707_c4553r0l3}
"""

import requests
import base64
import json
from nacl.public import PrivateKey, SealedBox
from nacl.encoding import Base64Encoder

# Server details
SERVER = "https://for300-2.pointeroverflowctf.com"
NONCE_ENDPOINT = "/api/v1/nonce"
FLAG_ENDPOINT = "/api/v1/flag"

def get_nonce():
    """Fetch nonce from the server"""
    url = f"{SERVER}{NONCE_ENDPOINT}"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    print(f"[+] Received nonce: {data['nonce']}")
    return data['nonce']

def get_flag(nonce, public_key_b64):
    """Send POST request to get the sealed flag"""
    url = f"{SERVER}{FLAG_ENDPOINT}"
    payload = {
        "nonce": nonce,
        "pk": public_key_b64
    }
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "SoundAndFury/1.0"
    }

    print(f"[+] Sending POST request with public key: {public_key_b64[:32]}...")
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()

    data = response.json()
    if "sealed_flag" not in data:
        raise ValueError("sealed_flag not found in response")

    print(f"[+] Received sealed_flag")
    return data['sealed_flag']

def main():
    # Generate keypair
    print("[+] Generating keypair...")
    private_key = PrivateKey.generate()
    public_key = private_key.public_key

    # Encode public key to base64
    public_key_b64 = base64.b64encode(bytes(public_key)).decode('ascii')

    # Get nonce from server
    nonce = get_nonce()

    # Get sealed flag from server
    sealed_flag_b64 = get_flag(nonce, public_key_b64)

    # Decode the sealed flag from base64
    print("[+] Decoding sealed_flag from base64...")
    sealed_flag = base64.b64decode(sealed_flag_b64)

    # Decrypt using SealedBox
    print("[+] Decrypting flag...")
    unseal_box = SealedBox(private_key)
    plaintext = unseal_box.decrypt(sealed_flag)

    # Print the flag
    flag = plaintext.decode('utf-8')
    print(f"\n[SUCCESS] Flag: {flag}\n")

    return flag

if __name__ == "__main__":
    main()
