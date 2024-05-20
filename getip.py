from _socket import gethostbyname

import re


def input_ip():
    ip = input('攻击地址的IP或URL：')
    if re.match(r'(^http)s?://', ip):
        ip = get_ip(ip)

        if not ip:
            print('格式错误！')
            input_ip()
        else:
            return ip

    # 简单判断IP地址格式
    elif not re.match(r'^(\d{1,3}\.){3}\d{1,3}$', ip):
        print('格式错误！')
        ip = input_ip()
    else:
        return ip


def get_ip(url):
    url = url.split('//')[1]
    if '/' in url:
        url = url.split('/')[0]
        ip = gethostbyname(url)
        return ip
    else:
        return False
