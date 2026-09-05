# 导入os模块，用于与操作系统交互
import os
# 导入操作系统相关模块
import glob as g
# 导入subprocess模块，用于执行子进程
import subprocess
from tkinter.constants import CURRENT

from utils import decode_subprocess_output, safe_path
from config import TEXT_ENCODING,WORKDIR
def run_bash(command: str) -> str:
    # 如果当前操作系统是Windows且命令是'date'（忽略前后空白并转为小写）
    if os.name == 'nt' and command.strip().lower() == 'date':
        # 将命令更改为Windows下同时输出日期和时间的命令
        command = 'date /t & time /t'
    # 定义危险命令的列表
    dangerous = ['rm -rf /', 'sudo', 'shutdown', 'reboot', '> /dev/']
    # 如果命令中包含任何一个危险命令
    if any(d in command for d in dangerous):
        # 返回错误提示，拦截执行危险命令
        return '错误：危险命令已被拦截'
    # 尝试执行命令，捕获异常
    try:
        # 使用subprocess.run运行命令
        r = subprocess.run(
            command,            # 要执行的命令
            shell=True,         # 在shell中执行
            cwd=os.getcwd(),    # 当x x x前工作目录设置为当前路径
            capture_output=True,# 捕获标准输出和标准错误
            timeout=120,        # 超时时间为120秒
        )
        # 解码输出内容，合并stdout和stderr(是二进制的字节序列，b''是byte类型，表示空的字节序列)，，并去除首尾空白
        out = decode_subprocess_output((r.stdout or b'') + (r.stderr or b'')).strip()
        # 返回输出内容的前50000个字符，如果无输出则返回'（无输出）'
        return out[:50000] if out else '（无输出）'
    # 捕获超时异常，返回超时错误信息
    except subprocess.TimeoutExpired:
        return '错误：超时（120 秒）'
    # 捕获文件未找到或OS错误，返回详细错误信息
    except (FileNotFoundError, OSError) as e:
        return f'错误：{e}'

def run_read(path:str, limit: int|None = None) -> str:
  try:
    lines = safe_path(path).read_text(encoding=TEXT_ENCODING).splitlines()
    if limit and limit < len(lines):
      lines = line[:limit] + [f'...（还有 {len(lines) - limit} 行）']
    return '\n'.join(lines)
  except Exception as e:
    return f"错误：{e}"

def run_write(path: str, content: str) -> str:
   try:
      file_path = safe_path(path)
      #确保文件父目录存在，若不存在则创建
      file_path.parent.mkdir(parents=True, exist_ok=True)
      file_path.write_text(content, encoding=TEXT_ENCODING)
      return f'已写入 {len(content)} 字节到 {path}'
   except Exception as e:
    return f"错误：{e}"

def run_edit(path: str, old_text: str, new_text: str) -> str:
    try:
       file_path = safe_path(path)
       text = file_path.read_text()
       if old_text not in text:
          return f'错误：在 {path} 中未找到指定文本'
       file_path.write_text(text.replace(old_text, new_text, 1), encoding=TEXT_ENCODING)
       return f'已编辑 {path}'
    except Exception as e:
        return f"错误：{e}"

# 定义glob通配符路径匹配函数，参数为模式
def run_glob(pattern: str) -> str:
    try:
        results = []
        for match in g.glob(pattern, root_dir=WORKDIR):
           # 检查匹配到的路径是否相对WORKDIR安全
           if (WORKDIR / match).resolve().is_relative_to(WORKDIR):
              results.append(match)
        return '\n'.join(results) if results else '（无匹配）'
    except Exception as e:
        # 捕获异常并返回错误信息
        return f"错误：{e}"

# 使用这个提示词测试：重构example/hello.py：添加类型注解、文档字符串和 main 保护（先列出 3 个步骤再执行）
CURRENT_TODOS: list[dict] = []
def run_todo_write(todos: list) -> str:
    global CURRENT_TODOS
    for index, todo in enumerate(todos):
        if 'content' not in todo or 'status' not in todo:
            return f"错误: todos[{index}] 缺少content或status"
        if todo["status"] not in ("pending", "in_progress", "completed"):
            return f"错误 : todos[{index}] 状态无效"
    CURRENT_TODOS = todos
    # 初始化显示用的lines列表，第一行为标题，并加黄颜色
    lines = ['\n\x1b[33m## 当前任务\x1b[0m']
    # 遍历所有当前任务
    for t in CURRENT_TODOS:
        icon = {'pending': '\x1b[33m等待中\x1b[0m', 'in_progress': '\x1b[36m处理中\x1b[0m',
                'completed': '\x1b[32m已完成\x1b[0m'}[t['status']]
        lines.append(f"  [{icon}] {t['content']}")
    print('\n'.join(lines))
    return f'已更新 {len(CURRENT_TODOS)} 个任务'


TOOL_HANDLERS = {
  "bash": run_bash,
  "read_file": run_read,
  'write_file': run_write,
  'edit_file': run_edit,
  'glob': run_glob,
  "todo_write": run_todo_write
}