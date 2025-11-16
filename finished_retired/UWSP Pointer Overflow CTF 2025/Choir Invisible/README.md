## Challenge Name
Choir Invisible

## Platform
UWSP Pointer Overflow CTF 2025

## Category
Exploit

## Difficulty
medium

## Challenge Description
This service simulates an in-kernel heap object with a leading function pointer that happens to have a use-after-free bug you can exploit remotely via a tiny TCP protocol.

req: uint32 op, uint32 size, uint8 data[size] resp: uint32 status (0=ok), uint32 size, uint8 data[size]

Operations:
- 1 CREATE — data: uint32 idx (0..127)
- 2 FREE — data: uint32 idx
- 3 SETBUF — data: uint32 idx | uint32 n | n bytes
- 4 TRIGGER — data: uint32 idx (invokes callback)
- 5 SPRAY — data: uint32 chunk_size | uint32 count | chunk_size bytes (payload replicated)
- 6 LEAK — returns two uint64 addresses (helpers for the lab)
- 7 READFLAG — returns /flag.txt if you’ve attained lab “root”


Your Target: exp300-1.pointeroverflowctf.com:15156

[Source](https://pointeroverflowctf.com/static/exp300-1.c)

And here's a little client for you to get started: [Clicking Buttons](https://pointeroverflowctf.com/static/exp300-1_client.py)