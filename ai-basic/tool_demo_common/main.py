# 工具调用示例共用：DeepSeek 客户端和三个工具。
"""Tool Calls 示例共用：DeepSeek 客户端 + 三工具。"""

# 导入json模块
import json
# 导入os模块
import os
# 从datetime模块中导入datetime、timedelta和timezone类
from datetime import datetime, timedelta, timezone

# 从dotenv模块导入load_dotenv函数
from dotenv import load_dotenv
# 从openai模块导入OpenAI类
from openai import OpenAI

# 加载环境变量，覆盖已存在变量
load_dotenv(override=True)

# 获取名为SSL_CERT_FILE的环境变量
_ssl_cert = os.getenv("SSL_CERT_FILE")
# 如果环境变量SSL_CERT_FILE存在且指定的文件不存在
if _ssl_cert and not os.path.isfile(_ssl_cert):
    # 从环境变量中移除SSL_CERT_FILE
    os.environ.pop("SSL_CERT_FILE", None)

# 创建OpenAI客户端对象
client = OpenAI(
    api_key=os.environ["OPENAI_API_KEY"],  # 从环境变量获取API密钥
    base_url=os.getenv("OPENAI_BASE_URL"), # 获取基础URL
)
# 获取模型ID
MODEL = os.environ["MODEL_ID"]


# 定义获取天气的函数
def get_weather(city: str) -> dict:
    # 定义城市对应的天气示例数据
    data = {
        "Beijing": {"temp": 25, "condition": "sunny"},
        "Shanghai": {"temp": 30, "condition": "rainy"},
        "北京": {"temp": 25, "condition": "sunny"},
        "上海": {"temp": 30, "condition": "rainy"},
    }
    # 返回对应城市的天气数据，找不到则返回默认值
    return data.get(city, {"temp": "unknown", "condition": "unknown"})


# 定义获取当前时间的函数
def get_time(tz: str) -> dict:
    # 支持的时区与对应的时差
    offsets = {"Asia/Shanghai": 8, "Asia/Hong_Kong": 8, "UTC": 0}
    # 获取时区对应的小时
    hours = offsets.get(tz, 8)
    # 获取当前时区的当前时间
    now = datetime.now(timezone(timedelta(hours=hours)))
    # 返回时区、时间和日期
    return {"timezone": tz, "time": now.strftime("%H:%M:%S"), "date": now.strftime("%Y-%m-%d")}


# 定义计算数学表达式的函数
def calculate(expression: str) -> dict:
    # 允许的字符集合
    allowed = set("0123456789+-*/(). ")
    # 检查表达式是否为空或含有非法字符
    if not expression or not all(c in allowed for c in expression):
        return {"error": "表达式含非法字符"}
    try:
        # 安全地计算表达式的结果
        result = eval(expression, {"__builtins__": {}}, {})  # noqa: S307
        # 返回表达式和结果
        return {"expression": expression, "result": result}
    except Exception as e:
        # 返回错误信息
        return {"error": str(e)}


# 定义函数类型工具的描述函数
def _fn_tool(name: str, description: str, properties: dict, required: list[str]) -> dict:
    # 返回OpenAI工具格式字典
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {"type": "object", "properties": properties, "required": required},
        },
    }


# 工具列表，每个工具都定义了参数和功能描述
available_tools = [
    _fn_tool("get_weather", "查询指定城市的天气。", {"city": {"type": "string"}}, ["city"]),
    _fn_tool("get_time", "查询指定时区当前时间。", {"timezone": {"type": "string"}}, ["timezone"]),
    _fn_tool("calculate", "计算数学表达式。", {"expression": {"type": "string"}}, ["expression"]),
]

# 工具处理函数的映射
TOOL_HANDLERS = {
    "get_weather": lambda args: get_weather(args["city"]),
    "get_time": lambda args: get_time(args["timezone"]),
    "calculate": lambda args: calculate(args["expression"]),
}


# 定义执行工具的函数
def execute_tool(tool_call) -> dict:
    # 获取工具名称
    name = tool_call.function.name
    # 解析工具参数（JSON字符串）
    args = json.loads(tool_call.function.arguments or "{}")
    # 查找工具处理函数
    handler = TOOL_HANDLERS.get(name)
    # 如果找到处理函数则执行，否则返回错误
    if handler:
        return handler(args)
    return {"error": f"Unknown tool: {name}"}


# 定义将assistant消息转为dict的函数
def assistant_dict(message) -> dict:
    # 转为字典并排除None值
    data = message.model_dump(exclude_none=True)
    # 设置角色为assistant
    data["role"] = "assistant"
    # 返回字典数据
    return data


# 定义Windows下标准输出编码重设函数
def setup_stdout():
    # 导入sys模块
    import sys
    # 如果操作系统为Windows，则重新设置标准输出的编码为utf-8
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8")
