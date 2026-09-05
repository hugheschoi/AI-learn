# 从 sqlalchemy 导入 create_engine, String, Integer, Table, ForeignKey, select, Column
from sqlalchemy import create_engine, String, Integer, Table, ForeignKey, select, Column
# 从 sqlalchemy.orm 导入 DeclarativeBase, Session, Mapped, mapped_column, relationship
from sqlalchemy.orm import DeclarativeBase, Session, Mapped, mapped_column, relationship

# 定义 ORM 声明式基类
class Base(DeclarativeBase):
# 占位，无额外实现
    pass

# 定义多对多中间关联表（非 ORM 类）
student_course = Table(
# 表名为student_course
# 中间表表名
    "student_course",
# 绑定到 Base 的元数据
    Base.metadata,
# 定义中间表的一列（含外键与主键）
    Column("student_id", Integer, ForeignKey("students.id"), primary_key=True),
# 定义中间表的一列（含外键与主键）
    Column("course_id", Integer, ForeignKey("courses.id"), primary_key=True),
)

# 定义 Student 模型，继承 Base
class Student(Base):
# 指定映射的数据库表名
    __tablename__ = "students"
# 主键列
    id: Mapped[int] = mapped_column(primary_key=True)
# 列字段定义
    name: Mapped[str] = mapped_column(String(50))
# 与Course模型建立多对多关系，通过student_course中间表，反向引用为students
# 字段定义：courses: Mapped[list["Course"]] = relationship(
    courses: Mapped[list["Course"]] = relationship(
# 执行："Course", secondary=student_course, back_populates="students"
        "Course", secondary=student_course, back_populates="students"
    )

# 定义对象的字符串表示，便于调试输出
    def __repr__(self):
# 返回格式化字符串
        return f"<Student(id={self.id}, name='{self.name}')>"

# 定义 Course 模型，继承 Base
class Course(Base):
# 指定映射的数据库表名
    __tablename__ = "courses"
# 主键列
    id: Mapped[int] = mapped_column(primary_key=True)
# 列字段定义
    title: Mapped[str] = mapped_column(String(100))
# 与Student模型建立多对多关系，通过student_course中间表，反向引用为courses
# 字段定义：students: Mapped[list["Student"]] = relationship(
    students: Mapped[list["Student"]] = relationship(
# 执行："Student", secondary=student_course, back_populates="courses"
        "Student", secondary=student_course, back_populates="courses"
    )

# 定义对象的字符串表示，便于调试输出
    def __repr__(self):
# 返回格式化字符串
        return f"<Course(id={self.id}, title='{self.title}')>"

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
# # 执行：course1 = Course(title="高等数学")
#     course1 = Course(title="高等数学")
# # 执行：course2 = Course(title="计算机基础")
#     course2 = Course(title="计算机基础")
# # 执行：student1 = Student(name="小明", courses=[course1, course2])
#     student1 = Student(name="小明", courses=[course1, course2])
# # 执行：student2 = Student(name="小红", courses=[course2])
#     student2 = Student(name="小红", courses=[course2])
# # 批量将对象加入会话
#     session.add_all([student1, student2])
# # 提交事务，写入数据库
#     session.commit()
# # 打印输出
#     print("创建学生和课程成功")

# 执行查询并取第一条结果
    stu = session.scalars(select(Student).where(Student.name=="小明")).first()
# 打印输出
    print(f"\n学生：{stu.name}")
# 打印输出
    print("所选课程：")
# 执行：for c in stu.courses:
    for c in stu.courses:
# 打印输出
        print(f"  - {c.title}")

# 执行查询并取第一条结果
    cour = session.scalars(select(Course).where(Course.title=="计算机基础")).first()
# 打印输出
    print(f"\n课程：{cour.title}")
# 打印输出
    print("选修学生：")
# 执行：for s in cour.students:
    for s in cour.students:
# 打印输出
        print(f"  - {s.name}")