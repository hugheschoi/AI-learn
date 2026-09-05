import json
from config import client, MODEL_ID, DEFAULT_MAX_TOKENS
from hooks import trigger_hooks
from prompt import get_system_prompt
from llm import call_llm
from utils import assistant_message_dict
from tools.executor import execute_tool

# 定义变量rounds_since_todo，用于记录自上次todo_write调用以来的轮数
rounds_since_todo = 0

def agent_loop(messages: list):
  # 声明全局变量rounds_since_todo
  global rounds_since_todo
  # 设置最大Token数和模型,未来这个值可能会变化
  max_tokens = DEFAULT_MAX_TOKENS
  model = MODEL_ID
  while True:
    # 获取系统提示词
    system_prompt = get_system_prompt()
    # 如果距离上次 todo 写入的轮数大于等于 3 且消息列表不为空
    if rounds_since_todo >= 3 and messages:
      # 在消息列表中添加一条用户的提醒，提示助手更新 todo 列表
      messages.append({'role': 'user', 'content': '<reminder>请更新你的 todo 列表。</reminder>'})
      print(f'\x1b[33m> 请更新你的 todo 列表。\x1b[0m')
      # 轮数计数器 rounds_since_todo 复位为 0
      rounds_since_todo = 0

    response = call_llm(system_prompt, messages, max_tokens, model)
    choice = response.choices[0]
    assistant = choice.message
    messages.append(assistant_message_dict(assistant))
    if not assistant.tool_calls:
      force = trigger_hooks('Stop', messages)
      if force:
        messages.append({'role': 'user', 'content': force})
        continue
      return
    rounds_since_todo += 1
    for tool_call in assistant.tool_calls:
      name = tool_call.function.name
      args = json.loads(tool_call.function.arguments or "{}")
      print(f'{name} {json.dumps(args, ensure_ascii=False)}')
      # reason = check_permission(name, args)
      blocked = trigger_hooks('PreToolUse', name, args)
      if blocked is not None:
        # 将权限被拒绝的信息添加到消息历史中
        messages.append({
          "role": "tool",
          "tool_call_id": tool_call.id,
          "content": str(blocked),
        })
        # 跳过本次工具调用，继续下一个
        continue
      output = execute_tool(name, args)
      trigger_hooks('PostToolUse', name, args, output)
      # 如果工具名称是 todo_write，则重置轮数计数器
      if name == 'todo_write':
        # 重置轮数计数器为 0
        rounds_since_todo = 0

      messages.append({
        "role": "tool",
        "tool_call_id": tool_call.id,
        "content": output
      })
