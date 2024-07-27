import os
import socket
import subprocess
import threading
import time
import concurrent.futures
from scapy.layers.inet import IP, TCP
from scapy.sendrecv import send


# 本地IP地址
LOCALIP = os.system("/sbin/ifconfig ens33 | grep \"inet\" | awk '/inet / { print $2 }' | cut -d: -f2")

# 单个用户最大每秒请求数量
BLACKLIST_THRESHOLD = 200

# 存储每个 IP 地址的 SYN 计数和最后一个 SYN 时间
ip_syn_count = {}
ip_last_syn_time = {}

# 存储每个 IP 地址的连接信息
ip_connection_info = {}


# 用于加入 IP 到黑名单的函数
def add_to_blacklist(ip):
    print(f"Adding {ip} to blacklist")
    # 添加 IP 到 iptables 黑名单
    subprocess.run(["sudo", "iptables", "-A", "INPUT", "-s", ip, "-j", "DROP"])
    # 删除存储的信息
    del ip_syn_count[ip]
    del ip_last_syn_time[ip]
    del ip_connection_info[ip]


# 处理接收到的数据包的函数
def handle_packet(data, source_port,host):
    global ip_syn_count, ip_last_syn_time

    # 检查是否是客户端发送的请求数据包
    if source_port != 80:
        # 检查是否是第一次收到该IP数据包
        if host not in ip_syn_count:
            ip_syn_count[host] = 1
            ip_last_syn_time[host] = time.time()
        else:
            # 计算客户端数据包发送频率
            current_time = time.time()
            if current_time - ip_last_syn_time[host] <= 1:
                ip_syn_count[host] += 1
                # 检查数据包发送频率是否超过阈值
                if ip_syn_count[host] >= BLACKLIST_THRESHOLD:
                    add_to_blacklist(host)
            else:
                ip_syn_count[host] += 1
            ip_last_syn_time[host] = current_time

        # 判断是否要丢弃数据包或转发到 80 端口
        if ip_syn_count.get(host, 0) > 1:
            # 转发数据包到 80 端口
            forward_packet_to_80(data)

    # 如果是来自 80 端口的响应数据包，转发回客户端
    else:
        forward_response(data, ip_connection_info[host])


# 转发数据包到 80 端口的函数
def forward_packet_to_80(data):
    target_host = 'localhost'
    target_port = 80
    # 创建套接字并连接到目标主机
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((target_host, target_port))
        # 发送数据包到目标主机
        s.sendall(data)


# 转发向客户端响应的报文的函数
def forward_response(data, target_address):
    # 源地址信息
    src_ip = LOCALIP
    src_port = 80
    # 目的地址信息
    dst_ip = target_address[0]
    dst_port = target_address[1]

    # 使用scapy库转发数据包
    pkg = (IP(dst=dst_ip,src=src_ip)/TCP(dport=dst_port,sport=src_port)/data)
    send(pkg)



# 监听 8080 端口的函数
def listen_to_8080():
    host = '0.0.0.0'
    port = 8080
    # 创建监听套接字
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen(1)
        print(f"Listening on port {port}...")
        while True:
            conn, addr = s.accept()
            with conn:
                data = conn.recv(1024)
                if data:
                    # 记录连接信息
                    name = addr[0]
                    if name is LOCALIP:
                        name += threading.get_ident()
                    ip_connection_info[name] = (addr[0], addr[1])
                    handle_packet(data, addr[1], name)


# 用于监控线程池中的线程数量
def monitor():
    # 创建一个线程池，最大线程数为500
    max_threads = 500
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_threads)

    # 提交一些初始任务到线程池中
    initial_tasks = 10
    for _ in range(initial_tasks):
        executor.submit(listen_to_8080)

    while True:
        num_threads = len(executor._threads)
        # 如果线程数量少于500个，补充新线程
        if num_threads < max_threads:
            num_new_threads = max_threads - num_threads
            for _ in range(num_new_threads):
                executor.submit(listen_to_8080)
        # 等待一段时间再次检查
        time.sleep(5)


if __name__ == '__main__':
    # 启动监控线程
    monitor_thread = threading.Thread(target=monitor)
    monitor_thread.start()

    # 阻塞主线程
    monitor_thread.join()