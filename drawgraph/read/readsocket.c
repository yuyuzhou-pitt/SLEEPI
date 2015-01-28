#include <sys/types.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <string.h>
#include <stdio.h>

#define NAME "socket_name" /*define the name of the socket*/

int main(){
struct	sockaddr_un local;
int	sk;
int     i;
char	buf[BUFSIZ];

sk=socket(AF_UNIX,SOCK_DGRAM,0);

local.sun_family=AF_UNIX;        /* Define the socket domain    */
strcpy(local.sun_path,NAME);     /* Define the socket name      */
bind(sk,(struct sockaddr *)&local,strlen(NAME)+2); /* Bind the name to the socket */

read(sk,buf,BUFSIZ);

printf("%s\n",buf);

unlink(NAME);
close(sk);

return 0;
}
