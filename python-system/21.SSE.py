# 导入 Flask 框架中的 Flask、Response、render_template_string
from flask import Flask, Response, render_template_string
# 导入时间模块用于模拟耗时操作
import time
# 导入随机数模块
import random

# 创建 Flask 应用对象
app = Flask(__name__)

# 定义网页的 HTML 内容
HTML_PAGE = '''
<!DOCTYPE html>
<html>
<head>
    <title>实时进度更新</title>
    <style>
        body { font-family: Arial; margin: 40px; }
        .progress-container {
            width: 500px;
            margin: 20px 0;
        }
        .progress-bar {
            width: 100%;
            height: 30px;
            background-color: #e0e0e0;
            border-radius: 15px;
            overflow: hidden;
        }
        .progress-fill {
            height: 100%;
            background-color: #4caf50;
            width: 0%;
            transition: width 0.3s;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
        }
        .status {
            margin: 10px 0;
            font-size: 18px;
        }
    </style>
</head>
<body>
    <h1>实时进度更新演示</h1>
    <button onclick="startTask()">开始任务</button>
    <div class="progress-container">
        <div class="progress-bar">
            <div class="progress-fill" id="progress">0%</div>
        </div>
    </div>
    <div class="status" id="status">等待开始...</div>
    
    <script>
        // 定义 EventSource 变量，用于后续连接
        let eventSource;
        
        // 定义开始任务函数
        function startTask() {
            // 连接到进度更新 SSE 接口
            eventSource = new EventSource('/progress');
            
            // 监听自定义 progress 事件
            eventSource.addEventListener('progress', function(e) {
                // 解析数据为 JS 对象
                const data = JSON.parse(e.data);
                // 获取进度条 Dom
                const progressBar = document.getElementById('progress');
                // 设置进度宽度
                progressBar.style.width = data.percent + '%';
                // 显示进度百分比文本
                progressBar.textContent = data.percent + '%';
                // 设置当前状态信息
                document.getElementById('status').textContent = data.message;
            });
            
            // 监听任务完成事件
            eventSource.addEventListener('complete', function(e) {
                // 解析数据
                const data = JSON.parse(e.data);
                // 显示完成状态
                document.getElementById('status').textContent = data.message;
                // 关闭 SSE 连接
                eventSource.close();
            });
        }
    </script>
</body>
</html>
'''

# 路由 '/' 返回 HTML 页面
@app.route('/')
def index():
    # 返回 HTML_PAGE 的内容到浏览器
    return render_template_string(HTML_PAGE)

# 路由 '/progress' 提供 SSE 实时进度
@app.route('/progress')
def progress():
    # 内部生成器：持续推送进度信息
    def generate():
        # 模拟总的任务步骤数量
        total_steps = 100
        
        # 从0到100共进行 total_steps+1 次循环
        for step in range(total_steps + 1):
            # 计算当前进度百分比
            percent = int((step / total_steps) * 100)
            
            # 根据进度设置不同的消息
            if step == 0:
                message = "任务开始..."
            elif step < total_steps:
                message = f"处理中... ({step}/{total_steps})"
            else:
                message = "任务完成！"
            
            # 组装进度数据字典
            progress_data = {
                "percent": percent,
                "step": step,
                "total": total_steps,
                "message": message
            }
            
            # 导入 json 模块
            import json
            # 序列化进度数据为 JSON 字符串
            json_data = json.dumps(progress_data)
            
            # 按 SSE 格式发送进度事件
            yield f"event: progress\ndata: {json_data}\n\n"
            
            # 模拟每一步的耗时
            time.sleep(0.1)
        
        # 组装完成后的消息数据
        complete_data = {
            "message": "所有任务已完成！",
            "timestamp": time.time()
        }
        # 再次导入 json 模块（可优化）
        import json
        # 按 SSE 格式发送完成事件
        yield f"event: complete\ndata: {json.dumps(complete_data)}\n\n"

    # 返回使用 text/event-stream 作为 mimetype 的 Response
    return Response(
        generate(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive'
        }
    )

# 如果直接运行本脚本，则启动 Flask WebServer
if __name__ == '__main__':
    # 以 debug 模式、支持多线程、端口3001运行
    app.run(debug=True, threaded=True, port=3001)