"""
# 基本用法
from pydantic import BaseModel

class User(BaseModel):
    name: str
    age: int
    email: str

user = User(name="Alice", age=30, email="alice@example.com")
print(user)
"""
"""
# 验证失败
# 导入 BaseModel
from pydantic import BaseModel

# 定义模型
class User(BaseModel):
    id: int
    name: str
    age: int = 18

# 故意传入错误类型：id 应该是 int，却传了字符串
try:
    User(id="不是数字", name="Bob")
except Exception as e:
    # 打印验证错误信息
    print(e)
"""

"""
# 自定义验证 导入 BaseModel 和 field_validator
from pydantic import BaseModel, field_validator

# 定义用户模型
class User(BaseModel):
    name: str
    # 要求密码至少 6 位
    password: str

    # 验证 password 字段
    @field_validator("password")
    @classmethod
    def password_not_short(cls, v: str) -> str:
        # 长度不足则抛出 ValueError
        if len(v) < 6:
            raise ValueError("密码至少 6 位")
        return v

# 正常创建
u = User(name="Alice", password="123456")
print(u)

# 密码太短会报错（少于 6 位）
try:
    User(name="Bob", password="123")
except Exception as e:
    # 捕获 ValidationError
    print("验证失败:", e)
"""
"""
# 导入 TypeAdapter
from pydantic import TypeAdapter

# 验证 dict[str, int]：键为字符串，值为整数
adapter = TypeAdapter(dict[str, int])
# 从字典验证
data = adapter.validate_python({"a": 1, "b": 2, "c": 3})
print("字典:", data)

# 从 JSON 解析
json_str = '{"x": 10, "y": 20}'
data2 = adapter.validate_json(json_str)
print("解析:", data2)

"""

from pydantic import TypeAdapter

# 验证 list[str]
adapter = TypeAdapter(list[str])
data = ["a", "b", "c"]

# 转成字典（对 list 来说就是 list 本身）
dumped = adapter.dump_python(data)
print("dump_python:", dumped)

# 转成 JSON 字符串（dump_json 返回 bytes，需 decode 成 str）
json_str = adapter.dump_json(data).decode()
print("dump_json:", json_str)