import socket
import threading
import time
import subprocess

# 代理服务器监听地址和端口
# 监听所有网卡接口
PROXY_IP = "0.0.0.0"
PROXY_PORT = 8080

# 目标服务器地址和端口
TARGET_IP = "127.0.0.1"
TARGET_PORT = 80

# 记录已经处理过的客户端 IP 地址
processed_clients = set()

# 记录每个 IP 地址的请求时间戳和请求数
ip_requests = {}

# ICMP 协议号
ICMP_PROTOCOL = 1


def is_client_processed(client_address):
    """检查客户端是否已经处理过"""
    return client_address[0] in processed_clients



def process_new_client(client_address):
    """处理新的客户端"""
    processed_clients.add(client_address[0])
    print(f"Discarding first packet from client {client_address}")



def add_to_blacklist(ip_address):
    """将 IP 地址加入黑名单"""
    # 使用 iptables 将 IP 地址加入黑名单
    command = ["sudo", "iptables", "-A", "INPUT", "-s", ip_address, "-j", "DROP"]
    try:
        # 执行命令
        subprocess.run(command, check=True)
        # 提示信息
        print(f"IP address {ip_address} added to blacklist!")
    except subprocess.CalledProcessError as e:
        # 返回错误信息
        print(f"Error adding {ip_address} to blacklist:", e)



def is_request_limit_exceeded(ip_address):
    """检查请求是否超过限制"""
    if ip_address in ip_requests:
        current_time = time.time()
        request_timestamps = ip_requests[ip_address]
        request_timestamps.append(current_time)
        # 清除一秒前的请求时间戳
        request_timestamps = [timestamp for timestamp in request_timestamps if current_time - timestamp <= 1]
        ip_requests[ip_address] = request_timestamps
        return len(request_timestamps) > 200
    else:
        ip_requests[ip_address] = [time.time()]
        return False



def handle_client(client_socket, client_address):
    """处理客户端请求"""
    if is_client_processed(client_address):
        print(f"Processing client {client_address}...")
    else:
        process_new_client(client_address)
        client_socket.close()
        return

    if is_request_limit_exceeded(client_address[0]):
        print(f"IP address {client_address[0]} exceeded request limit, adding to blacklist...")
        add_to_blacklist(client_address[0])
        return

    # 处理 ICMP 和 TCP 请求
    process_packet(client_socket, client_address)



def process_packet(client_socket, client_address):
    """处理客户端发送的数据包"""
    data, addr = client_socket.recvfrom(4096)

    # 判断是否为 ICMP 报文
    ip_header = data[:20]  # Assuming IPv4
    ip_version = ip_header[0] >> 4
    protocol = ip_header[9]
    if ip_version == 4 and protocol == ICMP_PROTOCOL:
        # 如果是 ICMP 报文，丢弃
        print("Discarding ICMP packet from client", client_address)
        client_socket.close()
        return

    # 处理 TCP 请求
    process_tcp_request(client_socket, client_address, data)



def process_tcp_request(client_socket, client_address, request_data):
    """处理 TCP 请求"""
    # 建立到目标服务器的连接
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.connect((TARGET_IP, TARGET_PORT))

        # 发送客户端的数据到目标服务器
        server_socket.sendall(request_data)

        # 接收来自目标服务器的响应数据
        response_data = server_socket.recv(4096)

    # 将目标服务器的响应数据发送给客户端
    client_socket.sendall(response_data)

    # 关闭连接
    client_socket.close()



def main():
    # 创建监听套接字
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((PROXY_IP, PROXY_PORT))
        server_socket.listen(5)
        print(f"Proxy server is listening on {PROXY_IP}:{PROXY_PORT}")

        while True:
            # 接受客户端连接
            client_socket, client_address = server_socket.accept()
            print(f"Accepted connection from {client_address}")

            # 创建线程处理客户端请求
            client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
            client_thread.start()



if __name__ == "__main__":
    main()
