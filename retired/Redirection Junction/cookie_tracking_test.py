#!/usr/bin/env python3
"""
Carefully track cookies throughout the entire chain
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

print("=" * 80)
print("Tracking cookies throughout the chain")
print("=" * 80)

# Step 1: Root
print("\n[Step 1] GET /")
resp1 = session.get(base_url, allow_redirects=False)
print(f"  Status: {resp1.status_code}")
print(f"  Response cookies: {dict(resp1.cookies)}")
print(f"  Session cookies after response: {dict(session.cookies)}")

# Step 2: /start
print("\n[Step 2] GET /start")
resp2 = session.get(base_url + "/start", headers={'Referer': base_url}, allow_redirects=False)
print(f"  Status: {resp2.status_code}")
print(f"  Response cookies: {dict(resp2.cookies)}")
print(f"  Session cookies after response: {dict(session.cookies)}")

# Step 3: /step_js
print("\n[Step 3] GET /step_js")
resp3 = session.get(base_url + "/step_js", headers={'Referer': base_url + "/start"}, allow_redirects=False)
print(f"  Status: {resp3.status_code}")
print(f"  Response cookies: {dict(resp3.cookies)}")
print(f"  Session cookies after response: {dict(session.cookies)}")

# Check if any cookies have specific path or domain constraints
print(f"  Cookie details via session.cookies:")
for cookie in session.cookies:
    print(f"    {cookie.name}: {cookie.value} (domain: {cookie.domain}, path: {cookie.path})")

# Step 4: /step_meta/bWV0YS10b2tlbi0x
print("\n[Step 4] GET /step_meta/bWV0YS10b2tlbi0x")
resp4 = session.get(base_url + "/step_meta/bWV0YS10b2tlbi0x", headers={'Referer': base_url + "/step_js"}, allow_redirects=False)
print(f"  Status: {resp4.status_code}")
print(f"  Response cookies: {dict(resp4.cookies)}")
print(f"  Session cookies after response: {dict(session.cookies)}")

# Step 5: /meta_decode/bWV0YS10b2tlbi0x
print("\n[Step 5] GET /meta_decode/bWV0YS10b2tlbi0x")
resp5 = session.get(base_url + "/meta_decode/bWV0YS10b2tlbi0x", headers={'Referer': base_url + "/step_meta/bWV0YS10b2tlbi0x"}, allow_redirects=False)
print(f"  Status: {resp5.status_code}")
print(f"  Location: {resp5.headers.get('Location', 'None')}")
print(f"  Response cookies: {dict(resp5.cookies)}")
print(f"  Session cookies after response: {dict(session.cookies)}")

# Now, let me try something NEW based on the challenge hint
# The challenge says: "decode client-side redirects yourself"
# What if we're NOT supposed to follow the redirect to meta-token-1?
# What if instead, we visit /final at this point?

print("\n" + "=" * 80)
print("TESTING: What if we go to /final right after step 5?")
print("=" * 80)

print("\nGoing to /final after step 5...")
final_resp = session.get(base_url + "/final", headers={'Referer': base_url + "/meta_decode/bWV0YS10b2tlbi0x"}, allow_redirects=False)
print(f"Status: {final_resp.status_code}")
print(f"Body: {final_resp.text}")
print(f"Cookies: {dict(session.cookies)}")

# Or what if we need to pass what we decoded as a parameter?
print("\nTest: /final?payload=bWV0YS10b2tlbi0x")
final_resp2 = session.get(base_url + "/final?payload=bWV0YS10b2tlbi0x", headers={'Referer': base_url + "/meta_decode/bWV0YS10b2tlbi0x"}, allow_redirects=False)
print(f"Status: {final_resp2.status_code}")
print(f"Body: {final_resp2.text}")

print("\nTest: /final?token=meta-token-1")
final_resp3 = session.get(base_url + "/final?token=meta-token-1", headers={'Referer': base_url + "/meta_decode/bWV0YS10b2tlbi0x"}, allow_redirects=False)
print(f"Status: {final_resp3.status_code}")
print(f"Body: {final_resp3.text}")
