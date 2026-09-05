"""示例模块：演示带类型注解的加法函数。"""


def add(a: int, b: int) -> int:
    """返回两个整数之和。

    Args:
        a: 第一个加数。
        b: 第二个加数。

    Returns:
        a 与 b 的和。
    """
    return a + b


def main() -> None:
    """运行一个简单的加法示例。"""
    print(add(1, 2))


if __name__ == "__main__":
    main()
