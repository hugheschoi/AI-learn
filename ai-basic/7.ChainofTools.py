# 指定使用 Python 3 解释器
#!/usr/bin/env python3
# 模块文档：Tool Calls 第 7.1 节工具调用链（多轮循环）
"""Tool Calls 工具调用链示例（对应 ToolCalls.md §7.1）：DeepSeek + 多轮循环。"""

# 导入 json 模块
import json
# 导入 os 模块
import os
# 导入 sys 模块
import sys
# 导入 datetime 相关类
from datetime import datetime, timedelta, timezone

# 导入 dotenv 加载环境变量
from dotenv import load_dotenv
# 导入 OpenAI 客户端
from openai import OpenAI

# 加载 .env 文件
load_dotenv(override=True)

# 读取 SSL 证书路径环境变量
_ssl_cert = os.getenv("SSL_CERT_FILE")
# 若证书路径无效则从环境中移除
if _ssl_cert and not os.path.isfile(_ssl_cert):
    os.environ.pop("SSL_CERT_FILE", None)

# 创建 OpenAI 客户端（DeepSeek 兼容接口）
client = OpenAI(
    api_key=os.environ["OPENAI_API_KEY"],
    base_url=os.getenv("OPENAI_BASE_URL"),
)
# 从环境变量读取模型 ID
MODEL = os.environ["MODEL_ID"]
# 工具调用链最大循环轮数
MAX_ITERATIONS = 5


# 定义模拟天气查询函数
def get_weather(city: str) -> dict:
    # 函数说明
    """模拟天气 API。"""
    # 预设城市天气数据
    data = {
        "Beijing": {"temp": 25, "condition": "sunny"},
        "Shanghai": {"temp": 30, "condition": "rainy"},
        "北京": {"temp": 25, "condition": "sunny"},
        "上海": {"temp": 30, "condition": "rainy"},
    }
    # 返回对应城市数据，未知城市返回 unknown
    return data.get(city, {"temp": "unknown", "condition": "unknown"})


# 定义获取指定时区时间的函数
def get_time(tz: str) -> dict:
    # 函数说明
    """返回指定时区当前时间。"""
    # 常用时区相对 UTC 的小时偏移
    offsets = {
        "Asia/Shanghai": 8,
        "Asia/Hong_Kong": 8,
        "Asia/Beijing": 8,
        "UTC": 0,
    }
    # 取偏移，默认东八区
    hours = offsets.get(tz, 8)
    # 构造带时区的当前时间
    now = datetime.now(timezone(timedelta(hours=hours)))
    # 返回时区、时分秒、日期
    return {
        "timezone": tz,
        "time": now.strftime("%H:%M:%S"),
        "date": now.strftime("%Y-%m-%d"),
    }


# 定义简单四则运算函数
def calculate(expression: str) -> dict:
    # 函数说明
    """简单四则运算。"""
    # 允许的字符集合
    allowed = set("0123456789+-*/(). ")
    # 表达式为空或含非法字符则报错
    if not expression or not all(c in allowed for c in expression):
        return {"error": "表达式含非法字符"}
    # 尝试 eval 计算
    try:
        result = eval(expression, {"__builtins__": {}}, {})  # noqa: S307
        return {"expression": expression, "result": result}
    # 捕获计算异常
    except Exception as e:
        return {"error": str(e)}


# 定义 OpenAI tools schema 构造辅助函数
def _fn_tool(name: str, description: str, properties: dict, required: list[str]) -> dict:
    # 返回标准 function tool 描述 dict
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required,
            },
        },
    }


# 注册三个可用工具 schema
available_tools = [
    _fn_tool(
        "get_weather",
        "查询指定城市的天气。",
        {"city": {"type": "string", "description": "城市名"}},
        ["city"],
    ),
    _fn_tool(
        "get_time",
        "查询指定时区的当前时间。",
        {"timezone": {"type": "string", "description": "IANA 时区，如 Asia/Shanghai"}},
        ["timezone"],
    ),
    _fn_tool(
        "calculate",
        "计算数学表达式。",
        {"expression": {"type": "string", "description": "如 25 * 4 + 10"}},
        ["expression"],
    ),
]

# 工具名到实现函数的映射
TOOL_HANDLERS = {
    "get_weather": lambda args: get_weather(args["city"]),
    "get_time": lambda args: get_time(args["timezone"]),
    "calculate": lambda args: calculate(args["expression"]),
}


# 执行单个 tool_call
def execute_tool(tool_call) -> dict:
    # 函数说明
    """执行单次 tool_call，返回 dict 结果。"""
    # 读取工具名
    name = tool_call.function.name
    # 解析 JSON 参数字符串
    args = json.loads(tool_call.function.arguments or "{}")
    # 查找处理函数
    handler = TOOL_HANDLERS.get(name)
    # 若存在则调用
    if handler:
        return handler(args)
    # 未知工具返回错误 dict
    return {"error": f"Unknown tool: {name}"}


# 将 SDK Message 转为可序列化的 assistant dict
def _assistant_message_dict(message) -> dict:
    # 导出 message 字段，忽略 None
    data = message.model_dump(exclude_none=True)
    # 显式设置 role
    data["role"] = "assistant"
    return data


# 工具调用链主函数：多轮直到无 tool_calls 或达上限
def chain_tool_calls(user_query: str) -> str:
    # 初始化 messages
    messages = [{"role": "user", "content": user_query}]

    # 最多循环 MAX_ITERATIONS 轮
    for i in range(1, MAX_ITERATIONS + 1):
        # 打印当前轮次
        print(f"\n--- 第 {i} 轮 ---")
        # 调用 LLM
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=available_tools,
            tool_choice="auto",
        )

        # 取出 assistant 消息
        assistant_msg = response.choices[0].message

        # 无 tool_calls 则返回最终文本
        if not assistant_msg.tool_calls:
            return assistant_msg.content or ""

        # 追加 assistant 消息到 history
        messages.append(_assistant_message_dict(assistant_msg))

        # 执行本轮所有 tool_calls
        for tool_call in assistant_msg.tool_calls:
            result = execute_tool(tool_call)
            print(f"  [tool] {tool_call.function.name} -> {result}")
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result, ensure_ascii=False),
            })

    # 超过最大轮数则返回提示
    return "Max iterations reached"


# 脚本直接运行
if __name__ == "__main__":
    # Windows 下配置 UTF-8 输出
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8")

    # 打印说明
    print(f"工具调用链示例（模型: {MODEL}，最多 {MAX_ITERATIONS} 轮）")
    print("输入问题，回车发送。直接回车使用默认问题。输入 q 退出。\n")

    # 默认问题：需多轮链式调用（天气 → 计算 → 时间）
    default = (
        "先查北京的天气；如果温度高于 20，就计算 25 * 4 + 10，"
        "否则计算 10 + 10；最后告诉我现在北京时间"
    )

    # 交互主循环
    while True:
        try:
            query = input(">> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if query.lower() == "q":
            break
        if not query:
            query = default
        print(chain_tool_calls(query))
        print()
