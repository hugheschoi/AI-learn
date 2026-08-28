# 导入 python-dotenv
from dotenv import load_dotenv
import os

# 加载 .env 文件中的环境变量
load_dotenv()

# 现在可以使用环境变量
api_key = os.getenv('API_KEY')
print(f"API Key: {api_key}")