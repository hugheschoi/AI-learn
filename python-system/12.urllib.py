"""
# 导入请求和解析模块
import urllib.request
import urllib.parse

# 定义查询参数字典
params = {'q': 'Python', 'page': 1, 'limit': 10}
# 将字典编码为查询字符串
query = urllib.parse.urlencode(params)
# 拼接完整 URL
url = f'https://httpbin.org/get?{query}'

# 发送带参数的 GET 请求
with urllib.request.urlopen(url) as response:
    print(response.read().decode('utf-8'))

"""
"""
# 导入请求模块和 json 模块
import urllib.request
import json

# 将字典转为 JSON 字符串再编码为字节
data = json.dumps({'name': '张三', 'age': 25}).encode('utf-8')

# 构造 POST 请求对象
req = urllib.request.Request(
    'https://httpbin.org/post',
    data=data,
    headers={'Content-Type': 'application/json'},
    method='POST'
)

# 发送请求并打印响应
with urllib.request.urlopen(req) as response:
    print(response.read().decode('utf-8'))
"""
# 导入请求和异常模块
import urllib.request
import urllib.error

# 定义自定义请求头
headers = {
    'User-Agent': 'MyApp/1.0',
    'Accept': 'application/json',
    'Authorization': 'Bearer your_token'
}
# 创建带请求头的 Request 对象
req = urllib.request.Request('https://httpbin.org/headers', headers=headers)

try:
    # 发送请求，设置 10 秒超时
    with urllib.request.urlopen(req, timeout=10) as response:
        print(response.read().decode('utf-8'))
except urllib.error.URLError as e:
    print(f"请求失败：{e.reason}")