# 指定使用 Python 3 解释器
#!/usr/bin/env python3
# 模块文档：Tool Calls 第 7.2 节并行工具执行
"""Tool Calls §7.2：并行工具执行优化。"""

# 导入 json 模块
import json
# 导入线程池，用于并行执行多个工具
from concurrent.futures import ThreadPoolExecutor

# 从共用模块导入客户端、工具列表等
from tool_demo_common import (
    MODEL,
    assistant_dict,
    available_tools,
    client,
    execute_tool,
    setup_stdout,
)


# 定义并行执行多个 tool_call 的函数
def execute_tools_parallel(tool_calls) -> list[dict]:
    # 创建最多 5 个工作线程的线程池
    with ThreadPoolExecutor(max_workers=5) as executor:
        # 为每个 tool_call 提交异步任务，保存 (id, future) 对
        futures = [(tc.id, executor.submit(execute_tool, tc)) for tc in tool_calls]
        # 存放最终 tool 消息列表
        results = []
        # 按提交顺序等待每个 future 完成
        for tool_call_id, future in futures:
            # 阻塞获取工具执行结果
            result = future.result()
            # 构造符合 API 的 tool 消息
            results.append({
                "role": "tool",
                "tool_call_id": tool_call_id,
                "content": json.dumps(result, ensure_ascii=False),
            })
        # 返回全部 tool 消息
        return results


# 定义主流程：用户提问 → 并行工具 → 最终回答
def run(user_query: str) -> str:
    # 初始化消息列表，加入用户消息
    messages = [{"role": "user", "content": user_query}]

    # 第一次调用 LLM，获取 tool_calls 决策
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=available_tools,
        tool_choice="auto",
    )
    # 取出 assistant 消息
    assistant_msg = response.choices[0].message

    # 若无 tool_calls，直接返回文本
    if not assistant_msg.tool_calls:
        return assistant_msg.content or ""

    # 将 assistant 消息（含 tool_calls）追加到 history
    messages.append(assistant_dict(assistant_msg))
    # 打印并行执行的工具数量
    print(f"  并行执行 {len(assistant_msg.tool_calls)} 个工具…")
    # 线程池并行执行所有工具
    tool_results = execute_tools_parallel(assistant_msg.tool_calls)

    # 逐条打印 tool 结果摘要
    for tr in tool_results:
        print(f"  [tool] {tr['tool_call_id']}: {tr['content'][:80]}")

    # 将全部 tool 消息追加到 history
    messages.extend(tool_results)

    # 第二次调用 LLM，生成最终汇总回答
    final = client.chat.completions.create(
        model=MODEL, messages=messages, tools=available_tools,
    )
    # 返回最终 assistant 文本
    return final.choices[0].message.content or ""


# 脚本直接运行时进入交互 REPL
if __name__ == "__main__":
    # 配置 stdout UTF-8
    setup_stdout()
    # 打印程序说明
    print(f"并行工具执行（模型: {MODEL}）")
    print("输入问题，回车发送。直接回车使用默认问题。输入 q 退出。\n")

    # 默认测试问题（三工具并行）
    default = "北京现在天气怎么样？现在几点了？顺便算一下 25 * 4 + 10"

    # 主循环
    while True:
        # 读取用户输入
        try:
            query = input(">> ").strip()
        # Ctrl+C / Ctrl+D 退出
        except (EOFError, KeyboardInterrupt):
            break
        # 输入 q 退出
        if query.lower() == "q":
            break
        # 空输入使用默认问题
        if not query:
            query = default
        # 执行并打印结果
        print(run(query))
        # 空行分隔
        print()
