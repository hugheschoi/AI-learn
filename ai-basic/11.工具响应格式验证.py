# 指定使用 Python 3 解释器
#!/usr/bin/env python3
# 模块文档：Tool Calls 第 7.5 节工具响应格式验证
"""Tool Calls §7.5：工具响应格式验证。"""

# 导入 json 模块，用于序列化 content
import json

# 从共用模块导入模型名与 stdout 配置函数
from tool_demo_common import MODEL, setup_stdout


# 定义工具响应验证函数
def validate_tool_response(response: dict, tool_call_id: str) -> dict:
    # 函数说明：验证 tool 消息是否符合 OpenAI API 要求
    """验证工具响应是否符合 API 要求。"""
    # 定义 tool 消息必须包含的字段列表
    required_fields = ["role", "tool_call_id", "content"]

    # 遍历每个必需字段
    for field in required_fields:
        # 若响应中缺少该字段
        if field not in response:
            # 抛出 ValueError 说明缺失字段名
            raise ValueError(f"Missing required field: {field}")

    # 若 role 不是 tool
    if response["role"] != "tool":
        # 抛出 ValueError 说明非法 role
        raise ValueError(f"Invalid role: {response['role']}")

    # 若 tool_call_id 与期望 ID 不一致
    if response["tool_call_id"] != tool_call_id:
        # 抛出 ID 不匹配错误
        raise ValueError("Tool call ID mismatch")

    # 若 content 不是字符串类型
    if not isinstance(response["content"], str):
        # 将 content 自动转为 JSON 字符串
        response["content"] = json.dumps(response["content"], ensure_ascii=False)

    # 返回校验（可能已修正）后的响应字典
    return response


# 定义单次测试用例运行函数
def _check(title: str, fn):
    # 尝试执行传入的测试函数
    try:
        fn()
        # 未抛异常则打印通过
        print(f"[{title}] ✓ 通过")
    # 捕获预期的 ValueError
    except ValueError as e:
        # 打印正确拒绝及原因
        print(f"[{title}] ✓ 正确拒绝: {e}")


# 定义演示入口：运行多组验证用例
def run_demo():
    # 打印标题与当前模型名
    print(f"工具响应格式验证（模型: {MODEL}）\n")

    # 测试用例 1：合法响应
    _check("合法响应", lambda: validate_tool_response({
        "role": "tool", "tool_call_id": "call_abc", "content": '{"temp": 25}',
    }, "call_abc"))

    # 测试用例 2：缺少 content 字段
    _check("缺少 content", lambda: validate_tool_response({
        "role": "tool", "tool_call_id": "call_abc",
    }, "call_abc"))

    # 测试用例 3：role 应为 tool 却为 user
    _check("role 错误", lambda: validate_tool_response({
        "role": "user", "tool_call_id": "call_abc", "content": "ok",
    }, "call_abc"))

    # 测试用例 4：tool_call_id 与期望不符
    _check("ID 不匹配", lambda: validate_tool_response({
        "role": "tool", "tool_call_id": "call_xyz", "content": "ok",
    }, "call_abc"))

    # 测试用例 5：content 为 dict，应自动转 JSON
    fixed = validate_tool_response({
        "role": "tool", "tool_call_id": "call_abc", "content": {"temp": 25},
    }, "call_abc")
    # 打印自动转换后的 content
    print(f"[content 自动转 JSON] ✓ 通过 → {fixed['content']}")


# 脚本直接运行时执行
if __name__ == "__main__":
    # 配置 Windows 控制台 UTF-8 输出
    setup_stdout()
    # 运行全部演示用例
    run_demo()
