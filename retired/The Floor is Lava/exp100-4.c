#include <stdio.h>
#include <stdlib.h>

void win(void){
    FILE *f=fopen("/flag","r");
    if(f){ char buf[256]; if(fgets(buf,sizeof buf,f)) printf("FLAG: %s\n",buf); fclose(f); }
    fflush(stdout);
}

int main(void){
    /* unbuffered so banners show up over TCP immediately */
    setvbuf(stdout, NULL, _IONBF, 0);

    char buf[64];
    puts("Welcome to the Floor Is Lava training program.");
    puts("Give me one line of input and I'll echo it back.");
    printf("> ");

    if(!fgets(buf, 512, stdin)) return 0;   /* intentional overflow for training */
    printf("You said: %s", buf);
    return 0;
}/* floor_is_lava.c
 * Very small vulnerable program for teaching stack smashing basics.
 * Compile with: gcc -o floor_is_lava floor_is_lava.c -fno-stack-protector -z execstack -no-pie
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

void win(void) {
    /* For remote deployments, read /flag and print it.
       For local testing you can set FLAG environment variable or
       create /flag file containing the flag. */
    FILE *f = fopen("/flag", "r");
    if (f) {
        char buf[256];
        if (fgets(buf, sizeof buf, f)) {
            printf("FLAG: %s\n", buf);
        } else {
            puts("FLAG file empty");
        }
        fclose(f);
    } else {
        /* fallback message for local practice */
        puts("You reached win()! (no /flag found)");
    }
    fflush(stdout);
}

int main(void) {
    setvbuf(stdout, NULL, _IONBF, 0);
    char buf[64];

    /* Ensure stdout is line-buffered even if not a tty (so prompts are visible over sockets). */

    puts("Welcome to the Floor Is Lava training program.");
    puts("Give me one line of input and I'll echo it back.");
    printf("> ");
    fflush(stdout);

    /* intentionally unsafe read for teaching */
    if (fgets(buf, 512, stdin) == NULL) {
        return 0;
    }

    printf("You said: ");
    printf("%s\n", buf);
    return 0;
}
