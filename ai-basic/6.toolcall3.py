# 指定使用 Python 3 的解释器
#!/usr/bin/env python3
# 文件头注释，说明本文件为 Tool Calls 的后台任务示例
"""Tool Calls 后台任务示例（对应 ToolCalls.md §6.3 / s13）：DeepSeek + 线程后台 + 通知注入。"""

# 导入处理 JSON 的模块
import json
# 导入操作系统相关的模块
import os
# 导入系统相关模块
import sys
# 导入线程相关的模块
import threading
# 导入时间相关的模块
import time

# 导入 dotenv 用于读取 .env 文件
from dotenv import load_dotenv
# 导入 OpenAI 接口库
from openai import OpenAI

# 加载 .env 文件中的环境变量，override=True 表示覆盖已存在的环境变量
load_dotenv(override=True)

# 获取 SSL 证书文件路径
_ssl_cert = os.getenv("SSL_CERT_FILE")
# 如果配置了 SSL 证书但对应文件不存在，则移除环境变量
if _ssl_cert and not os.path.isfile(_ssl_cert):
    os.environ.pop("SSL_CERT_FILE", None)

# 创建 OpenAI API 客户端，api_key 和 base_url 来自环境变量
client = OpenAI(
    api_key=os.environ["OPENAI_API_KEY"],
    base_url=os.getenv("OPENAI_BASE_URL"),
)
# 获取模型名称
MODEL = os.environ["MODEL_ID"]

# DEMO_SLEEP 表示模拟耗时任务的秒数（默认 5）
DEMO_SLEEP = int(os.getenv("DEMO_SLEEP", "5"))

# 定义工具的元数据结构生成函数
def _fn_tool(name: str, description: str, properties: dict, required: list[str]) -> dict:
    # 返回符合 OpenAI 函数调用协议的工具描述字典
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

# 定义一个模拟耗时任务的工具描述
long_running_tool = _fn_tool(
    "run_slow_task",
    "执行耗时任务。设置 run_in_background=true 时在后台运行，立即返回占位符。",
    {
        "task_name": {"type": "string", "description": "任务名称"},
        "seconds": {"type": "integer", "description": f"模拟耗时秒数，默认 {DEMO_SLEEP}"},
        "run_in_background": {"type": "boolean", "description": "是否在后台执行"},
    },
    ["task_name"],
)

# 定义一个计算数学表达式的工具描述
calculate_tool = _fn_tool(
    "calculate",
    "计算数学表达式。",
    {"expression": {"type": "string", "description": "如 123 + 456"}},
    ["expression"],
)

# 工具列表
TOOLS = [long_running_tool, calculate_tool]

# 定义模拟长时间任务的函数（阻塞线程）
def run_slow_task(task_name: str, seconds: int | None = None) -> dict:
    """模拟长时间任务（阻塞当前线程）。"""
    # 若提供 seconds 参数则用之，否则用默认值
    delay = seconds if seconds is not None else DEMO_SLEEP
    # 睡眠 delay 秒，模拟耗时
    time.sleep(delay)
    # 返回任务完成的信息
    return {
        "status": "completed",
        "task": task_name,
        "seconds": delay,
        "result": f"任务 {task_name} 已完成（耗时 {delay}s）",
    }

# 定义计算数学表达式的函数
def calculate(expression: str) -> dict:
    # 允许的字符集合
    allowed = set("0123456789+-*/(). ")
    # 判断表达式是否存在非法字符
    if not expression or not all(c in allowed for c in expression):
        return {"error": "表达式含非法字符"}
    try:
        # 使用 eval 计算表达式，禁用内置函数
        result = eval(expression, {"__builtins__": {}}, {})  # noqa: S307
        # 返回表达式和结果
        return {"expression": expression, "result": result}
    except Exception as e:
        # 捕获异常，返回错误信息
        return {"error": str(e)}

# 工具名称到处理函数的映射
TOOL_HANDLERS = {
    "run_slow_task": lambda args: run_slow_task(
        args["task_name"],
        args.get("seconds"),
    ),
    "calculate": lambda args: calculate(args["expression"]),
}

# 后台任务自增计数器
_bg_counter = 0
# 存储后台任务信息的字典
background_tasks: dict[str, dict] = {}
# 存储后台任务结果的字典
background_results: dict[str, dict] = {}
# 用于并发访问后台任务的锁
background_lock = threading.Lock()

# 判断工具是否应当在后台运行
def should_run_background(tool_name: str, tool_input: dict) -> bool:
    # 若参数设置 run_in_background，则后台执行
    if tool_input.get("run_in_background"):
        return True
    # 若是 run_slow_task 且 seconds 超过等于 3，则后台执行
    return tool_name == "run_slow_task" and tool_input.get("seconds", DEMO_SLEEP) >= 3

# 根据工具名称执行相应工具逻辑
def execute_tool(name: str, args: dict) -> dict:
    # 获取对应处理函数
    handler = TOOL_HANDLERS.get(name)
    # 若处理函数存在，调用
    if handler:
        return handler(args)
    # 否则返回未知工具错误
    return {"error": f"Unknown tool: {name}"}

