// ghostctl.c — minimal control utility for /dev/ghostlight
// Build: make
// Usage examples:
//   ./ghostctl hookon
//   ./ghostctl arm 0x41414141
//   ./ghostctl free
//   ./ghostctl spray <count> <fn_addr> <arg_val>
//   ./ghostctl poke      # triggers some syscalls to fire the hook

#define _GNU_SOURCE
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <unistd.h>
#include <errno.h>

#define GHOST_IOC_MAGIC  'G'
#define GHOST_IOC_ARM     _IOW(GHOST_IOC_MAGIC, 0x01, unsigned long)
#define GHOST_IOC_FREE    _IO(GHOST_IOC_MAGIC,  0x02)
#define GHOST_IOC_SPRAY   _IOW(GHOST_IOC_MAGIC, 0x03, unsigned long)
#define GHOST_IOC_HOOKON  _IO(GHOST_IOC_MAGIC,  0x04)
#define GHOST_IOC_HOOKOFF _IO(GHOST_IOC_MAGIC,  0x05)
#define GHOST_IOC_READFLAG _IOW(GHOST_IOC_MAGIC, 0x06, unsigned long)

struct spray_req {
    unsigned int count;
    unsigned long fn;
    unsigned long arg;
};

static void die(const char *msg) {
    perror(msg);
    exit(1);
}

} else if (!strcmp(argv[1], "readflag")) {
    unsigned int len = 1024;
    if (argc > 2) len = (unsigned int)strtoul(argv[2], NULL, 0);
    if (len == 0 || len > 4096) die("invalid len (max 4096)");

    struct flag_req {
        unsigned long buf;
        unsigned int len;
    } req;

    char *buf = malloc(len + 1);
    if (!buf) die("malloc");

    req.buf = (unsigned long)buf;
    req.len = len;

    /* ioctl returns number of bytes read on success */
    int rc = ioctl(fd, GHOST_IOC_READFLAG, &req);
    if (rc < 0) die("ioctl readflag");
    if (rc > 0) {
        buf[rc] = '\0';
        printf("%s\n", buf);
    } else {
        printf("(no bytes returned)\n");
    }
    free(buf);
}

int main(int argc, char **argv) {
    int fd = open("/dev/ghostlight", O_RDONLY);
    if (fd < 0) die("open(/dev/ghostlight)");

    if (argc < 2) {
        fprintf(stderr, "usage: %s [hookon|hookoff|arm <arg>|free|spray <n> <fn> <arg>|poke]\n", argv[0]);
        return 1;
    }

    if (!strcmp(argv[1], "hookon")) {
        if (ioctl(fd, GHOST_IOC_HOOKON, 0) < 0) die("ioctl hookon");
    } else if (!strcmp(argv[1], "hookoff")) {
        if (ioctl(fd, GHOST_IOC_HOOKOFF, 0) < 0) die("ioctl hookoff");
    } else if (!strcmp(argv[1], "arm")) {
        if (argc < 3) { fprintf(stderr, "arm <arg>\n"); return 1; }
        unsigned long a = strtoul(argv[2], NULL, 0);
        if (ioctl(fd, GHOST_IOC_ARM, a) < 0) die("ioctl arm");
    } else if (!strcmp(argv[1], "free")) {
        if (ioctl(fd, GHOST_IOC_FREE, 0) < 0) die("ioctl free");
    } else if (!strcmp(argv[1], "spray")) {
        if (argc < 5) { fprintf(stderr, "spray <n> <fn> <arg>\n"); return 1; }
        struct spray_req r;
        r.count = (unsigned int)strtoul(argv[2], NULL, 0);
        r.fn    = strtoul(argv[3], NULL, 0);
        r.arg   = strtoul(argv[4], NULL, 0);
        if (ioctl(fd, GHOST_IOC_SPRAY, (unsigned long)&r) < 0) die("ioctl spray");
    } else if (!strcmp(argv[1], "poke")) {
        // just cause a bunch of syscalls (tracepoint fires)
        for (int i = 0; i < 10000; i++) getpid();
    } else {
        fprintf(stderr, "unknown cmd\n");
        return 1;
    }

    return 0;
}
