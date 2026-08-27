"""
# ThreadPoolExecutor
from concurrent.futures import ThreadPoolExecutor
import time

def fetch(url):
  time.sleep(2)  # 模拟网络请求延迟
  return f"Fetched {url}"

urls = ["https://www.example.com", "https://www.example.org", "https://www.example.net"]
with ThreadPoolExecutor(max_workers=3) as executor:
  # map 批量提交，按输入顺序返回结果
    for result in executor.map(fetch, urls):
        print(result)
"""
"""
# 导入进程池执行器
from concurrent.futures import ProcessPoolExecutor
# 导入 math 用于开方计算
import math

# 判断一个数是否为质数
def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(math.sqrt(n)) + 1):
        if n % i == 0:
            return False
    return True

# 待检测的大整数列表
numbers = [112272535095293, 112582705942171]

# Windows 上进程池必须放在 main 保护块内
if __name__ == "__main__":
    # 创建进程池并批量计算
    with ProcessPoolExecutor() as executor:
        results = list(executor.map(is_prime, numbers))
    # 打印数字与是否为质数的对应关系
    print(list(zip(numbers, results)))
"""
"""
from concurrent.futures import ThreadPoolExecutor, as_completed

# 安全除法函数
def safe_divide(x, y):
    return x / y

# 四组除法任务，其中一组除数为零
tasks = [(10, 2), (20, 4), (30, 0), (40, 5)]

with ThreadPoolExecutor() as executor:
    # 提交所有任务，用字典关联 Future 与原始参数
    futures = {executor.submit(safe_divide, x, y): (x, y) for x, y in tasks}
    # 按完成顺序处理
    for future in as_completed(futures):
        x, y = futures[future]
        try:
            print(f"{x}/{y} = {future.result()}")
        except ZeroDivisionError:
            print(f"{x}/{y} = 错误：除数为零")
"""
# 导入线程池和 as_completed
from concurrent.futures import ThreadPoolExecutor, as_completed
# 导入 time 计时
import time
# 导入 random 模拟随机耗时
import random

# 模拟下载函数
def download(url, file_id):
    # 随机等待 0.5~1.5 秒
    time.sleep(random.uniform(0.5, 1.5))
    # 返回文件信息字典
    return {"file_id": file_id, "url": url, "size": random.randint(100, 1000)}

# 5 个待下载文件 (url, id)
files = [(f"http://example.com/f{i}.zip", i) for i in range(1, 6)]
# 记录开始时间
start = time.time()

# 最多 3 个并发下载
with ThreadPoolExecutor(max_workers=3) as executor:
    # 提交所有下载任务
    futures = {executor.submit(download, url, fid): fid for url, fid in files}
    # 按完成顺序处理结果
    for future in as_completed(futures):
        fid = futures[future]
        try:
            r = future.result()
            print(f"文件 {r['file_id']} 完成，{r['size']} KB")
        except Exception as e:
            print(f"文件 {fid} 失败: {e}")

# 打印总耗时
print(f"总耗时: {time.time() - start:.2f} 秒")