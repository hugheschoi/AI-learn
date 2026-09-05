# 导入异步IO库 asyncio
import asyncio

# 从官方 SDK 导入客户端会话类 ClientSession
from mcp import ClientSession

# 从官方 SDK 导入基于 Streamable HTTP 的上下文管理器
from mcp.client.streamable_http import streamable_http_client

# 设置 HTTP 服务器地址（需与服务器实际 host/port/path 对应）
SERVER_URL = "http://127.0.0.1:8000/mcp"

# 定义异步主函数
async def main() -> None:
    # 使用 streamable_http_client 创建 (read, write) 二元组的异步上下文
    async with streamable_http_client(SERVER_URL) as (read, write):
        # 在异步上下文中创建客户端会话 session
        async with ClientSession(read, write) as session:
            # 第一步：异步初始化，与服务器进行握手
            await session.initialize()

            # 第二步：异步获取工具列表
            tools = await session.list_tools()
            # 打印工具名称列表
            print("工具列表:", [t.name for t in tools.tools])

            # 第三步：异步调用 add 工具，传入参数 a=3, b=5
            result = await session.call_tool("add", {"a": 3, "b": 5})
            # 遍历结果内容中的每个 block
            for block in result.content:
                # 如果 block 有 text 属性，则打印返回结果
                if hasattr(block, "text"):
                    print("调用结果:", block.text)


# 判断当前模块是否被直接运行
if __name__ == "__main__":
    # 运行异步主函数
    asyncio.run(main()) 