import sys
import os
import struct
from string import join
import BaseHTTPServer
import urlparse

METAHDRSIZE=24

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
            meta_dict[fname] = (meta[0],meta[1],meta[2])
            fd_hs.seek(meta[1],os.SEEK_CUR)


class RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse.urlparse(self.path)
        params = urlparse.parse_qs(parsed_path.query)
        try:
            requested_pic = params.get('file')[0]
        except:
            return
        fname_hs = sys.argv[2]
        fd_hs = open(fname_hs,"r")
        hs_size = os.stat(fname_hs).st_size
        meta_dict = dict()
        MetaInfo.parse_meta(fd_hs,hs_size,meta_dict)
        if requested_pic in meta_dict:
            response_code = 200
            self.send_response(response_code)
            meta = meta_dict[requested_pic]
            fd_hs.seek(meta[0]+METAHDRSIZE+meta[2])
            message = fd_hs.read(meta[1])
            self.end_headers()
            self.wfile.write(message)
            fd_hs.close()
        else:
            fd_hs.close()
            response_code = 400
            self.send_response(response_code)
            self.end_headers()
        return

        

        
        
        

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

def run_server(server_class=BaseHTTPServer.HTTPServer,
        handler_class=RequestHandler):
    server_address = ('', 8000)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()


def main():
    if sys.argv[1] == "add":
        fname_source = sys.argv[2]
        fname_hs = sys.argv[3]
        add_file(fname_source,fname_hs)
    if sys.argv[1] == "start":
        run_server()


if __name__ == "__main__":
    main()
