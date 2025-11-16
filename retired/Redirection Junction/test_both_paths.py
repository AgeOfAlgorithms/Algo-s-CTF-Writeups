#!/usr/bin/env python3
"""
Test visiting BOTH the single-decode and double-decode paths
Maybe there's state that needs to be built up
"""

import requests
import base64
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

session = requests.Session()
session.verify = False
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
})

base_url = "https://web100-4.pointeroverflowctf.com"

print("=" * 80)
print("TESTING: Visiting BOTH path variations to build up state")
print("=" * 80)

# Follow the chain normally first
print("\n[Phase 1] Following the normal chain...")
print("\n[1] GET /")
session.get(base_url, allow_redirects=False)

print("[2] GET /start")
session.get(base_url + "/start", headers={'Referer': base_url}, allow_redirects=False)

print("[3] GET /step_js")
session.get(base_url + "/step_js", headers={'Referer': base_url + "/start"}, allow_redirects=False)

print("[4] GET /step_meta/bWV0YS10b2tlbi0x")
session.get(base_url + "/step_meta/bWV0YS10b2tlbi0x", headers={'Referer': base_url + "/step_js"}, allow_redirects=False)

print("[5] GET /meta_decode/bWV0YS10b2tlbi0x")
resp5 = session.get(base_url + "/meta_decode/bWV0YS10b2tlbi0x", headers={'Referer': base_url + "/step_meta/bWV0YS10b2tlbi0x"}, allow_redirects=False)
print(f"  Status: {resp5.status_code}, Location: {resp5.headers.get('Location')}")

print(f"  Cookies after step 5: {dict(session.cookies)}")

# Now, what if we visit the double-decoded path?
print("\n[Phase 2] Visiting the double-decoded path...")
print("[6] GET /step_meta/meta-token-1 (double-decoded path)")
resp6 = session.get(base_url + "/step_meta/meta-token-1", headers={'Referer': base_url + "/meta_decode/bWV0YS10b2tlbi0x"}, allow_redirects=False)
print(f"  Status: {resp6.status_code}")
print(f"  Body: {resp6.text[:200]}")
print(f"  Cookies: {dict(session.cookies)}")

# What comes after /step_meta/meta-token-1?
# Based on the pattern, maybe there's a follow-up?
print("\n[7] GET /meta_decode/meta-token-1")
resp7 = session.get(base_url + "/meta_decode/meta-token-1", headers={'Referer': base_url + "/step_meta/meta-token-1"}, allow_redirects=False)
print(f"  Status: {resp7.status_code}")
print(f"  Body: {resp7.text}")
print(f"  Location: {resp7.headers.get('Location', 'None')}")
print(f"  Cookies: {dict(session.cookies)}")

# Now try /final
print("\n[8] GET /final")
final_resp = session.get(base_url + "/final", headers={'Referer': base_url + "/meta_decode/meta-token-1"}, allow_redirects=False)
print(f"  Status: {final_resp.status_code}")
print(f"  Body: {final_resp.text}")

# What if the order matters? Let's try going to the double-decoded path FIRST
print("\n" + "=" * 80)
print("TESTING: Starting fresh - try double-decoded path FIRST")
print("=" * 80)

session2 = requests.Session()
session2.verify = False
session2.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
})

print("\n[1] GET /")
session2.get(base_url, allow_redirects=False)

print("[2] GET /start")
session2.get(base_url + "/start", headers={'Referer': base_url}, allow_redirects=False)

print("[3] GET /step_js")
session2.get(base_url + "/step_js", headers={'Referer': base_url + "/start"}, allow_redirects=False)

# Skip to double-decoded path
print("[4] GET /step_meta/meta-token-1 (double-decoded)")
resp4_alt = session2.get(base_url + "/step_meta/meta-token-1", headers={'Referer': base_url + "/step_js"}, allow_redirects=False)
print(f"  Status: {resp4_alt.status_code}, Body: {resp4_alt.text[:100]}")

# What if we need to visit many tokens?
print("\n" + "=" * 80)
print("TESTING: Visit multiple tokens to build up state")
print("=" * 80)

session3 = requests.Session()
session3.verify = False
session3.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
})

# Build up all state
session3.get(base_url, allow_redirects=False)
session3.get(base_url + "/start", headers={'Referer': base_url}, allow_redirects=False)
session3.get(base_url + "/step_js", headers={'Referer': base_url + "/start"}, allow_redirects=False)
session3.get(base_url + "/step_meta/bWV0YS10b2tlbi0x", headers={'Referer': base_url + "/step_js"}, allow_redirects=False)
session3.get(base_url + "/meta_decode/bWV0YS10b2tlbi0x", headers={'Referer': base_url + "/step_meta/bWV0YS10b2tlbi0x"}, allow_redirects=False)

# Try visiting a range of tokens
for i in range(1, 6):
    token = f"meta-token-{i}"
    print(f"\nTrying token: {token}")

    # Try the encoded path
    encoded = base64.b64encode(token.encode()).decode()
    test_url = base_url + f"/step_meta/{encoded}"
    resp = session3.get(test_url, headers={'Referer': base_url + "/meta_decode/bWV0YS10b2tlbi0x"}, allow_redirects=False)
    print(f"  /step_meta/{encoded} -> Status: {resp.status_code}")

    # Try the decoded path
    test_url2 = base_url + f"/step_meta/{token}"
    resp2 = session3.get(test_url2, headers={'Referer': base_url + "/meta_decode/bWV0YS10b2tlbi0x"}, allow_redirects=False)
    print(f"  /step_meta/{token} -> Status: {resp2.status_code}")
    if resp2.status_code == 200:
        print(f"  Body: {resp2.text[:200]}")

    # Check if cookies changed
    print(f"  Cookies: {dict(session3.cookies)}")
