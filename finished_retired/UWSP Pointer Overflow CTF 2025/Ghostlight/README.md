## Challenge Name
Ghostlight

## Platform
UWSP Pointer Overflow CTF 2025

## Category
exploit

## Difficulty
medium

## Challenge Description
Somewhere deep in the kernel, an old debugging hook was left behind — one that watches every system call. Unfortunately, it wasn’t removed cleanly. Due to copyright disputes with the King estate, let's call this /dev/ghostlight and definitely NOT deadlight.

You are provided the driver’s source (ghostlight.c) and a control program (ghostctl.c). The live instance at exp200-3.pointeroverflowctf.com:14990 is running this exact module.

Your goal: escalate the privileges of the running service process and read the flag stored at /root/flag, then return it to your client.

Interact with the remote service using the provided ghostctl or your own client code. All commands must be sent over the same TCP connection.

The service performs finalization and returns output only after your client has finished sending commands on that connection (signal EOF / close the write side). If you just send commands and leave the write side open, you will likely only see the immediate command acknowledgements. UPDATE: To nerf the challenge, players no longer need to send their own read. The helper will do the lifting IF you can get to an EOF with the correct command sequence and number of objects.

This is a kernel-level vulnerability exercise: you must exploit the device/module to raise the service’s privileges (the intended path is via a use-after-free vulnerability in the driver). The service will only provide the flag to a process that has been escalated to the required privilege level.

Do not attempt to break the contest infrastructure or exfiltrate other data on the host.

Hint: The device implements several ioctls — GHOST_IOC_ARM, GHOST_IOC_FREE, and GHOST_IOC_SPRAY. One of them doesn’t quite let go when it should…

[attachment](exp200-3.zip)

Hint: The device implements several ioctls — GHOST_IOC_ARM, GHOST_IOC_FREE, and GHOST_IOC_SPRAY. One of them doesn’t quite let go when it should…

Hint: Send your whole command sequence on a single TCP connection and then signal EOF (close or shutdown the write side) — the service finalizes the request and returns the flag only after that.

Hint: The device’s control API can allocate, free, and spray kernel objects. Think about what happens if the service holds a pointer to a freed object while you spray new objects into the same heap slot.

=== Host info inside container ===
uname: 6.1.0-40-cloud-amd64
kptr_restrict: 0
=== Symbols (raw) ===
ffffffffabcc5400 T commit_creds
ffffffffabcc56b0 T prepare_kernel_cred
ffffffffac4d8280 t maybe_init_creds
ffffffffacfe3e68 r __ksymtab_commit_creds
ffffffffacfea7a4 r __ksymtab_prepare_kernel_cred
ffffffffad659a00 D init_cred
