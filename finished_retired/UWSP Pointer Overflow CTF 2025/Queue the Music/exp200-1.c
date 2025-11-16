// /app/queuer.c
#define _GNU_SOURCE
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <errno.h>

static int starts_with(const char *s, const char *p) {
    size_t n = strlen(p);
    return strncmp(s, p, n) == 0;
}

int main(int argc, char **argv) {
    if (argc != 2) { fprintf(stderr, "usage: %s PATH\n", argv[0]); return 2; }
    const char *path = argv[1];

    // Get the path
    if (!starts_with(path, "/tmp/uploads/")) {
        fputs("bad path\n", stderr);
        return 2;
    }

    // Pre-check
    struct stat st;
    if (stat(path, &st) == -1) { perror("stat"); return 2; }
    if (!S_ISREG(st.st_mode) || st.st_size > 4096) {
        fputs("bad path\n", stderr);
        return 2;
    }

    // Use the path
    int in = open(path, O_RDONLY);
    if (in == -1) { perror("open"); return 2; }

    char buf[4096];
    ssize_t n = read(in, buf, sizeof(buf));
    if (n < 0) { perror("read"); close(in); return 2; }
    close(in);

    int out = open("/app/public/playlist.txt", O_WRONLY|O_APPEND);
    if (out == -1) { perror("playlist"); return 1; }
    if (write(out, buf, (size_t)n) < 0) { perror("write"); close(out); return 1; }
    close(out);

    return 0;
}
