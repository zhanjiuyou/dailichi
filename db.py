# 此文件主要是将redis我们需要的操作封装成函数，方便调用
# date：2020/10/27
# 此文件全部是利用redis有序集合的特性，利用每个成员分数来配合调用

MAX_SCORE = 100  # 最大分数100
MIN_SCORE = 0   # 最小分数0
INITIAL_SCORE = 10 # 初始分为10
REDIS_HOST = 'localhost' # 链接地址
REDIS_PORT = 6379  # 端口号，同意都是6379
REDIS_PASSWORD = None  # 没有密码
REDIS_KEY = 'proxies' # 有序集合的键名

import redis
from random import choice
# 创建redis操作类
class RedisClient(object):
    # 初始化类
    def __init__(self,host=REDIS_HOST,port=REDIS_PORT,password=REDIS_PASSWORD):
        # 由于要传参，所以上面提前吧参数传进去，下面直接调用。由于redis输出的是字节，这块我们用decode设置为字符串
        self.db = redis.StrictRedis(host=host,port=port,password=password,decode_responses=True)

    # 定义添加函数,如果返回的代理没有分数，则给此代理设置初始分数10
    def add(self,proxy,score=INITIAL_SCORE):
        if not self.db.zscore(REDIS_KEY,proxy): # 判断有序集合中指定成员的分数，如果没有就给添加一个初始分数
            # 这块有个注意的，py3.0后zadd的方法传参方式改变了，第二个参数为字典
            proxy_score = {
                proxy: score,
            }
            return self.db.zadd(REDIS_KEY,proxy_score)

    # 定义随机获取代理，先获取分数高的代理，随机获取，没有的话就按排名获取，否则抛出异常
    def random(self):
        result = self.db.zrangebyscore(REDIS_KEY,MAX_SCORE,MAX_SCORE)
        if len(result):
            return choice(result) # 如果有值就随机选取一个返回
        else:
            result = self.db.zrevrange(REDIS_KEY,0,100) # 通过索引获取0-100区间的成员，默认由大到小排列,随机返回一个
            if len(result):
                return choice(result)
            else:
                raise PoolEmptyError # 抛出异常

    # 代理值减一分，分数小于最小值的话直接删除代理
    def decrease(self,proxy):
        score = self.db.zscore(REDIS_KEY,proxy)
        if score and score > MIN_SCORE:
            print('代理',proxy,'当前分数',score,'减1分')
            # py3.0后zincrby的参数顺序改变了，分数在前面，值在后面
            return self.db.zincrby(REDIS_KEY,-1,proxy,)  # 给代理减去一分

        else:
            print('代理',proxy,'当前分数',score,'移除')
            return self.db.zrem(REDIS_KEY,proxy)  # 移除命令

    # 判断代理是否存在
    def exists(self,proxy):
        return not self.db.zscore(REDIS_KEY,proxy) == None   #利用查看分数确实是否存在，如存在返回True，不存在返回Flase

    # 将代理设置为最大分数
    def max(self,proxy):
        print('代理',proxy,'可用，分数设置为：',MAX_SCORE)
        return self.db.zadd(REDIS_KEY,MAX_SCORE,proxy)

    # 获取代理的数量
    def count(self):
        return self.db.zcard(REDIS_KEY)

    # 获取全部的代理，通过分数最低到最高
    def all(self):
        return self.db.zrangebyscore(REDIS_KEY,MIN_SCORE,MAX_SCORE)

