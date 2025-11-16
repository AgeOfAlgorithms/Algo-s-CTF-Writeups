#!/usr/bin/env python3
"""
Test the double-decode theory
"""

import base64

# The JavaScript payload
p = "L3N0ZXBfbWV0YS9iV1YwWVMxMGIydGxiaTB4"

print("JavaScript payload:", p)
print()

# First decode
try:
    first = base64.urlsafe_b64decode(p + '==').decode('utf-8')
    print("First decode (urlsafe + ==):", first)
except Exception as e:
    print("Error with urlsafe + ==:", e)

try:
    first = base64.urlsafe_b64decode(p).decode('utf-8')
    print("First decode (urlsafe):", first)
except Exception as e:
    print("Error with urlsafe:", e)

try:
    first = base64.b64decode(p).decode('utf-8')
    print("First decode (standard):", first)
except Exception as e:
    print("Error with standard:", e)

print()

# Second decode of the first result
first = "/step_meta/bWV0YS10b2tlbi0x"
print("Attempting second decode on:", first)
print("Splitting by '/step_meta/':", first.split('/step_meta/'))

path_part = first.split('/step_meta/')[1]
print("Path part:", path_part)

try:
    second = base64.b64decode(path_part).decode('utf-8')
    print("Second decode result:", second)
except Exception as e:
    print("Error with second decode:", e)

# What if the second decode is actually the one we need to use?
print()
print("=" * 60)
print("What if the JavaScript hint means we need to:\n1. Decode once to get: /step_meta/bWV0YS10b2tlbi0x\n2. Take the last part: bWV0YS10b2tlbi0x\n3. Decode again: meta-token-1")
print("=" * 60)
print()

# But what if the "double decode" means we need to keep BOTH results somehow?
result1 = "/step_meta/bWV0YS10b2tlbi0x"
result2 = "/step_meta/meta-token-1"

print("Path 1 (single decode):", result1)
print("Path 2 (double decode):", result2)
