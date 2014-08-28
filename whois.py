import sys
import select
import socket
from string import join


def get_whois_data(query,dst):
    sd = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sd_dict = dict()
    sd_dict[sd.fileno()] = sd
    poller = select.epoll()
    ro = select.EPOLLIN | select.EPOLLPRI | select.EPOLLERR | select.EPOLLHUP
    rw = ro | select.EPOLLOUT
    sd.connect((dst,43))
    sd.setblocking(0)
    poller.register(sd,rw)
    query = join((query,'\n'),'')
    run = 1
    data = str()
    while run == 1:
        event = poller.poll()
        for fd,flag in event:
            if flag & select.EPOLLOUT:
                sd.send(query)
                poller.modify(sd,ro)
            if flag & select.EPOLLIN:
                buf = sd_dict[fd].recv(9000)
                if not buf:
                    run = 0
                    continue
                else:
                    data+=buf
    sd.close()
    return data 
            

def whois_main():
    query = sys.argv[1]
    dst = sys.argv[2]
    data = get_whois_data(query,dst)
    print(data)
    exit(0)


if __name__ == "__main__":
    whois_main()
