# 导入操作系统相关模块
import os
# 导入与Python解释器交互的sys模块
import sys
# 导入异步IO模块
import asyncio

# mcp 2.x：会话与 stdio 参数从 mcp 导入，传输从 mcp.client.stdio 导入
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# 定义主异步函数
async def main():
    # 获取当前文件所在的目录路径
    base_dir = os.path.dirname(os.path.abspath(__file__))
    # 拼接得到服务端脚本的完整路径
    server_path = os.path.join(base_dir, "tool_server.py")
    # 创建StdioServerParameters对象，指定Python解释器和服务端脚本路径
    server_params = StdioServerParameters(
        command=sys.executable,
        args=[server_path],
    )

    # 使用stdio_client建立与服务端的异步通信，获取读写流
    async with stdio_client(server_params) as (read, write):
        # 创建客户端会话对象
        async with ClientSession(read, write) as session:
            # 初始化会话（必须先调用）
            await session.initialize()
            # 异步调用名为 search_city_weather 的工具，传入参数 {"city": "杭州"}
            result = await session.call_tool("search_city_weather", {"city": "杭州"})
            # 遍历返回结果内容中的每一个block
            for block in result.content:
                # 判断block对象是否有"text"属性
                if hasattr(block, "text"):
                    # 打印每个结果文本
                    print(block.text)
            # search_city_weather 示例返回: {"city": "杭州", "temp": "22°C", "condition": "晴"}

# 判断当前脚本是否作为主模块运行
if __name__ == "__main__":
    # 运行异步主函数
    asyncio.run(main())