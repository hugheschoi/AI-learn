from contextlib import contextmanager

@contextmanager
def my_context_manager():
    # 进入 with 时执行的准备工作
    print("进入 with，做准备工作")
    try:
        # 将值传给 as 后面的变量
        yield "你好"
    finally:
        # 退出 with 时执行的清理工作（无论是否异常）
        print("退出 with，做清理工作")


# 使用自定义上下文管理器，msg 接收 yield 的值
with my_context_manager() as msg:
    print("在 with 块内:", msg)

import time

@contextmanager
def timer(label: str = ''):
    start = time.perf_counter()
    try:
        yield
    finally:
        end = time.perf_counter()
        # 有标签时添加前缀，否则为空字符串
        prefix = f"[{label}] " if label else ""
        print(f"{prefix}耗时: {end - start:.4f} 秒")

with timer("示例操作"):
    # 模拟耗时操作
    time.sleep(1.5)
    print("执行业务逻辑...")


from contextlib import suppress
import os

with suppress(FileNotFoundError, PermissionError):
    # FileNotFoundError 或 PermissionError 时不会抛出异常，删除这个文件（其实没有这个文件）但不会报错
    os.remove("tmp.txt") 