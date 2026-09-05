# 导入 json 模块，用于操作 JSON 数据
import json
# 从 mcp.server.fastmcp 中导入 FastMCP 类
from mcp.server.mcpserver import MCPServer

# 实例化 FastMCP 对象，名称为 "resource-demo"
mcp = MCPServer(name="resource-demo")

# 使用 @mcp.resource 装饰器注册资源，指定 URI 和 mime_type
@mcp.resource("config://app", mime_type="application/json")
# 定义 app_config 函数，返回类型为 str
def app_config() -> str:
    # 为该函数添加文档字符串说明，表示为应用配置（静态资源，无参数）
    """应用配置（静态资源，无参数）。"""
    # 将字典转为 JSON 字符串，不转义中文，返回结果
    return json.dumps({"theme": "dark", "lang": "zh-CN"}, ensure_ascii=False)

# 使用 @mcp.resource 装饰器注册模板资源，URI 中 {title} 占位符会传递给函数参数 title，指定返回的内容类型为 text/plain
@mcp.resource("note://{title}", mime_type="text/plain")
# 定义 read_note 函数，接收一个字符串类型的 title 参数，返回一个字符串
def read_note(title: str) -> str:
    # 添加函数文档字符串，说明这是“按标题读取笔记” 
    """按标题读取笔记。"""
    # 返回包含标题和示例内容的字符串，格式化插入 title
    return f"笔记标题：{title}\n内容：这是 MCP 资源示例。"

# 判断当前模块是否为主程序入口
if __name__ == "__main__":
    # 启动 MCP 服务，采用 stdio 作为传输方式
    mcp.run(transport="stdio")