import socket
import ipaddress
import threading
from queue import Queue

# 定义线程数
NUM_THREADS = 200

# 定义队列
queue = Queue()

# 本地IP
LOCAL_IP = socket.gethostbyname(socket.gethostname())


# 扫描端口函数
def scan_port(ip, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex((str(ip), port))
        if result == 0:
            print(f"Port {port} is open on {ip}\t")
        sock.close()
    except socket.error:
        pass


def worker():
    while True:
        ip, port = queue.get()
        scan_port(ip, port)
        queue.task_done()


def main():
    target = input("输入要扫描的IP或网段: ")
    ports = input("输入要扫描的端口范围 (e.g., 1-1000，使用默认策略输入0): ")

    # 解析 IP 地址或网段
    try:
        network = ipaddress.ip_network(target)
        ips = [str(ip) for ip in network.hosts()]
    except ValueError:
        ips = [target]

    # 解析端口范围
    if ports == '0':
        # 处理端口范围扫描
        # 创建线程
        for _ in range(NUM_THREADS):
            t = threading.Thread(target=worker)
            t.daemon = True
            t.start()

        # 定义常用服务端口列表
        ports_default = [21, 22, 23, 25, 53, 80, 443, 3306, 8080, 8081, 8888]
        for ip in ips:
            for port in ports_default:
                queue.put((ip, port))

        # 等待所有任务完成
        queue.join()

    elif '-' in ports:
        # 处理端口范围扫描
        start_port, end_port = map(int, ports.split('-'))
        # 创建线程
        for _ in range(NUM_THREADS):
            t = threading.Thread(target=worker)
            t.daemon = True
            t.start()

        # 将任务放入队列
        for ip in ips:
            for port in range(start_port, end_port + 1):
                queue.put((ip, port))

        # 等待所有任务完成
        queue.join()

    else:
        # 处理单个端口扫描
        port = int(ports)
        for ip in ips:
            scan_port(ip, port)


if __name__ == '__main__':
    main()
