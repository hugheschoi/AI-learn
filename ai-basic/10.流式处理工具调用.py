# 指定使用 Python 3 解释器
#!/usr/bin/env python3
# 模块文档：Tool Calls 第 7.4 节流式处理工具调用
"""Tool Calls §7.4：流式处理工具调用。"""

# 导入 json 模块
import json

# 从共用模块导入客户端与工具
from tool_demo_common import (
    MODEL,
    available_tools,
    client,
    execute_tool,
    setup_stdout,
)


# 定义函数：合并流式响应中分片的 tool_calls
def _merge_stream_tool_calls(chunks: list) -> list[dict]:
    # 函数说明
    """合并流式 delta 中的 tool_calls 片段。"""
    # 按 index 累积每个 tool_call 的片段
    acc: dict[int, dict] = {}
    # 遍历每个 delta 中的 tool_call 片段
    for tc in chunks:
        # 获取片段所属的 tool_call 序号
        idx = tc.index
        # 若该序号尚未初始化
        if idx not in acc:
            # 创建空的 tool_call 结构
            acc[idx] = {"id": "", "type": "function", "function": {"name": "", "arguments": ""}}
        # 若本片段带有 id 则更新
        if tc.id:
            acc[idx]["id"] = tc.id
        # 若本片段带有 function 字段
        if tc.function:
            # 累加 function.name 片段
            if tc.function.name:
                acc[idx]["function"]["name"] += tc.function.name
            # 累加 function.arguments 片段
            if tc.function.arguments:
                acc[idx]["function"]["arguments"] += tc.function.arguments
    # 按 index 排序后返回完整 tool_calls 列表
    return [acc[i] for i in sorted(acc)]


# 定义主流程：流式 API 收集 tool_calls 并执行
def stream_with_tools(user_query: str) -> str:
    # 初始化 messages
    messages = [{"role": "user", "content": user_query}]

    # 开启流式 completions 请求
    stream = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=available_tools,
        tool_choice="auto",
        stream=True,
    )

    # 收集 tool_call 分片
    delta_tool_chunks = []
    # 收集 assistant 文本分片
    text_parts = []

    # 逐 chunk 消费流
    for chunk in stream:
        # 跳过无 choices 的空 chunk
        if not chunk.choices:
            continue
        # 取 delta 对象
        delta = chunk.choices[0].delta
        # 若有文本增量则追加
        if delta.content:
            text_parts.append(delta.content)
        # 若有 tool_calls 增量则追加
        if delta.tool_calls:
            delta_tool_chunks.extend(delta.tool_calls)

    # 若收集到流式文本则打印预览
    if text_parts:
        print("  [stream text]", "".join(text_parts)[:80])

    # 合并分片为完整 tool_calls
    merged = _merge_stream_tool_calls(delta_tool_chunks)
    # 若无 tool_calls 则直接返回文本
    if not merged:
        return "".join(text_parts) or ""

    # 打印合并后的 tool_call 数量
    print(f"  [stream] 收集到 {len(merged)} 个 tool_call")

    # 构造 assistant 消息并追加（含 tool_calls）
    messages.append({
        "role": "assistant",
        "content": "".join(text_parts) or None,
        "tool_calls": merged,
    })

    # 逐个执行合并后的 tool_call
    for tc in merged:
        # 定义简易对象模拟 SDK 的 tool_call 结构
        class _TC:
            pass
        # 创建实例
        obj = _TC()
        # 设置 id
        obj.id = tc["id"]
        # 动态构造 function 属性
        obj.function = type("F", (), {"name": tc["function"]["name"], "arguments": tc["function"]["arguments"]})()
        # 执行工具
        result = execute_tool(obj)
        # 打印执行结果
        print(f"  [tool] {tc['function']['name']} -> {result}")
        # 追加 tool 消息
        messages.append({
            "role": "tool",
            "tool_call_id": tc["id"],
            "content": json.dumps(result, ensure_ascii=False),
        })

    # 非流式第二次调用，获取最终回答
    final = client.chat.completions.create(
        model=MODEL, messages=messages, tools=available_tools,
    )
    # 返回最终文本
    return final.choices[0].message.content or ""


# 脚本直接运行
if __name__ == "__main__":
    setup_stdout()
    print(f"流式工具调用（模型: {MODEL}）")
    print("输入问题，回车发送。直接回车使用默认问题。输入 q 退出。\n")

    default = "北京现在天气怎么样？现在几点了？"

    while True:
        try:
            query = input(">> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if query.lower() == "q":
            break
        if not query:
            query = default
        print(stream_with_tools(query))
        print()
