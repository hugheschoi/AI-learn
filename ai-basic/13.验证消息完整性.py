# 指定 Python 解释器为 python3
#!/usr/bin/env python3
# 文件文档字符串，说明本文件用于工具调用 §8.2：验证消息完整性
"""Tool Calls §8.2：验证消息完整性。"""

# 从 tool_demo_common 模块中导入 MODEL 和 setup_stdout
from tool_demo_common import MODEL, setup_stdout

# 定义函数 validate_message_chain，参数为消息链列表，返回值为字符串列表
def validate_message_chain(messages: list) -> list[str]:
    # 函数文档字符串，说明功能是：验证消息链是否符合 API 要求。
    """验证消息链是否符合 API 要求。"""
    # 初始化一个空列表，用于保存错误信息
    errors = []

    # 遍历所有消息，i 为索引，msg 为元素
    for i, msg in enumerate(messages):
        # 如果当前消息是 assistant 且包含 tool_calls 字段
        if msg.get("role") == "assistant" and msg.get("tool_calls"):
            # 提取所有 tool_calls 的 id，组成一个列表
            tool_call_ids = [tc["id"] for tc in msg["tool_calls"]]

            # 初始化一个空列表，用于保存后续 tool 响应的 tool_call_id
            tool_responses = []
            # 从当前消息的下一个消息开始遍历
            for j in range(i + 1, len(messages)):
                # 如果后续消息的角色是 tool
                if messages[j].get("role") == "tool":
                    # 将该 tool 消息的 tool_call_id 加入 tool_responses
                    tool_responses.append(messages[j].get("tool_call_id"))
                # 如果遇到 assistant 或 user 角色，跳出循环
                elif messages[j].get("role") in ("assistant", "user"):
                    break

            # 检查每一个 tool_call_id，是否都在 tool_responses 列表中
            for tc_id in tool_call_ids:
                # 如果 tool_call_id 不在 tool_responses 中，记录错误
                if tc_id not in tool_responses:
                    errors.append(f"Missing tool response for {tc_id}")

    # 返回错误列表
    return errors

# 定义主演示函数
def run_demo():
    # 打印验证消息完整性的提示信息，展示模型名称
    print(f"验证消息完整性（模型: {MODEL}）\n")

    # 构造一个合法的消息链，包含 user、assistant、tool 和 assistant 各类消息
    valid = [
        {"role": "user", "content": "查天气"},
        {"role": "assistant", "content": None, "tool_calls": [
            {"id": "call_1", "type": "function", "function": {"name": "get_weather", "arguments": "{}"}},
            {"id": "call_2", "type": "function", "function": {"name": "get_time", "arguments": "{}"}},
        ]},
        {"role": "tool", "tool_call_id": "call_1", "content": "{}"},
        {"role": "tool", "tool_call_id": "call_2", "content": "{}"},
        {"role": "assistant", "content": "完成"},
    ]

    # 构造一个非法（残缺）的消息链，缺少对 call_2 的 tool 响应
    broken = [
        {"role": "user", "content": "查天气"},
        {"role": "assistant", "content": None, "tool_calls": [
            {"id": "call_1", "type": "function", "function": {"name": "get_weather", "arguments": "{}"}},
            {"id": "call_2", "type": "function", "function": {"name": "get_time", "arguments": "{}"}},
        ]},
        {"role": "tool", "tool_call_id": "call_1", "content": "{}"},
    ]

    # 对合法消息链调用验证函数，收集错误信息
    err_valid = validate_message_chain(valid)
    # 对非法消息链调用验证函数，收集错误信息
    err_broken = validate_message_chain(broken)

    # 打印合法消息链的错误信息，如果为 None，则显示“无”
    print(f"[合法消息链] errors={err_valid or '无'}")
    # 打印非法消息链的错误信息，如果为 None，则显示“无”
    print(f"[残缺消息链] errors={err_broken or '无'}")
    # 如果合法消息链没有错误，且非法消息链有错误，则表示验证器工作正常
    if not err_valid and err_broken:
        print("\n✓ 验证器工作正常")

# 判断是否为主模块
if __name__ == "__main__":
    # 设置 stdout 输出格式
    setup_stdout()
    # 运行主演示函数
    run_demo()