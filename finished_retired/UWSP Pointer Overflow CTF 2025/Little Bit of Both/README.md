## Challenge Name
Little Bit of Both

## Platform
UWSP Pointer Overflow CTF 2025

## Category
Exploit

## Difficulty
easy

## Challenge Description
Once you see this code, you will no doubt know exactly what to do with it. It's a very famous exploit from the distant pass when worms were worms and bubblegum cost a nickel. Once you're in a shell, you're looking for flag/flag.txt

Your Target: exp100-3.pointeroverflowctf.com:14667

[attachment](exp100-3)
Make: gcc -m64 -O0 -zexecstack -fno-stack-protector -no-pie -o exp100-3.bin exp100-3.c
[Source](https://pointeroverflowctf.com/static/exp100-3.c)
[attachment](libc_remote.so.6)
[attachment](ld-linux-x86-64.so.2)
