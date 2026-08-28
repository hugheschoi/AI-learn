# 导入 BaseSettings，用于定义配置类
from pydantic_settings import BaseSettings, SettingsConfigDict


# 定义配置类：继承 BaseSettings，字段即配置项
class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    # 应用名称，有默认值，未设置环境变量时使用
    app_name: str = "MyApp"
    # 是否调试模式，默认 False
    debug: bool = False
    # 数据库地址，无默认值，必须通过环境变量或 .env 提供
    database_url: str = "sqlite:///./demo.db"


# 实例化配置：自动从环境变量和 .env 加载
settings = Settings()

# 使用配置
print(settings.app_name)
print(settings.debug)
print(settings.database_url)