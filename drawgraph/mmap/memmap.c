#include <sys/types.h>
#include <sys/mman.h>
#include <err.h>
#include <fcntl.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
 
int mmapcall(int N){
    unsigned int i=0;
    int fd = -1;
    const char str1[] = "string 1";
    char *anon;
    while(i<N){
        anon = (char*)mmap(NULL, 4096, PROT_READ|PROT_WRITE, MAP_ANON|MAP_SHARED, fd, 0);
        if (anon == MAP_FAILED){
            errx(1, "either anon when i=%d", i);
        }
        //strcpy(anon, str1);
        munmap(anon, 4096);
        //usleep(1);
        i++;
    }
    return EXIT_SUCCESS;
}
