#!/usr/bin/env python3
"""
Detailed inspection of responses at each step
"""

import requests
import re
import base64
from bs4 import BeautifulSoup
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

session = requests.Session()
session.verify = False
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
})

base_url = "https://web100-4.pointeroverflowctf.com"

print("=" * 80)
print("INSPECTING /meta_decode/bWV0YS10b2tlbi0x IN DETAIL")
print("=" * 80)

url = base_url + "/meta_decode/bWV0YS10b2tlbi0x"
response = session.get(url, headers={'Referer': base_url + "/step_meta/bWV0YS10b2tlbi0x"}, allow_redirects=False)

print(f"Status Code: {response.status_code}")
print(f"\nAll Headers:")
for key, value in response.headers.items():
    print(f"  {key}: {value}")

print(f"\nResponse Body (raw):")
print(repr(response.text))

print(f"\nResponse Body (formatted):")
print(response.text[:1000])

print("\n" + "=" * 80)
print("INSPECTING /meta_decode/meta-token-1 RESPONSE IN DETAIL")
print("=" * 80)

url = base_url + "/meta_decode/meta-token-1"
response = session.get(url, headers={'Referer': base_url + "/meta_decode/bWV0YS10b2tlbi0x"}, allow_redirects=False)

print(f"Status Code: {response.status_code}")
print(f"\nAll Headers:")
for key, value in response.headers.items():
    print(f"  {key}: {value}")

print(f"\nResponse Body (raw):")
print(repr(response.text))

print(f"\nResponse Body (formatted):")
print(response.text[:1000])

print("\n" + "=" * 80)
print("TESTING: What if we combine steps in some way?")
print("=" * 80)

# Maybe we need to pass the encoded values as parameters?
print("\nTest 1: Access /meta_decode/meta-token-1?payload=bWV0YS10b2tlbi0x")
url = base_url + "/meta_decode/meta-token-1?payload=bWV0YS10b2tlbi0x"
response = session.get(url, headers={'Referer': base_url + "/meta_decode/bWV0YS10b2tlbi0x"}, allow_redirects=False)
print(f"Status: {response.status_code}")
print(f"Body: {response.text}")

print("\nTest 2: Access /final with the token as parameter")
url = base_url + "/final?token=meta-token-1"
response = session.get(url, headers={'Referer': base_url + "/meta_decode/meta-token-1"}, allow_redirects=False)
print(f"Status: {response.status_code}")
print(f"Body: {response.text}")
