from sqlalchemy import create_engine, String, Integer, select, func
from sqlalchemy.orm import DeclarativeBase, Session, Mapped, mapped_column

# 定义 ORM 声明式基类
class Base(DeclarativeBase):
# 占位，无额外实现
    pass

# 定义 Vip 模型，继承 Base
class Vip(Base):
# 指定映射的数据库表名
    __tablename__ = "vips"
# 主键列
    id: Mapped[int] = mapped_column(primary_key=True)
# 列字段定义
    name: Mapped[str] = mapped_column(String(50))
# 年龄字段，整型
    age: Mapped[int]
# 列字段定义
    city: Mapped[str] = mapped_column(String(50))

# 定义对象的字符串表示，便于调试输出
    def __repr__(self):
# 返回格式化字符串
        return f"<Vip(id={self.id}, name='{self.name}', age={self.age})>"

# 创建 MySQL 同步引擎
engine = create_engine(
    "mysql+pymysql://root:123456@127.0.0.1:3306/aidb?charset=utf8mb4",
    echo=True,
    pool_pre_ping=True,
)
# 根据ORM模型创建数据表（如果不存在则创建）
# 根据模型在数据库中创建表
Base.metadata.create_all(engine)

# 使用上下文管理器开启 Session
with Session(engine) as session:
    avg_age = session.execute(select(func.avg(Vip.age))).scalar_one()
    print(f"平均年龄：{avg_age:.2f}")

    max_age = session.execute(select(func.max(Vip.age))).scalar_one()
    print(f"最大年龄：{max_age}")

    min_age = session.execute(select(func.min(Vip.age))).scalar_one()
    print(f"最小年龄：{min_age}")

    total_age = session.execute(select(func.sum(Vip.age))).scalar_one()
    print(f"年龄总和：{total_age}")

    vip_count = session.execute(select(func.count(Vip.id))).scalar_one()
    print(f"会员总数：{vip_count}")

    city_stats = session.execute(
        select(
            Vip.city,
            func.count(Vip.id).label("count"),
            func.avg(Vip.age).label("avg_age")
        ).group_by(Vip.city)
    ).all()

    print("\n按城市分组统计：", city_stats, type(city_stats))

    print("\n按城市分组统计：")
    for city, count, avg_age in city_stats:
        print(f"  {city}: {count}人, 平均年龄{avg_age:.2f}")