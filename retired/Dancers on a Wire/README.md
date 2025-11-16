## Challenge Name
Dancers on a Wire

## Platform
UWSP Pointer Overflow CTF 2025

## Category
Exploit

## Difficulty
hard

## Challenge Description
xxxA tiny echo service installs a strict seccomp allowlist that kills most syscalls. No open*, no execve, no mprotect. That said - there's still a bit to work with.

Goal: print the contents of the flag to stdout.

sudo gcc -o exp400 dancers.c seccomp.c -O2 -fPIE -pie -Wno-nonnull -Wno-unused-result -Wno-nonnull-compare -Wno-stringop-overflow -Wno-format-security -fno-stack-protector -z relro -z now -z noexecstack
Allowed syscalls only: read, write, exit, exit_group, rt_sigreturn.

The flag file is pre-opened on file descriptor 3 when the service starts. You cannot open files yourself.
The service is a simple “read name” → “echo name” binary with a stack overflow (no canary).
A syscall; ret gadget exists in the binary’s .text (discoverable from the binary).
You do not need libc or any external files; an SROP chain with the allowed syscalls is sufficient.

Your Target: exp400.pointeroverflowctf.com 14664
[exp400](exp400)
[Source](https://pointeroverflowctf.com/static/exp400_source.txt)
[libc_remote.so.6](libc_remote.so.6)
[ld-linux-x86-64.so.2](ld-linux-x86-64.so.2)
