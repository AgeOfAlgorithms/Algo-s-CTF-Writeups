#!/usr/bin/env python3
"""
Manual test to understand the redirect chain
"""

import requests
import re
import base64
from bs4 import BeautifulSoup

# Disable SSL verification for this CTF site
session = requests.Session()
session.verify = False

# Suppress SSL warnings
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Set User-Agent
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
})

base_url = "https://web100-4.pointeroverflowctf.com"

print("=" * 60)
print("Step 1: Visit root URL")
print("=" * 60)
response = session.get(base_url, allow_redirects=False)
print(f"Status: {response.status_code}")
print(f"Location: {response.headers.get('Location', 'None')}")
print(f"Cookies: {dict(session.cookies)}")
print()

print("=" * 60)
print("Step 2: Visit /start")
print("=" * 60)
url = base_url + "/start"
response = session.get(url, headers={'Referer': base_url}, allow_redirects=False)
print(f"Status: {response.status_code}")
print(f"Location: {response.headers.get('Location', 'None')}")
print(f"Cookies: {dict(session.cookies)}")
print()

print("=" * 60)
print("Step 3: Visit /step_js")
print("=" * 60)
url = base_url + "/step_js"
response = session.get(url, headers={'Referer': base_url + "/start"}, allow_redirects=False)
print(f"Status: {response.status_code}")
print(f"Cookies set: {dict(response.cookies)}")
print(f"Cookies now: {dict(session.cookies)}")
print(f"Response body:\n{response.text[:500]}")
print()

# Parse JavaScript for base64 payload
soup = BeautifulSoup(response.text, 'html.parser')
script = soup.find('script')
if script and script.string:
    print("JavaScript content:")
    print(script.string[:300])
    print()

    # Extract base64 payload
    match = re.search(r'var\s+\w+\s*=\s*["\']([A-Za-z0-9+/=]+)["\']', script.string)
    if match:
        encoded = match.group(1)
        print(f"Found encoded payload: {encoded}")
        decoded = base64.b64decode(encoded).decode('utf-8')
        print(f"Decoded to: {decoded}")
        print()

print("=" * 60)
print("Step 4: Visit /step_meta/bWV0YS10b2tlbi0x")
print("=" * 60)
url = base_url + "/step_meta/bWV0YS10b2tlbi0x"
response = session.get(url, headers={'Referer': base_url + "/step_js"}, allow_redirects=False)
print(f"Status: {response.status_code}")
print(f"Cookies: {dict(session.cookies)}")
print(f"Response body:\n{response.text}")
print()

# Parse meta refresh
soup = BeautifulSoup(response.text, 'html.parser')
meta = soup.find('meta', attrs={'http-equiv': 'refresh'})
if meta and meta.get('content'):
    print(f"Meta refresh content: {meta['content']}")
    match = re.search(r'url=(.+)', meta['content'], re.I)
    if match:
        next_url = match.group(1).strip('"\'')
        print(f"Next URL: {next_url}")
        print()

# Check for any base64 strings in the page
import re
potential_encoded = re.findall(r'[A-Za-z0-9+/=-]{10,}', response.text)
print(f"Potential encoded strings found: {len(potential_encoded)}")
for i, encoded in enumerate(potential_encoded[:5]):  # Show first 5
    try:
        decoded = base64.b64decode(encoded).decode('utf-8')
        print(f"  {i+1}. {encoded} -> {decoded}")
    except:
        print(f"  {i+1}. {encoded} -> (not base64)")
print()

print("=" * 60)
print("Step 5: Visit /meta_decode/bWV0YS10b2tlbi0x")
print("=" * 60)
url = base_url + "/meta_decode/bWV0YS10b2tlbi0x"
response = session.get(url, headers={'Referer': base_url + "/step_meta/bWV0YS10b2tlbi0x"}, allow_redirects=False)
print(f"Status: {response.status_code}")
print(f"Location: {response.headers.get('Location', 'None')}")
print(f"Cookies: {dict(session.cookies)}")
print()

print("=" * 60)
print("Step 6: Visit /meta_decode/meta-token-1")
print("=" * 60)
url = base_url + "/meta_decode/meta-token-1"
response = session.get(url, headers={'Referer': base_url + "/meta_decode/bWV0YS10b2tlbi0x"}, allow_redirects=False)
print(f"Status: {response.status_code}")
print(f"Response body: {response.text}")
print(f"Cookies: {dict(session.cookies)}")
print()

print("=" * 60)
print("What about /final? Let me try accessing it")
print("=" * 60)
url = base_url + "/final"
response = session.get(url, headers={'Referer': base_url + "/meta_decode/meta-token-1"}, allow_redirects=False)
print(f"Status: {response.status_code}")
print(f"Response body: {response.text}")
print(f"Cookies: {dict(session.cookies)}")
print()
