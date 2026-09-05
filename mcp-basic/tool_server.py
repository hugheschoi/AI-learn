# 导入json库，用于进行JSON格式的数据编码和解码
import json
# 从mcp.server.fastmcp模块导入FastMCP类，用于创建MCP服务器
from mcp.server.mcpserver import MCPServer

# 创建一个FastMCP服务器实例，服务器名称为"weather-server"
mcp = MCPServer(name="weather-server")

# 使用mcp.tool装饰器注册天气查询工具
@mcp.tool(name="search_city_weather", description="根据城市名查询实时天气")
# 定义get_weather函数，入参为城市名，返回类型为字符串
def get_weather(city: str) -> str:
    # 函数文档字符串，描述该工具的用途
    """查询指定城市的当前天气。"""
    # 构建包含城市、温度和天气状况的字典数据
    data = {"city": city, "temp": "22°C", "condition": "晴"}
    # 将字典数据转换为JSON字符串并返回，确保中文字符正常显示
    return json.dumps(data, ensure_ascii=False)

# 如果当前模块作为主程序运行，则启动服务器
if __name__ == "__main__":
    # 启动MCP服务器，指定传输方式为stdio（标准输入输出）
    mcp.run(transport="stdio")