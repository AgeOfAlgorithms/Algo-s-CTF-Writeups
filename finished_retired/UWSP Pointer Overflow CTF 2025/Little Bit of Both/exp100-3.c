 /*
  * Finger server.
  */
  // gcc -O0 -fno-stack-protector -no-pie -z execstack -o exp100-3 exp100-3.c
 #include <sys/types.h>
 #include <sys/wait.h>
 #include <netinet/in.h>
 
 #include <stdio.h>
 #include <ctype.h>
 #include <stdlib.h>
 #include <unistd.h>
 
#include <signal.h>

void sig_handler(int signum) {

	printf("Timeout\n");
	exit(0);

}

void init() {

	alarm(60);
	signal(SIGALRM, sig_handler);

	setvbuf(stdin, NULL, _IONBF, 0);
	setvbuf(stdout, NULL, _IONBF, 0);
	setvbuf(stderr, NULL, _IONBF, 0);

	chdir(getenv("HOME"));

}
 
 int fatal(char *prog, char *s)
 {
 
     fprintf(stderr, "%s: ", prog);
     perror(s);
     exit(1);
 }

 int main(int argc, char *argv[])
 {
     register char *sp;
     char line[512];
 //    struct sockaddr sin;
     int i, p[2], pid, status;
     FILE *fp;
     char *av[4];
 
     init();
 
 //    i = sizeof (sin);
 //    if (getpeername(0, &sin, &i) < 0)
 //        fatal(argv[0], "getpeername");
     printf("-<>-<>-\n");
     line[0] = '\0';
     gets(line);
     sp = line;
     av[0] = "finger";
     i = 1;
     while (1) {
         while (isspace(*sp))
             sp++;
         if (!*sp)
             break;
         if (*sp == '/' && (sp[1] == 'W' || sp[1] == 'w')) {
             sp += 2;
             av[i++] = "-l";
         }
         if (*sp && !isspace(*sp)) {
             av[i++] = sp;
             while (*sp && !isspace(*sp))
                 sp++;
             *sp = '\0';
         }
     }
     av[i] = 0;
     if (pipe(p) < 0)
         fatal(argv[0], "pipe");
     if ((pid = fork()) == 0) {
         close(p[0]);
         if (p[1] != 1) {
             dup2(p[1], 1);
             close(p[1]);
         }
         execv("/usr/bin/finger", av);
         _exit(1);
     }
     if (pid == -1)
         fatal(argv[0], "fork");
     close(p[1]);
     if ((fp = fdopen(p[0], "r")) == NULL)
         fatal(argv[0], "fdopen");
     while ((i = getc(fp)) != EOF) {
         if (i == '\n')
             putchar('\r');
         putchar(i);
     }
     fclose(fp);
     while ((i = wait(&status)) != pid && i != -1)
         ;
     return(0);
 }
