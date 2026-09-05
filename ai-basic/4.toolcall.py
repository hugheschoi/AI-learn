# 指定 Python 解释器路径
#!/usr/bin/env python3
# 文件文档字符串，说明功能
"""Tool Calls 最小示例：DeepSeek + 天气/时间工具。"""

# 导入 json 模块，用于处理 JSON 数据
import json
# 导入 os 模块，用于操作环境变量和文件
import os
# 导入 sys 模块，用于操作系统交互
import sys
# 导入 datetime、timedelta、timezone 类，用于处理时间和时区
from datetime import datetime, timedelta, timezone

# 从 dotenv 模块导入 load_dotenv，用于加载环境变量
from dotenv import load_dotenv
# 从 openai 模块导入 OpenAI 类
from openai import OpenAI

# 加载 .env 文件中的环境变量（覆盖已有变量）
load_dotenv(override=True)

# 创建 OpenAI 客户端对象，使用环境变量中的 API_KEY 和 BASE_URL
client = OpenAI(
    api_key=os.environ["OPENAI_API_KEY"],
    base_url=os.getenv("OPENAI_BASE_URL"),
)
# 获取模型 ID
MODEL = os.environ["MODEL_ID"]


# 定义用于获取天气的函数，参数为城市名，返回字典
def get_weather(city: str) -> dict:
    # 模拟天气 API。
    """模拟天气 API。"""
    # 定义静态天气数据
    data = {
        "Beijing": {"temp": 25, "condition": "sunny", "unit": "celsius"},
        "Shanghai": {"temp": 30, "condition": "rainy", "unit": "celsius"},
        "北京": {"temp": 25, "condition": "sunny", "unit": "celsius"},
        "上海": {"temp": 30, "condition": "rainy", "unit": "celsius"},
    }
    # 根据城市名返回对应天气信息，若无则返回默认 unknown
    return data.get(city, {"temp": "unknown", "condition": "unknown", "unit": "celsius"})


# 定义用于获取时间的函数，参数为时区名，返回字典
def get_time(tz: str) -> dict:
    # 返回指定时区当前时间（固定 UTC 偏移，无需 tzdata）。
    """返回指定时区当前时间（固定 UTC 偏移，无需 tzdata）。"""
    # 定义部分时区的时差
    offsets = {
        "Asia/Shanghai": 8,
        "Asia/Hong_Kong": 8,
        "Asia/Beijing": 8,
        "UTC": 0,
    }
    # 获取该时区对应的小时偏移，默认为8
    hours = offsets.get(tz, 8)
    # 获取本地时间，并设置为指定时区
    now = datetime.now(timezone(timedelta(hours=hours)))
    # 返回当前时区、时间、日期信息
    return {
        "timezone": tz,
        "time": now.strftime("%H:%M:%S"),
        "date": now.strftime("%Y-%m-%d"),
    }


# 定义函数，用于构建 tools 需要的 function 调用描述
def _fn_tool(name: str, description: str, properties: dict, required: list[str]) -> dict:
    # 返回符合 OpenAI tool schema 的结构
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


# 构建 get_weather 工具的 schema
get_weather_tool = _fn_tool(
    "get_weather",
    "查询指定城市的天气。",
    {"city": {"type": "string", "description": "城市名，如 Beijing 或 北京"}},
    ["city"],
)

# 构建 get_time 工具的 schema
get_time_tool = _fn_tool(
    "get_time",
    "查询指定时区的当前时间。",
    {"timezone": {"type": "string", "description": "IANA 时区，如 Asia/Shanghai"}},
    ["timezone"],
)

# 定义全部可用工具
TOOLS = [get_weather_tool, get_time_tool]

# 定义工具回调函数字典，将工具名映射到 Lambda 处理方法
TOOL_HANDLERS = {
    "get_weather": lambda args: get_weather(args["city"]),
    "get_time": lambda args: get_time(args["timezone"]),
}


# 定义主流程函数，处理用户输入并调用 tool
def process_with_tools(user_query: str) -> str:
    # 构造初始 Messages，将用户输入内容加入
    messages = [{"role": "user", "content": user_query}]

    # 调用 OpenAI 接口获得初步 assistant 消息，可包含 tool_calls
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=TOOLS,
        tool_choice="auto",
    )

    # 取出第一条 assistant 响应
    assistant_message = response.choices[0].message
    print('assistant_message', assistant_message)

    # 如果没有建议调用工具则直接返回内容
    if not assistant_message.tool_calls:
        return assistant_message.content or ""

    # 否则，将 assistant 的 tool 调用信息追加入 messages
    messages.append({
        "role": "assistant",
        "content": assistant_message.content,
        "tool_calls": [
            {
                "id": tc.id,
                "type": tc.type,
                "function": {
                    "name": tc.function.name,
                    "arguments": tc.function.arguments,
                },
            }
            for tc in assistant_message.tool_calls
        ],
    })

    # 对于 assistant 请求调用的每个工具，逐一执行
    for tool_call in assistant_message.tool_calls:
        # 获取工具名
        name = tool_call.function.name
        # 解析参数（JSON 格式字符串）
        args = json.loads(tool_call.function.arguments or "{}")
        # 根据名字获取对应的处理回调
        handler = TOOL_HANDLERS.get(name)
        # 执行回调获取结果，若找不到工具则报错
        result = handler(args) if handler else {"error": f"Unknown tool: {name}"}
        # 打印调试信息
        print(f"  [tool] {name}({args}) -> {result}")

        # 把工具返回的结果加入 messages 供下一步模型使用
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": json.dumps(result, ensure_ascii=False),
        })
    print('messages', messages)
    # 工具结果返回后，再次发起请求让 assistant 总结输出
    final_response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=TOOLS,
    )

    # 获取最终响应
    final = final_response.choices[0].message
    # 如果还要调用工具，提示需要多运行一轮
    if final.tool_calls:
        return final.content or "（模型请求继续调用工具，请再运行一轮）"
    # 否则直接返回 assistant 文本内容
    return final.content or ""


# 如果作为主程序执行
if __name__ == "__main__":
    # 如果是 Windows 平台，需要将标准输出编码设为 utf-8
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8")
    # 打印模型和用法说明
    print(f"Tool Calls 示例（模型: {MODEL}）")
    print("输入问题，回车发送。输入 q 退出。\n")

    # 进入主循环，持续获取用户输入
    while True:
        try:
            # 获取用户输入，去掉首尾空白字符
            query = input(">> ").strip()
        except (EOFError, KeyboardInterrupt):
            # 捕捉 Ctrl+C、Ctrl+D 退出
            break
        # 如果用户输入 q 或 exit 或空则退出
        if query.lower() in ("q", "exit", ""):
            break
        # 处理用户输入并输出结果
        print(process_with_tools(query))
        # 打印空行分隔
        print()
