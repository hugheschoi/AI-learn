
# 从config模块导入工作目录变量
from config import WORKDIR

# 定义一个钩子字典，每个事件对应一个回调函数列表
HOOKS = {'UserPromptSubmit': [], 'PreToolUse': [], 'PostToolUse': [], 'Stop': []}

# 定义禁止执行的命令列表
DENY_LIST = ["rm -rf /", "sudo", "shutdown", "reboot", "mkfs", "dd if=", "> /dev/sda"]

# 定义需要用户确认的危险命令关键字列表（增加cmd的删除命令）
DESTRUCTIVE = ['rm ', '> /etc/', 'chmod 777', 'del ', 'erase ']

# 注册钩子函数，将回调添加到对应事件的钩子列表
def register_hook(event: str, callback):
    HOOKS[event].append(callback)

# 注入当前工作目录信息到用户查询
def workspace_inject_hook(query: str) -> str | None:
    # 打印注入工作目录的钩子信息
    print(f'\x1b[90m[HOOK] UserPromptSubmit：注入工作目录 {WORKDIR}\x1b[0m')
    # 返回带有工作目录信息的查询字符串
    return f'<workspace>\n当前工作目录：{WORKDIR}\n</workspace>\n\n{query}'

# 权限控制钩子函数，对命令执行进行校验
def permission_hook(name: str, args: dict):
    # 如果工具类型是bash命令
    if name == 'bash':
        # 检查是否包含禁止列表中的命令
        for pattern in DENY_LIST:
            if pattern in args.get('command', ''):
                # 打印拦截信息
                print(f"\n\x1b[31m⛔ 已拦截：'{pattern}'\x1b[0m")
                # 返回拒绝权限的提示
                return '禁止列表拒绝权限'
        # 检查是否包含破坏性关键字
        for kw in DESTRUCTIVE:
            if kw in args.get('command', ''):
                # 打印警告信息
                print(f'\n\x1b[33m⚠  可能破坏性的命令\x1b[0m')
                print(f'   工具: {name}({args})')
                # 询问用户是否允许
                choice = input('   允许？[y/N] ').strip().lower()
                # 如果用户未确认，拒绝操作
                if choice not in ('y', 'yes'):
                    return '用户拒绝权限'
    # 如果是写文件或编辑文件操作
    if name in ('write_file', 'edit_file'):
        # 获取目标路径
        path = args.get('path', '')
        # 校验路径是否在工作目录下
        if not (WORKDIR / path).resolve().is_relative_to(WORKDIR):
            # 警告工作区外写入
            print(f'\n\x1b[33m⚠  在工作区外写入\x1b[0m')
            print(f'   工具: {name}({args})')
            # 询问用户是否允许
            choice = input('   允许？[y/N] ').strip().lower()
            # 如果用户未确认，拒绝操作
            if choice not in ('y', 'yes'):
                return '用户拒绝权限'
    # 返回None表示通过检查
    return None  

# 日志钩子函数，记录调用信息
def log_hook(name: str, args: dict):
    # 取参数前两项并转换为字符串用于预览
    args_preview = str(list(args.values())[:2])[:60]
    # 打印钩子触发信息
    print(f'\x1b[90m[HOOK] {name}({args_preview})\x1b[0m')
    # 无特殊行为，直接返回None
    return None 

# 钩子，处理工具输出过大的情况
def large_output_hook(name: str, args: dict, output):
    # 判断输出长度是否超过10万字符
    if len(str(output)) > 100000:
        # 打印输出过大警告
        print(f'\x1b[33m[HOOK] ⚠ {name} 输出过大：{len(str(output))} 字符\x1b[0m')
    # 返回None
    return None  

# 会话统计钩子函数
def summary_hook(messages: list):
    # 统计工具调用的次数
    tool_count = sum(1 for m in messages if m.get('role') == 'tool')
    # 打印工具调用次数信息
    print(f'\x1b[90m[HOOK] Stop：本次会话共使用 {tool_count} 次工具调用\x1b[0m')
    # 无特殊返回，直接None
    return None       

# 注册“用户提交”事件的钩子
register_hook('UserPromptSubmit', workspace_inject_hook)
# 注册“工具使用前”权限检查钩子
register_hook('PreToolUse', permission_hook)
# 注册“工具使用前”日志记录钩子
register_hook('PreToolUse', log_hook)
# 注册“工具使用后”大输出检测钩子
register_hook('PostToolUse', large_output_hook)
# 注册停止事件的会话总结钩子
register_hook('Stop', summary_hook)

# 触发用户输入相关的钩子链
def trigger_user_prompt_hooks(query: str) -> str:
    # 当前待处理的查询
    current = query
    # 依次触发钩子
    for callback in HOOKS['UserPromptSubmit']:
        # 调用每个钩子获取结果
        result = callback(current)
        # 如果返回字符串则更新current
        if isinstance(result, str):
            current = result
    # 返回处理后的查询
    return current

# 通用钩子触发函数
def trigger_hooks(event: str, *args):
    # 按注册顺序依次触发对应事件下的钩子
    for callback in HOOKS[event]:
        # 调用钩子并获取返回值
        result = callback(*args)
        # 如果返回非None则终止并返回
        if result is not None:
            return result
    # 所有钩子都返回None则返回None
    return None
