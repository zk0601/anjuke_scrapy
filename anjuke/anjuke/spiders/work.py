import scrapy
from scrapy import Selector
import json
import re
import logging
import os
from ..items import AnjukeItem

LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'log', 'anjuke.log')
# 连同scrapy信息一起输出到log
# logging.basicConfig(level=logging.DEBUG, filename=LOG_FILE)

logger = logging.getLogger(__name__)
# 只输出代码控制的信息到log
file_handler = logging.FileHandler(LOG_FILE)
logger.addHandler(file_handler)

DB_HOST = '10.30.194.84'
DB_USER = 'developer'
DB_PASSWORD = 'pEo4IH7z'
DB_DATABASE = 'dataRepository'


class DmozSpider(scrapy.Spider):
    name = "anjuke"
    allowed_domains = ["anjuke.com"]

    headers = {
        "accept": "application/json, text/javascript, */*; q=0.01",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "zh-CN,zh;q=0.9",
        "cache-control": "max-age=0",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36",
    }

    ajax_headers = {
        "accept": "application/json, text/javascript, */*; q=0.01",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "zh-CN,zh;q=0.9",
        "cache-control": "max-age=0",
        "x-requested-with": "XMLHttpRequest",
        "user-agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36",
    }

    def __init__(self, *args, **kwargs):
        super(DmozSpider, self).__init__(*args, **kwargs)
        self.url = 'https://shanghai.anjuke.com/prop/view/A1784181767?from=filter&spread=commsearch_p&uniqid=pc5d5a454005bb37.26636206&position=3&kwtype=filter&now_time=1566197056'
        self.output_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output.txt')
        self.city, self.ajk_city_id = '上海', 11

    def start_requests(self):
        yield scrapy.Request(url=self.url, headers=self.headers, callback=self.parse, dont_filter=True)

    def parse(self, response):
        if response.status != 200:
            logger.error('请求报错，url: %s' % response.url)
            return
        broker_id, token, prop_id, city_id = None, None, None, self.ajk_city_id
        html = response.text
        rs = Selector(text=html, type='html')
        ext_code = response.url.split('?')[0].split('/')[-1]
        broker_name = response.css('.brokercard-name').xpath('./text()').extract_first().strip()
        broker_company = response.css('.broker-company>p:first-child').xpath('./a/text()').extract_first().strip()
        broker_store = response.css('.broker-company>p:nth-child(2)').xpath('./span/text()').extract_first().strip()

        # 做请求phone的准备
        rs = rs.xpath('.//script').extract()
        for script in rs:
            if 'phoneParam' in script:
                broder_pattern = r"broker_id:'(\d+)'"
                token_pattern = r"token: '(\w+)'"
                prop_pattern = r"prop_id: '(\d+)'"
                broker_id = re.search(broder_pattern, script).group(1)
                token = re.search(token_pattern, script).group(1)
                prop_id = re.search(prop_pattern, script).group(1)
        ajax_url = 'https://shanghai.anjuke.com/v3/ajax/broker/phone/?' \
                   'broker_id=%s&token=%s&prop_id=%s&prop_city_id=%s' % (broker_id, token, prop_id, city_id)
        cookie_list = response.headers.getlist('Set-Cookie')
        cookie = ''
        for item in cookie_list:
            cookie = cookie + item.decode()
        self.ajax_headers['cookie'] = cookie
        meta_data = {
            'ext_code': ext_code,
            'broker_name': broker_name,
            'broker_company': broker_company,
            'broker_store': broker_store
        }

        yield scrapy.Request(url=ajax_url, headers=self.ajax_headers, callback=self.get_phone, meta=meta_data, dont_filter=True)

    def get_phone(self, response):
        if response.status == 200:
            json_data = json.loads(response.text)
            if json_data['code'] == 0:
                broker_phone = ''.join(json_data['val'].split())
                logger.info(broker_phone)
                item = AnjukeItem()
                item['city'] = self.city
                item['ext_code'] = response.meta['ext_code']
                item['broker_name'] = response.meta['broker_name']
                item['broker_company'] = response.meta['broker_company']
                item['broker_store'] = response.meta['broker_store']
                yield item
            else:
                logger.error('请求电话失败:%s' % json_data['msg'])
        else:
            logger.error('请求报错')

