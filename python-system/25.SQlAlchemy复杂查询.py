# 从 sqlalchemy 导入 create_engine, String, and_, or_, select
from sqlalchemy import create_engine, String, and_, or_, select
# 从 sqlalchemy.orm 导入 DeclarativeBase, Session, Mapped, mapped_column
from sqlalchemy.orm import DeclarativeBase, Session, Mapped, mapped_column

# 定义 ORM 声明式基类
class Base(DeclarativeBase):
# 占位，无额外实现
    pass

# 定义 User 模型，继承 Base
class User(Base):
# 指定映射的数据库表名
    __tablename__ = "users"
# id字段，主键，自增长
# 主键列
    id: Mapped[int] = mapped_column(primary_key=True)
# name字段，最大长度50
# 列字段定义
    name: Mapped[str] = mapped_column(String(50))
# age字段
# 年龄字段，整型
    age: Mapped[int]
# city字段，最大长度50
# 列字段定义
    city: Mapped[str] = mapped_column(String(50))

# 定义对象的字符串表示，便于调试输出
    def __repr__(self):
# 返回格式化字符串
        return f"<User(id={self.id}, name='{self.name}', age={self.age}, city='{self.city}')>"

# 创建 MySQL 同步引擎
engine = create_engine(
    "mysql+pymysql://root:root@127.0.0.1:3306/aidb?charset=utf8mb4",
    echo=True,
    pool_pre_ping=True,
)
# 根据ORM模型生成数据库表
# 根据模型在数据库中创建表
Base.metadata.create_all(engine)

# 使用上下文管理器开启 Session
with Session(engine) as session:
# 构建用户数据列表
# 查询或组装用户数据
    users = [
# 创建模型实例
        User(name="张三", age=25, city="北京"),
# 创建模型实例
        User(name="李四", age=30, city="上海"),
# 创建模型实例
        User(name="王五", age=28, city="北京"),
# 创建模型实例
        User(name="赵六", age=35, city="广州"),
# 执行：]
    ]
# 批量将对象加入会话
    session.add_all(users)
# 提交事务，写入数据库
    session.commit()

# 执行查询并取全部结果
    result1 = session.scalars(select(User).where(and_(User.age > 25, User.city == "北京"))).all()
# 打印输出
    print("年龄大于25且城市为北京的用户：")
# 执行：for user in result1:
    for user in result1:
# 打印输出
        print(user)

# 执行查询并取全部结果
    result2 = session.scalars(select(User).where(or_(User.age < 25, User.city == "上海"))).all()
# 打印输出
    print("\n年龄小于25或城市为上海的用户：")
# 执行：for user in result2:
    for user in result2:
# 打印输出
        print(user)

# 执行查询并取全部结果
    result3 = session.scalars(select(User).where(User.name.like("张%"))).all()
# 打印输出
    print("\n姓名以'张'开头的用户：")
# 执行：for user in result3:
    for user in result3:
# 打印输出
        print(user)

# 执行查询并取全部结果
    result4 = session.scalars(select(User).where(User.city.in_(["北京", "上海"]))).all()
# 打印输出
    print("\n城市为北京或上海的用户：")
# 执行：for user in result4:
    for user in result4:
# 打印输出
        print(user)

# 执行查询并取全部结果
    result5 = session.scalars(select(User).where(User.age.between(28, 32))).all()
# 打印输出
    print("\n年龄在28到32之间的用户：")
# 执行：for user in result5:
    for user in result5:
# 打印输出
        print(user)