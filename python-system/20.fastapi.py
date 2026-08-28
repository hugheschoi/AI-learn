# 导入 FastAPI 类
from fastapi import FastAPI
# 导入 uvicorn 用于启动服务器
import uvicorn
# 创建 FastAPI 应用实例，title 会显示在自动文档中
app = FastAPI(title="我的第一个 API")

# 使用 @app.get 定义 GET 请求的路由，"/" 表示根路径
@app.get("/")
def read_root():
    # 返回一个字典，FastAPI 会自动转为 JSON
    return {"message": "Hello, FastAPI!"}


# 定义 GET /items/{item_id}，item_id 是路径参数
@app.get("/items/{item_id}")
def read_item(item_id: int):
    # 路径参数会自动解析并做类型校验
    return {"item_id": item_id, "name": f"商品{item_id}"}


# 程序入口：直接运行此文件时执行
if __name__ == "__main__":

    # 启动服务器，host 和 port 为监听地址和端口
    uvicorn.run(app, host="127.0.0.1", port=8000)