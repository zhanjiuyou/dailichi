# 此文件为我们本次代理模块的最终调度模块，主要是为了方便控制所有的文件开关
# date：2020.11.2
# My blog：jiaokangyang.com

# 使用多进程模块运行，process是多进程函数
from multiprocessing import Process
from api import app
from crawler import Getter
from tester import Tester
import time

# 上面两个变量是循环时间，下面三个则为对于模块的开关，我们设置为True
TESTER_CYCLE = 20
GETTER_CYCLE = 20
TESTER_ENABLED = False
GETTER_ENABLED = False
API_ENABLED = True
API_HOST = '0.0.0.0'
API_PORT = 5000


class Scheduler():
    # 测试模块
    def schedule_tester(self,cycle=TESTER_CYCLE):
        # 定时测试代理
        tester = Tester()
        while True:
            print('测试模块开始运行')
            tester.run()
            time.sleep(cycle)

    # 获取模块执行
    def schedule_getter(self,cycle=GETTER_CYCLE):
        # 定时获取代理
        getter = Getter()
        while True:
            print('开始抓取代理')
            getter.run()
            time.sleep(cycle)

    # api 模块
    def schedule_api(self):
        # 开启api
        app.run(API_HOST,API_PORT)

    def run(self):
        print('代理池开始运行')
        if TESTER_ENABLED:
            # 创建进程
            tester_process = Process(target=self.schedule_tester)
            # 启动进程
            tester_process.start()

        if GETTER_ENABLED:
            getter_process = Process(target=self.schedule_getter)
            getter_process.start()

        if API_ENABLED:
            api_process = Process(target=self.schedule_api)
            api_process.start()


if __name__ == '__main__':
    a = Scheduler()
    a.run()