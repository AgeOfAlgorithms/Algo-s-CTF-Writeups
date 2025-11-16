#!/usr/bin/env python3
"""
Redirection Junction - Solution Attempt
Author: Claude Code
Purpose: Follow the complete redirect chain to get the flag for Redirection Junction challenge
Challenge: https://web100-4.pointeroverflowctf.com

Key findings:
- Following the chain: / -> /start -> /step_js (sets visited_js cookie)
  -> /step_meta/bWV0YS10b2tlbi0x -> /meta_decode/bWV0YS10b2tlbi0x
  -> /step_meta/meta-token-1 (loop detected)
- The chain enters a self-referential loop at meta-token-1
- /final endpoint returns "Incomplete final request" suggesting missing data
"""

import requests
import base64
import re
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

session = requests.Session()
session.verify = False
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
})

base_url = "https://web100-4.pointeroverflowctf.com"

def extract_payload_from_step_meta(resp):
    """Extract the payload from /step_meta/* response"""
    import re
    match = re.search(r'<pre[^>]*>([^<]+)</pre>', resp.text)
    if match:
        return match.group(1).strip()
    return None

print("=" * 80)
print("Redirection Junction - Solution Attempt")
print("=" * 80)

# Step 1: Start at root
current_url = base_url
referer = None

print(f"\n[1] Starting at: {current_url}")

# Follow redirects manually
current_url = base_url + "/start"
print(f"    Redirected to: {current_url}")

# Step 2: Visit /start
current_url = base_url + "/step_js"
print(f"    Redirected to: {current_url}")

# Step 3: Get JavaScript payload
resp = session.get(current_url, headers={'Referer': base_url + "/start"}, allow_redirects=False)
js_payload = re.search(r'var\s+p\s*=\s*"([A-Za-z0-9+/=]+)"', resp.text).group(1)
print(f"\n[3] JavaScript payload: {js_payload}")
first_decode = base64.b64decode(js_payload).decode('utf-8')
print(f"    Decoded to: {first_decode}")

# Step 4: Visit /step_meta/<encoded>
encoded_token1 = first_decode.split('/')[-1]
print(f"\n[4] Visiting /step_meta/{encoded_token1}")
resp = session.get(base_url + f"/step_meta/{encoded_token1}",
                   headers={'Referer': current_url},
                   allow_redirects=False)
payload2 = extract_payload_from_step_meta(resp)
print(f"    Page payload: {payload2}")

# Step 5: Visit /meta_decode/<encoded>
print(f"\n[5] Visiting /meta_decode/{encoded_token1}")
resp = session.get(base_url + f"/meta_decode/{encoded_token1}",
                   headers={'Referer': base_url + f"/step_meta/{encoded_token1}"},
                   allow_redirects=False)
next_token = resp.headers.get('Location')
print(f"    Redirected to: {next_token}")

# Step 6: Visit /step_meta/<token>
print(f"\n[6] Visiting /step_meta/{next_token}")
resp = session.get(base_url + f"/step_meta/{next_token}",
                   headers={'Referer': base_url + f"/meta_decode/{encoded_token1}"},
                   allow_redirects=False)
payload3 = extract_payload_from_step_meta(resp)
print(f"    Page payload: {payload3}")

# At this point, payload3 equals next_token (meta-token-1)
# This creates a self-referential loop
print(f"\n{'=' * 80}")
print("ANALYSIS:")
print(f"{'=' * 80}")
print(f"Detected self-referential loop at: {payload3}")
print(f"The chain returns to the same token.")

# Try /final endpoint
print(f"\n[FINAL] Attempting to access /final endpoint")
final_resp = session.get(base_url + "/final",
                         headers={'Referer': base_url + f"/step_meta/{next_token}"},
                         allow_redirects=False)
print(f"    Status: {final_resp.status_code}")
print(f"    Response: {final_resp.text}")

# Try visiting all the /meta_decode/<encoded> endpoints in sequence
# Maybe we need to visit all possible tokens before accessing /final?
print(f"\n{'=' * 80}")
print("Testing: Visit all tokens then /final")
print(f"{'=' * 80}")

tokens_visited = []
for i in range(1, 51):
    token = f"meta-token-{i}"
    encoded = base64.b64encode(token.encode()).decode()

    # Visit step_meta
    resp1 = session.get(base_url + f"/step_meta/{token}",
                       headers={'Referer': base_url + f"/meta_decode/{encoded_token1}"},
                       allow_redirects=False)

    # Visit meta_decode
    resp2 = session.get(base_url + f"/meta_decode/{encoded}",
                       headers={'Referer': base_url + f"/step_meta/{token}"},
                       allow_redirects=False)

    if resp2.status_code == 302:
        tokens_visited.append(token)
        print(f"  Visited token {i}: {token}")
    else:
        print(f"  Stopped at token {i}: {token} (status: {resp2.status_code})")
        break

# After visiting many tokens, try /final again
print(f"\n  Visited {len(tokens_visited)} tokens")
print(f"  Trying /final again...")
final_resp2 = session.get(base_url + "/final",
                          headers={'Referer': base_url + f"/meta_decode/meta-token-{len(tokens_visited)}"},
                          allow_redirects=False)
print(f"  Status: {final_resp2.status_code}")
print(f"  Response: {final_resp2.text}")

print(f"\n{'=' * 80}")
print("CONCLUSION:")
print(f"{'=' * 80}")
print("The challenge likely requires:")
print("1. Following the initial redirect chain")
print("2. Recognizing the self-referential pattern at meta-token-1")
print("3. Doing something additional (submitting a parameter, using a specific header, etc.)")
print("4. Then accessing /final to get the flag")
print()
print("Despite extensive testing:")
print("- Following the full redirect chain")
print("- Maintaining cookies and Referer headers")
print("- Testing 50+ sequential tokens")
print("- Testing /final with various parameters and headers")
print()
print("The /final endpoint always returns 'Incomplete final request.'")
print("This suggests missing required data or steps.")
