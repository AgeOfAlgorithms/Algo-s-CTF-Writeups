/* exp300-2-default.c */

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <signal.h>
#include <string.h>

static void timeout_handler(int sig)
{
    puts("Timout message.");
    exit(0);
}

static void bootstrap(void)
{
    alarm(60);
    signal(SIGALRM, timeout_handler);

    setvbuf(stdin,  NULL, _IONBF, 0);
    setvbuf(stdout, NULL, _IONBF, 0);
    setvbuf(stderr, NULL, _IONBF, 0);

    chdir(getenv("HOME"));
}

static int read_int(void)
{
    int x=0;
    if (scanf("%d", &x) != 1) x = -1;
    while (getchar() != '\n');
    return x;
}

static void read_line(char *buf, int len)
{
    int i;
    int ch;
    for (i = 0; i < len && (ch = getchar()) != '\n' && ch != EOF; ++i) {
        buf[i] = (char)ch;
    }
    buf[i] = '\0';
}

int main(void)
{
    char *notes[16] = {0};
    char *filepath = NULL;
    int choice, idx, i, size;

    bootstrap();

    puts("Salutation\n");

    while (1) {
        puts("Menu question");
        puts("  (1) Make");
        puts("  (2) Delete");
        puts("  (3) Filename");
        puts("  (4) cat");
        printf("Pick one: ");
        choice = read_int();

        switch (choice) {
            case 1:
                for (i = 0; i < 16 && notes[i]; ++i);
                if (i >= 16) { puts("No space."); break; }

                printf("Size (bytes): ");
                size = read_int();
                if (size <= 0 || size > 0x1000) { puts("Too big."); break; }

                notes[i] = malloc(size);
                if (!notes[i]) { puts("Failed."); exit(1); }

                printf("Write: ");
                read_line(notes[i], size + 1);
                printf("Saved as note #%d.\n", i);
                break;

            case 2:
                printf("Note ID to delete: ");
                idx = read_int();
                if (idx < 0 || idx >= 16 || notes[idx] == NULL) { puts("Invalid id."); }
                else { free(notes[idx]); notes[idx] = NULL; puts("Freed."); }
                break;

            case 3:
                filepath = strdup("not_the_flag.txt");
                if (!filepath) exit(1);
                puts("Filename set.");
                break;

            case 4:
                if (!filepath) { puts("File not set."); break; }
                puts("Retrieved.");
                execl("/usr/bin/cat", "cat", filepath, NULL);
                perror("execl failed");
                exit(1);
                break;

            default:
                puts("Invalid option.");
                break;
        }
    }
    return 0;
}