# 启动一个后台任务
def start_background_task(tool_call_id: str, name: str, args: dict) -> str:
    # 声明使用全局计数器
    global _bg_counter
    # 自增计数，生成后台任务 ID
    _bg_counter += 1
    bg_id = f"bg_{_bg_counter:04d}"
    # 获取任务标签（用于显示）
    label = args.get("task_name") or args.get("command") or name

    # 定义线程工作函数
    def worker():
        # 执行具体工具
        result = execute_tool(name, args)
        # 上锁写入任务状态和结果
        with background_lock:
            background_tasks[bg_id]["status"] = "completed"
            background_results[bg_id] = result

    # 上锁添加任务到后台任务列表，设置状态
    with background_lock:
        background_tasks[bg_id] = {
            "tool_call_id": tool_call_id,
            "command": label,
            "status": "running",
        }
    # 启动后台线程，执行 worker
    threading.Thread(target=worker, daemon=True).start()
    # 打印后台任务派发信息
    print(f"  [后台] 已派发 {bg_id}: {label}")
    # 返回后台任务 ID
    return bg_id

# 收集所有已经完成的后台任务结果，并生成通知
def collect_background_results() -> list[str]:
    # 上锁，获取所有已完成的后台任务 ID
    with background_lock:
        ready_ids = [bid for bid, t in background_tasks.items() if t["status"] == "completed"]

    # 用于存放所有通知
    notifications = []
    # 遍历所有已完成的后台任务 ID
    for bg_id in ready_ids:
        # 上锁读取并删除任务及结果
        with background_lock:
            task = background_tasks.pop(bg_id)
            output = background_results.pop(bg_id, {})
        # 将输出内容转换为 JSON 字符串
        summary = json.dumps(output, ensure_ascii=False)
        # 如内容太长则截断
        if len(summary) > 200:
            summary = summary[:200] + "..."
        # 创建任务完成通知字符串
        notifications.append(
            f"<task_notification>\n"
            f"  <task_id>{bg_id}</task_id>\n"
            f"  <status>completed</status>\n"
            f"  <command>{task['command']}</command>\n"
            f"  <summary>{summary}</summary>\n"
            f"</task_notification>"
        )
        # 打印后台任务完成日志
        print(f"  [后台完成] {bg_id}: {task['command']}")
    # 返回所有通知
    return notifications

# 支持后台任务的主处理流程，处理用户输入并多轮与模型交互
def process_with_background_tasks(user_query: str) -> str:
    # 初始化消息列表，加入用户输入
    messages = [{"role": "user", "content": user_query}]

    # 无限循环，直到模型给出最终回复
    while True:
        # 收集后台任务完成的通知
        notifications = collect_background_results()
        # 如果有通知，注入进消息列表
        if notifications:
            messages.append({
                "role": "user",
                "content": "\n\n".join(notifications),
            })
            # 打印注入后台通知数
            print(f"  [注入] {len(notifications)} 条后台通知")

        # 向 OpenAI 模型发起聊天补全请求
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
        )

        # 取出助手的消息
        assistant_msg = response.choices[0].message

        # 将助手回复（包括 tools）加入消息列表
        messages.append({
            "role": "assistant",
            "content": assistant_msg.content,
            **({"tool_calls": [
                {
                    "id": tc.id,
                    "type": tc.type,
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    },
                }
                for tc in assistant_msg.tool_calls
            ]} if assistant_msg.tool_calls else {}),
        })

        # 如果没有工具调用，则表明会话结束，直接返回内容
        if not assistant_msg.tool_calls:
            return assistant_msg.content or ""

        # 逐个处理工具调用
        for tool_call in assistant_msg.tool_calls:
            # 获取工具名称
            name = tool_call.function.name
            # 解析工具调用的参数
            args = json.loads(tool_call.function.arguments or "{}")
            # 打印当前调用的工具
            print(f"> {name}")

            # 判定是否需要后台调度
            if should_run_background(name, args):
                # 启动后台任务
                bg_id = start_background_task(tool_call.id, name, args)
                # 构造后台任务启动的返回内容
                output = {
                    "background_task_id": bg_id,
                    "status": "running",
                    "message": "任务已在后台启动，完成后将通过 task_notification 通知。",
                }
            else:
                # 前台直接执行，并打印结果
                output = execute_tool(name, args)
                print(f"  [sync] {output}")

            # 把工具执行结果写入消息流
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(output, ensure_ascii=False),
            })

        # 等待本轮后台任务全部完成，避免多轮嵌套产生竞态
        while True:
            # 上锁判断是否仍有运行中的后台任务
            with background_lock:
                running = any(t["status"] == "running" for t in background_tasks.values())
            # 若都已完成则退出等待循环
            if not running:
                break
            # 否则短暂睡眠后再检查
            time.sleep(0.2)

# 主程序入口
if __name__ == "__main__":
    # 如果在 Windows 平台，确保标准输出为 UTF-8 编码
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8")

    # 打印提示
    print(f"后台任务示例（模型: {MODEL}，模拟耗时: {DEMO_SLEEP}s）")
    print("输入问题，回车发送。直接回车使用默认问题。输入 q 退出。\n")

    # 定义默认问题，用于快捷演示
    default = (
        f"用 run_in_background 在后台执行 run_slow_task，任务名 pip-sim，耗时 {DEMO_SLEEP} 秒；"
        "同时用 calculate 计算 123 + 456"
    )

    # 进入主循环，持续获取用户输入
    while True:
        try:
            # 获取用户输入，并去掉首尾空白
            query = input(">> ").strip()
        except (EOFError, KeyboardInterrupt):
            # 响应 Ctrl+C/EOF，退出主循环
            break
        # 输入 q 则退出
        if query.lower() == "q":
            break
        # 若输入为空则使用默认问题
        if not query:
            query = default
        # 处理并返回模型结果
        print(process_with_background_tasks(query))
        # 打印空行分割多次对话
        print()