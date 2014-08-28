import sys
import select
import socket
from string import join
import re


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


def asn_from_asset(as_set,as_list,as_set_dict,dst):
    query = join(("-T as-set ",as_set),'')
    data = get_whois_data(query,dst)
    for line in data.split('\n'):
            if re.match("members:\s+(.*)",line):
                line = line.split()
                if len(line) < 2:
                    print("error")
                    continue
                for cntr in xrange(1,len(line)):
                    as_obj = line[cntr]
                    if re.search("AS-",as_obj):
                        if as_obj not in as_set_dict:
                            as_set_dict[as_obj] = 1
                            asn_from_asset(as_obj,as_list,as_set_dict,dst)
                    else:
                        as_list.append(as_obj)

def route_for_asn(asn,route_dict,dst):
    query = join(("-T route -i origin ",asn),'')
    data = get_whois_data(query,dst)
    for line in data.split('\n'):
        if re.match("route:\s+(.*)",line):
            line = line.split()
            if len(line)!=2:
                print("error")
                continue
                
            if line[1] not in route_dict:
                route_dict[line[1]] = 1


#query ripe db for all the routes in particular as-set
def whois_routes():
    as_set = sys.argv[1]
    dst = sys.argv[2]
    as_list = list()
    as_set_dict = dict()
    route_dict = dict()
    asn_from_asset(as_set,as_list,as_set_dict,dst)
    for asn in as_list:
        route_for_asn(asn,route_dict,dst)
    for route in route_dict:
        print(route)
    exit(0)   


if __name__ == "__main__":
    whois_routes()
