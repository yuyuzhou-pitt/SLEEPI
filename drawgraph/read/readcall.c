#include <stdio.h>
#include <unistd.h>
#include <fcntl.h>
 
int readcall(char *filename){
    struct timespec tim;
    tim.tv_sec = 0;
    tim.tv_nsec = 1;

    char buffer[BUFSIZ];
    int filedesc = open(filename, O_RDONLY);
    if(filedesc < 0) return 1;
    //while(read(filedesc,buffer,sizeof(buffer))>0);
    //while(read(filedesc,buffer,sizeof(buffer))>0) nanosleep(&tim, NULL);
    while(read(filedesc,buffer,sizeof(buffer))>0) usleep(1);
    return 0;
}
