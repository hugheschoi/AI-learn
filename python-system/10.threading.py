"""
import threading
import time

# 定义工作函数，接收线程名和延迟秒数
def worker(name, delay):
    # 打印线程开始信息
    print(f"线程 {name} 开始")
    # 模拟耗时操作
    time.sleep(delay)
    # 打印线程结束信息
    print(f"线程 {name} 结束")

# 创建线程 A，目标函数为 worker，参数为 ("A", 2)
t1 = threading.Thread(target=worker, args=("A", 2))
# 创建线程 B，延迟 1 秒
t2 = threading.Thread(target=worker, args=("B", 1))
# 启动线程 A
t1.start()
# 启动线程 B
t2.start()
# 等待线程 A 结束
t1.join()
# 等待线程 B 结束
t2.join()
# 所有子线程完成后打印提示
print("所有线程已完成")
"""
"""
# 导入 threading 模块
import threading
counter = 0
lock = threading.Lock()
# 定义自增函数，使用锁保证线程安全
def increment():
    global counter
    for _ in range(100_000):
        # 获取锁，确保同一时间只有一个线程修改 counter
        with lock:
            counter += 1
# 创建 10 个线程执行 increment
threads = [threading.Thread(target=increment) for _ in range(10)]
# 启动所有线程
for t in threads:
    t.start()
# 等待所有线程完成
for t in threads:
    t.join()
# 打印最终计数值
print(f"最终计数值: {counter}") # 1000_000 ，如果没有锁，可能会小于 1000_000
"""

import threading
import time
import queue

# 创建线程安全队列
q = queue.Queue()

# 生产者：向队列放入 5 条数据
def producer():
    for i in range(5):
        # 放入数据
        q.put(f"数据-{i}")
        # 模拟生产间隔
        time.sleep(1)
    # 放入 None 作为结束信号
    q.put(None)

# 消费者：从队列取数据并处理
def consumer():
    while True:
        # 阻塞等待获取数据
        item = q.get()
        # 收到结束信号则退出循环
        if item is None:
            break
        # 打印消费的数据
        print(f"消费 {item}")


# 启动生产者线程
threading.Thread(target=producer).start()
# 启动消费者线程
threading.Thread(target=consumer).start()