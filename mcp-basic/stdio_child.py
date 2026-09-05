# 导入 sys 模块，用来访问标准输入输出和错误
import sys

# 使用一个无限循环，持续处理父进程传来的请求
while True:
    # 从标准输入读取一行数据；如果父进程没写会阻塞等待
    line = sys.stdin.readline()
    # 如果读取到空字符串，表示输入流被关闭，子进程需退出
    if not line:
        break
    # 去除收到数据的首尾空白字符，并存入 message 变量
    message = line.strip()
    # 如果处理后字符串为空（如仅输入回车），则跳过本次循环
    if not message:
        continue
    # 向标准错误输出打印调试信息（确保协议数据不会干扰）
    print(f"[子进程] 收到: {message}", file=sys.stderr)
    # 构造一条回复消息，表示已收到父进程发来的内容
    reply = f"子进程回复: 已收到「{message}」"
    # 将回复消息写入标准输出，父进程可以读取
    sys.stdout.write(reply + "\n")
    # 刷新标准输出缓冲区，确保消息及时发送到父进程
    sys.stdout.flush()
