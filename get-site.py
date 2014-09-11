import select
import socket
from string import join
import sys

RECVSIZE  = 9000
CRLF = '\r\n'

def main():
    raddr_list = socket.getaddrinfo(sys.argv[1],80,
                                   socket.AF_UNSPEC, socket.SOCK_STREAM)
    for raddr in raddr_list:
        sd = socket.socket(raddr[0],raddr[1])
        try:
            sd.connect((sys.argv[1],80))
        except:
            continue
        print(raddr)
        get_data(sd,sys.argv[1])
        break


def get_data(sd, host):
    sd.setblocking(0)
    sd_dict = dict()
    sd_dict[sd.fileno()] = sd
    poller = select.epoll()
    ro = select.EPOLLIN
    rw = ro | select.EPOLLOUT
    poller.register(sd,rw)
    run = 1
    request = join(('GET / HTTP/1.1\n',
                    'Host:',host,'\n',
                    'User-Agent:Chromium\n',
                    'Connection: close\n',
                    CRLF),'')
    while run == 1:
        event = poller.poll()
        for fd,flag in event:
            if flag & select.EPOLLIN:
                data = sd_dict[fd].recv(RECVSIZE)
                if not data:
                    poller.unregister(sd_dict[fd])
                    sd_dict[fd].close()
                    del sd_dict[fd]
                    run  = 0
                else:
                    print(data)
            if flag& select.EPOLLOUT:
                sd_dict[fd].send(request)
                poller.modify(sd_dict[fd],ro)
                        
                
if __name__ == "__main__":
    main() 
    
        
