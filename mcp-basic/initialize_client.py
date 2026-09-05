
# 官方客户端 API 是异步的
import asyncio
# 导入操作系统相关的模块，用于处理文件路径等
import os
# 导入系统相关的模块，用于获取解释器路径等
import sys

# 导入会话类和子进程启动参数，用于与服务器通信
from mcp import ClientSession, StdioServerParameters
# 导入 stdio 传输模块，用于通过标准输入输出连接服务器
from mcp.client.stdio import stdio_client


# 定义主异步函数
async def main() -> None:
    # 获取当前文件所在目录的绝对路径
    base_dir = os.path.dirname(os.path.abspath(__file__))
    # 拼接服务器脚本的完整路径
    server_path = os.path.join(base_dir, "initialize_server.py")

    # 配置服务器子进程启动参数
    server_params = StdioServerParameters(
        # 指定 Python 解释器的路径
        command=sys.executable,
        # 指定启动的服务器脚本
        args=[server_path],
    )

    # 建立 stdio 连接并自动启动子进程
    async with stdio_client(server_params) as (read, write):
        # 创建会话对象，与服务器进行通信
        async with ClientSession(read, write) as session:
            # ★ 进行初始化握手，必须最先调用
            result = await session.initialize()

            # 初始化成功后，输出协商得到的信息（mcp 2.x 字段为 snake_case）
            print("协议版本:", result.protocol_version)
            # 判断服务器信息是否存在，存在就输出名称，否则输出“未知”
            print("服务器名称:", result.server_info.name if result.server_info else "未知")

            # 初始化完成后，可以调用业务接口
            tools = await session.list_tools()
            # 输出获取到的工具列表名称
            print("工具列表:", [t.name for t in tools.tools])


# 如果当前模块为主程序则执行 main
if __name__ == "__main__":
    asyncio.run(main())