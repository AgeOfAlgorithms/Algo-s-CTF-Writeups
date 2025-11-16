## Challenge Name
Paper Tigers

## Platform
UWSP Pointer Overflow CTF 2025

## Category
Exploit

## Difficulty
easy

## Challenge Description
Ah, the classic Exploit 100 challenge... A harken back to the old days before DEP/NX and other exploit mitigations. It's the quinessentiual entry-level challenge, and one I give my students every Spring in Application Security as their very first assignment. Source code is at the link below. Nothing beats the classics, especially with a little ret2libc twist to give it just a little spice. The flag can be found in /flag/flag.txt once you get a shell. Happy hunting!

Your Target: exp100-1.pointeroverflowctf.com:14660

[Source](https://pointeroverflowctf.com/static/exploit100-1.c)

[attachment](libc_remote.so.6)
gcc -O0 -no-pie -fno-stack-protector -o /out/vuln /src/vuln.c -ldl
