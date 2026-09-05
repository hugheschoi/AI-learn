# 导入 MCPServer 模块，用于自动处理 initialize 握手（mcp 2.x 中 FastMCP 已改名为 MCPServer）
from mcp.server.mcpserver import MCPServer

# 创建 MCPServer 服务器实例，name 参数会显示在 serverInfo 里
mcp = MCPServer(name="hello-server")

# 使用装饰器注册 greet 工具，初始化时会自动声明 tools 能力
@mcp.tool()
def greet(name: str = "World") -> str:
    # 返回问候语字符串
    return f"Hello, {name}!"

# 判断是否作为主程序运行
if __name__ == "__main__":
    # 以 stdio 模式启动服务器，等待客户端连接
    mcp.run(transport="stdio")
