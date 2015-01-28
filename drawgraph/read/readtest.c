#include <stdio.h>
#define N 1

int main(void){
    char *filename = "text/dict_10k.txt";
    int i;
    printf("+------------------+\n");
    printf("| READ TEST START  |\n");
    for(i=0;i<N;i++){
        readcall(filename);
    }
    printf("| READ TEST DONE   |\n");
    printf("+------------------+\n");
    return 0;
}
