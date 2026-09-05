# 指定使用 Python 3 解释器
#!/usr/bin/env python3
# 模块文档：Tool Calls 第 7.3 节错误处理和重试
"""Tool Calls §7.3：错误处理和重试。"""

# 导入 json 模块
import json
# 导入 time 模块，用于重试退避 sleep
import time

# 从共用模块导入模型名、工具执行函数、stdout 配置
from tool_demo_common import MODEL, execute_tool, setup_stdout

# 记录每个 tool_call_id 已失败次数的全局字典
_fail_counts: dict[str, int] = {}


# 定义带重试的工具执行函数
def execute_tool_with_retry(
    tool_call,
    executor=None,
    max_retries: int = 3,
) -> dict:
    # 若未传入 executor 则使用默认 execute_tool
    run = executor or execute_tool
    # 最多尝试 max_retries 次
    for attempt in range(max_retries):
        # 尝试执行工具
        try:
            result = run(tool_call)
            # 成功则构造标准 tool 消息并返回
            return {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result, ensure_ascii=False),
            }
        # 捕获任意执行异常
        except Exception as e:
            # 若已是最后一次尝试
            if attempt == max_retries - 1:
                # 返回包含错误信息的 tool 消息
                return {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps({
                        "error": str(e),
                        "message": "Tool execution failed after retries",
                    }, ensure_ascii=False),
                }
            # 计算指数退避延迟（1s, 2s, 4s…）
            delay = 2 ** attempt
            # 打印重试日志
            print(f"  [retry] 第 {attempt + 1} 次失败，{delay}s 后重试: {e}")
            # 等待后进入下一轮重试
            time.sleep(delay)


# 定义模拟不稳定的工具执行：前 2 次失败，第 3 次成功
def flaky_execute_tool(tool_call) -> dict:
    # 函数说明
    """模拟前 2 次失败、第 3 次成功。"""
    # 以 tool_call.id 作为计数键
    key = tool_call.id
    # 累加该 ID 的调用次数
    _fail_counts[key] = _fail_counts.get(key, 0) + 1
    # 前两次调用故意抛错
    if _fail_counts[key] < 3:
        raise RuntimeError(f"模拟瞬态错误（第 {_fail_counts[key]} 次）")
    # 第三次起调用真实 execute_tool
    return execute_tool(tool_call)


# 定义演示入口
def run_demo():
    # 打印标题
    print(f"错误处理和重试（模型: {MODEL}）\n")

    # 定义简易 tool_call 占位类
    class _TC:
        pass

    # 创建模拟 tool_call 实例
    tc = _TC()
    # 设置 tool_call_id
    tc.id = "call_demo"
    # 构造 function 对象（name + arguments）
    tc.function = type("F", (), {
        "name": "get_weather",
        "arguments": '{"city": "北京"}',
    })()

    # 使用 flaky 执行器调用带重试的执行函数
    msg = execute_tool_with_retry(tc, executor=flaky_execute_tool, max_retries=3)
    # 打印最终 tool 消息 content
    print(f"  最终结果: {msg['content']}")


# 脚本直接运行时执行
if __name__ == "__main__":
    # 配置 stdout 编码
    setup_stdout()
    # 运行演示
    run_demo()
