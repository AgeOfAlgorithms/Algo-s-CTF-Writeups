#!/usr/bin/env python3
"""
Follow the complete chain from JavaScript hint to completion
Based on the pattern seen in responses
"""

import requests
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

def extract_payload_from_step_meta(resp):
    """Extract the base64 encoded payload from /step_meta/* response"""
    soup = BeautifulSoup(resp.text, 'html.parser')
    pre = soup.find('pre')
    if pre:
        return pre.get_text().strip()
    return None

print("=" * 80)
print("Following the complete chain")
print("=" * 80)

# Step 1: / → /start (302)
print("\n[1] GET /")
resp = session.get(base_url, allow_redirects=False)
next_url = resp.headers.get('Location')
print(f"    Redirects to: {next_url}")

# Step 2: /start → /step_js (302)
print("\n[2] GET /start")
resp = session.get(base_url + "/start", headers={'Referer': base_url}, allow_redirects=False)
next_url = resp.headers.get('Location')
print(f"    Redirects to: {next_url}")

# Step 3: /step_js → extract base64 payload (200)
print("\n[3] GET /step_js")
resp = session.get(base_url + "/step_js", headers={'Referer': base_url + "/start"}, allow_redirects=False)
# Extract base64 from JavaScript
import re
match = re.search(r'var\s+p\s*=\s*"([A-Za-z0-9+/=]+)"', resp.text)
if match:
    js_payload = match.group(1)
    print(f"    JavaScript payload: {js_payload}")
    # Decode the payload
    first_decode = base64.b64decode(js_payload).decode('utf-8')
    print(f"    First decode: {first_decode}")
    next_url = first_decode
else:
    print("ERROR: Could not find JavaScript payload")
    exit(1)

# Step 4: /step_meta/bWV0YS10b2tlbi0x → extract encoded payload (200)
print("\n[4] GET /step_meta/bWV0YS10b2tlbi0x")
resp = session.get(base_url + next_url, headers={'Referer': base_url + "/step_js"}, allow_redirects=False)
encoded_token1 = extract_payload_from_step_meta(resp)
print(f"    Encoded payload: {encoded_token1}")
print(f"    Decoded: {base64.b64decode(encoded_token1).decode('utf-8')}")

# Step 5: /meta_decode/bWV0YS10b2tlbi0x → 302 redirect
print("\n[5] GET /meta_decode/bWV0YS10b2tlbi0x")
resp = session.get(base_url + "/meta_decode/bWV0YS10b2tlbi0x",
                   headers={'Referer': base_url + next_url},
                   allow_redirects=False)
next_token = resp.headers.get('Location')
print(f"    Redirects to: {next_token}")

# Step 6: /step_meta/meta-token-1 → extract next encoded payload (200)
print("\n[6] GET /step_meta/meta-token-1")
resp = session.get(base_url + f"/step_meta/{next_token}",
                   headers={'Referer': base_url + "/meta_decode/bWV0YS10b2tlbi0x"},
                   allow_redirects=False)
encoded_token2 = extract_payload_from_step_meta(resp)
print(f"    Payload from page: {encoded_token2}")
try:
    decoded_test = base64.b64decode(encoded_token2).decode('utf-8')
    print(f"    Decoded: {decoded_test}")
except:
    print(f"    (Not base64 encoded, treating as plaintext)")

# Step 7: The token here is plaintext, not base64!
# We need to re-encode it before visiting /meta_decode/
print("\n[7] The payload is plaintext: " + str(encoded_token2))
print(f"    Treating as token, re-encoding for /meta_decode/...")

# If the payload is already plaintext, we need to encode it
if encoded_token2 == next_token:  # It's the same as the current token
    print(f"    Token is plaintext, encoding for next /meta_decode/ step")
    encoded_for_next = base64.b64encode(encoded_token2.encode()).decode()
    print(f"    Encoded to: {encoded_for_next}")
else:
    encoded_for_next = encoded_token2

# Now visit /meta_decode/ with the encoded value
print(f"\n[7] GET /meta_decode/{encoded_for_next}")
resp = session.get(base_url + f"/meta_decode/{encoded_for_next}",
                   headers={'Referer': base_url + f"/step_meta/{next_token}"},
                   allow_redirects=False)
next_token2 = resp.headers.get('Location')
print(f"    Redirects to: {next_token2}")

if next_token2:
    # Step 8: Continue the chain with next token
    current_token = next_token2
    prev_token_url = f"/meta_decode/{encoded_for_next}"
    for i in range(8, 30):  # Follow up to 30 steps
        print(f"\n[{i}] GET /step_meta/{current_token}")
        resp = session.get(base_url + f"/step_meta/{current_token}",
                           headers={'Referer': base_url + prev_token_url},
                           allow_redirects=False)

        print(f"    Status: {resp.status_code}")

        if resp.status_code != 200:
            print(f"    ERROR: Got status {resp.status_code}")
            print(f"    Response: {resp.text}")
            break

        # Check for flag
        if 'flag{' in resp.text.lower() or 'ptovr{' in resp.text.lower():
            print("\n" + "=" * 80)
            print("FLAG FOUND!")
            print("=" * 80)
            print(resp.text)
            break

        # Extract next encoded token
        next_encoded = extract_payload_from_step_meta(resp)
        print(f"    Encoded payload: {next_encoded}")

        # Decode it to see what it is
        try:
            decoded = base64.b64decode(next_encoded).decode('utf-8')
            print(f"    Decoded: {decoded}")
        except:
            print(f"    Could not decode as base64")

        # Get next token via 302 redirect
        print(f"\n[{i}-redirect] GET /meta_decode/{next_encoded}")
        resp2 = session.get(base_url + f"/meta_decode/{next_encoded}",
                           headers={'Referer': base_url + f"/step_meta/{current_token}"},
                           allow_redirects=False)

        if resp2.status_code == 302:
            prev_token = current_token
            current_token = resp2.headers.get('Location')
            print(f"    Redirects to: {current_token}")

            # Try /final at this point
            print(f"\n    Trying /final after this step...")
            final_resp = session.get(base_url + "/final",
                                     headers={'Referer': base_url + f"/meta_decode/{next_encoded}"},
                                     allow_redirects=False)
            print(f"    /final status: {final_resp.status_code}")
            if final_resp.status_code == 200 and ('flag{' in final_resp.text.lower() or 'ptovr{' in final_resp.text.lower()):
                print("\n" + "=" * 80)
                print("FLAG FOUND AT /final!")
                print("=" * 80)
                print(final_resp.text)
                break
        else:
            print(f"    ERROR: Got status {resp2.status_code} instead of 302")
            print(f"    Response: {resp2.text}")
            break

        if current_token == next_token:  # Loop detection
            print(f"\nDetected loop, stopping")
            break

else:
    print(f"\nERROR: No redirect found in step 7")
    print(f"Response: {resp.text}")
