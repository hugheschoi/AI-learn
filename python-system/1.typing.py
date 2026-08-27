def is_even(num: int) -> bool:
    """Check if a number is even."""
    return num % 2 == 0

name: str = "Alice"
items: list[int] = [1, 2, 3, 4, 5]

# 容器类型
# 字符串列表去重为集合
def get_unique_items(items: list[str]) -> set[str]:
    return set(items)

# 导入 Callable 类型
from typing import Callable

# 对列表每个元素应用传入的一元函数
def apply_operation(
    numbers: list[int],
    operation: Callable[[int], int]
) -> list[int]:
    return [operation(x) for x in numbers]

# 用 lambda 对每个数求平方
apply_operation([1, 2, 3], lambda x: x ** 2)

from typing import Generic, TypeVar

T = TypeVar('T')
def identity(x: T) -> T:
    return x

def identityList(x: T) -> list[T]:
    return [x]

class Box(Generic[T]):
    def __init__(self, content: T):
        self.content = content

    def get(self) -> T:
        return self.content

    def set(self, content: T) -> None:
        self.content = content

init_box: Box[int] = Box(123)
print(init_box.get())  # 输出: 123