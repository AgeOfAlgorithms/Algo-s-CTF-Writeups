#!/usr/bin/env python3
"""
Check if /meta_decode endpoints set any cookies
"""

import base64
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

session = requests.Session()
session.verify = False
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
})

base_url = "https://web100-4.pointeroverflowctf.com"

print("=" * 80)
print("Checking if /meta_decode endpoints set cookies")
print("=" * 80)

# Build initial state
print("\nBuilding initial state...")
session.get(base_url, allow_redirects=False)
session.get(base_url + "/start", headers={'Referer': base_url}, allow_redirects=False)
session.get(base_url + "/step_js", headers={'Referer': base_url + "/start"}, allow_redirects=False)
print(f"Cookies after /step_js: {dict(session.cookies)}")

# Visit /step_meta/bWV0YS10b2tlbi0x
print("\nVisiting /step_meta/bWV0YS10b2tlbi0x...")
resp = session.get(base_url + "/step_meta/bWV0YS10b2tlbi0x", headers={'Referer': base_url + "/step_js"}, allow_redirects=False)
print(f"Status: {resp.status_code}")
print(f"Response cookies: {dict(resp.cookies)}")
print(f"Session cookies: {dict(session.cookies)}")

# Visit /meta_decode/bWV0YS10b2tlbi0x (this is the 302 redirect)
print("\nVisiting /meta_decode/bWV0YS10b2tlbi0x...")
resp = session.get(base_url + "/meta_decode/bWV0YS10b2tlbi0x", headers={'Referer': base_url + "/step_meta/bWV0YS10b2tlbi0x"}, allow_redirects=False)
print(f"Status: {resp.status_code}")
print(f"Location: {resp.headers.get('Location')}")
print(f"Response cookies: {dict(resp.cookies)}")
print(f"Session cookies: {dict(session.cookies)}")

# Now let's follow through to meta-token-1 and see if any other cookies are set
print("\nVisiting /step_meta/meta-token-1...")
resp = session.get(base_url + "/step_meta/meta-token-1", headers={'Referer': base_url + "/meta_decode/bWV0YS10b2tlbi0x"}, allow_redirects=False)
print(f"Status: {resp.status_code}")
print(f"Response cookies: {dict(resp.cookies)}")
print(f"Session cookies: {dict(session.cookies)}")

# Visit /meta_decode/meta-token-1
print("\nVisiting /meta_decode/meta-token-1...")
resp = session.get(base_url + "/meta_decode/meta-token-1", headers={'Referer': base_url + "/step_meta/meta-token-1"}, allow_redirects=False)
print(f"Status: {resp.status_code}")
print(f"Status line shows: {resp.status_code} (not 302, so something different here!)")
print(f"Response text: {resp.text[:200]}")
print(f"Response cookies: {dict(resp.cookies)}")
print(f"Session cookies: {dict(session.cookies)}")
if 'Location' in resp.headers:
    print(f"Location header: {resp.headers['Location']}")

# Visit /step_meta/meta-token-2
print("\nVisiting /step_meta/meta-token-2...")
resp = session.get(base_url + "/step_meta/meta-token-2", headers={'Referer': base_url + "/meta_decode/meta-token-1"}, allow_redirects=False)
print(f"Status: {resp.status_code}")
print(f"Response cookies: {dict(resp.cookies)}")
print(f"Session cookies: {dict(session.cookies)}")

# Visit /meta_decode/meta-token-2
print("\nVisiting /meta_decode/meta-token-2...")
resp = session.get(base_url + "/meta_decode/meta-token-2", headers={'Referer': base_url + "/step_meta/meta-token-2"}, allow_redirects=False)
print(f"Status: {resp.status_code}")
print(f"Response text: {resp.text[:200]}")
print(f"Response cookies: {dict(resp.cookies)}")
print(f"Session cookies: {dict(session.cookies)}")

# What if we need to /final after visiting a certain number of these?
print("\nTrying /final after meta-token-2...")
final_resp = session.get(base_url + "/final", headers={'Referer': base_url + "/meta_decode/meta-token-2"}, allow_redirects=False)
print(f"Status: {final_resp.status_code}")
print(f"Body: {final_resp.text}")
