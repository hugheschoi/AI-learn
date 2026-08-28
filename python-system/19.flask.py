# 导入Flask类
# Flask类用于创建Web应用实例
"""
from flask import Flask

# 创建Flask应用实例
# __name__用于确定应用的根路径，Flask会根据它找到模板和静态文件
app = Flask(__name__)

@app.route("/")  # 定义路由：访问根路径时触发
def hello():
    # 返回响应内容
    return "Hello, Flask!"

# 打印应用对象信息（用于验证）
print(f"Flask应用已创建: {app}")
print(f"应用名称: {app.name}")
# 定义动态路由
# <name>是URL参数，会被传递给函数
# 访问 /user/张三 时，name='张三'
@app.route('/user/<name>')
def show_user(name):
    # 使用URL参数生成响应
    return f'<h1>你好，{name}！</h1>'

# 定义带类型的动态路由
# <int:post_id>表示post_id必须是整数
# 访问 /post/123 时，post_id=123（整数）
@app.route('/post/<int:post_id>')
def show_post(post_id):
    # 使用整数参数
    return f'<h1>文章 #{post_id}</h1>'

app.run(host='0.0.0.0', port=3000, debug=True)
"""
"""
# 好的做法：使用 g 对象
from flask import g, Flask

def get_user_posts(user_id):
    # 直接从 g 对象获取数据库连接
    posts = g.db.query(...).filter_by(user_id=user_id).all()
    return posts

@app.route('/user/<user_id>')
def show_user(user_id):
    g.db = get_database_connection()  # 存储到 g 对象
    posts = get_user_posts(user_id)  # 不需要传递db
    comments = get_user_comments(user_id)  # 不需要传递db
    return render_template('user.html', posts=posts, comments=comments)
"""