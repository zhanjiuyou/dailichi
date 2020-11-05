# 此文件为代理的测试模块，主要是检验代理的可用性，及给每个代理在有序集合中打分
# 2020.11.2
# 我的个人博客：jiaokangyang.com

import aiohttp
from aiohttp import ClientError,ClientConnectorError
from db import RedisClient
import asyncio
import time


# 设置状态码,如需多个，可在列表中多添加价格
VALID_STATUS_CODES = [200]

# 设置测试网站，这里我们选择百度
TEST_URL = 'http://www.baidu.com/'
# 设置批量测试的最大值
BATCH_TEST_SIZE = 100

# 创建测试类
class Tester(object):
    # 初始化类
    def __init__(self):
        # 实例化redis类给redis对象
        self.redis = RedisClient()
    # 声明函数是异步的,且定义测试函数，测试单个代理
    async def test_single_proxy(self,proxy):
        # 限制异步的输数量，且不验证是否为https，这块也不是很懂,照着写
        conn = aiohttp.TCPConnector(verify_ssl=False)
        # 用aiohttp创建实例,命名为session
        async with aiohttp.ClientSession(connector=conn) as session:
            # 由于可能会发生报错等等，这里用try except
            try:
                if isinstance(proxy,bytes):  # isinstance方法为判断数据类型，如果为bytes则执行下面语句
                    proxy = proxy.decode('utf-8') # 如果是字节则解码为utf-8
                # 给代理前面加http
                real_proxy = 'http://' + proxy
                print('正在测试代理：',proxy)
                # 下面方法与requests类似，加入代理后测试我们预设的网站
                async with session.get(TEST_URL,proxy=real_proxy,timeout=15) as response:
                    # 如果状态码在上面定义的列表中，则代理可用，并设置分数为100，上面我们只添加了状态码200
                    if response.status in VALID_STATUS_CODES:
                        self.redis,max(proxy)
                        print('代理可用',proxy)
                    else:
                        self.redis.decrease(proxy)
                        print('请求响应码不合法',proxy) # 如果响应码不为200，则减分
            # 如果中途报错则抛出异常,说明代理不成功，减分
            # except (ClientError,ClientConnectorError,TimeoutError,AttributeError):
            except:
                self.redis.decrease(proxy)
                print('代理请求失败',proxy)
    # 上面我们定义了单个代理的测试，现在运行测试函数
    def run(self):
        print('测试器开始运行')
        try:
            # 将所有的代理获取出来
            proxies = self.redis.all()
            # 创建一个协程
            loop = asyncio.get_event_loop()
            # 开始批量测试，每次调用100个,这快运用了列表的切片功能
            for i in range(0,len(proxies),BATCH_TEST_SIZE):
                # 第一个循环取0-99 第二次取100-199，以此类推，这快看了好久才反应过来，基础知识很重要
                test_proxies = proxies[i:i+BATCH_TEST_SIZE]
                # 将每个测试代理的对象加到列表中。异步执行此批量方法。异步这块由于边看边学，有的地方理解不透
                tasks = [self.test_single_proxy(proxy) for proxy in test_proxies]
                loop.run_until_complete(asyncio.wait(tasks))
                time.sleep(5)

        except Exception as e:
            print('测试器发生错误',e.args)



if __name__ == '__main__':
    a = Tester()
    a.run()