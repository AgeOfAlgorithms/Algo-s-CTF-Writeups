#!/usr/bin/env python3
"""
ZIP password cracker
Author: CTF Solver
Purpose: Crack the password of the reconstructed ZIP file
Created: 2025-11-09
Expected: Find the password and extract the flag
Last updated: 2025-11-09
Result: Attempting to crack...
"""

import zipfile
import sys

def crack_zip(zip_path, wordlist_path=None):
    """Attempt to crack a ZIP file password"""

    # Try common passwords first
    common_passwords = [
        b'password',
        b'123456',
        b'12345678',
        b'qwerty',
        b'abc123',
        b'monkey',
        b'letmein',
        b'trustno1',
        b'dragon',
        b'baseball',
        b'111111',
        b'iloveyou',
        b'master',
        b'sunshine',
        b'ashley',
        b'bailey',
        b'passw0rd',
        b'shadow',
        b'123123',
        b'654321',
        b'superman',
        b'qazwsx',
        b'michael',
        b'football',
        b'',  # Empty password
        b'admin',
        b'root',
        b'flag',
        b'buckeye',
        b'ctf',
        b'buckeyectf',
        b'zip2john2zip',
    ]

    print(f"[*] Attempting to crack {zip_path}")
    print(f"[*] Trying {len(common_passwords)} common passwords first...")

    try:
        zf = zipfile.ZipFile(zip_path)
    except Exception as e:
        print(f"[-] Error opening ZIP file: {e}")
        return None

    # Try common passwords
    for i, password in enumerate(common_passwords, 1):
        try:
            zf.extractall(pwd=password)
            print(f"\n[+] SUCCESS! Password found: {password.decode('utf-8', errors='replace')}")
            return password.decode('utf-8', errors='replace')
        except:
            sys.stdout.write(f"\r[*] Tried {i}/{len(common_passwords)} common passwords")
            sys.stdout.flush()

    print("\n[-] Common passwords failed")

    # Try wordlist if provided
    if wordlist_path:
        print(f"[*] Trying wordlist: {wordlist_path}")
        try:
            with open(wordlist_path, 'rb') as f:
                count = 0
                for line in f:
                    count += 1
                    password = line.strip()
                    try:
                        zf.extractall(pwd=password)
                        print(f"\n[+] SUCCESS! Password found: {password.decode('utf-8', errors='replace')}")
                        return password.decode('utf-8', errors='replace')
                    except:
                        if count % 1000 == 0:
                            sys.stdout.write(f"\r[*] Tried {count} passwords...")
                            sys.stdout.flush()
        except FileNotFoundError:
            print(f"[-] Wordlist not found: {wordlist_path}")
        except Exception as e:
            print(f"[-] Error reading wordlist: {e}")

    print("\n[-] Password not found")
    return None

if __name__ == "__main__":
    zip_file = "flag.zip"
    rockyou_path = "/usr/share/wordlists/rockyou.txt"

    # Try without wordlist first
    password = crack_zip(zip_file)

    # If that fails, try rockyou
    if not password:
        print(f"\n[*] Trying rockyou.txt wordlist...")
        password = crack_zip(zip_file, rockyou_path)
