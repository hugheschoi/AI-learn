#!/usr/bin/env python3
"""Tool Calls 多工具并行示例（对应 ToolCalls.md §6.2）：DeepSeek + weather/time/calculate。"""

import json
import os
import sys
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(override=True)

_ssl_cert = os.getenv("SSL_CERT_FILE")
if _ssl_cert and not os.path.isfile(_ssl_cert):
    os.environ.pop("SSL_CERT_FILE", None)

client = OpenAI(
    api_key=os.environ["OPENAI_API_KEY"],
    base_url=os.getenv("OPENAI_BASE_URL"),
)
MODEL = os.environ["MODEL_ID"]


def get_weather(city: str) -> dict:
    """模拟天气 API。"""
    data = {
        "Beijing": {"temp": 25, "condition": "sunny"},
        "Shanghai": {"temp": 30, "condition": "rainy"},
        "北京": {"temp": 25, "condition": "sunny"},
        "上海": {"temp": 30, "condition": "rainy"},
    }
    return data.get(city, {"temp": "unknown", "condition": "unknown"})


def get_time(tz: str) -> dict:
    """返回指定时区当前时间。"""
    offsets = {
        "Asia/Shanghai": 8,
        "Asia/Hong_Kong": 8,
        "Asia/Beijing": 8,
        "UTC": 0,
    }
    hours = offsets.get(tz, 8)
    now = datetime.now(timezone(timedelta(hours=hours)))
    return {
        "timezone": tz,
        "time": now.strftime("%H:%M:%S"),
        "date": now.strftime("%Y-%m-%d"),
    }


def calculate(expression: str) -> dict:
    """简单四则运算（仅允许数字与 +-*/()）。"""
    allowed = set("0123456789+-*/(). ")
    if not expression or not all(c in allowed for c in expression):
        return {"error": "表达式含非法字符"}
    try:
        result = eval(expression, {"__builtins__": {}}, {})  # noqa: S307
        return {"expression": expression, "result": result}
    except Exception as e:
        return {"error": str(e)}


def _fn_tool(name: str, description: str, properties: dict, required: list[str]) -> dict:
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


weather_tool = _fn_tool(
    "get_weather",
    "查询指定城市的天气。",
    {"city": {"type": "string", "description": "城市名"}},
    ["city"],
)

time_tool = _fn_tool(
    "get_time",
    "查询指定时区的当前时间。",
    {"timezone": {"type": "string", "description": "IANA 时区，如 Asia/Shanghai"}},
    ["timezone"],
)

calculator_tool = _fn_tool(
    "calculate",
    "计算数学表达式。",
    {"expression": {"type": "string", "description": "如 25 * 4 + 10"}},
    ["expression"],
)

TOOLS = [weather_tool, time_tool, calculator_tool]

TOOL_HANDLERS = {
    "get_weather": lambda args: get_weather(args["city"]),
    "get_time": lambda args: get_time(args["timezone"]),
    "calculate": lambda args: calculate(args["expression"]),
}


def handle_multiple_tools(user_query: str) -> str:
    messages = [{"role": "user", "content": user_query}]

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=TOOLS,
        tool_choice="auto",
    )

    assistant_msg = response.choices[0].message

    if not assistant_msg.tool_calls:
        return assistant_msg.content or ""

    messages.append({
        "role": "assistant",
        "content": assistant_msg.content,
        "tool_calls": [
            {
                "id": tc.id,
                "type": tc.type,
                "function": {
                    "name": tc.function.name,
                    "arguments": tc.function.arguments,
                },
            }
            for tc in assistant_msg.tool_calls
        ],
    })

    tool_results = []
    for tool_call in assistant_msg.tool_calls:
        name = tool_call.function.name
        args = json.loads(tool_call.function.arguments or "{}")
        handler = TOOL_HANDLERS.get(name)
        result = handler(args) if handler else {"error": f"Unknown tool: {name}"}
        print(f"  [tool] {name}({args}) -> {result}")

        tool_results.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": json.dumps(result, ensure_ascii=False),
        })

    messages.extend(tool_results)

    final_response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=TOOLS,
    )

    final = final_response.choices[0].message
    if final.tool_calls:
        return final.content or "（模型请求继续调用工具，请再运行一轮）"
    return final.content or ""


if __name__ == "__main__":
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8")

    print(f"多工具并行示例（模型: {MODEL}）")
    print("输入问题，回车发送。直接回车使用默认问题。输入 q 退出。\n")

    default = "北京现在天气怎么样？现在几点了？顺便算一下 25 * 4 + 10"

    while True:
        try:
            query = input(">> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if query.lower() == "q":
            break
        if not query:
            query = default
        print(handle_multiple_tools(query))
        print()
