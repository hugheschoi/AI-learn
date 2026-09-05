# -*- coding: utf-8 -*-
# 说明：导入 tiktoken
import tiktoken


def count_message_tokens(messages: list, model: str = "gpt-4o") -> int:
    """估算 OpenAI Chat API messages 列表的总 Token 数（近似值）。"""
    # 说明：按模型获取编码器
    enc = tiktoken.encoding_for_model(model)
    # 说明：每条消息的固定格式开销
    tokens_per_message = 3
    # 说明：累计 Token 总数
    total = 0
    # 说明：遍历每条消息
    for msg in messages:
        # 说明：加上本条消息的固定开销
        total += tokens_per_message
        # 说明：遍历 role、content 等字段并累加 Token
        for key, value in msg.items():
            total += len(enc.encode(value))
    # 说明：加上模型回复的起始开销
    total += 3
    return total


# 说明：构造典型的对话消息
messages = [
    {"role": "system", "content": "你是一名 Python 编程助手，回答简洁清晰。"},
    {"role": "user", "content": "列表和元组有什么区别？"},
]

# 说明：估算并打印总 Token 数
print("messages 约", count_message_tokens(messages), "tokens")