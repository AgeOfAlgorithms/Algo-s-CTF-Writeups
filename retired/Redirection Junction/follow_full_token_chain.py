#!/usr/bin/env python3
"""
Follow Full Token Chain
Author: Claude Code
Purpose: Follow the complete path through multiple tokens in sequence
Created: 2025-11-10
Last Updated: 2025-11-10
Expected Result: Find the flag by following all tokens
Produced Result: TBD
"""

import requests
import base64
import re
from bs4 import BeautifulSoup

# Start a session
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
})

# Follow the initial chain
print("Following initial chain...\n")

session.get("https://web100-4.pointeroverflowctf.com", allow_redirects=False)
session.get("https://web100-4.pointeroverflowctf.com/start",
           headers={'Referer': 'https://web100-4.pointeroverflowctf.com'},
           allow_redirects=False)
session.get("https://web100-4.pointeroverflowctf.com/step_js",
           headers={'Referer': 'https://web100-4.pointeroverflowctf.com/start'},
           allow_redirects=False)

print(f"Initial cookies: {dict(session.cookies)}\n")

# Now follow tokens 1, 2, 3, etc. in sequence
last_referer = "https://web100-4.pointeroverflowctf.com/step_js"

for i in range(1, 51):  # Try up to 50 tokens
    token = f"meta-token-{i}"
    token_b64 = base64.b64encode(token.encode()).decode()

    print("="*80)
    print(f"Token {i}: {token}")
    print("="*80)

    # Step 1: /step_meta/token_b64
    url1 = f"https://web100-4.pointeroverflowctf.com/step_meta/{token_b64}"
    print(f"\n1. GET {url1}")
    resp = session.get(url1, headers={'Referer': last_referer}, allow_redirects=False)
    print(f"   Status: {resp.status_code}")

    if resp.status_code != 200:
        print(f"   Unexpected status, stopping")
        break

    # Parse meta refresh
    soup = BeautifulSoup(resp.text, 'html.parser')
    meta_refresh = soup.find('meta', attrs={'http-equiv': re.compile('refresh', re.I)})
    if not meta_refresh:
        print(f"   No meta refresh found, stopping")
        break

    content = meta_refresh['content']
    match = re.search(r'url=(.+)', content, re.I)
    if not match:
        print(f"   Could not parse meta refresh, stopping")
        break

    next_path = match.group(1).strip('\'"')

    # Step 2: /meta_decode/token_b64
    url2 = f"https://web100-4.pointeroverflowctf.com{next_path}"
    print(f"\n2. GET {url2}")
    resp = session.get(url2, headers={'Referer': url1}, allow_redirects=False)
    print(f"   Status: {resp.status_code}")

    if resp.status_code == 302:
        location = resp.headers.get('Location')
        print(f"   Redirects to: {location}")

        # Step 3: Follow the redirect
        url3 = f"https://web100-4.pointeroverflowctf.com/meta_decode/{location}"
        print(f"\n3. GET {url3}")
        resp = session.get(url3, headers={'Referer': url2}, allow_redirects=False)
        print(f"   Status: {resp.status_code}")

        if resp.status_code == 200:
            print(f"\n   SUCCESS! Token {i} returned 200!")
            print(f"   Response:\n{resp.text}")

            if 'flag{' in resp.text.lower() or 'poctf{' in resp.text.lower() or 'ptovr{' in resp.text.lower():
                print("\n" + "="*80)
                print("*** FLAG FOUND! ***")
                print("="*80)
                break
        elif resp.status_code == 302:
            # Another redirect?
            location2 = resp.headers.get('Location')
            print(f"   Redirects again to: {location2}")

            # Update last_referer for next iteration
            last_referer = url3
            continue
        elif resp.status_code != 400:
            print(f"   Unexpected status: {resp.text[:100]}")

        # Update referer for next token
        last_referer = url3
    else:
        print(f"   Expected 302, got {resp.status_code}")
        break

    print()

print("\nDone.")
