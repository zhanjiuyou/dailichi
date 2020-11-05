# 此文件为我们的代理调用接口，利用flask的web服务来调用，
# 除了方便之外，也是保护我们的数据库敏感信息
# date:2020.11.2
# My blog:jiaokangyang.com

from flask import Flask,g
from db import RedisClient

# __all__定义了该代码中那些方法可被调用
__all__ = ['app']
# 创建的应用名为app
app = Flask(__name__)

# 链接数据库
def get_conn():
    # 使用g，来定义一个redis变量，实例化redis类
    if not hasattr(g,'redis'):
        g.redis = RedisClient()
    return g.redis

# route是flask框架的路由
@app.route('/')
def index():
    return '<h2>欢迎使用焦康阳的代理池接口</h2>' # 这里首页为一个欢迎语

# 获取一个随机代理，
@app.route('/random')
def get_proxy():
    conn = get_conn()
    return conn.random()

# 获取代理池数量
@app.route('/count')
def get_counts():
    conn = get_conn()
    return str(conn.count())

if __name__ == '__main__':
    app.run()