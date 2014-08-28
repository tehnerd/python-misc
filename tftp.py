import sys
import select
import socket
import random
import struct



def tftpclient():
    seq = 0
    ltid = random.randint(32100,65535)
    lsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    while 1==1:
        try:
            lsocket.bind(('',ltid))
            break
        except:
            ltid = random.randint(1025,65535)
    lsocket.setblocking(0)
    poller = select.epoll()
    ro = select.EPOLLIN | select.EPOLLPRI | select.EPOLLERR | select.EPOLLHUP
    rw = ro | select.EPOLLOUT
    poller.register(lsocket,rw)
    sock_dict = dict()
    sock_dict[lsocket.fileno()] = lsocket
    SERVER = sys.argv[1]
    RTID = 69
    need_send = 1
    msg = struct.pack("!H",1)
    msg += sys.argv[2]
    msg += struct.pack("!B",0)
    msg += "octet"
    msg += struct.pack("!B",0)
    dst_file = open("/tmp/tftp_test","w")
    run = 1
    while run == 1:
        event = poller.poll()
        for fd,flag in event:
            if fd not in sock_dict:
                pass
            if flag & select.EPOLLOUT:
                if need_send == 1:
                    sock_dict[fd].sendto(msg,(SERVER,RTID))
                    need_send = 0
            if flag & select.EPOLLIN:
                data,dst = sock_dict[fd].recvfrom(9000)
                if RTID != dst[1]:
                    RTID = dst[1]
                header = struct.unpack_from("!HH",data)
                seq = header[1]
                msg = struct.pack("!HH",4,seq)
                need_send = 1
                if len(data) < 516:
                    run = 0
                dst_file.write(data[4:])
    dst_file.close()
    lsocket.close()
    print("exit")

if __name__ == "__main__":
    tftpclient()
                
            

