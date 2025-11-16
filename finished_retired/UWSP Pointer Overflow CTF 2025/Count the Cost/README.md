## Challenge Name
Count the Cost

## Platform
UWSP Pointer Overflow CTF 2025

## Category
Exploit

## Difficulty
medium

## Challenge Description
Track transactions (0..7), set amounts and notes. set_note reads a 2-byte length (uint16) and that many bytes. Find a way to make checkout reveal the flag.

Source
CFLAGS := -O2 -fno-stack-protector -z noexecstack -no-pie -fno-pic -Wl,-z,relro -Wl,-z,now

[attachment](exp200-2.bin)
Your Target: 34.9.14.80:14992