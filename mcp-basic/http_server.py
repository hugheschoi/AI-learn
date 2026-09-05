# 导入 FastMCP 类
from mcp.server.mcpserver import MCPServer

# 创建一个 FastMCP 服务器实例，名称为 "http-demo"
mcp = MCPServer(
    # 指定服务器名称
    name="http-demo",
)

# 将下面的函数注册为工具，可通过 HTTP 被调用
@mcp.tool()
# 定义一个加法工具函数，用于测试 HTTP 模式的调用功能
def add(a: int, b: int) -> str:
    # 返回两个参数相加后的字符串结果
    return str(a + b)

# 程序主入口，使用 streamable-http 作为数据传输方式（不再使用 stdin/stdout）
if __name__ == "__main__":
    # 启动 FastMCP 服务器，使用 streamable-http 传输
    mcp.run(transport="streamable-http")