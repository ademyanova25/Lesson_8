# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class InstagramItem(scrapy.Item):
    # define the fields for your item here like:
    user_id = scrapy.Field()
    username = scrapy.Field()
    follower_id = scrapy.Field()
    follower_name = scrapy.Field()
    follower_photo = scrapy.Field()
    type = scrapy.Field()
