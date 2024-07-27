import psutil
import matplotlib.pyplot as plt
import time

# 初始化图表数据
cpu_usage = []
memory_usage = []
net_sent = []
net_recv = []
syn_recv_count = []

# 设置监控时长和时间间隔
duration = 120  # 秒
interval = 0.1  # 秒
num_intervals = int(duration / interval)  # 计算总的间隔数

start_time = time.time()
last_net_counters = psutil.net_io_counters()  # 存储初始的网络I/O计数

# 循环收集数据直到达到监控时长
for i in range(num_intervals):
    # 收集CPU使用率
    cpu_usage.append(psutil.cpu_percent(interval=False))

    # 收集内存使用率
    memory_usage.append(psutil.virtual_memory().percent)


    # 等待一段时间，然后继续下一个数据点的收集
    time.sleep(interval)

    # 收集网络I/O数据
    net_counters = psutil.net_io_counters()
    bytes_sent = net_counters.bytes_sent - last_net_counters.bytes_sent
    bytes_recv = net_counters.bytes_recv - last_net_counters.bytes_recv
    # 将字节转换为KB
    net_sent.append(bytes_sent / interval / 1024)
    net_recv.append(bytes_recv / interval / 1024)
    last_net_counters = net_counters  # 更新最后的计数

    # 收集SYN-RECEIVED状态的TCP连接数量
    syn_recv_connections = [conn for conn in psutil.net_connections() if conn.status == 'SYN-RECEIVED']
    syn_recv_count.append(len(syn_recv_connections))

# 由于最后一个间隔没有绘制，我们需要添加最终的CPU和内存使用率数据点
cpu_usage.append(psutil.cpu_percent(interval=False))
memory_usage.append(psutil.virtual_memory().percent)

# 使用默认主题样式
plt.style.use('default')

# 绘制CPU使用率图表
plt.figure(figsize=(14, 7))
plt.plot(cpu_usage, label='CPU Usage %')
plt.xlabel('Time (millisecond)')
plt.ylabel('CPU Usage (%)')
plt.title('CPU Usage Over Time')
plt.legend()
plt.grid(True)

# 保存图表为文件
plt.savefig('cpu_usage_over_time.png')

# 绘制内存使用率图表
plt.figure(figsize=(14, 7))
plt.plot(memory_usage, label='Memory Usage %')
plt.xlabel('Time (millisecond)')
plt.ylabel('Memory Usage (%)')
plt.title('Memory Usage Over Time')
plt.legend()
plt.grid(True)
plt.savefig('memory_usage_over_time.png')

# 绘制网络I/O图表
plt.figure(figsize=(14, 7))
plt.plot(net_sent, label='Network Sent (KB/s)', color='red')
plt.plot(net_recv, label='Network Received (KB/s)', color='orange')
plt.xlabel('Time (millisecond)')
plt.ylabel('Network I/O (KB/second)')
plt.title('Network I/O Over Time')
plt.legend()
plt.grid(True)
plt.savefig('network_io_over_time.png')

# 绘制SYN-RECEIVED状态的TCP连接数量图表
plt.figure(figsize=(14, 7))
plt.plot(syn_recv_count, label='SYN-RECEIVED Connections', color='purple')
plt.xlabel('Time (millisecond)')
plt.ylabel('Number of SYN-RECEIVED Connections')
plt.title('SYN-RECEIVED Connections Over Time')
plt.legend()
plt.grid(True)
plt.savefig('ssyn_received_connections_over_time.png')