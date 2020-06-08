import scrapy
from scrapy import Selector
import re
import json
import requests
from bs4 import BeautifulSoup
import os

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
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:76.0) Gecko/20100101 Firefox/76.0"
    }

    def __init__(self, *args, **kwargs):
        self.url1 = 'https://sh.58.com/jingan/ershoufang/0/'
        # self.url = 'https://www.baidu.com/'
        # self.url = 'https://sh.58.com/ershoufang/39711059408642x.shtml'
        # self.url = 'https://sh.58.com/ershoufang/42358467844118x.shtml'

    def start_requests(self):
        yield scrapy.Request(url=self.url1, headers=self.headers, callback=self.parse1, dont_filter=True)
        # yield scrapy.Request(url=self.url, headers=self.headers, callback=self.parse, dont_filter=True)

    def parse1(self, response):
        if response.status != 200:
            print('请求报错，url: %s' % response.url)
            return
        page_doms = response.css('.pager').xpath('.//a')
        url_frefix = response.url.split('58.com')[0] + '58.com'
        city = response.css('.main-wrap>div:first-child>a:first-child').xpath('./text()').extract_first().split('58')[0]
        ershou_dom_list = response.css('ul.house-list-wrap>li')
        if len(ershou_dom_list) == 0:
            return
        for ershou_dom in ershou_dom_list:
            href = ershou_dom.css('.list-info>.title>a')
            detail_url = href.attrib.get('href')
            detail_url = detail_url.split('?')[0]
            if not detail_url.startswith(url_frefix):
                continue
            gj_code = re.search(r'/ershoufang/(\w+)\.', detail_url).group(1)
            print(detail_url, gj_code)
            yield scrapy.Request(url=detail_url, headers=self.headers, callback=self.parse, dont_filter=True)


    def parse(self, response):
        # c_url = response.url.split('?')[0]
        # gj_code = 1
        # city = '贵阳'
        # if not gj_code or not city:
        #     return
        if response.status == 200:
            if not response.css('.content.clearfix'):
                html = response.body.decode()
                soup = BeautifulSoup(response.body, 'html.parser')
                js_str = soup.find('script', {'type': 'text/javascript'}).get_text()
                aa = js_str.split('____json4fe = ')
                a = aa[2].split("____json4fe.sid")[0].replace(";", "")
                url = "https://miniapp.58.com/landlord/getprivacyphone"
                payload = {
                    "user_id": json.loads(a)['userid'],
                    "info_id": 42209662457100
                }
                rs = requests.get(url, params=payload).content
                print(requests.get(url, params=payload).content)
                result_file = os.path.join('../../', '58_phone.txt')
                with open(result_file, 'a') as f:
                    f.write(rs.decode()+'\n')




        # if response.status != 200:
        #     print('请求报错，url: %s' % response.url)
        #     return
        # page_doms = response.css('.pager').xpath('.//a')
        # url_frefix = response.url.split('58.com')[0] + '58.com'
        # for page_dom in page_doms[:-1]:
        #     # 下一页就不用放进去
        #     url = url_frefix + page_dom.attrib.get('href')
        #     print(url)
        # city = response.css('.main-wrap>div:first-child>a:first-child').xpath('./text()').extract_first().split('58')[0]
        # print(city)
        # ershou_dom_list = response.css('ul.house-list-wrap>li')
        # if len(ershou_dom_list) == 0:
        #     return
        # for ershou_dom in ershou_dom_list:
        #     href = ershou_dom.css('.list-info>.title>a')
        #     detail_url = href.attrib.get('href')
        #     detail_url = detail_url.split('?')[0]
        #     if not detail_url.startswith(url_frefix):
        #         continue
        #     gj_code = re.search(r'/ershoufang/(\w+)\.', detail_url).group(1)
        #     print(detail_url, gj_code)


