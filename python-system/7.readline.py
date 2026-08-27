# 导入 readline 模块
import readline
# 导入路径处理工具
from pathlib import Path

# 定义历史文件路径（存放在当前目录）
HISTORY = Path("history.txt")
# 启动时加载历史
# 若历史文件已存在则读取
if HISTORY.exists():
    # 从文件加载命令历史到内存
    readline.read_history_file(HISTORY)

# 使用 try/finally 确保退出时保存历史
try:
    # 提示用户输入并获取姓名
    name = input("你叫什么名字？ ")
    # 打印问候语
    print(f"你好，{name}！")
    # 手动将输入加入历史（可选）
    readline.add_history(f"name {name}")
finally:
    # 退出时保存历史
    # 将内存中的命令历史写入文件
    readline.write_history_file(HISTORY)