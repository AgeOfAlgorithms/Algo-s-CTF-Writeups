// labkernel.c — "Choir Invisible": Simulated kernel UAF in a lab server.
#include <arpa/inet.h>
#include <errno.h>
#include <netinet/in.h>
#include <signal.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <unistd.h>

typedef struct choir {
    void (*cb)(struct choir*);
    char *buf;
    size_t len;
} choir_t;

static choir_t* slots[128];
static void** spray_chunks = NULL;
static size_t spray_cap = 0, spray_count = 0;
static int is_root = 0;

static void die(const char* msg){ perror(msg); exit(1); }

static void choir_sing(choir_t* c){ (void)c; }
static void give_root(choir_t* c){ (void)c; is_root = 1; }

static uint32_t rd32(int fd){ uint32_t x; if (read(fd,&x,4)!=4) exit(0); return x; }
static void rd(int fd, void* b, size_t n){ if (read(fd,b,n)!=(ssize_t)n) exit(0); }
static void wr32(int fd, uint32_t x){ write(fd,&x,4); }
static void wr(int fd, const void* b, size_t n){ write(fd,b,n); }

static void respond(int fd, uint32_t status, const void* data, uint32_t size){
    wr32(fd, status); wr32(fd, size); if (size) wr(fd, data, size);
}

static void op_create(int fd, const uint8_t* d, uint32_t n){
    if (n != 4){ respond(fd, 1, "bad args", 8); return; }
    uint32_t idx = *(uint32_t*)d;
    if (idx >= 128){ respond(fd, 2, "bad idx", 7); return; }
    if (slots[idx]){ respond(fd, 3, "busy", 4); return; }
    choir_t* c = (choir_t*)malloc(sizeof(choir_t));
    if (!c){ respond(fd, 4, "oom", 3); return; }
    c->cb = choir_sing;
    c->len = 0x100;
    c->buf = (char*)malloc(c->len);
    memset(c->buf, 0, c->len);
    slots[idx] = c;
    respond(fd, 0, NULL, 0);
}

static void op_free(int fd, const uint8_t* d, uint32_t n){
    if (n != 4){ respond(fd, 1, "bad args", 8); return; }
    uint32_t idx = *(uint32_t*)d;
    if (idx >= 128 || !slots[idx]){ respond(fd, 2, "bad idx", 7); return; }
    choir_t* c = slots[idx];
    free(c->buf);
    free(c);
    // BUG: leave dangling pointer in slots[idx]
    respond(fd, 0, NULL, 0);
}

static void op_setbuf(int fd, const uint8_t* d, uint32_t n){
    if (n < 8){ respond(fd, 1, "bad args", 8); return; }
    uint32_t idx = *(uint32_t*)d;
    uint32_t m = *(uint32_t*)(d+4);
    if (idx >= 128 || !slots[idx]){ respond(fd, 2, "bad idx", 7); return; }
    choir_t* c = slots[idx];
    if (!c || !c->buf){ respond(fd, 5, "dangling", 8); return; }
    if (m > c->len) m = c->len;
    memcpy(c->buf, d+8, m);
    respond(fd, 0, NULL, 0);
}

static void op_trigger(int fd, const uint8_t* d, uint32_t n){
    if (n != 4){ respond(fd, 1, "bad args", 8); return; }
    uint32_t idx = *(uint32_t*)d;
    if (idx >= 128 || !slots[idx]){ respond(fd, 2, "bad idx", 7); return; }
    choir_t* c = slots[idx];
    void (*f)(choir_t*) = c->cb; // UAF sink if c was freed and chunk reclaimed
    f(c);
    respond(fd, 0, NULL, 0);
}

