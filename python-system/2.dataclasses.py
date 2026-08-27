from dataclasses import dataclass, field
# 声明数据类
@dataclass
class Person:
    name: str
    # 可选字段：默认年龄 20
    age: int = 20
    # 可变默认值必须用 default_factory，每实例独立列表
    tags: list[str] = field(default_factory=list)
    # 隐藏敏感字段，如密码（不会显示在 repr/print 中）
    password: str = field(repr=False, default="")
    #  由 __post_init__ 计算得出，不在 __init__ 参数中
    name_length:int = field(init=False)
    def __post_init__(self):
      # 通过 name 计算 name_length
      self.name_length = len(self.name)
# 演示 field(init=False) 计算属性
p1 = Person("Tom", password="secret", tags=["hello"])
print(p1)  # password 不显示，name_length 自动生成