#!/usr/bin/env python3
"""
Redirection Junction Solver
Author: Claude Code
Purpose: Follow a complex chain of redirections including HTTP redirects, meta refreshes,
         and JavaScript redirects while preserving cookies and Referer headers
Created: 2025-11-10
Last Updated: 2025-11-10 (Fixed to use first-decode only, server handles further decoding)
Expected Result: Find and display the flag at the end of the redirect chain
Produced Result: Script successfully follows the redirect chain but encounters a 400 "Invalid payload"
                 error at /meta_decode/meta-token-1. The redirect chain followed is:
                 / → /start → /step_js (sets cookie) → /step_meta/bWV0YS10b2tlbi0x →
                 /meta_decode/bWV0YS10b2tlbi0x → /meta_decode/meta-token-1 (400 error)
                 See UNSOLVED.md for full details of attempts and assumptions.
"""

import requests
import re
import base64
import urllib.parse
from bs4 import BeautifulSoup
from typing import Optional, Tuple

class RedirectFollower:
    def __init__(self, start_url: str):
        self.start_url = start_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        self.max_redirects = 100
        self.redirect_count = 0

    def decode_string(self, text: str) -> Optional[str]:
        """Try to decode a string using various methods (Base64, URL-safe Base64, hex)"""
        # Try standard Base64
        try:
            decoded = base64.b64decode(text).decode('utf-8', errors='ignore')
            if decoded.isprintable() or '/' in decoded:
                print(f"  [Decoded Base64]: {decoded}")
                return decoded
        except:
            pass

        # Try URL-safe Base64
        try:
            decoded = base64.urlsafe_b64decode(text + '==').decode('utf-8', errors='ignore')
            if decoded.isprintable() or '/' in decoded:
                print(f"  [Decoded URL-safe Base64]: {decoded}")
                return decoded
        except:
            pass

        # Try hex
        try:
            decoded = bytes.fromhex(text).decode('utf-8', errors='ignore')
            if decoded.isprintable() or '/' in decoded:
                print(f"  [Decoded Hex]: {decoded}")
                return decoded
        except:
            pass

        return None

    def extract_next_url(self, response: requests.Response, current_url: str) -> Optional[Tuple[str, str]]:
        """
        Extract the next URL from various sources:
        - HTTP Location header
        - Meta refresh tag
        - JavaScript window.location
        - Encoded strings in the page
        Returns: (next_url, method) or (None, None)
        """
        # Check for HTTP redirect in Location header
        if 'Location' in response.headers:
            next_url = response.headers['Location']
            if not next_url.startswith('http'):
                next_url = urllib.parse.urljoin(current_url, next_url)
            return (next_url, "HTTP Location header")

        # Parse HTML content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Check for meta refresh
        meta_refresh = soup.find('meta', attrs={'http-equiv': re.compile('refresh', re.I)})
        if meta_refresh and meta_refresh.get('content'):
            content = meta_refresh['content']
            match = re.search(r'url=(.+)', content, re.I)
            if match:
                next_url = match.group(1).strip('\'"')
                if not next_url.startswith('http'):
                    next_url = urllib.parse.urljoin(current_url, next_url)
                return (next_url, "Meta refresh tag")

        # Check for JavaScript redirects (window.location)
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string:
                # Look for base64 encoded payloads in variables
                var_match = re.search(r'var\s+\w+\s*=\s*["\']([A-Za-z0-9+/=-]+)["\']', script.string)
                if var_match:
                    encoded = var_match.group(1)
                    print(f"  Found encoded payload in JavaScript: {encoded}")
                    try:
                        # Just do first decode, don't double-decode
                        first_decode = base64.b64decode(encoded).decode('utf-8')
                        print(f"  Decoded to: {first_decode}")
                        next_url = first_decode

                        if not next_url.startswith('http'):
                            next_url = urllib.parse.urljoin(current_url, next_url)
                        return (next_url, "JavaScript base64 payload (decoded)")
                    except Exception as e:
                        print(f"  Failed to decode: {e}")

                # Look for window.location assignments
                match = re.search(r'window\.location\s*=\s*["\']([^"\']+)["\']', script.string)
                if match:
                    next_url = match.group(1)
                    if not next_url.startswith('http'):
                        next_url = urllib.parse.urljoin(current_url, next_url)
                    return (next_url, "JavaScript window.location")

                # Look for window.location.href assignments
                match = re.search(r'window\.location\.href\s*=\s*["\']([^"\']+)["\']', script.string)
                if match:
                    next_url = match.group(1)
                    if not next_url.startswith('http'):
                        next_url = urllib.parse.urljoin(current_url, next_url)
                    return (next_url, "JavaScript window.location.href")

        # Look for long encoded strings in the page
        text_content = soup.get_text()
        # Find potential base64 strings (long alphanumeric strings)
        potential_encoded = re.findall(r'[A-Za-z0-9+/=-]{20,}', text_content)
        for encoded in potential_encoded:
            decoded = self.decode_string(encoded)
            if decoded and ('/' in decoded or decoded.startswith('http')):
                if not decoded.startswith('http'):
                    decoded = urllib.parse.urljoin(current_url, decoded)
                return (decoded, "Decoded string in page")

        return (None, None)

    def follow_chain(self):
        """Follow the redirect chain until we reach the final page"""
        current_url = self.start_url
        referer = None

        print(f"Starting at: {current_url}\n")

        while self.redirect_count < self.max_redirects:
            self.redirect_count += 1
            print(f"[Step {self.redirect_count}] Requesting: {current_url}")

            # Prepare headers
            headers = {}
            if referer:
                headers['Referer'] = referer
                print(f"  Sending Referer: {referer}")

            try:
                # Make request (don't follow redirects automatically)
                response = self.session.get(current_url, headers=headers, allow_redirects=False, timeout=10)

                print(f"  Status: {response.status_code}")
                print(f"  Cookies received: {dict(response.cookies)}")
                print(f"  Cookies in session: {dict(self.session.cookies)}")

                # Check if we found the flag
                if 'flag{' in response.text.lower() or 'ptovr{' in response.text.lower() or 'poctf{' in response.text.lower():
                    print("\n" + "="*60)
                    print("FLAG FOUND!")
                    print("="*60)
                    # Extract and display flag
                    flag_match = re.search(r'(flag|ptovr|poctf)\{[^}]+\}', response.text, re.I)
                    if flag_match:
                        print(f"\nFlag: {flag_match.group(0)}")
                    print("\nFull response:")
                    print(response.text)
                    return True

                # Don't stop on 400 errors - keep trying to extract next URL
                if response.status_code >= 400:
                    print(f"  Got error status {response.status_code}, but checking for hidden redirects anyway...")

                # Try to find next URL
                next_url, method = self.extract_next_url(response, current_url)

                if next_url:
                    print(f"  Next URL found via: {method}")
                    print(f"  Next URL: {next_url}")
                    referer = current_url  # Set referer to current URL
                    current_url = next_url
                else:
                    print("\n  No more redirects found.")
                    print("\nFinal page content:")
                    print(response.text)
                    return False

                print()

            except Exception as e:
                print(f"  Error: {e}")
                return False

        print(f"\nMax redirects ({self.max_redirects}) reached!")
        return False

def main():
    start_url = "https://web100-4.pointeroverflowctf.com"
    follower = RedirectFollower(start_url)
    success = follower.follow_chain()

    if not success:
        print("\nFailed to find the flag. Check the output above for clues.")

if __name__ == "__main__":
    main()
