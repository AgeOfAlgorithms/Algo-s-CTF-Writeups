#!/usr/bin/env python3
"""
Follow the discovered chain using the double-decoded path
"""

import requests
import re
import base64
import urllib3
from bs4 import BeautifulSoup
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

session = requests.Session()
session.verify = False
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
})

base_url = "https://web100-4.pointeroverflowctf.com"

def extract_meta_refresh(resp):
    """Extract meta refresh URL from response"""
    soup = BeautifulSoup(resp.text, 'html.parser')
    meta = soup.find('meta', attrs={'http-equiv': 'refresh'})
    if meta and meta.get('content'):
        content = meta['content']
        match = re.search(r'url=(.+)', content, re.I)
        if match:
            return match.group(1).strip('"\'')
    return None

def extract_encoded_payload(resp):
    """Extract base64 encoded payload from response"""
    soup = BeautifulSoup(resp.text, 'html.parser')
    pre = soup.find('pre')
    if pre:
        return pre.get_text().strip()
    return None

print("=" * 80)
print("Following the double-decoded chain")
print("=" * 80)

# Build up the initial state like before
print("\n[Building initial state...]")
session.get(base_url, allow_redirects=False)
session.get(base_url + "/start", headers={'Referer': base_url}, allow_redirects=False)
session.get(base_url + "/step_js", headers={'Referer': base_url + "/start"}, allow_redirects=False)
session.get(base_url + "/step_meta/bWV0YS10b2tlbi0x", headers={'Referer': base_url + "/step_js"}, allow_redirects=False)

# Follow the redirect to meta-token-1
print("[Following redirect to meta-token-1...]")
resp = session.get(base_url + "/meta_decode/bWV0YS10b2tlbi0x", headers={'Referer': base_url + "/step_meta/bWV0YS10b2tlbi0x"}, allow_redirects=False)
print(f"  Got redirect to: {resp.headers.get('Location')}")
print(f"  Now visiting: {base_url}/step_meta/meta-token-1")

# Visit /step_meta/meta-token-1
print("\n[Visiting /step_meta/meta-token-1...]")
resp = session.get(base_url + "/step_meta/meta-token-1", headers={'Referer': base_url + "/meta_decode/bWV0YS10b2tlbi0x"}, allow_redirects=False)
print(f"  Status: {resp.status_code}")

# Extract the meta refresh
meta_url = extract_meta_refresh(resp)
print(f"  Meta refresh points to: {meta_url}")

# Extract the encoded payload
encoded_payload = extract_encoded_payload(resp)
print(f"  Encoded payload: {encoded_payload}")

if encoded_payload:
    # Decode the payload
    decoded_payload = base64.b64decode(encoded_payload).decode('utf-8')
    print(f"  Decoded payload: {decoded_payload}")

    # Follow the pattern: visit /meta_decode/<encoded>, then get redirected to next meta-token
    print(f"\n[Visiting /meta_decode/{encoded_payload}...]")
    resp2 = session.get(base_url + f"/meta_decode/{encoded_payload}",
                       headers={'Referer': base_url + "/step_meta/meta-token-1"},
                       allow_redirects=False)
    print(f"  Status: {resp2.status_code}")
    print(f"  Location: {resp2.headers.get('Location')}")

    next_token = resp2.headers.get('Location')
    if next_token:
        print(f"  Next token appears to be: {next_token}")

        # Visit the next step_meta/
        print(f"\n[Visiting /step_meta/{next_token}...]")
        resp3 = session.get(base_url + f"/step_meta/{next_token}",
                           headers={'Referer': base_url + f"/meta_decode/{encoded_payload}"},
                           allow_redirects=False)
        print(f"  Status: {resp3.status_code}")

        # Extract next meta refresh
        next_meta = extract_meta_refresh(resp3)
        print(f"  Next meta refresh: {next_meta}")

        # Get next encoded payload
        next_encoded = extract_encoded_payload(resp3)
        print(f"  Next encoded payload: {next_encoded}")

        if next_encoded:
            next_decoded = base64.b64decode(next_encoded).decode('utf-8')
            print(f"  Next decoded: {next_decoded}")

# Try /final now
print("\n[Checking /final...]")
final_resp = session.get(base_url + "/final",
                         headers={'Referer': base_url + f"/step_meta/{next_token}"},
                         allow_redirects=False)
print(f"  Status: {final_resp.status_code}")
print(f"  Body: {final_resp.text}")

# Check for flag in response
if 'flag{' in final_resp.text.lower() or 'ptovr{' in final_resp.text.lower():
    print("\n" + "=" * 80)
    print("FLAG FOUND!")
    print("=" * 80)
    print(final_resp.text)
else:
    print("\nNo flag yet...")
