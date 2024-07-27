import socket
import threading
import time

# 代理服务器监听地址和端口
PROXY_IP = "0.0.0.0"  # 监听所有网卡接口
PROXY_PORT = 8080

# 目标服务器地址和端口
TARGET_IP = "127.0.0.1"
TARGET_PORT = 80

# 记录已经处理过的客户端 IP 地址
processed_clients = set()

# 记录每个 IP 地址的请求时间戳和请求数
ip_requests = {}


def handle_client(client_socket, client_address):
    global processed_clients

    # 如果是已经处理过的客户端 IP，则放行
    if client_address[0] in processed_clients:
        print(f"Processing client {client_address}...")
    else:
        # 将客户端 IP 添加到已处理集合中，并丢弃该连接
        processed_clients.add(client_address[0])
        print(f"Discarding first SYN packet from client {client_address}")
        client_socket.close()
        return

    # 如果该 IP 地址在一秒内发送超过 200 个请求，则加入黑名单
    if client_address[0] in ip_requests:
        current_time = time.time()
        request_timestamps = ip_requests[client_address[0]]
        request_timestamps.append(current_time)
        # 清除一秒前的请求时间戳
        request_timestamps = [timestamp for timestamp in request_timestamps if current_time - timestamp <= 1]
        ip_requests[client_address[0]] = request_timestamps
        if len(request_timestamps) > 200:
            print(f"IP address {client_address[0]} exceeded request limit, adding to blacklist...")
            # 加入黑名单
            # 简单地输出提示信息
            print(f"IP address {client_address[0]} added to blacklist!")
            return

    # 建立到目标服务器的连接
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.connect((TARGET_IP, TARGET_PORT))

        # 接收来自客户端的数据
        request_data = client_socket.recv(4096)

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
