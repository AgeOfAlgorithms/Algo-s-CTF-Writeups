#!/usr/bin/env python3
"""
Test browser-like behavior on the /meta_decode/meta-token-1 endpoint
"""

import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

session = requests.Session()
session.verify = False

# Use a more accurate browser User-Agent
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1'
})

base_url = "https://web100-4.pointeroverflowctf.com"

print("=" * 80)
print("Following the chain step-by-step with proper Referer")
print("=" * 80)

# Step 1: Root
print("\n[Step 1] GET /")
resp1 = session.get(base_url, allow_redirects=False)
print(f"Status: {resp1.status_code}")
print(f"Cookies: {dict(session.cookies)}")

# Step 2: /start
print("\n[Step 2] GET /start")
resp2 = session.get(base_url + "/start", headers={'Referer': base_url}, allow_redirects=False)
print(f"Status: {resp2.status_code}")
print(f"Cookies: {dict(session.cookies)}")

# Step 3: /step_js
print("\n[Step 3] GET /step_js")
resp3 = session.get(base_url + "/step_js", headers={'Referer': base_url + "/start"}, allow_redirects=False)
print(f"Status: {resp3.status_code}")
print(f"Cookies received: {dict(resp3.cookies)}")
print(f"Cookies now: {dict(session.cookies)}")

# Step 4: /step_meta/bWV0YS10b2tlbi0x
print("\n[Step 4] GET /step_meta/bWV0YS10b2tlbi0x")
resp4 = session.get(base_url + "/step_meta/bWV0YS10b2tlbi0x", headers={'Referer': base_url + "/step_js"}, allow_redirects=False)
print(f"Status: {resp4.status_code}")
print(f"Cookies now: {dict(session.cookies)}")

# Step 5: /meta_decode/bWV0YS10b2tlbi0x
print("\n[Step 5] GET /meta_decode/bWV0YS10b2tlbi0x")
resp5 = session.get(base_url + "/meta_decode/bWV0YS10b2tlbi0x", headers={'Referer': base_url + "/step_meta/bWV0YS10b2tlbi0x"}, allow_redirects=False)
print(f"Status: {resp5.status_code}")
print(f"Location: {resp5.headers.get('Location', 'None')}")
print(f"Cookies now: {dict(session.cookies)}")

# Step 6: /meta_decode/meta-token-1 - Let's test various combinations
print("\n[Step 6] Testing /meta_decode/meta-token-1 with different combinations")

# Test A: Just the Referer
print("\n  Test A: With Referer only")
resp6a = session.get(base_url + "/meta_decode/meta-token-1", headers={'Referer': base_url + "/meta_decode/bWV0YS10b2tlbi0x"}, allow_redirects=False)
print(f"  Status: {resp6a.status_code}")
print(f"  Body: {resp6a.text[:100]}")

# Test B: With Referer and all cookies
print("\n  Test B: With Referer and explicitly setting visited_js cookie")
cookies = {'visited_js': '1'}
resp6b = session.get(base_url + "/meta_decode/meta-token-1", headers={'Referer': base_url + "/meta_decode/bWV0YS10b2tlbi0x"}, cookies=cookies, allow_redirects=False)
print(f"  Status: {resp6b.status_code}")
print(f"  Body: {resp6b.text[:100]}")

# Test C: Try with Origin header too (some servers check this)
print("\n  Test C: With Referer and Origin headers")
headers = {
    'Referer': base_url + "/meta_decode/bWV0YS10b2tlbi0x",
    'Origin': base_url
}
resp6c = session.get(base_url + "/meta_decode/meta-token-1", headers=headers, allow_redirects=False)
print(f"  Status: {resp6c.status_code}")
print(f"  Body: {resp6c.text[:100]}")

# Test D: Let's check what a real browser following redirects would do
print("\n  Test D: Using session with redirect following enabled")
resp6d = session.get(base_url + "/meta_decode/bWV0YS10b2tlbi0x", headers={'Referer': base_url + "/step_meta/bWV0YS10b2tlbi0x"}, allow_redirects=True)
print(f"  Final URL: {resp6d.url}")
print(f"  Status: {resp6d.status_code}")
print(f"  Body: {resp6d.text[:200]}")

# Test E: Check all response headers
print("\n  Test E: Checking response headers for any additional clues")
resp6e = session.get(base_url + "/meta_decode/meta-token-1", headers={'Referer': base_url + "/meta_decode/bWV0YS10b2tlbi0x"}, allow_redirects=False)
print(f"  Status: {resp6e.status_code}")
print(f"  All Headers:")
for k, v in resp6e.headers.items():
    print(f"    {k}: {v}")

print("\n" + "=" * 80)
print("DONE")
print("=" * 80)
