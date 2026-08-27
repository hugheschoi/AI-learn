# 导入 logging 模块
import logging

# 设置全局日志级别为 WARNING
# 配置日志输出到文件
logging.basicConfig(
    # 只记录 INFO 及以上级别
    level=logging.INFO,
    # 日志格式
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    # 日志文件路径
    filename="app.log",
    # 追加模式写入
    filemode="a",
    # 使用 UTF-8 编码避免中文乱码
    encoding="utf-8",
)
"""
# DEBUG 级别低于 WARNING，不会显示
logging.debug("不会显示")
# INFO 级别低于 WARNING，不会显示
logging.info("不会显示")
# WARNING 级别达标，会显示
logging.warning("会显示")
# ERROR 级别达标，会显示
logging.error("会显示")

# 记录异常
try:
    1 / 0
except ZeroDivisionError as e:
    logging.exception("捕获到异常：%s", e)


# 导入按大小轮转的 Handler
from logging.handlers import RotatingFileHandler
# 创建自定义 Logger
logger = logging.getLogger("my_app")
# 设置 Logger 最低记录级别为 DEBUG
logger.setLevel(logging.DEBUG)
# 创建按大小轮转的文件处理器
handler = RotatingFileHandler(
    # 日志文件路径
    "app.log",
    # 单文件上限 10MB
    maxBytes=10 * 1024 * 1024,
    # 最多保留 5 个备份文件
    backupCount=5,
    # UTF-8 编码
    encoding="utf-8",
)
# 设置日志格式
handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
# 将处理器添加到 Logger
logger.addHandler(handler)
"""

# 创建名为 my_app 的自定义 Logger
app_logger = logging.getLogger("my_app.database")
# 设置 Logger 最低记录级别为 DEBUG
app_logger.setLevel(logging.DEBUG)

# 创建控制台输出处理器
handler = logging.StreamHandler()
# 为处理器设置日志格式
handler.setFormatter(logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
))
# 将处理器添加到 Logger
app_logger.addHandler(handler)

# 记录程序启动信息
app_logger.info("程序启动")
