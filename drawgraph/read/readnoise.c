#include <stdio.h>
#define N 8
int main(void){
    char *filename = "text/Hacker_Crackdown_1k.txt";
    int i;
    printf("+------------------+\n");
    printf("+ READ NOISE START +\n");
    for(i=0;i<N;i++){
        readcall(filename);
    }
    printf("+ READ NOISE DONE  +\n");
    printf("+------------------+\n");
    return 0;
}
