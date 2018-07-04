# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy.exceptions import DropItem
from scrapy.pipelines.images import ImagesPipeline, ImageException
from scrapy.http import Request

class CwhPipeline(object):
    def __init__(self):
        self.ids_seen = set()

    def process_item(self, item, spider):
        ref = (spider.name, item['SKU'])
        
        if ref in self.ids_seen:
            raise DropItem("Duplicate item found: %s" % item)
        else:
            self.ids_seen.add(ref)
            item.pop('IMAGE URLS', None)
            item.pop('images', None)
            return item

class CwhImagePipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        return [Request(x, meta={'image_name': item["PRODUCT NAME"]})
                for x in item.get('IMAGE URLS', [])]
        
    def file_path(self, request, response=None, info=None):
        return '%s.jpg' % request.meta['image_name']
