# 导入 os 模块，用于后面拼接子进程脚本路径
import os
# 导入 subprocess 模块, 用于创建子进程以及操作标准输入输出管道
import subprocess
# 导入 sys 模块, 用于获取当前 Python 解释器路径
import sys

# 获取当前脚本文件的所在目录
base_dir = os.path.dirname(os.path.abspath(__file__))
# 拼接得到子进程要运行的脚本的完整路径
child_path = os.path.join(base_dir, "stdio_child.py")

# 创建子进程对象，启动子进程并设置参数
proc = subprocess.Popen(
    # 指定用当前的 Python 解释器来运行目标子进程脚本
    [sys.executable, child_path],
    # 把子进程的标准输入设置为管道，父子进程之间可通信
    stdin=subprocess.PIPE,
    # 把子进程的标准输出设置为管道
    stdout=subprocess.PIPE,
    # 子进程的标准错误输出继承父进程（直接显示在终端），便于输出日志
    stderr=None,
    # 文本模式，直接用字符串读写，而不是字节
    text=True,
    # 指定使用 utf-8 编码，避免 Windows 下中文乱码
    encoding="utf-8",
)

# 要发送给子进程的消息内容
request = "你好，子进程"
# 在父进程终端打印发送的消息内容
print(f"[父进程] 发送: {request}")
# 把消息写入到子进程的标准输入，需要加换行符以便子进程读取完整一行
proc.stdin.write(request + "\n")
# 刷新标准输入管道，确保消息及时发送到子进程
proc.stdin.flush()
# 从子进程的标准输出读取一行并去除字符串首尾空白字符
response = proc.stdout.readline().strip()

# 在父进程终端输出接收到的子进程回应
print(f"[父进程] 收到: {response}")

# 关闭父进程到子进程标准输入的写入端，让子进程检测到 EOF 并退出
proc.stdin.close()
# 等待子进程退出，最多等待 3 秒
proc.wait(timeout=3)
