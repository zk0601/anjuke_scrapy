import scrapy
from scrapy import Selector
import re
import json
import requests
from bs4 import BeautifulSoup
import os
import base64
from io import BytesIO
from fontTools.ttLib import TTFont
import decimal

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
        # self.url1 = 'https://sh.58.com/jingan/ershoufang/0/'
        self.url = 'https://sh.58.com/ershoufang/42337565589135x.shtml'

    def start_requests(self):
        # yield scrapy.Request(url=self.url1, headers=self.headers, callback=self.parse1, dont_filter=True)
        yield scrapy.Request(url=self.url, headers=self.headers, callback=self.parse, dont_filter=True)

    def get_page_show_ret(self, bs64_str, string):
        if not string:
            return ''
        try:
            font = TTFont(BytesIO(base64.decodebytes(bs64_str.encode())))
        except:
            return ''
        c = font['cmap'].tables[0].ttFont.tables['cmap'].tables[0].cmap
        ret_list = []
        for char in string:
            decode_num = ord(char)
            if decode_num in c:
                num = c[decode_num]
                num = int(num[-2:]) - 1
                ret_list.append(num)
            else:
                ret_list.append(char)
        ret_str_show = ''
        for num in ret_list:
            ret_str_show += str(num)
        return ret_str_show

    def get_bs64_str(self, response):
        script_list = response.xpath('.//script').extract()
        base64_script = ''
        for script in script_list:
            if 'base64' in script:
                base64_script = script

        r_com = re.compile('charset=utf-8;base64,(.*?)\\\'\)')
        bs64_rs = r_com.search(base64_script)
        if not bs64_rs:
            return ''
        bs64_str = bs64_rs.group(1)
        return bs64_str

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
        c_url = response.url.split('?')[0]
        gj_code = 1
        city = '贵阳'
        if not gj_code or not city:
            return
        bs64_str = self.get_bs64_str(response)

        seller_name = ''

        comm = response.css('.house-basic-item3>li:first-child>span:nth-child(2)>a:first-child').xpath('./text()').extract_first().strip()
        area = response.css('.house-basic-item3>li:first-child>span:nth-child(2)>a:nth-child(2)').xpath('./text()').extract_first().strip()
        district = response.css('.house-basic-item3>li:nth-child(2)>span:nth-child(2)>a:first-child').xpath('./text()').extract_first().strip()
        address = response.css('.house-basic-item3>li:nth-child(2)>span:nth-child(2)>a:nth-child(2)').xpath('./text()').extract_first().strip()
        address = address.replace('－', ' ').strip()

        print(comm, area, district, address)

        # house_info_value = get_page_show_ret(bs64_str, build_area_ttf)

        total_price = response.css('.price.strongbox').xpath('./text()').extract_first().strip()
        total_price = self.get_page_show_ret(bs64_str, total_price)
        total_price = decimal.Decimal(total_price) * 10000
        # unit_price = response.css('.unit.strongbox').xpath('./text()').extract_first().strip()
        build_area = response.css('.general-item-wrap>.general-item-left>li:nth-child(3)')[0]
        build_area = build_area.xpath('./span[2]/text()').extract_first().replace('㎡', '').strip()
        build_area = decimal.Decimal(build_area)
        unit_price = round(total_price / build_area)
        print(total_price, build_area, unit_price)

        title = response.css('.house-title h1').xpath('./text()').extract_first().strip()
        print(title)

        direction = response.css('.general-item-wrap>.general-item-left>li:nth-child(4)')[0]
        direction = direction.xpath('./span[2]/text()').extract_first().strip()
        fix_level = response.css('.general-item-wrap>.general-item-right>li:nth-child(2)')[0]
        fix_level = fix_level.xpath('./span[2]/text()').extract_first().strip()
        build_year = ''
        floor_info = response.css('.general-item-wrap>.general-item-right>li:nth-child(1)')[0]
        floor_info = floor_info.xpath('./span[2]/text()').extract_first().strip()
        layout_info = response.css('.general-item-wrap>.general-item-left>li:nth-child(2)')[0]
        layout_info = layout_info.xpath('./span[2]/text()').extract_first().strip()
        print(direction, fix_level, build_year, floor_info, layout_info)

        house_info = response.css('.pic-desc-word')[0].xpath('./text()').extract_first().strip()
        print(house_info)

        html_text = response.xpath('.').extract_first()

        imgs = response.css('#houseBasicPic>.basic-pic-list>ul>li')
        for img in imgs:
            img_url = img.attrib.get('data-value')
            print(img_url)
        return


    # def parse(self, response):
    #     # c_url = response.url.split('?')[0]
    #     # gj_code = 1
    #     # city = '贵阳'
    #     # if not gj_code or not city:
    #     #     return
    #     if response.status == 200:
    #         if not response.css('.content.clearfix'):
    #             html = response.body.decode()
    #             soup = BeautifulSoup(response.body, 'html.parser')
    #             js_str = soup.find('script', {'type': 'text/javascript'}).get_text()
    #             aa = js_str.split('____json4fe = ')
    #             a = aa[2].split("____json4fe.sid")[0].replace(";", "")
    #             url = "https://miniapp.58.com/landlord/getprivacyphone"
    #             payload = {
    #                 "user_id": json.loads(a)['userid'],
    #                 "info_id": 42209662457100
    #             }
    #             rs = requests.get(url, params=payload).content
    #             print(requests.get(url, params=payload).content)
    #             result_file = os.path.join('../../', '58_phone.txt')
    #             with open(result_file, 'a') as f:
    #                 f.write(rs.decode()+'\n')




