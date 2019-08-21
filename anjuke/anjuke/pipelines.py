# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import os
import json


class AnjukePipeline(object):
    def __init__(self):
        self.file = os.path.join('.', 'anjuke_result')

    def process_item(self, item, spider):
        with open(self.file, 'ab') as f:
            line = json.dumps(dict(item)) + "\n"
            f.write(line)
        return item
