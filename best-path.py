import sys
from string import join

def ip2int(v4fmt):
    ip = 0
    for cntr in xrange(0,4):
        ip += (int(v4fmt[cntr])<<(24-8*cntr))
    return ip

def int2ip(ip_int):
    ip = list()
    for cntr in xrange(0,4):
        octet = (ip_int[0]>>(24-8*cntr))&((1<<8)-1)
        ip.append(octet)
    ip_str = join((str(ip[0]),'.',
                   str(ip[1]),'.',
                   str(ip[2]),'.',
                   str(ip[3])),'')
    return (ip_str,ip_int[1])
    

def gen_dict(rdict,fd):
    #file with route's format: x.x.x.x/x
    for line in fd:
        line = line.split('/')
        mask = int(line[1])
        v4fmt = line[0].split('.')
        net = ip2int(v4fmt)
        rdict[net] = mask

def best_match(rdict,ip):
    ip_int = ip2int(ip.split('.'))
    match_dict = dict()
    for key in rdict:
        if key == ip_int&(((1<<32)-1)>>(32-rdict[key])<<(32-rdict[key])):
            match_dict[key] = rdict[key]
    print(match_dict)
    if len(match_dict) > 0:
        ans = sorted(match_dict.items(),key=lambda x:x[1])[-1]
    else:
        print("not found")
        exit(0)
    bmatch = int2ip(ans)
    print("for %s best route is %s/%s"%(ip,bmatch[0],bmatch[1]))

def main():
    fd = open(sys.argv[1],"r")
    ip = sys.argv[2]
    rdict = dict()
    gen_dict(rdict,fd)
    fd.close()
    best_match(rdict,ip)

if __name__ == "__main__":
    main()
    
    
