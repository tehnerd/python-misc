import sys
import os
import struct
from string import join


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
            meta_packed = fd_hs.read(24)
            meta = struct.unpack('!QQQ',meta_packed)
            print(meta)
            fname = fd_hs.read(meta[2])
            meta_dict[fname] = (meta[0],meta[1])
            fd_hs.seek(meta[1],os.SEEK_CUR)
        
        
        

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


def main():
    if sys.argv[1] == "add":
        fname_source = sys.argv[2]
        fname_hs = sys.argv[3]
        add_file(fname_source,fname_hs)
    if sys.argv[1] == "start":
        fname_hs = sys.argv[2]
        fd_hs = open(fname_hs,"r")
        hs_size = os.stat(fname_hs).st_size
        meta_dict = dict()
        MetaInfo.parse_meta(fd_hs,hs_size,meta_dict)
        print(meta_dict)
        fd_hs.close()


if __name__ == "__main__":
    main()
