// gcc -O0 -fno-stack-protector -no-pie -z execstack -o exp1002 server.c
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <signal.h>
#include <fcntl.h>
#include <string.h>
#include <sys/stat.h>
#include <openssl/ssl.h>

__asm__(
".global jmprsp\n"
"jmprsp:\n"
"    jmp *%rsp\n"
);

static void sig_handler(int signum) {
    printf("Timeout\n");
    exit(0);
}

static void init(void) {
    alarm(60);
    signal(SIGALRM, sig_handler);

    setvbuf(stdin,  NULL, _IONBF, 0);
    setvbuf(stdout, NULL, _IONBF, 0);
    setvbuf(stderr, NULL, _IONBF, 0);

    chdir(getenv("HOME"));
}

__attribute__((noinline))
static void serve(void) {
    int len = 0;


    struct {
        char data[64];
        char pad[32];
        char flag[128];
    } frame;

    memset(&frame, 0, sizeof(frame));
    memcpy(frame.pad, "LEAK->", 6);

    int fd = open("/flag", O_RDONLY);
    if (fd >= 0) {
        read(fd, frame.flag, sizeof(frame.flag) - 1);
        close(fd);
    } else {
        strcpy(frame.flag, "Flag missing. Notify @CTF_Admin\n");
    }

    printf("TLS heartbeat simulator\n");
    printf("  example input: 5:HELLO   (requests 5 bytes of response)\n");

    do {
        printf("\nWaiting for heart beat request...\n");
        if (scanf(" %d:%63s", &len, frame.data) != 2) break;

        printf("Sending heart beat response...\n");
        write(STDOUT_FILENO, frame.data, (size_t)len);

    } while (len > 0);
}

int main(void) {
    init();
    serve();
    return 0;
}