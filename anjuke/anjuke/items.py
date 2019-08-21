# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class AnjukeItem(scrapy.Item):

    city = scrapy.Field()
    ext_code = scrapy.Field()
    broker_name = scrapy.Field()
    broker_company = scrapy.Field()
    broker_store = scrapy.Field()
    broker_phone = scrapy.Field()

