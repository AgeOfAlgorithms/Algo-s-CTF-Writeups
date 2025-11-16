#!/usr/bin/env python3
"""
Follow tokens sequentially starting from meta-token-1
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

def extract_encoded_payload(resp):
    """Extract base64 encoded payload from response"""
    soup = BeautifulSoup(resp.text, 'html.parser')
    pre = soup.find('pre')
    if pre:
        return pre.get_text().strip()
    return None

# Build initial state
print("Building initial state...")
session.get(base_url, allow_redirects=False)
session.get(base_url + "/start", headers={'Referer': base_url}, allow_redirects=False)
session.get(base_url + "/step_js", headers={'Referer': base_url + "/start"}, allow_redirects=False)
session.get(base_url + "/step_meta/bWV0YS10b2tlbi0x", headers={'Referer': base_url + "/step_js"}, allow_redirects=False)
session.get(base_url + "/meta_decode/bWV0YS10b2tlbi0x", headers={'Referer': base_url + "/step_meta/bWV0YS10b2tlbi0x"}, allow_redirects=False)

# Start at meta-token-1
current_token = "meta-token-1"
referer = base_url + "/meta_decode/bWV0YS10b2tlbi0x"

print(f"\n{"=" * 80}")
print(f"Starting token chain with: {current_token}")
print(f"{"=" * 80}")

for i in range(1, 50):
    print(f"\n[Step {i}] Current token: {current_token}")

    # Visit /step_meta/
    url = base_url + f"/step_meta/{current_token}"
    print(f"  Visiting: {url}")
    resp = session.get(url, headers={'Referer': referer}, allow_redirects=False)
    print(f"  Status: {resp.status_code}")
    print(f"  Cookies: {dict(session.cookies)}")

    if resp.status_code != 200:
        print(f"  ERROR: Got status {resp.status_code}")
        break

    # Check for flag
    if 'flag{' in resp.text.lower() or 'ptovr{' in resp.text.lower():
        print("\n" + "=" * 80)
        print("FLAG FOUND!")
        print("=" * 80)
        print(resp.text)
        break

    # Get the "payload" shown on the page
    payload = extract_encoded_payload(resp)
    print(f"  Payload shown on page: {payload}")

    if not payload:
        print(f"  No payload found, stopping")
        print(f"  Full response: {resp.text[:500]}")
        break

    # If we get back the same token, we're in a loop or at the end
    if payload == current_token:
        print(f"  Payload matches current token, might be at an endpoint")

        # What if we need to go to /final now?
        print(f"\n  Trying /final after {current_token}...")
        final_resp = session.get(base_url + "/final", headers={'Referer': url}, allow_redirects=False)
        print(f"  Final status: {final_resp.status_code}")
        print(f"  Final body: {final_resp.text}")

        if 'flag{' in final_resp.text.lower() or 'ptovr{' in final_resp.text.lower():
            print("\n" + "=" * 80)
            print("FLAG FOUND AT /final!")
            print("=" * 80)
            print(final_resp.text)
            break

        # Try to extract next token from payload
        # Maybe tokens increment: meta-token-1, meta-token-2, meta-token-3, ...
        try:
            token_num = int(current_token.split('-')[-1])
            next_token_num = token_num + 1
            next_token = f"meta-token-{next_token_num}"
            print(f"  Assuming next token: {next_token}")
            current_token = next_token
            referer = url
            continue
        except:
            print(f"  Could not parse token number, stopping")
            break

    # Decode the payload to get the next step
    try:
        next_url_part = base64.b64decode(payload).decode('utf-8')
        print(f"  Decoded payload: {next_url_part}")

        # This should be like "/meta_decode/...something..."
        if next_url_part.startswith('/meta_decode/'):
            print(f"  Following to: {next_url_part}")

            # Visit the meta_decode endpoint
            meta_url = base_url + next_url_part
            print(f"  Visiting meta_decode: {meta_url}")
            meta_resp = session.get(meta_url, headers={'Referer': url}, allow_redirects=False)
            print(f"  Meta decode status: {meta_resp.status_code}")
            print(f"  Meta decode location: {meta_resp.headers.get('Location')}")

            # Get the next token from the Location header
            next_token = meta_resp.headers.get('Location')
            if next_token:
                current_token = next_token
                referer = meta_url
                print(f"  Next token: {current_token}")
            else:
                print(f"  No Location header, stopping")
                break
        else:
            print(f"  Unexpected decoded format: {next_url_part}")
            break
    except Exception as e:
        print(f"  Error decoding payload: {e}")
        break

        if i > 1 and current_token == "meta-token-1":
            print(f"\nDetected loop, stopping")
            break

print(f"\nChain completed after {i} steps")
