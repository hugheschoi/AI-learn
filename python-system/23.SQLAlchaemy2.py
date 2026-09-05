# 从 sqlalchemy 导入 create_engine, String, Integer, ForeignKey, select
from sqlalchemy import create_engine, String, Integer, ForeignKey, select
# 从 sqlalchemy.orm 导入 DeclarativeBase, Session, Mapped, mapped_column, relationship
from sqlalchemy.orm import DeclarativeBase, Session, Mapped, mapped_column, relationship

# 定义 ORM 声明式基类
class Base(DeclarativeBase):
# 占位，无额外实现
    pass

# 定义 User 模型，继承 Base
class User(Base):
# 指定映射的数据库表名
    __tablename__ = "users"
# 主键列
    id: Mapped[int] = mapped_column(primary_key=True)
# 列字段定义
    name: Mapped[str] = mapped_column(String(50))
# 年龄字段，整型
    age: Mapped[int]
# 字段定义：addresses: Mapped[list["Address"]] = relationship(
    addresses: Mapped[list["Address"]] = relationship(
# 执行："Address", back_populates="user", cascade="all, delete-orphan"
        "Address", back_populates="user", cascade="all, delete-orphan"
    )

# 定义对象的字符串表示，便于调试输出
    def __repr__(self):
# 返回格式化字符串
        return f"<User(id={self.id}, name='{self.name}')>"

# 定义 Address 模型，继承 Base
class Address(Base):
# 指定映射的数据库表名
    __tablename__ = "addresses"
# 主键列
    id: Mapped[int] = mapped_column(primary_key=True)
# 外键列
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
# 列字段定义
    email: Mapped[str] = mapped_column(String(100))
# 字段定义：user: Mapped[User] = relationship("User", back_populates="addresses")
    user: Mapped[User] = relationship("User", back_populates="addresses")

# 定义对象的字符串表示，便于调试输出
    def __repr__(self):
# 返回格式化字符串
        return f"<Address(id={self.id}, email='{self.email}')>"

# 创建 MySQL 同步引擎
engine = create_engine(
    "mysql+pymysql://root:123456@127.0.0.1:3306/aidb?charset=utf8mb4",
    echo=True,
    pool_pre_ping=True,
)
# 根据模型在数据库中创建表
Base.metadata.create_all(engine)

# 使用上下文管理器开启 Session
with Session(engine) as session:

# 执行查询并取第一条结果
    user = session.scalars(select(User).where(User.name == "赵六")).first()
# 打印输出
    print(f"\n用户：{user.name}")
# 打印输出
    print("地址列表：")
# 执行：for address in user.addresses:
    for address in user.addresses:
# 打印输出
        print(f"  - {address.email}")

# 通过地址查用户
# 执行查询并取第一条结果
    address = session.scalars(select(Address).where(Address.email == "zhaoliu@example.com")).first()
# 打印输出
    print(f"\n地址：{address.email}")
# 打印输出
    print(f"所属用户：{address.user.name}")