static void* xmalloc(size_t n){ void* p = malloc(n); if(!p) die("malloc"); return p; }
static void reserve_spray(size_t need){
    if (need <= spray_cap) return;
    size_t nc = need*2 + 16;
    spray_chunks = (void**)realloc(spray_chunks, nc*sizeof(void*));
    if(!spray_chunks) die("realloc");
    memset(spray_chunks + spray_cap, 0, (nc - spray_cap)*sizeof(void*));
    spray_cap = nc;
}
static void op_spray(int fd, const uint8_t* d, uint32_t n){
    if (n < 8){ respond(fd, 1, "bad args", 8); return; }
    uint32_t chunk = *(uint32_t*)d;
    uint32_t count = *(uint32_t*)(d+4);
    if (chunk == 0 || chunk > (1<<20) || count > (1<<16)){ respond(fd, 6, "bounds", 6); return; }
    if (n != 8 + chunk){ respond(fd, 1, "bad args", 8); return; }
    reserve_spray(spray_count + count);
    const uint8_t* payload = d+8;
    for (uint32_t i=0;i<count;i++){
        void* p = xmalloc(chunk);
        memcpy(p, payload, chunk);
        spray_chunks[spray_count++] = p;
    }
    respond(fd, 0, NULL, 0);
}

static void op_leak(int fd){
    struct { uint64_t a; uint64_t b; } out = { (uint64_t)(uintptr_t)&give_root, (uint64_t)(uintptr_t)&choir_sing };
    respond(fd, 0, &out, sizeof(out));
}

static void op_readflag(int fd){
    if (!is_root){ respond(fd, 13, "eperm", 5); return; }
    FILE* f = fopen("/flag.txt","rb");
    if (!f){ respond(fd, 14, "noflag", 6); return; }
    char buf[512]; size_t m = fread(buf,1,sizeof(buf),f); fclose(f);
    respond(fd, 0, buf, (uint32_t)m);
}

static void handle_client(int cfd){
    while (1){
        uint32_t op, size;
        ssize_t r = read(cfd, &op, 4);
        if (r == 0){ break; }
        if (r != 4){ break; }
        if (read(cfd, &size, 4) != 4) break;
        uint8_t* buf = NULL;
        if (size){
            buf = (uint8_t*)malloc(size);
            if (!buf) break;
            if (read(cfd, buf, size) != (ssize_t)size){ free(buf); break; }
        }
        switch (op){
            case 1: op_create(cfd, buf, size); break;
            case 2: op_free(cfd, buf, size); break;
            case 3: op_setbuf(cfd, buf, size); break;
            case 4: op_trigger(cfd, buf, size); break;
            case 5: op_spray(cfd, buf, size); break;
            case 6: op_leak(cfd); break;
            case 7: op_readflag(cfd); break;
            default: respond(cfd, 0xdead, "bad op", 6); break;
        }
        if (buf) free(buf);
    }
    close(cfd);
}

static int listen_on(const char* host, uint16_t port){
    int s = socket(AF_INET, SOCK_STREAM, 0);
    if (s<0) die("socket");
    int one = 1;
    setsockopt(s, SOL_SOCKET, SO_REUSEADDR, &one, sizeof(one));
    struct sockaddr_in a; memset(&a,0,sizeof(a));
    a.sin_family = AF_INET;
    a.sin_port = htons(port);
    a.sin_addr.s_addr = INADDR_ANY;
    if (bind(s, (struct sockaddr*)&a, sizeof(a))<0) die("bind");
    if (listen(s, 16)<0) die("listen");
    return s;
}

int main(int argc, char** argv){
    if (argc<3){ fprintf(stderr,"usage: %s HOST PORT\n", argv[0]); return 1; }
    signal(SIGPIPE, SIG_IGN);
    uint16_t port = (uint16_t)atoi(argv[2]);
    int s = listen_on(argv[1], port);
    fprintf(stderr, "[choir-invisible] listening on %s:%u\n", argv[1], port);
    while (1){
        int c = accept(s, NULL, NULL);
        if (c<0) continue;
        if (!fork()){
            close(s);
            handle_client(c);
            return 0;
        }
        close(c);
    }
}