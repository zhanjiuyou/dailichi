# 此文件主要用来获取代理
# 代码参照老崔的python网络爬虫实战，由于老崔的代理有好多用不了，这块自己添加了几个
# 2020.10.25
# 我的个人博客：jiaokangyang.com

from pyquery import PyQuery as pq
import requests
import time
import random
from db import RedisClient

# 这块将获取网页html的代码直接写成函数方便后面调用
def get_page(url):
    # 将很多的头信息放到一块，随机选用，提高爬虫反爬
    user_agent = ['Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.25 Safari/537.36 Core/1.70.3776.400 QQBrowser',
                  'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36']
    headers = {
        'User-Agent':random.choice(user_agent), # 随机选择一个头，让爬虫更顺利一点

    }

    r = requests.get(url,headers=headers)
    html = r.text
    return html


# 这里创建一个元类，说实话我对元类也不是很懂，照猫画虎，感觉和函数的装饰器有点像，主要功能是给下面的类添加几个属性，不在改变元代码的基础上操作。
class ProxyMetaclass(type):
    def __new__(cls,name,bases,attrs):
        count = 0
        # 添加一个属性为list，将我们后面带crawl标识的函数加到里面，后面自有它的用处
        attrs['__CrawlFunc__'] = []
        # attrs包含了类的属性，我们遍历所有的属性，筛选出带关键字的
        for k,v in attrs.items():
            # print(k,v)
            if 'crawl_' in k:
                # 将带关键字的函数名全部加到该属性中，K是筛选出来的函数名
                attrs['__CrawlFunc__'].append(k)
                count += 1 # 统计数量
        attrs['__CrawlFunCount__'] = count
        return type.__new__(cls,name,bases,attrs)

# 下面的类就是获取代理的具体内容了,
class Crawler(object,metaclass=ProxyMetaclass):
    # 该函数获取对应函数返回的代理
    def get_proxies(self,callback):
        # 创建一个空列表，用来存放我们的代理
        proxies = []
        # callback代表的是该类中我们筛选的函数名，这里，我们直接用eval函数直接执行，返回结果
        for proxy in eval("self.{}()".format(callback)):
            print('成功获取到代理',proxy)
            proxies.append(proxy)  #将获取到的代理加入到list中
        return proxies

    # 66 网站的代理,这里我们获取前4页的,网站为www.66ip.cn 函数统一前缀为crawl
    def crawl_daili66(self,page_count=10):
        # 起始网页
        start_url = 'http://www.66ip.cn/{}.html'
        # 将前4页的网页链接写到list中
        urls = [start_url.format(page) for page in range(1,page_count + 1)]
        for url in urls:
            print('地址:',url)
            time.sleep(1)  #为保证正常访问，必须降低抓取频率
            html = get_page(url)
            if html:
                a = pq(html)
                # 由于第一个是标题，我们用gt伪类从0以后开始选取匹配
                trs = a('.containerbox table tr:gt(0)').items()
                for tr in trs:
                    ip = tr.find('td:nth-child(1)').text()
                    port = tr.find('td:nth-child(2)').text()
                    yield ':'.join([ip,port])

    # 下面为kuaidaili的代理获取,方法同上
    def crawl_kuaidaili(self,page_count=10):
        start_url = 'https://www.kuaidaili.com/free/inha/{}/'
        urls = [start_url.format(page) for page in range(1,page_count+1)]
        for url in urls:
            print('爬取页面',url)
            time.sleep(1) # 由于该网站有反爬，必须将抓取频率降低
            html = get_page(url)
            if html:
                a = pq(html)
                trs = a('.table tbody tr').items()
                for tr in trs:
                    ip = tr.find('td:nth-child(1)').text()
                    port = tr.find('td:nth-child(2)').text()
                    yield ':'.join([ip,port])

    # 后期添加代理直接添加
    # http://www.ip3366.net/
    #

# 下面的类用来执行上面代理获取模块，获取代理并储存到redis中
POOL_UPPER_THRESHOLD = 1000 #设置代理池上线为500
class Getter():
    def __init__(self):
        self.redis = RedisClient()
        self.crawler = Crawler()

    # 设置一个函数判断代理池是否达到上限
    def is_over_threshold(self):
        if self.redis.count() >= POOL_UPPER_THRESHOLD: # 如果超过或等于上限
            return True
        else:
            return False

    # 执行函数
    def run(self):
        print('执行获取代理开始')
        if not self.is_over_threshold():
            # 通过上个类里面统计到的函数数量，循环挨个执行函数获取代理
            for callback_lable in range(self.crawler.__CrawlFunCount__):
                callback = self.crawler.__CrawlFunc__[callback_lable]  # callback为Crawler类中的代理函数名
                # 用到Crawler类中的get_proxies函数，将抓取到的函数保存到一个列表中，并且返回
                proxies = self.crawler.get_proxies(callback)
                # 遍历返回的列表，将抓到的数据保存到redis中
                for proxy in proxies:
                    self.redis.add(proxy)  # 将代理加入到有序集合proxies中,并设置初始分
