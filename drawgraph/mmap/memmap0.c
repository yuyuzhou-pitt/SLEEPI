#include <sys/types.h>
#include <sys/mman.h>
#include <err.h>
#include <fcntl.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#define N 60000
 
int mmapcall(void){
    unsigned int i=0;
    int fd = -1;
    const char str1[] = "string 1";
    char *anon[N];
    int len = 4096;
    
    while(i<N){
        anon[i] = (char*)mmap(NULL, len, PROT_READ|PROT_WRITE, MAP_ANON|MAP_SHARED, fd, 0);
        if (anon[i] == MAP_FAILED){
            errx(1, "either anon when i=%d", i);
        }
        //strcpy(anon, str1);
        //munmap(anon, len);
        //usleep(1);
        i++;
    }
    i = 0;
    while(i<N){
        munmap(anon[i], len);
        i++;
    }
    return EXIT_SUCCESS;
}
