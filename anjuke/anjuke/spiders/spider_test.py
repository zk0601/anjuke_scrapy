import scrapy
from scrapy import Selector

class DmozSpider(scrapy.Spider):
    name = "ganji"
    allowed_domains = ["58.com"]

    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }

    def __init__(self, *args, **kwargs):
        self.url = 'https://sh.58.com/pudongxinqu/ershoufang/0/'
        # self.url = 'https://www.baidu.com/'

    def start_requests(self):
        yield scrapy.Request(url=self.url, headers=self.headers, callback=self.parse, dont_filter=True)

    def parse(self, response):
        if response.status != 200:
            print('请求报错，url: %s' % response.url)
            return

