#include <sys/types.h> // size_t, pthread_attr_t, time_t http://pubs.opengroup.org/onlinepubs/009695399/basedefs/sys/types.h.html
#include <sys/mman.h> //PROT_READ, MAP_ANON, MAP_SHARED, MAP_FIXED, MAP_FAILED
#include <fcntl.h> // file control options, open, fcntl
#include <err.h> // errx (exit if error) http://man7.org/linux/man-pages/man3/err.3.html
#include <stdio.h> // fopen, fclose, fseek, fprintf, getc, putc
#include <stdlib.h> // EXIT_SUCCESS, atoi, exit, free, malloc, rand, qsort, random
#include <unistd.h> // read, write, lseek, fork, sleep, usleep
 
int mmapcall(int N){
    size_t len = 4096; // page size

    int fd = -1; // anonymous mapping
    char *anon;

    char *addr = NULL;
    /* initial mapping address */
    addr = (char*)mmap(addr, len, PROT_READ, MAP_ANON|MAP_SHARED, fd, 0);
    printf("addr=%p.\n", addr);

    unsigned int i=0;
    while(i<N){
        /* allocate memory by using the same address with flag MAP_FIXED, 
         * to avoid using up memory */
        anon = (char*)mmap(addr, len, PROT_READ, MAP_ANON|MAP_SHARED|MAP_FIXED, fd, 0);
        if (anon == MAP_FAILED){
            errx(1, "either anon when i=%d", i);
        }
        /* sleep 1 us, to avoid using up cpu (usage ~= 50%). 
         * Use 'mpstat -P ALL 1' to check each CPU usage */
        //usleep(1);
        i++;
    }
    munmap(anon, len);
    return EXIT_SUCCESS;
}
