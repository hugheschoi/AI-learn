# 从 sqlalchemy 导入 create_engine
from sqlalchemy import create_engine, Integer, String, Column, select, desc
from sqlalchemy.orm import DeclarativeBase, Session, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class User(Base):
    # 指定表名为 users
    __tablename__ = "users"
    # 定义 id 主键字段，类型为 Integer
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    # 定义 name 字段，类型为 String(50)，长度 50
    name: Mapped[str] = mapped_column(String(50))
    # 
    city: Mapped[str] = mapped_column(String(50))
    age: Mapped[int] = mapped_column(Integer)


# 定义 MySQL 连接 URL（按本地修改用户名、密码、主机、库名）
DATABASE_URL = (
    "mysql+pymysql://root:123456@127.0.0.1:3306/aidb?charset=utf8mb4"
)
# 创建引擎：echo 打印 SQL，pool_pre_ping 检测连接可用性
engine = create_engine(DATABASE_URL, echo=True, pool_pre_ping=True) 

# 创建所有模型定义的表（仅首次运行需要）
Base.metadata.create_all(engine)
"""
# 手动提交
user = User(name="Alice", city="New York")
with Session(engine) as session:
    session.add(user)
    session.commit()
"""
"""
# 自动提交
user = User(name="Bob", city="Los Angeles")
with Session(engine) as session:
    # 自动提交事务
    with session.begin():
        # 带提交的状态
        session.add(user)
        #  session.commit()  # 可选，自动提交时不需要显式调用
"""
"""
# 自动提交写法二：sessionmaker + begin
# 从 sqlalchemy.orm 导入 sessionmaker 工厂函数
from sqlalchemy.orm import sessionmaker
# 创建 Session 工厂，指定绑定的引擎
user = User(name="David", city="Chicago", age=30)
SessionFactory = sessionmaker(bind=engine)
# 使用工厂的 begin() 方法自动管理事务与 Session 生命周期
with SessionFactory.begin() as session:
    # 添加 user 对象到会话，退出 with 时自动提交
    session.add(user)
"""
"""
# Read 读
with Session(engine) as session:
    # 查询所有 User 对象
    all_users = session.scalars(select(User)).all()
    first = session.scalars(select(User)).first()

    users = session.scalars(select(User))
    for user in users:
        print(f"ID: {user.id}, Name: {user.name}, City: {user.city}")
    by_id = session.get(User, 1)
    top2 = session.scalars(select(User).order_by(desc(User.age)).limit(2)).all()
    # 执行查询并取第一条结果
    bob = session.scalars(select(User).where(User.name == "Bob")).first()
    print(f"查询结果: {bob.name}, {bob.city}")
"""
"""
# 更新
from sqlalchemy import update, select
with Session(engine) as session:
    user = session.scalars(select(User).where(User.name == "Alice")).first()
    if user:
        user.city = "San Francisco"
        session.commit()
    session.execute(update(User).where(User.age > 20).values(age=20))
    session.commit()
"""

# 删除
from sqlalchemy import delete, select
with Session(engine) as session:
    user = session.scalars(select(User).where(User.name == "Bob")).first()
    if user:
        session.delete(user)
        session.commit()
    deleted = session.execute(delete(User).where(User.age < 20)).rowcount
    session.commit()
    print(f"删除了 {deleted} 条记录")