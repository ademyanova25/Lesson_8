# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import os

import scrapy
from itemadapter import ItemAdapter
from scrapy.pipelines.images import ImagesPipeline
from pymongo import MongoClient
from pprint import pprint
import hashlib
from scrapy.utils.python import to_bytes
from scrapy.http import Request


class InstagramPipeline:
    def __init__(self):
        client = MongoClient('127.0.0.1', 27017)
        self.mongobase = client['Library'].insta_spider

    def process_item(self, item, spider):
        my_item = dict(item)
        collection = self.mongobase[spider.name]
        collection.insert_one(my_item)
        return item


class LeroyPhotosPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item['follower_photo']:
            try:
                yield scrapy.Request(item['follower_photo'], meta=item)
            except Exception as e:
                print(e)

    def item_completed(self, results, item, info):
        if results:
            item['follower_photo'] = [itm[1] for itm in results if itm[0]]
        return item

    def file_path(self, request, response=None, info=None, *, item=None):
        image_guid = hashlib.sha1(to_bytes(request.url)).hexdigest()
        return f'{item["follower_name"]}/{image_guid}.jpg'
