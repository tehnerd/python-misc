import sys
import os
import struct
from string import join
import select
import socket
import re

METAHDRSIZE=24
SBUFFSIZE = 4096

class MetaInfo(object):
    @staticmethod
    def create_meta(fname_source,fname_hs):
        size = os.stat(fname_source).st_size
        try:
            offset = os.stat(fname_hs).st_size
        except:
            offset = 0
        fname = fname_source.split('/')[-1]
        fname_len = len(fname)
        print(fname)
        packed_meta = struct.pack('!QQQ',offset,size,fname_len)
        packed_meta = join((packed_meta,fname),'')
        return packed_meta
    @staticmethod
    def parse_meta(fd_hs,size,meta_dict):
        fd_hs.seek(0)
        while fd_hs.tell() < size:
            meta_packed = fd_hs.read(METAHDRSIZE)
            meta = struct.unpack('!QQQ',meta_packed)
            print(meta)
            fname = fd_hs.read(meta[2])
            meta_dict[fname] = (meta[0],meta[1],meta[2])
            fd_hs.seek(meta[1],os.SEEK_CUR)


class HSTestHandler(object):
    
    def __init__(self,meta_dict,hs_descriptor):
        self.meta_dict = meta_dict
        self.hs_descriptor = hs_descriptor

    def GetHSData(self, msg):
        reply = str()
        for line in msg.split('\n'):
            if re.match("GET (.+)? .*?",line):
                path = re.findall("GET (.+)? .*?",line)[0]
                if path == "/":
                    reply = "HTTP/1.1 200 OK\n\n"
                    for key in self.meta_dict:
                        reply = join((reply,key,'\n'),'')
                    reply = join((reply,'\r\n'),'')
                elif re.search("file=",path):
                    path = path.split("file=")
                    fname = path[1]
                    if fname in self.meta_dict:
                        reply = "HTTP/1.1 200 OK\n\n"
                        if re.match(".*?\.jpg",fname):
                            reply = join((reply[:-1],"Content-Type:image/jpeg\n\n"),'')
                        meta = self.meta_dict[fname]
                        self.hs_descriptor.seek(meta[0]+METAHDRSIZE+meta[2])
                        data = self.hs_descriptor.read(meta[1])
                        reply = join((reply,data,'\r\n'),'')
                    else:
                        reply = "HTTP/1.1 404 NotFound\n\r\n"
                else:
                    reply = "HTTP/1.1 404 NotFound\n\r\n"
                break
        return reply
    
        

        
        
        

def write_to_hs(fd_source,fd_dst,meta):
    fd_dst.write(meta)
    for line in fd_source:
        fd_dst.write(line)


def add_file(fname_source, fname_hs):
    meta = MetaInfo.create_meta(fname_source,fname_hs)
    fd_source = open(fname_source,"rb")
    fd_dst = open(fname_hs,"ab+")
    write_to_hs(fd_source,fd_dst,meta)
    fd_source.close()
    fd_dst.close()


def unregister_sock(sock,poller,sd_dict,msg_dict):
    poller.unregister(sock)
    del sd_dict[sock.fileno()]
    del msg_dict[sock.fileno()]
    sock.close()
    return True

def run_async_server():
    fname_hs = sys.argv[2]
    fd_hs = open(fname_hs,"rb")
    hs_size = os.stat(fname_hs).st_size
    meta_dict = dict()
    MetaInfo.parse_meta(fd_hs,hs_size,meta_dict)
    poller = select.epoll()
    ro = select.EPOLLIN | select.EPOLLERR | select.EPOLLPRI | select.EPOLLHUP
    rw = ro | select.EPOLLOUT
    serv_sd = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    serv_sd.bind(('',8000))
    serv_sd.setblocking(0)
    sd_dict = dict()
    msg_dict = dict()
    sd_dict[serv_sd.fileno()] = serv_sd
    poller.register(serv_sd,ro)
    serv_sd.listen(1000)
    HS = HSTestHandler(meta_dict, fd_hs)
    while True:
        events = poller.poll()
        for fd,flag in events:
            if flag&select.EPOLLIN:
                sock = sd_dict[fd]
                if sock == serv_sd:
                    client,radr = sock.accept()
                    client.setblocking(0)
                    sd_dict[client.fileno()] = client
                    msg_dict[client.fileno()] = str()
                    poller.register(client,ro)
                else:
                    data = sock.recv(SBUFFSIZE)
                    if not data:
                        unregister_sock(sock,poller,sd_dict,msg_dict)
                        continue
                    msg_dict[sock.fileno()]+=data
                    if msg_dict[sock.fileno()][-2:] == '\r\n':
                        msg_dict[sock.fileno()]=HS.GetHSData(msg_dict[sock.fileno()])
                        poller.modify(sock,rw)
            if flag&select.EPOLLOUT:
                sock = sd_dict[fd]
                sock.send(msg_dict[sock.fileno()])
                unregister_sock(sock,poller,sd_dict,msg_dict)

    


def main():
    if sys.argv[1] == "add":
        fname_source = sys.argv[2]
        fname_hs = sys.argv[3]
        add_file(fname_source,fname_hs)
    if sys.argv[1] == "start":
        run_async_server()


if __name__ == "__main__":
    main()
