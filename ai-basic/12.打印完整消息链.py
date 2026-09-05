# 指定使用 Python 3 解释器
#!/usr/bin/env python3
# 模块文档：Tool Calls 第 8.1 节打印完整消息链
"""Tool Calls §8.1：打印完整消息链。"""

# 导入 json 模块
import json

# 从共用模块导入所需组件
from tool_demo_common import (
    MODEL,
    assistant_dict,
    available_tools,
    client,
    execute_tool,
    setup_stdout,
)


# 定义调试函数：格式化打印 messages 列表
def debug_messages(messages: list):
    # 打印分隔线
    print("=" * 50)
    # 打印标题
    print("MESSAGE CHAIN:")
    # 遍历每条消息及其索引
    for i, msg in enumerate(messages):
        # 打印序号与 role
        print(f"\n[{i}] Role: {msg['role']}")
        # 若有 content 则打印前 100 字符
        if msg.get("content"):
            text = str(msg["content"])
            print(f"    Content: {text[:100]}{'...' if len(text) > 100 else ''}")
        # 若有 tool_calls 则打印数量与详情
        if msg.get("tool_calls"):
            print(f"    Tool Calls: {len(msg['tool_calls'])}")
            for tc in msg["tool_calls"]:
                name = tc["function"]["name"]
                print(f"        - {name} ({tc['id']})")
        # 若是 tool 消息则打印 tool_call_id
        if msg.get("tool_call_id"):
            print(f"    Tool Call ID: {msg['tool_call_id']}")
    # 打印结束分隔线
    print("=" * 50)


# 定义主流程
def run(user_query: str) -> str:
    # 初始化 messages
    messages = [{"role": "user", "content": user_query}]

    # 第一次 LLM 调用
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=available_tools,
        tool_choice="auto",
    )
    assistant_msg = response.choices[0].message

    # 无 tool_calls：打印当前链并返回
    if not assistant_msg.tool_calls:
        debug_messages(messages)
        return assistant_msg.content or ""

    # 追加 assistant 消息
    messages.append(assistant_dict(assistant_msg))

    # 逐个同步执行工具
    for tool_call in assistant_msg.tool_calls:
        result = execute_tool(tool_call)
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": json.dumps(result, ensure_ascii=False),
        })

    # 工具执行后打印完整消息链（调试用）
    debug_messages(messages)

    # 第二次 LLM 调用获取最终回答
    final = client.chat.completions.create(
        model=MODEL, messages=messages, tools=available_tools,
    )
    return final.choices[0].message.content or ""


# 脚本直接运行
if __name__ == "__main__":
    setup_stdout()
    print(f"打印完整消息链（模型: {MODEL}）")
    print("输入问题，回车发送。直接回车使用默认问题。输入 q 退出。\n")

    default = "北京的天气怎么样？"

    while True:
        try:
            query = input(">> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if query.lower() == "q":
            break
        if not query:
            query = default
        print(run(query))
        print()
